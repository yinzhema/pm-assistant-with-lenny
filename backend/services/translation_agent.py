"""
Translation Agent — drives PRD → agent.md conversion.

Model tiering:
  FRONTIER  — PRD extraction, agent.md generation, gap analysis, final synthesis
  EFFICIENT — per-gap clarification Q&A (fast resolution of individual gaps)
"""
import asyncio
import json
from typing import AsyncIterator

from data.agent_md_template import AGENT_MD_SECTIONS, GAP_CATEGORIES
from services.llm_router import LLMRouter, LLMTier


class TranslationAgent:
    def __init__(self, retriever, llm_router: LLMRouter):
        self.retriever = retriever
        self.router = llm_router

    # ------------------------------------------------------------------
    # Phase 1: Extract structured content from PRD  [FRONTIER]
    # ------------------------------------------------------------------
    async def stream_extract_prd(self, prd_text: str) -> AsyncIterator[tuple[str, dict]]:
        """
        Yields:
          ("token", text)  — progress tokens while extracting
          ("done", dict)   — final extracted_sections dict
        """
        system = (
            "You are a technical analyst extracting structured information from a Product Requirements Document. "
            "Extract the following sections into a JSON object. "
            "For each field, copy relevant text verbatim from the PRD when possible. "
            "If a section is not present in the PRD, set it to null.\n\n"
            "Required JSON schema:\n"
            "{\n"
            '  "product_name": "string or null",\n'
            '  "purpose": "what this product/feature does",\n'
            '  "users": "who uses it and what they need",\n'
            '  "capabilities": ["list of capabilities"],\n'
            '  "tools_integrations": ["list of tools/APIs mentioned"],\n'
            '  "constraints": ["list of constraints or limitations"],\n'
            '  "success_metrics": ["list of metrics or success criteria"],\n'
            '  "scope_boundaries": "what is explicitly out of scope",\n'
            '  "implicit_judgments": ["phrases like \'use best judgment\', \'as appropriate\', etc."],\n'
            '  "escalation_hints": ["any mentions of approval flows, human review, etc."]\n'
            "}\n\n"
            "Return ONLY valid JSON. No markdown fences, no explanation."
        )

        user = f"PRD to extract:\n\n{prd_text[:8000]}"  # cap at 8k chars
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        full_response = ""
        async for token in self.router.achat_stream(
            messages, LLMTier.FRONTIER, temperature=0.1, max_tokens=1500
        ):
            full_response += token
            yield ("token", token)

        # Parse JSON
        try:
            # Strip markdown fences if model included them anyway
            clean = full_response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            extracted = json.loads(clean.strip())
        except Exception:
            extracted = {"error": "Failed to parse PRD", "raw": full_response[:500]}

        yield ("done", extracted)

    # ------------------------------------------------------------------
    # Phase 2: Generate agent.md sections  [FRONTIER]
    # ------------------------------------------------------------------
    async def stream_generate_agent_md(
        self, extracted_sections: dict
    ) -> AsyncIterator[tuple[str, any]]:
        """
        Yields:
          ("token", text)              — streaming tokens
          ("section", section_dict)    — completed section: {section_key, html, confidence}
          ("done", list[section_dict]) — all sections
        """
        sections_prompt = "\n".join(
            f"- {s.key} ({s.label}): {s.description}"
            for s in AGENT_MD_SECTIONS
        )

        system = (
            "You are an expert at converting product requirements into agent.md specifications. "
            "Transform the extracted PRD content into an agent.md with these sections:\n"
            f"{sections_prompt}\n\n"
            "For EACH section, output a JSON object on its own line:\n"
            '{"section_key": "...", "html": "<p>...</p>", "confidence": "green|yellow|red"}\n\n'
            "Confidence levels:\n"
            "  green  = directly and clearly derivable from the PRD\n"
            "  yellow = requires inference — PM should review\n"
            "  red    = missing from PRD — agent cannot determine this\n\n"
            "For red sections, write: <p><em>[MISSING: brief description of what's needed]</em></p>\n"
            "Use clean HTML: <p>, <ul>, <li>, <strong>, <table>, <tr>, <td>. No markdown."
        )

        user = f"Extracted PRD content:\n{json.dumps(extracted_sections, indent=2)}"
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        full_response = ""
        async for token in self.router.achat_stream(
            messages, LLMTier.FRONTIER, temperature=0.3, max_tokens=3000
        ):
            full_response += token
            yield ("token", token)

        # Parse the line-by-line JSON objects
        sections = []
        for line in full_response.splitlines():
            line = line.strip()
            if line.startswith("{") and "section_key" in line:
                try:
                    sec = json.loads(line)
                    sections.append(sec)
                    yield ("section", sec)
                except Exception:
                    pass

        yield ("done", sections)

    # ------------------------------------------------------------------
    # Phase 3: Gap analysis  [FRONTIER]
    # ------------------------------------------------------------------
    async def analyze_gaps(
        self, prd_text: str, agent_sections: list
    ) -> list[dict]:
        """
        Returns a list of GapItem dicts across 6 categories.
        Single non-streaming call — ~5s acceptable.
        """
        categories_desc = "\n".join(
            f"  - {c}" for c in GAP_CATEGORIES
        )
        red_sections = [
            s for s in agent_sections if s.get("confidence") == "red"
        ]
        yellow_sections = [
            s for s in agent_sections if s.get("confidence") == "yellow"
        ]

        system = (
            "You are a rigorous PRD reviewer analyzing gaps between a human-readable PRD "
            "and an agent.md specification.\n\n"
            "Identify gaps in EACH of these categories:\n"
            f"{categories_desc}\n\n"
            "Return a JSON array of gap objects. Each object:\n"
            "{\n"
            '  "category": "one of the categories above",\n'
            '  "section": "which agent.md section is affected",\n'
            '  "description": "what is missing or ambiguous",\n'
            '  "severity": "high|medium|low",\n'
            '  "suggested_question": "the clarifying question to ask the PM"\n'
            "}\n\n"
            "Return ONLY a valid JSON array. No explanation."
        )

        user = (
            f"PRD (first 4000 chars):\n{prd_text[:4000]}\n\n"
            f"Red (missing) sections: {json.dumps(red_sections)}\n"
            f"Yellow (uncertain) sections: {json.dumps(yellow_sections)}"
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        response = await self.router.achat(
            messages, LLMTier.FRONTIER, temperature=0.2, max_tokens=2000
        )

        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            gaps = json.loads(clean.strip())
            if not isinstance(gaps, list):
                gaps = []
        except Exception:
            gaps = []

        return gaps

    # ------------------------------------------------------------------
    # Clarification: resolve a single gap  [EFFICIENT]
    # ------------------------------------------------------------------
    async def stream_resolve_clarification(
        self,
        section_key: str,
        section_label: str,
        gap_description: str,
        pm_answer: str,
        current_html: str,
    ) -> AsyncIterator[tuple[str, str]]:
        """
        Yields:
          ("token", text)    — streaming tokens
          ("done", html)     — final updated section HTML
        """
        system = (
            "You are updating a single section of an agent.md specification based on "
            "a PM's clarifying answer. Return ONLY the updated HTML for that section. "
            "Keep it concise. Use <p>, <ul>, <li>, <strong>. No markdown fences."
        )
        user = (
            f"Section: {section_label}\n"
            f"Gap that was identified: {gap_description}\n"
            f"PM's answer: {pm_answer}\n\n"
            f"Current section HTML:\n{current_html}\n\n"
            "Return updated HTML for this section only."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        full = ""
        async for token in self.router.achat_stream(
            messages, LLMTier.EFFICIENT, temperature=0.4, max_tokens=500
        ):
            full += token
            yield ("token", token)

        yield ("done", full)

    # ------------------------------------------------------------------
    # Final synthesis incorporating all clarifications  [FRONTIER]
    # ------------------------------------------------------------------
    async def stream_finalize(
        self,
        agent_sections: list,
        clarifications: dict,
        agent_name: str = "Agent",
    ) -> AsyncIterator[tuple[str, str]]:
        """
        Yields:
          ("token", text)  — streaming tokens
          ("done", html)   — final complete agent.md HTML
        """
        # Retrieve KB context for agent.md best practices
        kb_context = ""
        try:
            result = await asyncio.to_thread(
                self.retriever.retrieve_with_context,
                "AI agent specification CLAUDE.md agent.md best practices",
                4,
            )
            kb_context = result.get("context", "")
        except Exception:
            pass

        sections_summary = "\n".join(
            f"## {s.get('section_key', '?')}\n{s.get('html', '')}"
            for s in agent_sections
        )
        clarifications_summary = "\n".join(
            f"- {qid}: {ans}" for qid, ans in clarifications.items()
        )

        system = (
            "You are producing the final, polished agent.md specification. "
            "Incorporate all sections and clarifications into one clean, complete HTML document. "
            "Use <h1> for agent name, <h2> for sections, <h3> for subsections. "
            "Mark nothing as missing — use the clarifications to fill gaps. "
            "Return ONLY clean HTML. No markdown fences, no preamble."
        )

        user_parts = [
            f"Agent name: {agent_name}",
            f"\nCurrent sections:\n{sections_summary}",
        ]
        if clarifications_summary:
            user_parts.append(f"\nClarifications from PM:\n{clarifications_summary}")
        if kb_context:
            user_parts.append(f"\nPM Knowledge Base context:\n{kb_context}")
        user_parts.append("\n\nGenerate the complete final agent.md HTML.")

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": "\n".join(user_parts)},
        ]

        full = ""
        async for token in self.router.achat_stream(
            messages, LLMTier.FRONTIER, temperature=0.5, max_tokens=3000
        ):
            full += token
            yield ("token", token)

        yield ("done", full)
