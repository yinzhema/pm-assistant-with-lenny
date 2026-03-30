# 🎙️ PM Assistant with Lenny

An AI-powered product management assistant with a modern, professional interface that surfaces insights from Lenny's Podcast to help product builders get expert advice. Ask any PM question and get answers backed by conversations with world-class product leaders.

## ✨ Features

### Core Capabilities
- 🤖 **Conversational AI**: Natural chat interface powered by OpenAI GPT-4
- 🔍 **Semantic Search**: Find relevant insights across 300+ podcast episodes
- 📚 **Source Citations**: Every answer includes links to specific podcast moments
- 💬 **Context-Aware**: Maintains conversation history for follow-up questions
- 🎯 **Expert Knowledge**: Insights from industry leaders at Airbnb, Meta, Google, Stripe, and more

### Enhanced Interface
- 🔐 **Authentication**: Login/signup flow for personalized experience
- 💬 **Conversation Management**: Create, manage, and switch between multiple conversations
- ⚡ **Response Styles**: Choose from Quick (3 sources), Recommended (5 sources), or Comprehensive (7 sources)
- 🎨 **Modern UI**: Professional design with dark sidebar, message bubbles, and smooth transitions
- 📱 **Responsive**: Works great on different screen sizes

## Architecture

```
User Query → Embedding → Vector Search (ChromaDB) → Context Retrieval
                                                           ↓
User ← Formatted Response ← OpenAI GPT-4 ← Context + System Prompt
```

**Tech Stack:**
- **Frontend**: Streamlit (chat interface)
- **Vector DB**: ChromaDB (embedded, persistent)
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small
- **Language**: Python 3.9+

## Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd pm-assistant-with-lenny
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

Your `.env` file should look like:
```
OPENAI_API_KEY=sk-...your-key-here...
```

### Initial Setup: Ingest Transcripts

Before using the assistant, you need to process the podcast transcripts and create embeddings:

```bash
python scripts/ingest_transcripts.py
```

This will:
- Parse all 300+ episode transcripts
- Chunk them into semantic segments
- Generate embeddings using OpenAI
- Store everything in ChromaDB

**⏱️ Time**: ~10-15 minutes  
**💰 Cost**: ~$0.60 in OpenAI API credits (one-time)

#### Ingestion Options

```bash
# Ingest all episodes (default)
python scripts/ingest_transcripts.py

# Ingest with custom settings
python scripts/ingest_transcripts.py --batch-size 5 --chunk-size 1000

# Ingest a single episode (for testing)
python scripts/ingest_transcripts.py --episode brian-chesky
```

### Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🚀 Usage

### First Time Setup

1. **Create an Account**
   - Enter a username and password
   - Click "Create Account" (or "Log In" if returning)
   - You'll be logged in automatically

2. **Start Chatting**
   - Click on a sample question or type your own
   - Choose your preferred response style in the sidebar:
     - ⚡ **Quick**: Fast responses with 3 sources
     - 🎯 **Recommended**: Balanced responses with 5 sources (default)
     - 🧠 **Comprehensive**: Detailed responses with 7 sources

3. **Manage Conversations**
   - Click "➕ New Chat" to start a new conversation
   - Select previous conversations from the sidebar
   - Delete conversations with the 🗑️ button
   - Conversations are automatically titled from your first message

### Example Questions

- "How do I find product-market fit?"
- "What are the best practices for user research?"
- "How should I prioritize features on my roadmap?"
- "What makes a great product manager?"
- "How do I build a strong product culture?"

### Features in Action

1. **Authentication**: Secure login protects your conversation history
2. **Multiple Conversations**: Organize different topics in separate chats
3. **Source Citations**: Every answer includes links to specific podcast moments with timestamps
4. **Response Styles**: Adjust depth of responses based on your needs
5. **Conversation History**: Access all your previous conversations anytime

## Project Structure

