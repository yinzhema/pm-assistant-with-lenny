"""
AskProduct - Revamped Streamlit Chat Interface
Enhanced with authentication, conversation history, and style settings
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Literal
import streamlit as st
from dotenv import load_dotenv

from src.retrieval.vector_store import VectorStore
from src.ingestion.embedder import EmbeddingGenerator
from src.retrieval.retriever import Retriever
from src.agent.pm_assistant import PMAssistant
from src.storage.conversation_store import load_conversations, upsert_conversation, submit_feedback

load_dotenv()

# Type definitions
SettingsTier = Literal["quick", "recommended", "comprehensive"]

# Page configuration
st.set_page_config(
    page_title="AskProduct",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern design
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hide header decoration and toolbar, but keep sidebar toggle */
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stHeader"] {background: transparent !important; border-bottom: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {display: none !important;}

    /* Always show sidebar expand button — cover all Streamlit version variants */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stCollapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    
    /* Main container */
    .main {
        padding: 0 !important;
    }
    
    /* Auth page styling */
    .auth-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .auth-icon {
        background: #2563eb;
        width: 60px;
        height: 60px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    /* Chat interface */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
    }
    
    .empty-state-icon {
        background: #2563eb;
        width: 80px;
        height: 80px;
        border-radius: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.5rem;
    }
    
    .sample-questions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 0.75rem;
        margin-top: 2rem;
    }
    
    .sample-question {
        padding: 1rem;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
    }
    
    .sample-question:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
    }
    
    /* Message bubbles */
    .message-user {
        background: #2563eb;
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .message-assistant {
        background: #f1f5f9;
        color: #0f172a;
        padding: 1rem 1.25rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #f9f9f9 !important;
        border-right: 1px solid #e5e5e5;
    }

    [data-testid="stSidebarContent"] {
        padding: 0.75rem 0.5rem 0.75rem 0.5rem !important;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    /* All sidebar text */
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown {
        color: #374151;
    }

    /* All sidebar buttons — base */
    [data-testid="stSidebar"] .stButton button {
        background: transparent;
        color: #374151;
        border: none;
        border-radius: 8px;
        font-weight: 400;
        padding: 0.4rem 0.65rem;
        font-size: 0.85rem;
        text-align: left;
        justify-content: flex-start;
        transition: background 0.15s;
        min-height: 2rem;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: #ececec !important;
        color: #111827 !important;
    }

    /* New Chat button — first stButton in sidebar */
    [data-testid="stSidebar"] > div > div > div > div:first-child .stButton button,
    [data-testid="stSidebarContent"] > div:first-child .stButton button {
        background: white !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }

    [data-testid="stSidebar"] > div > div > div > div:first-child .stButton button:hover,
    [data-testid="stSidebarContent"] > div:first-child .stButton button:hover {
        background: #f3f4f6 !important;
        border-color: #9ca3af !important;
    }

    /* Conversation list — active item */
    [data-testid="stSidebar"] .stButton button[kind="primary"] {
        background: #ececec !important;
        color: #111827 !important;
        border: none !important;
        font-weight: 500 !important;
    }

    /* Conversation list — inactive */
    [data-testid="stSidebar"] .stButton button[kind="secondary"] {
        background: transparent !important;
        color: #374151 !important;
        border: none !important;
    }

    [data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
        background: #ececec !important;
        color: #111827 !important;
    }

    /* Tier selector — override primary to use dark style */
    .tier-selector [data-testid="stSidebar"] .stButton button[kind="primary"],
    .tier-selector .stButton button[kind="primary"] {
        background: #111827 !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }

    .tier-selector .stButton button[kind="primary"]:hover {
        background: #1f2937 !important;
    }

    .tier-selector .stButton button[kind="secondary"] {
        background: transparent !important;
        color: #6b7280 !important;
    }

    .tier-selector .stButton button[kind="secondary"]:hover {
        background: #f3f4f6 !important;
        color: #374151 !important;
    }

    /* Empty state hint */
    .sidebar-empty-hint {
        color: #9ca3af;
        font-size: 0.78rem;
        line-height: 1.5;
        padding: 0.5rem 0.5rem;
        margin: 0;
    }

    /* Section label (e.g. "Style", "Recent") */
    .sidebar-section-label {
        color: #9ca3af;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 0.75rem 0 0.25rem 0.5rem;
        padding: 0;
    }

    /* User profile bar */
    .sidebar-profile-bar {
        border-top: 1px solid #e5e5e5;
        margin-top: 0.5rem;
        padding: 0.75rem 0.5rem 0.25rem 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .profile-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #2563eb;
        color: white;
        font-size: 0.85rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .profile-info {
        display: flex;
        flex-direction: column;
        flex: 1;
        min-width: 0;
    }

    .profile-name {
        color: #111827;
        font-size: 0.875rem;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block;
    }

    .profile-label {
        color: #9ca3af;
        font-size: 0.72rem;
        display: block;
    }

    /* Sign out button */
    [data-testid="stSidebar"] .element-container:last-child .stButton button {
        background: transparent !important;
        color: #6b7280 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
        font-size: 0.8rem !important;
        padding: 0.3rem 0.75rem !important;
        margin-top: 0.1rem !important;
        justify-content: center !important;
        text-align: center !important;
    }

    [data-testid="stSidebar"] .element-container:last-child .stButton button:hover {
        background: #f9fafb !important;
        border-color: #d1d5db !important;
        color: #374151 !important;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    if "active_conversation_id" not in st.session_state:
        st.session_state.active_conversation_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "settings_tier" not in st.session_state:
        st.session_state.settings_tier = "recommended"
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    if "conversations_loaded" not in st.session_state:
        st.session_state.conversations_loaded = False


def render_auth_flow():
    """Render the authentication flow (login/signup)."""
    st.markdown("""
    <div style="min-height: 100vh; display: flex; align-items: center; justify-center; 
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);">
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="auth-container">
            <div class="auth-header">
                <div class="auth-icon">
                    <span style="font-size: 32px;">🎙️</span>
                </div>
                <h1 style="margin: 0; font-size: 2rem; color: #0f172a;">PM Assistant</h1>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        is_login = st.session_state.auth_mode == "login"
        
        st.markdown(f"""
        <h2 style="text-align: center; color: #475569; margin-bottom: 2rem;">
            {'Welcome back' if is_login else 'Create your account'}
        </h2>
        """, unsafe_allow_html=True)
        
        with st.form("auth_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submit_button = st.form_submit_button(
                "Log In" if is_login else "Create Account",
                use_container_width=True
            )
            
            if submit_button and username.strip():
                st.session_state.authenticated = True
                st.session_state.username = username
                # Don't create conversation at launch - user will click New Chat
                st.rerun()
        
        # Toggle between login and signup
        toggle_text = "Don't have an account? Sign up" if is_login else "Already have an account? Log in"
        if st.button(toggle_text, key="auth_toggle", use_container_width=True):
            st.session_state.auth_mode = "signup" if is_login else "login"
            st.rerun()


