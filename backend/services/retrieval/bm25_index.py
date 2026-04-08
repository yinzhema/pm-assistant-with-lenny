"""
In-memory BM25 keyword search index for hybrid retrieval.

The corpus is persisted as data/bm25_corpus.jsonl so it survives app restarts.
It is rebuilt incrementally after each web ingestion run.
"""
import json
import os
import re
from typing import List, Tuple, Optional

from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> List[str]:
    """Simple whitespace + punctuation tokenizer, lowercased."""
    text = text.lower()
    tokens = re.findall(r"\b[a-z0-9][a-z0-9'_-]*\b", text)
    return tokens


class BM25Index:
    """
    BM25 keyword search over the full chunk corpus.

    Usage:
        index = BM25Index()
        index.load("data/bm25_corpus.jsonl")   # at startup
        results = index.search("product market fit", n_results=20)
    """

    DEFAULT_CORPUS_PATH = "data/bm25_corpus.jsonl"

    def __init__(self):
        self.bm25: Optional[BM25Okapi] = None
        self.chunk_ids: List[str] = []
        self._corpus: List[dict] = []   # [{'id': str, 'text': str}]

    # ── Build ────────────────────────────────────────────────────────────────

    def build(self, chunks: List[dict]) -> None:
        """
        Build index from list of {'id': str, 'text': str} dicts.
        Replaces any existing index.
        """
        self._corpus = [{"id": c["id"], "text": c["text"]} for c in chunks if c.get("text")]
        self._fit()

    def add_chunks(self, chunks: List[dict]) -> None:
        """Incrementally add new chunks to the existing corpus."""
        existing_ids = {c["id"] for c in self._corpus}
        new = [{"id": c["id"], "text": c["text"]} for c in chunks
               if c.get("text") and c["id"] not in existing_ids]
        if not new:
            return
        self._corpus.extend(new)
        self._fit()

    def _fit(self) -> None:
        if not self._corpus:
            self.bm25 = None
            self.chunk_ids = []
            return
        tokenized = [_tokenize(c["text"]) for c in self._corpus]
        self.bm25 = BM25Okapi(tokenized)
        self.chunk_ids = [c["id"] for c in self._corpus]

    # ── Search ───────────────────────────────────────────────────────────────

    def search(self, query: str, n_results: int = 20) -> List[Tuple[str, float]]:
        """
        Returns list of (chunk_id, bm25_score) sorted descending.
        Returns empty list if index is not built.
        """
        if self.bm25 is None or not self.chunk_ids:
            return []

        tokens = _tokenize(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        ranked = sorted(zip(self.chunk_ids, scores), key=lambda x: x[1], reverse=True)
        return [(cid, score) for cid, score in ranked[:n_results] if score > 0]

    # ── Persistence ──────────────────────────────────────────────────────────

    def save(self, path: str = DEFAULT_CORPUS_PATH) -> None:
        """Save corpus to JSONL file."""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for item in self._corpus:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"[BM25] Saved {len(self._corpus)} chunks to {path}")

    def load(self, path: str = DEFAULT_CORPUS_PATH) -> bool:
        """
        Load corpus from JSONL file and rebuild index.
        Returns True if successful, False if file not found.
        """
        if not os.path.exists(path):
            return False
        corpus = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        corpus.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        self._corpus = corpus
        self._fit()
        print(f"[BM25] Loaded {len(self._corpus)} chunks from {path}")
        return True

    def __len__(self) -> int:
        return len(self._corpus)
