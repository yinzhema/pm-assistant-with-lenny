"""
AskProduct v2 — AI-powered PM workspace.
Chat mode: single-column Q&A grounded in multi-source PM knowledge base.
Workspace mode: split-panel chat + live document canvas.
"""
import os
from datetime import datetime
from typing import List, Dict, Optional

import streamlit as st
from dotenv import load_dotenv

from src.retrieval.vector_store import VectorStore
from src.ingestion.embedder import EmbeddingGenerator
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.bm25_index import BM25Index
from src.agent.pm_assistant import PMAssistant
from src.agent.document_agent import DocumentAgent, TEMPLATES
from src.storage.conversation_store import submit_feedback
from src.ui.document_canvas import render_canvas, render_template_picker
from src.agent import export as doc_export

load_dotenv()

st.set_page_config(
    page_title="AskProduct",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── CSS ───────────────────────────────────────────────────────────────────────

def _inject_css(workspace_mode: bool):
    max_width = "100%" if workspace_mode else "760px"
    st.markdown(f"""
<style>
  /* ── Streamlit chrome ── */
  #MainMenu {{visibility:hidden;}}
  footer {{visibility:hidden;}}
  [data-testid="stDecoration"] {{display:none!important;}}
  [data-testid="stHeader"] {{background:transparent!important;border-bottom:none!important;pointer-events:none!important;}}
  [data-testid="stToolbar"] {{visibility:hidden!important;}}
  [data-testid="stStatusWidget"] {{display:none!important;}}
  [data-testid="stSidebar"] {{display:none!important;}}
  [data-testid="collapsedControl"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="stCollapsedControl"] {{display:none!important;}}

  /* ── Layout ── */
  .main {{padding:0!important;}}
  .main .block-container {{
    padding-top:3.75rem!important;
    padding-bottom:3rem!important;
    max-width:{max_width}!important;
    margin:0 auto!important;
    {"padding-left:1.25rem!important;padding-right:1.25rem!important;" if workspace_mode else ""}
  }}

  /* ── Top bar (4-col or 5-col row) ── */
  [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4)) {{
    position:fixed!important;top:0!important;left:0!important;right:0!important;
    z-index:200!important;width:100%!important;max-width:100%!important;
    height:3.5rem!important;min-height:3.5rem!important;box-sizing:border-box!important;
    margin:0!important;padding:0 1.25rem 0 1.5rem!important;gap:0.75rem!important;
    flex-wrap:nowrap!important;align-items:center!important;
    background:#ffffff!important;border-bottom:1px solid #e5e7eb!important;
  }}
  [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4))
    [data-testid="column"] {{min-width:0!important;padding-top:0!important;padding-bottom:0!important;}}
  .app-header-title {{
    font-size:0.95rem!important;font-weight:700!important;color:#111827!important;
    letter-spacing:-0.01em!important;line-height:1.2!important;margin:0!important;
  }}
  [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4))
    [data-testid="column"]:nth-child(n+3) {{
    flex:0 0 auto!important;width:auto!important;min-width:fit-content!important;
    display:flex!important;justify-content:flex-end!important;align-items:center!important;
  }}
  [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4)) button {{
    background:white!important;color:#6b7280!important;border:1px solid #e5e7eb!important;
    border-radius:8px!important;padding:0.35rem 0.85rem!important;font-size:0.875rem!important;
    font-weight:500!important;min-height:unset!important;white-space:nowrap!important;
    width:auto!important;transition:all 0.15s!important;
  }}
  [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4)) button:hover {{
    background:#f3f4f6!important;color:#111827!important;border-color:#d1d5db!important;
  }}
  /* Workspace button — highlighted when active */
  button[data-testid="stBaseButton-secondary"].workspace-active {{
    background:#eff6ff!important;color:#1d4ed8!important;border-color:#bfdbfe!important;
  }}

  /* ── Feedback form ── */
  [data-testid="stForm"] {{
    position:fixed!important;top:3.5rem!important;left:50%!important;
    transform:translateX(-50%)!important;z-index:150!important;
    width:min(760px,calc(100vw - 2rem))!important;background:white!important;
    border:1px solid #e5e7eb!important;border-radius:0 0 14px 14px!important;
    padding:1.25rem 1.5rem!important;margin:0!important;
    box-shadow:0 8px 24px rgba(0,0,0,.10)!important;
  }}

  /* ── Empty state ── */
  .empty-state {{text-align:center;padding:3rem 2rem 2rem;}}
  .empty-state-icon {{
    background:#111827;width:68px;height:68px;border-radius:16px;
    display:inline-flex;align-items:center;justify-content:center;margin-bottom:1.25rem;
  }}

  /* ── Sample question cards ── */
  [data-testid="stColumns"] .stButton button {{
    background:#fafafa!important;color:#374151!important;
    border:1px solid #e5e7eb!important;border-radius:10px!important;
    font-size:0.875rem!important;padding:0.75rem 1rem!important;
    text-align:left!important;font-weight:400!important;line-height:1.45!important;
    transition:all 0.15s!important;min-height:unset!important;
  }}
  [data-testid="stColumns"] .stButton button:hover {{
    background:#f3f4f6!important;border-color:#d1d5db!important;color:#111827!important;
  }}

  /* ── Chat bubbles ── */
  .message-user {{
    background:#2563eb;color:white;
    padding:0.875rem 1.125rem;border-radius:1rem 1rem 0.25rem 1rem;
    margin:0.75rem 0 0.75rem auto;width:fit-content;max-width:85%;
    line-height:1.55;word-wrap:break-word;
  }}
  .message-assistant {{
    background:#f1f5f9;color:#0f172a;
    padding:0.875rem 1.125rem;border-radius:1rem 1rem 1rem 0.25rem;
    margin:0.75rem 0;width:100%;line-height:1.55;word-wrap:break-word;
  }}

  /* ── Workspace: canvas column ── */
  .canvas-panel {{
    border-left:1px solid #e5e7eb;
    padding-left:1.25rem;
  }}
  .canvas-header {{
    font-size:0.78rem;font-weight:600;color:#9ca3af;
    text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.75rem;
  }}

  /* ── Document toolbar buttons ── */
  [data-testid="stBaseButton-secondary"]:has(div:contains("💾")),
  [data-testid="stBaseButton-secondary"]:has(div:contains("⬇️")),
  [data-testid="stBaseButton-secondary"]:has(div:contains("📊")),
  [data-testid="stBaseButton-secondary"]:has(div:contains("🕐")),
  [data-testid="stBaseButton-secondary"]:has(div:contains("✕")) {{
    font-size:0.78rem!important;padding:0.3rem 0.5rem!important;
    border-radius:6px!important;
  }}

  /* ── Workspace divider ── */
  .ws-divider {{
    width:1px;background:#e5e7eb;align-self:stretch;margin:0 0.5rem;
  }}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────

def init_session_state():
    defaults = {
        "messages":        [],
        "show_feedback":   False,
        "workspace_mode":  False,
        # Document state
        "document_html":   "",
        "document_title":  "Untitled",
        "document_id":     None,
        "template_id":     None,
        "show_templates":  False,
        "pending_action":  None,   # {action, selectedText, fullHtml}
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── Initialization ────────────────────────────────────────────────────────────

@st.cache_resource
def initialize_all():
    """Initialize all components (cached across reruns)."""
    for var in ("OPENAI_API_KEY", "PINECONE_API_KEY"):
        if not os.getenv(var):
            st.error(f"⚠️ {var} not found.")
            st.stop()

    vector_store = VectorStore()
    embedder     = EmbeddingGenerator()
    bm25         = BM25Index()
    bm25.load(BM25Index.DEFAULT_CORPUS_PATH)

    retriever    = HybridRetriever(vector_store, embedder, bm25)
    pm_assistant = PMAssistant(retriever)
    doc_agent    = DocumentAgent(retriever)

    return pm_assistant, doc_agent, vector_store


# ── Top bar ───────────────────────────────────────────────────────────────────

def render_top_bar(workspace_mode: bool):
    """Fixed header: logo · spacer · Feedback · New chat · Workspace"""
    c_logo, _sp, c_fb, c_nc, c_ws = st.columns(
        [2.4, 3.5, 1.6, 1.6, 1.8], gap="small"
    )
    with c_logo:
        st.markdown(
            '<p class="app-header-title">🎙️&nbsp;&nbsp;AskProduct</p>',
            unsafe_allow_html=True,
        )
    with _sp:
        st.empty()
    with c_fb:
        fb = st.button("💬  Feedback", key="feedback_btn")
    with c_nc:
        nc = st.button("↺  New chat",  key="new_chat_btn")
    with c_ws:
        ws_label = "⬅️  Chat" if workspace_mode else "🖊️  Workspace"
        ws = st.button(ws_label, key="workspace_btn")
    return fb, nc, ws


def render_feedback_form():
    with st.form("feedback_form", clear_on_submit=True):
        st.markdown("**Share feedback** — What would you like to see?")
        comment = st.text_area(
            "feedback_input",
            placeholder="Your thoughts or feature requests...",
            label_visibility="collapsed",
            height=80,
        )
        c1, c2, _ = st.columns([1, 1, 3])
        with c1:
            submitted = st.form_submit_button("Submit", use_container_width=True)
        with c2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

    if submitted and comment.strip():
        submit_feedback("anonymous", comment)
        st.session_state.show_feedback = False
        st.toast("Thanks for your feedback!", icon="✓")
        st.rerun()
    elif submitted or cancelled:
        st.session_state.show_feedback = False
        st.rerun()


# ── Chat mode ─────────────────────────────────────────────────────────────────

def render_empty_state(assistant: PMAssistant) -> Optional[str]:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-state-icon"><span style="font-size:38px;">🎙️</span></div>
      <h1 style="font-size:2.25rem;margin:0 0 0.5rem;color:#0f172a;font-weight:800;letter-spacing:-0.02em;">
        AskProduct
      </h1>
      <p style="font-size:1.1rem;color:#64748b;margin:0 0 2.25rem;line-height:1.6;">
        Your AI thinking partner for product management
      </p>
    </div>""", unsafe_allow_html=True)

    st.markdown(
        '<p style="font-size:0.78rem;font-weight:600;color:#9ca3af;'
        'text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.6rem;">Try asking</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for idx, q in enumerate(assistant.get_example_questions()[:6]):
        with cols[idx % 2]:
            if st.button(q, key=f"sample_{idx}", use_container_width=True):
                return q
    return None


def render_chat_messages(messages: List[Dict]):
    for msg in messages:
        cls = "message-user" if msg["role"] == "user" else "message-assistant"
        st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)

        if msg.get("sources"):
            with st.expander("📚 View Sources"):
                for src in msg["sources"]:
                    guest       = src.get("guest", "")
                    author      = src.get("author", "")
                    source_name = src.get("source_name", "Lenny's Podcast")
                    display     = guest or author or source_name

                    st.markdown(f"**{src['number']}. {display}** — {src['title']}")
                    st.caption(source_name)

                    yt_url    = src.get("youtube_url", "")
                    art_url   = src.get("url", "")
                    timestamp = src.get("timestamp", "")

                    if yt_url and timestamp:
                        ts = timestamp.replace(":", "h", 1).replace(":", "m") + "s"
                        st.markdown(f"[▶️ Watch at {timestamp}]({yt_url}&t={ts})")
                    elif art_url:
                        st.markdown(f"[🔗 Read article]({art_url})")

                    st.caption(f"Relevance: {src['similarity_score']:.1%}")
                    st.divider()


def handle_chat_message(
    prompt: str,
    assistant: PMAssistant,
    doc_agent: DocumentAgent,
    conversation_history: List[Dict],
):
    """Process a user message, detect template intent, generate response."""
    st.session_state.messages.append({
        "role": "user", "content": prompt, "timestamp": datetime.now(),
    })

    # Check if message wants to generate a document
    template_id = doc_agent.detect_template_intent(prompt)

    with st.spinner("Thinking…"):
        result = assistant.answer_question(
            prompt,
            conversation_history=conversation_history or None,
            n_results=8,
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result.get("sources", []),
        "timestamp": datetime.now(),
    })

    # If template intent detected, auto-open workspace and generate doc
    if template_id and not st.session_state.workspace_mode:
        st.session_state.workspace_mode = True
        st.session_state.template_id    = template_id
        st.session_state.document_title = TEMPLATES.get(template_id, "Document")
        st.session_state.show_templates  = False

        with st.spinner(f"Generating {TEMPLATES[template_id]}…"):
            html = doc_agent.generate_from_template(
                template_id, prompt, conversation_history
            )
        st.session_state.document_html = html


