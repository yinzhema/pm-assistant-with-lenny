"""
FastAPI backend for AskProduct (PM Assistant).
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all singletons on startup and store in app.state."""
    from services.retrieval.vector_store import VectorStore
    from services.retrieval.embedder import EmbeddingGenerator
    from services.retrieval.bm25_index import BM25Index
    from services.retrieval.hybrid_retriever import HybridRetriever
    from services.pm_assistant import PMAssistant
    from services.document_agent import DocumentAgent

    # Core retrieval infrastructure
    vector_store = VectorStore()
    embedder = EmbeddingGenerator()

    bm25_index = BM25Index()
    bm25_corpus_path = os.getenv("BM25_CORPUS_PATH", "/app/data/bm25_corpus.jsonl")
    loaded = bm25_index.load(bm25_corpus_path)
    if not loaded:
        print(f"[startup] BM25 corpus not found at {bm25_corpus_path} — keyword search disabled")

    hybrid_retriever = HybridRetriever(
        vector_store=vector_store,
        embedder=embedder,
        bm25_index=bm25_index,
    )

    pm_assistant = PMAssistant(retriever=hybrid_retriever)
    doc_agent = DocumentAgent(retriever=hybrid_retriever)

    from openai import AsyncOpenAI
    async_openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Store in app.state so routers can access via request.app.state
    app.state.vector_store = vector_store
    app.state.embedder = embedder
    app.state.bm25_index = bm25_index
    app.state.hybrid_retriever = hybrid_retriever
    app.state.pm_assistant = pm_assistant
    app.state.doc_agent = doc_agent
    app.state.async_openai = async_openai

    print("[startup] All singletons initialized")
    yield

    # Cleanup (nothing needed for these stateless clients)
    print("[shutdown] Cleaning up")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AskProduct API",
        description="PM Assistant backed by Lenny's Podcast and curated PM content",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    allowed_origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    from routers.chat import router as chat_router
    from routers.documents import router as documents_router
    from routers.feedback import router as feedback_router
    from routers.health import router as health_router

    app.include_router(health_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(documents_router, prefix="/api")
    app.include_router(feedback_router, prefix="/api")

    @app.get("/")
    async def root():
        return {"status": "AskProduct API"}

    return app


app = create_app()
