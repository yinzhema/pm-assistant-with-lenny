"""
Deduplication: prevent re-ingesting documents already in the Pinecone index.

Two-level strategy:
1. URL dedup   — check if a vector with matching 'url' metadata exists
2. Hash dedup  — check sha256(text) against known 'content_hash' values
"""
from typing import List, Set, Optional

from .sources.base import RawDocument


class Deduplicator:
    """
    Filter out documents already present in the Pinecone index.

    Loads known URLs and content hashes once per ingestion run (lazy,
    cached in memory) via the VectorStore's list+fetch API.
    """

    def __init__(self, vector_store):
        self._vector_store = vector_store
        self._known_urls: Optional[Set[str]] = None
        self._known_hashes: Optional[Set[str]] = None

    def filter_new(self, documents: List[RawDocument]) -> List[RawDocument]:
        """Return only documents not already in the index."""
        if not documents:
            return []

        self._ensure_loaded()

        new_docs = []
        for doc in documents:
            if doc.url in self._known_urls:
                print(f"  [dedup] Skipping (URL match): {doc.url[:80]}")
                continue
            if doc.content_hash in self._known_hashes:
                print(f"  [dedup] Skipping (hash match): {doc.title[:60]}")
                continue
            new_docs.append(doc)

        return new_docs

    def mark_ingested(self, documents: List[RawDocument]) -> None:
        """Update in-memory cache after ingesting new documents."""
        if self._known_urls is None:
            return
        for doc in documents:
            self._known_urls.add(doc.url)
            self._known_hashes.add(doc.content_hash)

    def _ensure_loaded(self) -> None:
        if self._known_urls is not None:
            return

        print("  [dedup] Loading existing URLs and hashes from Pinecone...")
        urls: Set[str] = set()
        hashes: Set[str] = set()

        try:
            # Collect all vector IDs
            all_ids = []
            for id_page in self._vector_store.index.list():
                all_ids.extend(id_page)

            # Fetch in batches of 100 to get metadata
            batch_size = 100
            for i in range(0, len(all_ids), batch_size):
                batch = all_ids[i : i + batch_size]
                result = self._vector_store.index.fetch(ids=batch)
                for vec in result.get("vectors", {}).values():
                    meta = vec.get("metadata", {})
                    url = meta.get("url", "")
                    content_hash = meta.get("content_hash", "")
                    if url:
                        urls.add(url)
                    if content_hash:
                        hashes.add(content_hash)

            print(f"  [dedup] Found {len(urls)} known URLs, {len(hashes)} known hashes")
        except Exception as e:
            print(f"  [dedup] Warning: could not load existing data ({e}). Proceeding without dedup.")

        self._known_urls = urls
        self._known_hashes = hashes
