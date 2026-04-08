"""
Health check endpoint.
"""
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    """Return service health status including BM25 corpus size and Pinecone connectivity."""
    bm25_index = request.app.state.bm25_index
    vector_store = request.app.state.vector_store

    bm25_corpus_size = len(bm25_index)

    pinecone_connected = False
    try:
        count = vector_store.count()
        pinecone_connected = count >= 0  # any non-exception result means connected
    except Exception:
        pinecone_connected = False

    return {
        "status": "ok",
        "bm25_corpus_size": bm25_corpus_size,
        "pinecone_connected": pinecone_connected,
    }
