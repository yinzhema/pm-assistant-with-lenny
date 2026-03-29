"""
PM Assistant with Lenny - Streamlit Chat Interface
"""
import os
import streamlit as st
from dotenv import load_dotenv

from src.retrieval.vector_store import VectorStore
from src.ingestion.embedder import EmbeddingGenerator
from src.retrieval.retriever import Retriever
from src.agent.pm_assistant import PMAssistant

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PM Assistant with Lenny",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    .example-question {
        background-color: #e8f4f8;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_assistant():
    """Initialize the PM Assistant (cached)."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OPENAI_API_KEY not found. Please set it in your .env file.")
        st.stop()
    
    vector_store = VectorStore()
    embedder = EmbeddingGenerator()
    retriever = Retriever(vector_store, embedder)
    assistant = PMAssistant(retriever)
    
    return assistant, vector_store


def display_sources(sources):
    """Display source citations in an expandable section."""
    if not sources:
        return
    
    with st.expander("📚 View Sources", expanded=False):
        for source in sources:
            st.markdown(f"**{source['number']}. {source['guest']}** - {source['title']}")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if source['youtube_url']:
                    # Create YouTube link with timestamp
                    timestamp = source['timestamp'].replace(':', 'h', 1).replace(':', 'm') + 's'
                    url_with_timestamp = f"{source['youtube_url']}&t={timestamp}"
                    st.markdown(f"[▶️ Watch at {source['timestamp']}]({url_with_timestamp})")
            with col2:
                st.caption(f"Relevance: {source['similarity_score']:.1%}")
            
            st.divider()


def main():
    """Main application."""
    
    # Header
    st.markdown('<div class="main-header">🎙️ PM Assistant with Lenny</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Get expert product management advice from Lenny\'s Podcast</div>', 
                unsafe_allow_html=True)
    
    # Initialize assistant
    assistant, vector_store = initialize_assistant()
    
    # Check if vector store has data
    chunk_count = vector_store.count()
    if chunk_count == 0:
        st.warning("⚠️ The knowledge base is empty. Please run the ingestion script first:")
        st.code("python scripts/ingest_transcripts.py", language="bash")
        st.info("💡 This will process all podcast transcripts and create embeddings. It may take 10-15 minutes.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.info(f"""
        This assistant is powered by **{chunk_count:,} insights** from Lenny's Podcast, 
        featuring conversations with world-class product leaders.
        
        Ask any product management question and get advice backed by real expertise!
        """)
        
        st.header("Example Questions")
        example_questions = assistant.get_example_questions()
        
        for question in example_questions[:5]:
            if st.button(question, key=f"example_{question}", use_container_width=True):
                st.session_state.example_question = question
        
        st.divider()
        
        st.header("Settings")
        n_results = st.slider("Number of sources to retrieve", 3, 10, 5)
        st.session_state.n_results = n_results
        
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                display_sources(message["sources"])
    
    # Handle example question click
    if "example_question" in st.session_state:
        question = st.session_state.example_question
        del st.session_state.example_question
        
        # Add to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(question)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                n_results = st.session_state.get("n_results", 5)
                result = assistant.answer_question(question, n_results=n_results)
                
                st.markdown(result['answer'])
                display_sources(result['sources'])
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['answer'],
                    "sources": result['sources']
                })
    
    # Chat input
    if prompt := st.chat_input("Ask a product management question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Searching through podcast insights..."):
                # Get conversation history for context
                conversation_history = []
                for msg in st.session_state.messages[-6:-1]:  # Last 3 exchanges
                    if msg["role"] in ["user", "assistant"]:
                        conversation_history.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                
                n_results = st.session_state.get("n_results", 5)
                result = assistant.answer_question(
                    prompt, 
                    conversation_history=conversation_history if conversation_history else None,
                    n_results=n_results
                )
                
                st.markdown(result['answer'])
                display_sources(result['sources'])
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['answer'],
                    "sources": result['sources']
                })


if __name__ == "__main__":
    main()

# Made with Bob