def create_new_conversation():
    """Create a new conversation."""
    new_conv = {
        "id": str(datetime.now().timestamp()),
        "title": "New Chat",
        "timestamp": datetime.now(),
        "messages": []
    }
    st.session_state.conversations.insert(0, new_conv)
    st.session_state.active_conversation_id = new_conv["id"]
    st.session_state.messages = []


def get_active_conversation():
    """Get the active conversation."""
    for conv in st.session_state.conversations:
        if conv["id"] == st.session_state.active_conversation_id:
            return conv
    return None


def update_conversation_title(first_message: str):
    """Update conversation title with first message."""
    conv = get_active_conversation()
    if conv and conv["title"] == "New Chat":
        title = first_message[:50] + ("..." if len(first_message) > 50 else "")
        conv["title"] = title


def render_sidebar():
    """Render the sidebar with conversation history and settings."""
    with st.sidebar:
        # New Chat button — only navigate to empty state, don't create a conversation yet
        st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
        if st.button("+ New Chat", key="new_chat", use_container_width=True):
            if st.session_state.messages:  # only act if currently in a conversation
                st.session_state.messages = []
                st.session_state.active_conversation_id = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Conversation history
        if st.session_state.conversations:
            st.markdown('<p class="sidebar-section-label">Recent</p>', unsafe_allow_html=True)
            for conv in st.session_state.conversations:
                is_active = conv["id"] == st.session_state.active_conversation_id
                label = conv["title"]
                if len(label) > 32:
                    label = label[:32] + "…"
                if st.button(
                    f"💬  {label}",
                    key=f"conv_{conv['id']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.active_conversation_id = conv["id"]
                    st.session_state.messages = conv.get("messages", [])
                    st.rerun()
        else:
            st.markdown(
                '<p class="sidebar-empty-hint">Ask a question to start learning from product management experts.</p>',
                unsafe_allow_html=True
            )

        # Spacer pushes style + user to bottom
        st.markdown('<div style="flex:1; min-height:1rem"></div>', unsafe_allow_html=True)

        # Style — vertical stacked buttons
        st.markdown('<p class="sidebar-section-label">Response style</p>', unsafe_allow_html=True)
        tier_options = [
            ("quick", "⚡  Quick", "Faster, fewer sources"),
            ("recommended", "🎯  Recommended", "Balanced depth & speed"),
            ("comprehensive", "🧠  Comprehensive", "Deep dive, more sources"),
        ]
        current = st.session_state.settings_tier
        st.markdown('<div class="tier-selector">', unsafe_allow_html=True)
        for tier_id, label, _ in tier_options:
            is_selected = current == tier_id
            if st.button(
                label,
                key=f"tier_{tier_id}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.settings_tier = tier_id
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Feedback expander
        with st.expander("💬  Feedback"):
            st.markdown("**What would you like to see?**")
            feedback_comment = st.text_area(
                "feedback_text",
                placeholder="Share your thoughts or feature requests...",
                label_visibility="collapsed"
            )
            if st.button("Submit", key="feedback_submit", use_container_width=True):
                if feedback_comment.strip():
                    submit_feedback(st.session_state.username, feedback_comment)
                    st.success("Thanks for your feedback!")

        # User profile section at very bottom
        username = st.session_state.username
        initials = username[0].upper() if username else "?"
        st.markdown(f"""
        <div class="sidebar-profile-bar">
            <div class="profile-avatar">{initials}</div>
            <div class="profile-info">
                <span class="profile-name">{username}</span>
                <span class="profile-label">Personal account</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign out", key="logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.conversations = []
            st.session_state.messages = []
            st.session_state.conversations_loaded = False
            st.rerun()


def render_empty_state(assistant: PMAssistant):
    """Render the empty state with sample questions."""
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">
            <span style="font-size: 48px; color: white;">🎙️</span>
        </div>
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem; color: #0f172a;">
            AskProduct
        </h1>
        <p style="font-size: 1.25rem; color: #64748b; margin-bottom: 2rem;">
            Get expert product management advice from Lenny's Podcast
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample questions
    st.markdown("### 💡 Sample Questions")
    
    sample_questions = assistant.get_example_questions()[:5]
    
    cols = st.columns(2)
    for idx, question in enumerate(sample_questions):
        with cols[idx % 2]:
            if st.button(question, key=f"sample_{idx}", use_container_width=True):
                return question
    
    return None


def render_chat_interface(assistant: PMAssistant):
    """Render the main chat interface."""
    # Display messages
    for msg in st.session_state.messages:
        role_class = "message-user" if msg["role"] == "user" else "message-assistant"
        st.markdown(f'<div class="{role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        
        if msg.get("sources"):
            with st.expander("📚 View Sources"):
                for source in msg["sources"]:
                    st.markdown(f"**{source['number']}. {source['guest']}** - {source['title']}")
                    if source.get('youtube_url'):
                        timestamp = source['timestamp'].replace(':', 'h', 1).replace(':', 'm') + 's'
                        url_with_timestamp = f"{source['youtube_url']}&t={timestamp}"
                        st.markdown(f"[▶️ Watch at {source['timestamp']}]({url_with_timestamp})")
                    st.caption(f"Relevance: {source['similarity_score']:.1%}")
                    st.divider()
    
    # Chat input
    prompt = st.chat_input("Ask a product management question...")
    
    return prompt


@st.cache_resource
def initialize_assistant():
    """Initialize the PM Assistant (cached)."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OPENAI_API_KEY not found. Please set it in your environment / Streamlit secrets.")
        st.stop()
    if not os.getenv("PINECONE_API_KEY"):
        st.error("⚠️ PINECONE_API_KEY not found. Please set it in your environment / Streamlit secrets.")
        st.stop()

    vector_store = VectorStore()
    embedder = EmbeddingGenerator()
    retriever = Retriever(vector_store, embedder)
    assistant = PMAssistant(retriever)

    return assistant, vector_store


def main():
    """Main application."""
    init_session_state()
    
    # Show auth flow if not authenticated
    if not st.session_state.authenticated:
        render_auth_flow()
        return

    # Load conversations from Supabase once per session
    if not st.session_state.conversations_loaded:
        st.session_state.conversations = load_conversations(st.session_state.username)
        st.session_state.conversations_loaded = True

    # Initialize assistant
    assistant, vector_store = initialize_assistant()
    
    # Render sidebar
    render_sidebar()

    # Main content area
    if not st.session_state.messages:
        # Empty state
        sample_question = render_empty_state(assistant)
        if sample_question:
            prompt = sample_question
        else:
            prompt = st.chat_input("Ask a product management question...")
    else:
        # Chat interface
        prompt = render_chat_interface(assistant)
    
    # Handle new message
    if prompt:
        # Auto-create conversation if none is active (empty list or after New Chat)
        if not st.session_state.active_conversation_id:
            create_new_conversation()

        # Add user message
        user_msg = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(user_msg)

        # Update conversation title if first message
        if len(st.session_state.messages) == 1:
            update_conversation_title(prompt)
        
        # Get conversation history
        conversation_history = []
        for msg in st.session_state.messages[-6:-1]:
            if msg["role"] in ["user", "assistant"]:
                conversation_history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Get tier settings
        tier_sources = {
            "quick": 3,
            "recommended": 5,
            "comprehensive": 7
        }
        n_results = tier_sources.get(st.session_state.settings_tier, 5)
        print(f"[DEBUG] tier={st.session_state.settings_tier!r}, n_results={n_results}")

        # Generate response
        with st.spinner("Searching through podcast insights..."):
            result = assistant.answer_question(
                prompt,
                conversation_history=conversation_history if conversation_history else None,
                n_results=n_results
            )
        
        # Add assistant message
        assistant_msg = {
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", []),
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(assistant_msg)
        
        # Update conversation and persist to Supabase
        conv = get_active_conversation()
        if conv:
            conv["messages"] = st.session_state.messages
            upsert_conversation(st.session_state.username, conv)

        st.rerun()


if __name__ == "__main__":
    main()

# Made with Bob