# ── Workspace mode ────────────────────────────────────────────────────────────

def render_workspace(assistant: PMAssistant, doc_agent: DocumentAgent):
    """Two-panel layout: chat (left) + document canvas (right)."""
    col_chat, col_canvas = st.columns([1, 1], gap="large")

    # ── Left: Chat ────────────────────────────────────────────────────────────
    with col_chat:
        st.markdown(
            '<p class="canvas-header">Chat</p>',
            unsafe_allow_html=True,
        )

        # Chat history
        if st.session_state.messages:
            render_chat_messages(st.session_state.messages)
        else:
            st.markdown(
                '<p style="color:#9ca3af;font-size:0.9rem;margin-top:1rem;">'
                'Ask a question or describe what you want to create.</p>',
                unsafe_allow_html=True,
            )

        prompt = st.chat_input("Ask or generate a document…", key="ws_chat_input")
        if prompt:
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[-6:-1]
                if m["role"] in ("user", "assistant")
            ]
            handle_chat_message(prompt, assistant, doc_agent, history)
            st.rerun()

    # ── Right: Canvas ─────────────────────────────────────────────────────────
    with col_canvas:
        st.markdown(
            '<p class="canvas-header">Document</p>',
            unsafe_allow_html=True,
        )

        # No document yet → show template picker
        if not st.session_state.document_html:
            selected_tpl = render_template_picker()
            if selected_tpl:
                st.session_state.template_id    = selected_tpl
                st.session_state.document_title = TEMPLATES.get(selected_tpl, "Document")
                st.session_state.show_templates  = False

                with st.spinner(f"Generating {TEMPLATES[selected_tpl]}…"):
                    html = doc_agent.generate_from_template(selected_tpl, "")
                st.session_state.document_html = html
                st.rerun()
        else:
            # Document exists — show canvas
            result = render_canvas(
                content_html=st.session_state.document_html,
                document_id=st.session_state.document_id,
                title=st.session_state.document_title,
                height=560,
            )
            _handle_canvas_action(result, doc_agent)


