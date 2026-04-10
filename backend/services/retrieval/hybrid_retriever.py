"""
Hybrid retriever combining semantic (Pinecone) + keyword (BM25) search
with Reciprocal Rank Fusion (RRF) and credibility tier boosting.

Drop-in replacement for Retriever: same retrieve() / retrieve_with_context()
signatures, so PMAssistant and app.py require minimal changes.
"""
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Tuple

from services.retrieval.vector_store import VectorStore
from services.retrieval.bm25_index import BM25Index
from services.retrieval.embedder import EmbeddingGenerator


# Credibility boost multipliers (applied after RRF fusion)
_TIER_BOOST = {1: 1.15, 2: 1.0, 3: 0.85}
_DEFAULT_TIER_BOOST = 1.15  # missing tier → assume tier-1 (existing Lenny chunks)


class HybridRetriever:
    """
    1. Semantic search (Pinecone vector similarity) — top-20
    2. BM25 keyword search (local in-memory index)  — top-20
    3. Reciprocal Rank Fusion                        — merged ranking
    4. Credibility tier boost                        — final rerank
    5. Return top n_results
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: EmbeddingGenerator,
        bm25_index: BM25Index,
        semantic_weight: float = 0.7,
        bm25_weight: float = 0.3,
        rrf_k: int = 60,
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.bm25_index = bm25_index
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight
        self.rrf_k = rrf_k

    # ── Public API (same as Retriever) ───────────────────────────────────────

    def retrieve(
        self, query: str, n_results: int = 8, filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.

        Returns list of chunk dicts with keys:
            id, text, metadata, similarity_score
        """
        # 1 & 2. Run semantic embedding+search and BM25 search in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            semantic_future = executor.submit(
                self._semantic_search, query, 20, filters
            )
            bm25_future = executor.submit(self.bm25_index.search, query, 20)

        semantic_results = semantic_future.result()
        bm25_results = bm25_future.result()

        # 3. RRF fusion
        fused_ids = self._rrf_fuse(semantic_results, bm25_results)

        # 4. Build full result objects (resolve metadata from semantic results)
        id_to_chunk = {c["id"]: c for c in semantic_results}
        chunks = []
        for chunk_id, rrf_score in fused_ids:
            if chunk_id in id_to_chunk:
                chunk = dict(id_to_chunk[chunk_id])
            else:
                # BM25 hit not in semantic results — skip (no metadata available)
                continue
            chunk["similarity_score"] = rrf_score
            chunks.append(chunk)

        # 5. Credibility tier boost + final sort
        chunks = self._apply_credibility_boost(chunks)
        chunks.sort(key=lambda c: c["similarity_score"], reverse=True)

        return chunks[:n_results]

    def retrieve_with_context(self, query: str, n_results: int = 8) -> Dict:
        """
        Retrieve chunks and format them for LLM context.

        Returns:
            {'context': str, 'sources': List[Dict]}
        """
        chunks = self.retrieve(query, n_results)

        if not chunks:
            return {"context": "No relevant information found.", "sources": []}

        context_parts = []
        sources = []

        for i, chunk in enumerate(chunks, 1):
            metadata = chunk["metadata"]
            source_name = metadata.get("source_name", "")
            author = metadata.get("author", "")
            guest = metadata.get("guest", "")
            url = metadata.get("url", "") or metadata.get("youtube_url", "")
            title = metadata.get("title", "Unknown")
            timestamp = metadata.get("timestamp", "")

            # Build attribution line
            if source_name:
                by = f"{author} — " if author else ""
                attribution = f"{by}{source_name}"
            elif guest:
                attribution = f"{guest} (Lenny's Podcast)"
            else:
                attribution = "Unknown"

            context_parts.append(
                f"[Source {i}] {attribution} — {title}"
                + (f" (at {timestamp})" if timestamp else "")
                + f":\n{chunk['text']}\n"
            )

            sources.append({
                "number": i,
                "guest": guest or author,
                "title": title,
                "timestamp": timestamp,
                "youtube_url": metadata.get("youtube_url", ""),
                "url": url,
                "source_name": source_name or "Lenny's Podcast",
                "author": author,
                "credibility_tier": metadata.get("credibility_tier", 1),
                "similarity_score": chunk["similarity_score"],
            })

        return {"context": "\n---\n".join(context_parts), "sources": sources}

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _semantic_search(
        self, query: str, n_results: int, filters: Optional[Dict]
    ) -> List[Dict]:
        query_embedding = self.embedder.generate_embedding(query)
        if not query_embedding:
            return []

        raw = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            where=filters,
        )

        chunks = []
        if raw["ids"] and raw["ids"][0]:
            for i in range(len(raw["ids"][0])):
                chunks.append({
                    "id": raw["ids"][0][i],
                    "text": raw["documents"][0][i],
                    "metadata": raw["metadatas"][0][i],
                    "similarity_score": 1 - raw["distances"][0][i],
                })
        return chunks

    def _rrf_fuse(
        self,
        semantic_results: List[Dict],
        bm25_results: List[Tuple[str, float]],
    ) -> List[Tuple[str, float]]:
        """
        Reciprocal Rank Fusion: score = Σ weight_i / (k + rank_i).
        Returns (chunk_id, fused_score) pairs sorted descending.
        """
        scores: Dict[str, float] = {}
        k = self.rrf_k

        for rank, chunk in enumerate(semantic_results, 1):
            cid = chunk["id"]
            scores[cid] = scores.get(cid, 0.0) + self.semantic_weight / (k + rank)

        for rank, (cid, _) in enumerate(bm25_results, 1):
            scores[cid] = scores.get(cid, 0.0) + self.bm25_weight / (k + rank)

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def _apply_credibility_boost(self, chunks: List[Dict]) -> List[Dict]:
        """Multiply similarity_score by tier-based boost factor."""
        for chunk in chunks:
            tier = chunk["metadata"].get("credibility_tier")
            boost = _TIER_BOOST.get(tier, _DEFAULT_TIER_BOOST)
            chunk["similarity_score"] *= boost
        return chunks
