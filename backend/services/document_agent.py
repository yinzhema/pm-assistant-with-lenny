"""
AI co-creation agent for PM document generation and editing.
Uses GPT-4o (not mini) for document-quality output grounded in the PM knowledge base.
"""
import os
import re
from typing import Optional, List, Dict

from openai import OpenAI

# Template IDs and their human-readable names
TEMPLATES = {
    # Docs
    "prd-1pager":          "PRD (1-pager)",
    "prd-full":            "PRD (Full)",
    "strategy-doc":        "Strategy Doc",
    # Prioritization
    "rice":                "RICE Prioritization",
    "ice":                 "ICE Prioritization",
    "moscow":              "MoSCoW Prioritization",
    "kano":                "Kano Model",
    "wsjf":                "WSJF Prioritization",
    # Roadmap
    "now-next-later":      "Now / Next / Later Roadmap",
    "outcome-roadmap":     "Outcome-Based Roadmap",
    # Discovery
    "jtbd":                "Jobs-to-be-Done",
    "opp-solution-tree":   "Opportunity Solution Tree",
}

# Keywords that map chat messages to template IDs
# Checked in order — first match wins. More specific phrases go before generic ones.
_INTENT_KEYWORDS: List[tuple] = [
    ("prd-full",          ["full prd", "detailed prd", "product requirements document"]),
    ("prd-1pager",        ["1-pager", "one pager", "one-pager", "prd"]),
    ("strategy-doc",      ["strategy doc", "strategic doc", "strategy document", "strategic document",
                           "strategy", "strategic"]),
    ("rice",              ["rice score", "rice framework", "rice model", "rice prioritization", "rice"]),
    ("ice",               ["ice score", "ice framework", "ice model", "ice"]),
    ("moscow",            ["moscow", "must have", "should have", "could have"]),
    ("kano",              ["kano"]),
    ("wsjf",              ["wsjf", "weighted shortest"]),
    ("now-next-later",    ["now next later", "now/next/later"]),
    # outcome-roadmap: catch all "outcome * roadmap" phrasings and bare "template for roadmap"
    ("outcome-roadmap",   ["outcome based roadmap", "outcome-based roadmap", "outcome roadmap",
                           "outcome driven roadmap", "outcome-driven roadmap", "outcomes roadmap",
                           "outcome-based", "template for roadmap", "roadmap template"]),
    ("jtbd",              ["jobs to be done", "jobs-to-be-done", "jtbd", "job to be done"]),
    ("opp-solution-tree", ["opportunity solution tree", "opp solution tree",
                           "opportunity-solution tree"]),
    # Generic fallbacks (must come last)
    ("outcome-roadmap",   ["roadmap"]),   # bare "roadmap" with a generate verb → outcome-based
    ("rice",              ["prioriti"]),  # "prioritize/prioritization" → RICE as default
]

_GENERATE_VERBS = ["create", "write", "build", "generate", "make", "draft", "help me"]

# Keywords for MENTIONING a template type (no generate verb needed) — used for offer CTA
_MENTION_KEYWORDS: List[tuple] = [
    ("outcome-roadmap",   ["outcome based roadmap", "outcome-based roadmap",
                           "outcome driven roadmap", "outcome-driven roadmap",
                           "outcome roadmap", "outcomes roadmap",
                           "template for roadmap", "roadmap template",
                           "outcome-based", "outcome based"]),
    ("now-next-later",    ["now next later", "now/next/later"]),
    ("rice",              ["rice framework", "rice scoring", "rice model", "rice prioritization"]),
    ("ice",               ["ice framework", "ice scoring", "ice model"]),
    ("moscow",            ["moscow framework", "moscow model", "moscow method"]),
    ("kano",              ["kano model", "kano framework"]),
    ("wsjf",              ["wsjf", "weighted shortest job first"]),
    ("prd-full",          ["product requirements document", "full prd", "detailed prd"]),
    ("prd-1pager",        ["one-page prd", "1-page prd", "prd 1-pager", "one pager prd"]),
    ("strategy-doc",      ["strategy document", "strategy doc", "strategic document", "strategic doc"]),
    ("jtbd",              ["jobs to be done", "jtbd", "job to be done"]),
    ("opp-solution-tree", ["opportunity solution tree", "opportunity-solution tree"]),
]