def _handle_canvas_action(result: Optional[dict], doc_agent: DocumentAgent):
    """Route canvas component events to the right handler."""
    if not result or result.get("type") != "action":
        return

    action       = result.get("action", "")
    full_html    = result.get("fullHtml", st.session_state.document_html)
    selected     = result.get("selectedText", "")

    # Keep document_html in sync
    if full_html:
        st.session_state.document_html = full_html

    if action in ("improve", "expand", "critique", "simplify", "rewrite"):
        if not selected:
            st.warning("Select some text first, then click an action.")
            return
        with st.spinner(f"AI is working on '{action}'…"):
            replacement = doc_agent.improve_selection(selected, full_html, action)
        # Replace selected text with AI output in the HTML
        if replacement:
            st.session_state.document_html = full_html.replace(
                selected, replacement, 1
            )
        st.rerun()

    elif action == "save":
        _save_document()

    elif action == "export_md":
        md = doc_export.export_to_markdown(
            full_html, st.session_state.document_title
        )
        fname = (st.session_state.document_title or "document").replace(" ", "_") + ".md"
        st.download_button(
            "⬇️ Download Markdown",
            data=md,
            file_name=fname,
            mime="text/markdown",
            key="dl_md",
        )

    elif action == "export_excel":
        xlsx = doc_export.export_to_excel(
            full_html, st.session_state.document_title
        )
        fname = (st.session_state.document_title or "document").replace(" ", "_") + ".xlsx"
        st.download_button(
            "⬇️ Download Excel",
            data=xlsx,
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_xl",
        )

    elif action == "versions":
        _show_versions(doc_agent)

    elif action == "close":
        st.session_state.document_html  = ""
        st.session_state.document_id    = None
        st.session_state.document_title = "Untitled"
        st.session_state.template_id    = None
        st.rerun()