```
pm-assistant-with-lenny/
├── app.py                          # Streamlit chat interface
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── PLAN.md                         # Technical architecture document
│
├── src/
│   ├── ingestion/
│   │   ├── parser.py              # Parse transcript YAML + content
│   │   ├── chunker.py             # Semantic chunking
│   │   └── embedder.py            # Generate OpenAI embeddings
│   │
│   ├── retrieval/
│   │   ├── vector_store.py        # ChromaDB interface
│   │   └── retriever.py           # Hybrid retrieval system
│   │
│   └── agent/
│       └── pm_assistant.py        # Main assistant logic
│
├── scripts/
│   └── ingest_transcripts.py     # One-time ingestion script
│
├── data/
│   └── chroma_db/                 # Persistent vector database
│
├── episodes/                       # 300+ podcast transcripts
│   └── {guest-name}/
│       └── transcript.md          # YAML frontmatter + dialogue
│
└── index/                         # Topic-based episode index
    └── {topic}.md                 # Episodes by topic
```

## Deployment

### Streamlit Cloud (Free Tier)

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set `app.py` as the main file
   - Add `OPENAI_API_KEY` in Secrets (Advanced settings)

3. **Secrets Configuration**
In Streamlit Cloud dashboard, add to Secrets:
```toml
OPENAI_API_KEY = "sk-...your-key..."
```

4. **Important**: Make sure to run ingestion locally first and commit the `data/chroma_db/` directory, or run ingestion after deployment.

### Alternative: Local/Server Deployment

```bash
# Run with custom port
streamlit run app.py --server.port 8080

# Run in production mode
streamlit run app.py --server.headless true
```

## Cost Estimation

### One-Time Setup
- **Embeddings**: 300 episodes × ~10 chunks × $0.00002/1K tokens ≈ **$0.60**
- **Storage**: Free (local ChromaDB)

### Per-Query Cost
- **Retrieval**: Free (local search)
- **LLM Response**: ~1000 tokens × $0.00015/1K tokens ≈ **$0.0002/query**

### Monthly Cost (100 queries)
- **Total**: ~**$0.02/month** (essentially free!)

## Development

### Testing Individual Components

```bash
# Test parser
python -m src.ingestion.parser

# Test chunker
python -m src.ingestion.chunker

# Test embedder (requires API key)
python -m src.ingestion.embedder

# Test retriever
python -m src.retrieval.retriever

# Test assistant
python -m src.agent.pm_assistant
```

### Adding New Episodes

1. Add transcript to `episodes/{guest-name}/transcript.md`
2. Run ingestion for that episode:
```bash
python scripts/ingest_transcripts.py --episode {guest-name}
```

## Extending the System

### Adding New Knowledge Sources

The system is designed to be extensible. To add new sources (books, articles, etc.):

1. Create a new parser in `src/ingestion/`
2. Implement the same chunking interface
3. Add metadata to distinguish sources
4. Run ingestion with the new parser

See `PLAN.md` for detailed architecture and extension guidelines.

## Troubleshooting

### "Vector store is empty"
Run the ingestion script first:
```bash
python scripts/ingest_transcripts.py
```

### "OPENAI_API_KEY not found"
Make sure you have a `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

### Slow responses
- Reduce `n_results` in the sidebar (fewer sources = faster)
- Use a faster model (already using gpt-4o-mini)
- Check your internet connection

### Import errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add more sophisticated query understanding
- [ ] Implement query caching for common questions
- [ ] Add topic-based filtering in UI
- [ ] Support for multi-turn conversations with better context
- [ ] Add analytics/feedback collection
- [ ] Improve citation formatting
- [ ] Add export functionality (save conversations)

## License

This project is for educational and personal use. Podcast content belongs to Lenny Rachitsky and respective guests.

## Acknowledgments

- **Lenny Rachitsky** for creating an incredible podcast with world-class guests
- All the product leaders who shared their insights
- OpenAI for providing the AI infrastructure
- Streamlit for the easy-to-use UI framework

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `PLAN.md` for technical details
3. Open an issue on GitHub

---

**Built with ❤️ for the product management community**
