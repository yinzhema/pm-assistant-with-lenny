"""
Chunk RawDocument objects (articles/newsletters) into Pinecone-ready dicts.
Uses paragraph-aware chunking: splits on paragraph boundaries when possible.
"""
import re
import unicodedata
from typing import List, Dict, Optional
from datetime import date

from .sources.base import RawDocument


def _ascii_id(s: str) -> str:
    """Convert a string to an ASCII-safe Pinecone vector ID."""
    normalized = unicodedata.normalize("NFKD", s)
    return normalized.encode("ascii", "ignore").decode("ascii")


class ArticleChunker:
    """
    Chunk RawDocument objects into dicts compatible with VectorStore.add_chunks().

    ID format: '{source_id}-{YYYYMMDD}-{chunk_index:03d}'
    e.g. 'svpg-20240115-001'
    """

    # Rough chars-per-token estimate (conservative for mixed prose)
    CHARS_PER_TOKEN = 4

    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 100):
        self.chunk_size = chunk_size          # target tokens per chunk
        self.chunk_overlap = chunk_overlap    # overlap in tokens

    def chunk_document(self, doc: RawDocument) -> List[Dict]:
        """
        Returns list of chunk dicts ready for VectorStore.add_chunks().
        Each dict has: 'id', 'text', 'metadata' (no 'embedding' yet).
        """
        paragraphs = self._split_paragraphs(doc.text)
        if not paragraphs:
            return []

        chunks = self._merge_into_chunks(paragraphs)
        date_slug = (doc.publish_date or date.today().strftime("%Y-%m-%d")).replace("-", "")

        result = []
        for i, chunk_text in enumerate(chunks):
            chunk_id = _ascii_id(f"{doc.source_id}-{date_slug}-{i:03d}")
            result.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": self._build_metadata(doc, i),
            })
        return result

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split on double newlines; discard very short fragments."""
        raw = re.split(r"\n\n+", text)
        return [p.strip() for p in raw if len(p.strip()) > 60]

    def _merge_into_chunks(self, paragraphs: List[str]) -> List[str]:
        """
        Greedily merge paragraphs up to chunk_size tokens.
        When a chunk is full, start the next chunk with the last
        chunk_overlap tokens of the previous chunk (for continuity).
        """
        max_chars = self.chunk_size * self.CHARS_PER_TOKEN
        overlap_chars = self.chunk_overlap * self.CHARS_PER_TOKEN

        chunks: List[str] = []
        current_parts: List[str] = []
        current_len = 0

        for para in paragraphs:
            para_len = len(para)

            if current_len + para_len > max_chars and current_parts:
                # Flush current chunk
                chunk_text = "\n\n".join(current_parts)
                chunks.append(chunk_text)

                # Start next chunk with overlap from the end of current
                overlap_text = chunk_text[-overlap_chars:] if overlap_chars else ""
                current_parts = [overlap_text] if overlap_text else []
                current_len = len(overlap_text)

            current_parts.append(para)
            current_len += para_len

        if current_parts:
            chunks.append("\n\n".join(current_parts))

        return chunks

    def _build_metadata(self, doc: RawDocument, chunk_index: int) -> Dict:
        return {
            # New schema fields
            "source_name": doc.source_name,
            "source_id": doc.source_id,
            "source_type": doc.source_type,
            "author": doc.author,
            "url": doc.url,
            "credibility_tier": doc.credibility_tier,
            "content_hash": doc.content_hash,
            # Shared fields (used by retriever for display)
            "title": doc.title,
            "publish_date": doc.publish_date or "",
            "chunk_index": chunk_index,
            # Empty podcast-specific fields (for backward compat with retriever)
            "guest": "",
            "youtube_url": "",
            "timestamp": "",
            "keywords": "",
        }