def _save_document():
    from src.storage.document_store import save_document
    try:
        doc_id = save_document(
            session_id  = st.session_state.get("session_id", "anonymous"),
            title       = st.session_state.document_title,
            template_id = st.session_state.template_id or "custom",
            content_html= st.session_state.document_html,
            document_id = st.session_state.document_id,
        )
        if doc_id:
            st.session_state.document_id = doc_id
            st.toast("Document saved!", icon="✓")
        else:
            st.warning("Save failed — check Supabase credentials.")
    except Exception as e:
        st.warning(f"Save failed: {e}")


def _show_versions(doc_agent: DocumentAgent):
    from src.storage.document_store import get_versions, restore_version
    if not st.session_state.document_id:
        st.info("Save the document first to enable version history.")
        return
    versions = get_versions(st.session_state.document_id)
    if not versions:
        st.info("No previous versions found.")
        return
    st.markdown("**Version history** (last 3)")
    for v in versions:
        col_ver, col_restore = st.columns([3, 1])
        with col_ver:
            st.caption(f"v{v['version_number']} · {v['created_at'][:16]}")
        with col_restore:
            if st.button("Restore", key=f"restore_{v['id']}"):
                html = restore_version(st.session_state.document_id, v["id"])
                if html:
                    st.session_state.document_html = html
                    st.toast("Version restored!", icon="✓")
                    st.rerun()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    init_session_state()
    assistant, doc_agent, _ = initialize_all()

    _inject_css(st.session_state.workspace_mode)

    # Top bar
    fb_clicked, nc_clicked, ws_clicked = render_top_bar(st.session_state.workspace_mode)

    if nc_clicked:
        st.session_state.messages       = []
        st.session_state.show_feedback  = False
        st.session_state.document_html  = ""
        st.session_state.document_id    = None
        st.session_state.document_title = "Untitled"
        st.session_state.template_id    = None
        st.rerun()

    if fb_clicked:
        st.session_state.show_feedback = not st.session_state.show_feedback
        st.rerun()

    if ws_clicked:
        st.session_state.workspace_mode = not st.session_state.workspace_mode
        st.rerun()

    if st.session_state.show_feedback:
        render_feedback_form()

    # ── Render mode ───────────────────────────────────────────────────────────
    if st.session_state.workspace_mode:
        render_workspace(assistant, doc_agent)
        return

    # ── Chat mode ─────────────────────────────────────────────────────────────
    if not st.session_state.messages:
        sample = render_empty_state(assistant)
        prompt = sample or st.chat_input("Ask a product management question…")
    else:
        render_chat_messages(st.session_state.messages)
        prompt = st.chat_input("Ask a product management question…")

    if prompt:
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-6:-1]
            if m["role"] in ("user", "assistant")
        ]
        handle_chat_message(prompt, assistant, doc_agent, history)
        st.rerun()


if __name__ == "__main__":
    main()
