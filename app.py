"""
AskProduct - Streamlit Chat Interface
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
from src.storage.conversation_store import submit_feedback

load_dotenv()

st.set_page_config(
    page_title="AskProduct",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* ── Hide Streamlit chrome ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stHeader"] {background: transparent !important; border-bottom: none !important; pointer-events: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {display: none !important;}

    /* ── Hide sidebar & toggle ── */
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stCollapsedControl"] {display: none !important;}

    /* ── Main layout ── */
    .main {padding: 0 !important;}
    .main .block-container {
        padding-top: 5rem !important;
        padding-bottom: 3rem !important;
        max-width: 760px !important;
        margin: 0 auto !important;
    }

    /* ── Top bar: logo + actions in one Streamlit row (see render_top_bar) ──
       Match the 4-column header row only (sample questions use 2 columns,
       feedback form uses 3). Uses descendant selectors to survive Streamlit
       wrapper div changes.
    ── */
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4)) {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 200 !important;
        width: 100% !important;
        max-width: 100% !important;
        height: 3.5rem !important;
        min-height: 3.5rem !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        padding: 0 1.25rem 0 1.5rem !important;
        gap: 0.75rem !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        background: #ffffff !important;
        border-bottom: 1px solid #e5e7eb !important;
        box-shadow: none !important;
    }
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4))
      [data-testid="column"] {
        min-width: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Logo column */
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4))
      [data-testid="column"]:nth-child(1) .stMarkdown {
        margin-bottom: 0 !important;
    }
    .app-header-title {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
        letter-spacing: -0.01em !important;
        line-height: 1.2 !important;
        margin: 0 !important;
    }
    /* Action columns: hug content */
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4))
      [data-testid="column"]:nth-child(3),
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4))
      [data-testid="column"]:nth-child(4) {
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: fit-content !important;
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
    }
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4)) button {
        background: white !important;
        color: #6b7280 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 0.35rem 0.85rem !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        min-height: unset !important;
        white-space: nowrap !important;
        width: auto !important;
        transition: all 0.15s !important;
    }
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(4)) button:hover {
        background: #f3f4f6 !important;
        color: #111827 !important;
        border-color: #d1d5db !important;
    }

    /* ── Feedback form card (fixed dropdown below header) ── */
    [data-testid="stForm"] {
        position: fixed !important;
        top: 3.5rem !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 150 !important;
        width: min(760px, calc(100vw - 2rem)) !important;
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 0 0 14px 14px !important;
        padding: 1.25rem 1.5rem !important;
        margin: 0 !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.10) !important;
    }
    [data-testid="stForm"] .stTextArea textarea {
        border-radius: 8px !important;
        font-size: 0.875rem !important;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem 2rem;
    }
    .empty-state-icon {
        background: #111827;
        width: 68px;
        height: 68px;
        border-radius: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.25rem;
    }

    /* ── Sample question buttons ── */
    [data-testid="stColumns"] .stButton button {
        background: #fafafa !important;
        color: #374151 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        font-size: 0.875rem !important;
        padding: 0.75rem 1rem !important;
        text-align: left !important;
        font-weight: 400 !important;
        line-height: 1.45 !important;
        transition: all 0.15s !important;
        min-height: unset !important;
    }
    [data-testid="stColumns"] .stButton button:hover {
        background: #f3f4f6 !important;
        border-color: #d1d5db !important;
        color: #111827 !important;
    }

    /* ── Message bubbles ── */
    .message-user {
        background: #2563eb;
        color: white;
        padding: 0.875rem 1.125rem;
        border-radius: 1rem 1rem 0.25rem 1rem;
        margin: 0.75rem 0 0.75rem auto;
        width: fit-content;
        max-width: 85%;
        line-height: 1.55;
        word-wrap: break-word;
    }
    .message-assistant {
        background: #f1f5f9;
        color: #0f172a;
        padding: 0.875rem 1.125rem;
        border-radius: 1rem 1rem 1rem 0.25rem;
        margin: 0.75rem 0;
        width: 100%;
        line-height: 1.55;
        word-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_feedback" not in st.session_state:
        st.session_state.show_feedback = False


def render_top_bar():
    """Single top row: logo + spacer + Feedback + New chat. CSS fixes the whole row as the header bar."""
    col_logo, _spacer, col_fb, col_nc = st.columns([2.6, 4.5, 1.8, 1.8], gap="small")
    with col_logo:
        st.markdown(
            '<p class="app-header-title">🎙️&nbsp;&nbsp;AskProduct</p>',
            unsafe_allow_html=True,
        )
    with _spacer:
        st.empty()
    with col_fb:
        feedback_clicked = st.button("💬  Feedback", key="feedback_btn")
    with col_nc:
        newchat_clicked = st.button("↺  New chat", key="new_chat_btn")
    return feedback_clicked, newchat_clicked


def render_feedback_form():
    """Inline feedback form shown when the Feedback button is toggled."""
    with st.form("feedback_form", clear_on_submit=True):
        st.markdown("**Share feedback** — What would you like to see?")
        comment = st.text_area(
            "feedback_input",
            placeholder="Your thoughts or feature requests...",
            label_visibility="collapsed",
            height=80,
        )
        col_submit, col_cancel, _ = st.columns([1, 1, 3])
        with col_submit:
            submitted = st.form_submit_button("Submit", use_container_width=True)
        with col_cancel:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
    if submitted and comment.strip():
        submit_feedback("anonymous", comment)
        st.session_state.show_feedback = False
        st.toast("Thanks for your feedback!", icon="✓")
        st.rerun()
    elif submitted or cancelled:
        st.session_state.show_feedback = False
        st.rerun()


def render_empty_state(assistant: PMAssistant):
    """Render the empty state with sample questions."""
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">
            <span style="font-size: 38px;">🎙️</span>
        </div>
        <h1 style="font-size: 2.25rem; margin: 0 0 0.5rem; color: #0f172a;
                   font-weight: 800; letter-spacing: -0.02em;">
            AskProduct
        </h1>
        <p style="font-size: 1.1rem; color: #64748b; margin: 0 0 2.25rem; line-height: 1.6;">
            Get expert product management advice from Lenny's Podcast
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p style="font-size:0.78rem;font-weight:600;color:#9ca3af;'
        'text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.6rem;">'
        'Try asking</p>',
        unsafe_allow_html=True
    )

    sample_questions = assistant.get_example_questions()[:6]
    cols = st.columns(2)
    for idx, question in enumerate(sample_questions):
        with cols[idx % 2]:
            if st.button(question, key=f"sample_{idx}", use_container_width=True):
                return question
    return None


def render_chat_interface(assistant: PMAssistant):
    """Render the main chat interface."""
    for msg in st.session_state.messages:
        role_class = "message-user" if msg["role"] == "user" else "message-assistant"
        st.markdown(f'<div class="{role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

        if msg.get("sources"):
            with st.expander("📚 View Sources"):
                for source in msg["sources"]:
                    guest = source.get("guest", "")
                    author = source.get("author", "")
                    source_name = source.get("source_name", "Lenny's Podcast")
                    display_name = guest or author or source_name

                    st.markdown(f"**{source['number']}. {display_name}** — {source['title']}")
                    st.caption(source_name)

                    youtube_url = source.get("youtube_url", "")
                    article_url = source.get("url", "")
                    timestamp = source.get("timestamp", "")

                    if youtube_url and timestamp:
                        ts = timestamp.replace(":", "h", 1).replace(":", "m") + "s"
                        st.markdown(f"[▶️ Watch at {timestamp}]({youtube_url}&t={ts})")
                    elif article_url:
                        st.markdown(f"[🔗 Read article]({article_url})")

                    st.caption(f"Relevance: {source['similarity_score']:.1%}")
                    st.divider()

    return st.chat_input("Ask a product management question...")


@st.cache_resource
def initialize_assistant():
    """Initialize the PM Assistant (cached)."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OPENAI_API_KEY not found.")
        st.stop()
    if not os.getenv("PINECONE_API_KEY"):
        st.error("⚠️ PINECONE_API_KEY not found.")
        st.stop()

    vector_store = VectorStore()
    embedder = EmbeddingGenerator()

    # Load BM25 index if corpus file exists, else semantic-only fallback
    bm25_index = BM25Index()
    bm25_index.load(BM25Index.DEFAULT_CORPUS_PATH)

    retriever = HybridRetriever(vector_store, embedder, bm25_index)
    return PMAssistant(retriever), vector_store


def main():
    init_session_state()
    assistant, _ = initialize_assistant()

    # ── Top bar: logo + actions (CSS fixes entire row to top of viewport) ──
    feedback_clicked, newchat_clicked = render_top_bar()

    # ── Handle button actions ──
    if newchat_clicked:
        st.session_state.messages = []
        st.session_state.show_feedback = False
        st.rerun()

    if feedback_clicked:
        st.session_state.show_feedback = not st.session_state.show_feedback
        st.rerun()

    # ── Main content ──
    if not st.session_state.messages:
        sample_question = render_empty_state(assistant)
        if st.session_state.show_feedback:
            render_feedback_form()
        prompt = sample_question or st.chat_input("Ask a product management question...")
    else:
        if st.session_state.show_feedback:
            render_feedback_form()
        prompt = render_chat_interface(assistant)

    # ── Handle new message ──
    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now(),
        })

        conversation_history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-6:-1]
            if m["role"] in ("user", "assistant")
        ]

        with st.spinner("Searching through podcast insights..."):
            result = assistant.answer_question(
                prompt,
                conversation_history=conversation_history or None,
                n_results=5,
            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", []),
            "timestamp": datetime.now(),
        })

        st.rerun()


if __name__ == "__main__":
    main()

# Made with Bob