class DocumentAgent:
    """GPT-4o powered document co-creation grounded in the PM knowledge base."""

    def __init__(self, retriever, model: str = "gpt-4o"):
        self.retriever = retriever
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    # ── Public API ────────────────────────────────────────────────────────────

    def detect_template_mention(self, message: str) -> Optional[str]:
        """
        Detect if a message MENTIONS a PM artifact type without requiring a generate verb.
        Used to surface a template creation offer CTA after the assistant's response.
        Returns a template_id string or None.
        """
        msg = message.lower()
        for template_id, keywords in _MENTION_KEYWORDS:
            if any(kw in msg for kw in keywords):
                return template_id
        return None

    def detect_template_intent(self, message: str) -> Optional[str]:
        """
        Detect if a chat message is asking to create a PM artifact.
        Returns a template_id string or None.
        Fast heuristic — no LLM call needed.
        """
        msg = message.lower()
        has_verb = any(v in msg for v in _GENERATE_VERBS)
        if not has_verb:
            return None
        for template_id, keywords in _INTENT_KEYWORDS:
            if any(kw in msg for kw in keywords):
                return template_id
        return None

    def generate_from_template(
        self,
        template_id: str,
        user_context: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """
        Generate a PM artifact as Tiptap-compatible HTML.

        Args:
            template_id:          One of the TEMPLATES keys.
            user_context:         The user's description / chat message.
            conversation_history: Recent chat for additional context.

        Returns:
            HTML string suitable for injecting into the Tiptap editor.
        """
        rag_context = self._retrieve_context(
            f"{TEMPLATES.get(template_id, '')} {user_context}"
        )
        system = self._template_system_prompt(template_id)
        user_msg = self._build_generate_prompt(template_id, user_context, rag_context)

        messages = [{"role": "system", "content": system}]
        if conversation_history:
            messages.extend(conversation_history[-4:])
        messages.append({"role": "user", "content": user_msg})

        html = self._call(messages, max_tokens=2000)
        return self._ensure_html(html)

    def improve_selection(
        self,
        selected_text: str,
        full_document: str,
        instruction: str,
    ) -> str:
        """
        Rewrite a selected passage according to instruction.
        instruction: 'improve' | 'expand' | 'critique' | 'simplify' | 'rewrite'

        Returns replacement HTML for the selection only.
        """
        rag_context = self._retrieve_context(selected_text)
        action_desc = {
            "improve":  "Improve the clarity, precision, and impact of the following text. Keep the same meaning but make it sharper and more compelling.",
            "expand":   "Expand the following text with more detail, examples, and supporting reasoning. Ground it in PM best practices.",
            "critique": "Critically review the following text as a senior PM would. Identify weaknesses, missing elements, and suggest specific improvements. Return the critique as structured HTML.",
            "simplify": "Simplify the following text. Remove jargon, shorten sentences, and make it easier to understand without losing substance.",
            "rewrite":  "Rewrite the following text from scratch. Keep the core idea but find a clearer, more effective way to express it.",
        }.get(instruction, "Improve the following text.")

        prompt = f"""{action_desc}

SELECTED TEXT:
{selected_text}

DOCUMENT CONTEXT (for coherence — do not rewrite this, just use for context):
{self._strip_html(full_document)[:1500]}

PM KNOWLEDGE BASE CONTEXT:
{rag_context}

Return ONLY the replacement HTML for the selected text. No preamble, no explanation."""

        messages = [
            {"role": "system", "content": "You are an expert PM writing coach. Return clean HTML only — no markdown, no code fences."},
            {"role": "user", "content": prompt},
        ]
        html = self._call(messages, max_tokens=800)
        return self._ensure_html(html)

    def critique_document(self, document_html: str, template_id: str) -> str:
        """
        Provide a structured critique of the document grounded in PM best practices.
        Returns HTML critique (displayed in the canvas as a separate panel or inline).
        """
        doc_text = self._strip_html(document_html)
        template_name = TEMPLATES.get(template_id, "PM document")
        rag_context = self._retrieve_context(f"best practices for {template_name} common mistakes")

        prompt = f"""You are reviewing a {template_name} as a senior product leader.

DOCUMENT:
{doc_text[:3000]}

PM KNOWLEDGE BASE CONTEXT:
{rag_context}

Provide a structured critique covering:
1. What's strong
2. What's missing or weak
3. Specific suggestions to improve it (be concrete, reference frameworks where relevant)

Return as clean HTML with <h3> headers and <ul>/<li> for suggestions."""

        messages = [
            {"role": "system", "content": "You are a senior PM coach. Return clean HTML only."},
            {"role": "user", "content": prompt},
        ]
        return self._call(messages, max_tokens=1000)

    # ── Template system prompts ───────────────────────────────────────────────

    def _template_system_prompt(self, template_id: str) -> str:
        base = (
            "You are an expert product management advisor. Generate high-quality PM documents "
            "grounded in best practices from SVPG, Lenny's Podcast, Intercom, and Stratechery. "
            "Return ONLY clean HTML — no markdown, no code fences, no preamble. "
            "Use <h1>, <h2>, <h3>, <p>, <ul>, <li>, <table>, <th>, <td>, <strong>, <em> tags. "
            "Make documents practical, specific, and actionable."
        )
        specifics = {
            "prd-1pager": " Keep it to one page. Use sections: Problem, Solution, Goals, Non-goals, Key Metrics, Open Questions.",
            "prd-full": " Include: Overview, Problem Statement, Goals & Success Metrics, User Stories, Functional Requirements, Non-functional Requirements, Out of Scope, Open Questions, Timeline.",
            "strategy-doc": " Include: Context & Background, Strategic Bets, Why Now, Competitive Landscape, Key Risks, Success Metrics, Next Steps.",
            "rice": " Generate a RICE scoring table with columns: Feature, Reach, Impact (0.25/0.5/1/2/3), Confidence (%), Effort (person-weeks), RICE Score. Include 5-8 example features based on the user's context.",
            "ice": " Generate an ICE scoring table with columns: Feature, Impact (1-10), Confidence (1-10), Ease (1-10), ICE Score. Include 5-8 features.",
            "moscow": " Organize features into Must Have, Should Have, Could Have, Won't Have sections with rationale for each.",
            "kano": " Generate a Kano model with sections: Must-Be (Basic), Performance (Linear), Delighters (Excitement), Indifferent, Reverse. Include a table mapping features to categories.",
            "wsjf": " Generate a WSJF table with columns: Feature, User/Business Value, Time Criticality, Risk Reduction, Job Size, WSJF Score. Include 5-8 features.",
            "now-next-later": " Create a Now / Next / Later roadmap table. Now = current quarter, Next = next quarter, Later = 6+ months. Include theme, initiative, and outcome columns.",
            "outcome-roadmap": " Organize by outcomes (not features). For each outcome: the goal, why it matters, leading indicators, and initiatives to achieve it.",
            "jtbd": " Use the format: When [situation], I want to [motivation], so I can [expected outcome]. Include 5-8 jobs across different user segments. Add a section on underserved jobs.",
            "opp-solution-tree": " Structure as: Desired Outcome → Opportunities (3-5) → Solutions per opportunity (2-3 each) → Assumptions to test. Use a hierarchical HTML structure.",
        }
        return base + specifics.get(template_id, "")

    def _build_generate_prompt(
        self, template_id: str, user_context: str, rag_context: str
    ) -> str:
        template_name = TEMPLATES.get(template_id, "document")
        return f"""Create a {template_name} for the following:

USER CONTEXT:
{user_context}

PM KNOWLEDGE BASE (use this to ground your output in best practices):
{rag_context}

Generate the complete {template_name} as clean HTML. Be specific — use the user's context to fill in real content, not placeholders."""

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _retrieve_context(self, query: str, n: int = 5) -> str:
        try:
            result = self.retriever.retrieve_with_context(query, n_results=n)
            return result.get("context", "")
        except Exception:
            return ""

    def _call(self, messages: List[Dict], max_tokens: int = 1500) -> str:
        if not self.client:
            return "<p>OPENAI_API_KEY not set.</p>"
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            print(f"[DocumentAgent] LLM call failed: {e}")
            return "<p>Error generating document. Please try again.</p>"

    def _strip_html(self, html: str) -> str:
        return re.sub(r"<[^>]+>", " ", html).strip()

    def _ensure_html(self, text: str) -> str:
        """Wrap plain text in <p> tags if the model forgot to return HTML."""
        text = text.strip()
        # Strip code fences if model wrapped output
        text = re.sub(r"^```html?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()
        if text and not text.startswith("<"):
            text = "<p>" + text.replace("\n\n", "</p><p>") + "</p>"
        return text
