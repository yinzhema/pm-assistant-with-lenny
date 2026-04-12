"""
Artifact Builder Agent — drives the step-by-step Q&A artifact builder.

Model tiering:
  EFFICIENT — per-answer live section preview (needs <500ms latency)
  FRONTIER  — final full artifact synthesis after all Q&A collected
"""
import asyncio
import json
from typing import AsyncIterator, Optional

from services.llm_router import LLMRouter, LLMTier


class ArtifactBuilderAgent:
    def __init__(self, retriever, llm_router: LLMRouter):
        self.retriever = retriever
        self.router = llm_router

    # ------------------------------------------------------------------
    # Per-answer section preview  [EFFICIENT model]
    # ------------------------------------------------------------------
    async def stream_section_preview(
        self,
        artifact_type: str,
        section_key: str,
        section_label: str,
        answer: str,
        answers_so_far: dict,
    ) -> AsyncIterator[str]:
        """
        Stream HTML for a single artifact section based on the user's answer.
        Keeps responses short (<150 words) for real-time rendering.
        """
        system = (
            "You are a concise PM document writer. "
            "Generate ONLY the HTML content for a single section of a PM artifact. "
            "Maximum 150 words. Use simple HTML: <p>, <ul>, <li>, <strong>. "
            "Be specific and professional — no filler phrases. "
            "Return ONLY the HTML fragment, no markdown, no code fences."
        )

        # Minimal context from prior answers to keep the section coherent
        prior_context = ""
        if answers_so_far:
            lines = [f"- {k}: {v}" for k, v in list(answers_so_far.items())[:3]]
            prior_context = "\nPrior answers for context:\n" + "\n".join(lines)

        user = (
            f"Artifact type: {artifact_type}\n"
            f"Section: {section_label}\n"
            f"User's answer: {answer}"
            f"{prior_context}\n\n"
            "Generate the HTML for this section only."
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        async for token in self.router.achat_stream(
            messages, LLMTier.EFFICIENT, temperature=0.5, max_tokens=300
        ):
            yield token

    # ------------------------------------------------------------------
    # KB snippet retrieval (no LLM — pure RAG)
    # ------------------------------------------------------------------
    def get_kb_snippet(self, kb_query: str) -> Optional[str]:
        """
        Retrieve a short inline KB snippet for the given query.
        Returns the top chunk's text, truncated to ~200 chars.
        """
        try:
            result = self.retriever.retrieve_with_context(kb_query, n_results=1)
            sources = result.get("sources", [])
            if not sources:
                return None
            top = sources[0]
            text = top.get("text", "")
            if len(text) > 220:
                text = text[:220].rsplit(" ", 1)[0] + "…"
            guest = top.get("guest", "")
            title = top.get("title", "")
            citation = f" — {guest}" if guest else ""
            if title:
                citation += f", {title}"
            return f"{text}{citation}" if text else None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Full artifact synthesis  [FRONTIER model]
    # ------------------------------------------------------------------
    async def synthesize_artifact(
        self,
        artifact_type: str,
        artifact_title: str,
        questions: list,
        answers: dict,
        skipped: list,
    ) -> AsyncIterator[str]:
        """
        Synthesize the complete artifact HTML using all collected Q&A answers.
        Uses the FRONTIER model for document-quality output.
        """
        # Retrieve KB context for synthesis
        kb_context = ""
        try:
            result = await asyncio.to_thread(
                self.retriever.retrieve_with_context,
                f"{artifact_type} {artifact_title} best practices framework",
                8,
            )
            kb_context = result.get("context", "")
        except Exception:
            pass

        # Build Q&A summary
        qa_lines = []
        for q in questions:
            qid = q["id"] if isinstance(q, dict) else q.id
            label = q["section_label"] if isinstance(q, dict) else q.section_label
            if qid in skipped:
                qa_lines.append(f"**{label}**: [skipped — leave as TBD]")
            elif qid in answers:
                qa_lines.append(f"**{label}**: {answers[qid]}")
            else:
                qa_lines.append(f"**{label}**: [not answered — leave as TBD]")

        qa_summary = "\n".join(qa_lines)

        system = (
            f"You are an expert PM document writer producing a high-quality {artifact_title}. "
            "Generate a complete, professional HTML document based on the Q&A answers below. "
            "Structure it with clear headings (<h1>, <h2>), paragraphs (<p>), and lists (<ul>/<li>) where appropriate. "
            "Synthesize the answers into coherent prose — do not just repeat them verbatim. "
            "Mark any [skipped] or [not answered] sections as '<em>TBD — to be completed</em>'. "
            "Return ONLY clean HTML. No markdown fences, no preamble."
        )

        user_parts = [f"# {artifact_title}\n\n## Answers\n{qa_summary}"]
        if kb_context:
            user_parts.append(f"\n## Relevant PM Knowledge Base Context\n{kb_context}")
        user_parts.append("\n\nGenerate the complete HTML artifact.")

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": "\n".join(user_parts)},
        ]

        async for token in self.router.achat_stream(
            messages, LLMTier.FRONTIER, temperature=0.7, max_tokens=3000
        ):
            yield token
