#!/usr/bin/env python3
"""
Ingest all web sources defined in src/ingestion/sources/registry.py into Pinecone.

Usage:
    python scripts/ingest_web_sources.py
    python scripts/ingest_web_sources.py --source svpg
    python scripts/ingest_web_sources.py --source lenny-newsletter --dry-run
    python scripts/ingest_web_sources.py --dry-run   # fetch only, no write
"""
import argparse
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.ingestion.sources.registry import SOURCES
from src.ingestion.article_chunker import ArticleChunker
from src.ingestion.deduplicator import Deduplicator
from src.ingestion.embedder import EmbeddingGenerator
from src.retrieval.vector_store import VectorStore
from src.retrieval.bm25_index import BM25Index


def parse_args():
    parser = argparse.ArgumentParser(description="Ingest web sources into AskProduct knowledge base")
    parser.add_argument(
        "--source",
        help="Ingest only this source_id (e.g. svpg). Omit to ingest all.",
        default=None,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and chunk documents but do NOT write to Pinecone.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.dry_run:
        if not os.getenv("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY not set")
            sys.exit(1)
        if not os.getenv("PINECONE_API_KEY"):
            print("ERROR: PINECONE_API_KEY not set")
            sys.exit(1)

    # Select sources
    sources = SOURCES
    if args.source:
        sources = [s for s in SOURCES if s.get_source_id() == args.source]
        if not sources:
            ids = [s.get_source_id() for s in SOURCES]
            print(f"ERROR: Unknown source '{args.source}'. Available: {ids}")
            sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"AskProduct v2 — Web Source Ingestion")
    print(f"Sources: {[s.get_source_id() for s in sources]}")
    print(f"Dry run: {args.dry_run}")
    print(f"{'=' * 60}\n")

    # Initialize components
    chunker = ArticleChunker(chunk_size=700, chunk_overlap=100)
    bm25_index = BM25Index()
    bm25_corpus_path = "data/bm25_corpus.jsonl"

    embedder = None
    vector_store = None
    deduplicator = None
    before_count = 0

    if not args.dry_run:
        embedder = EmbeddingGenerator()
        vector_store = VectorStore()
        deduplicator = Deduplicator(vector_store)
        # Load existing BM25 corpus if available
        bm25_index.load(bm25_corpus_path)
        before_count = vector_store.count()
        print(f"Pinecone vectors before ingestion: {before_count}\n")

    total_new_docs = 0
    total_new_chunks = 0

    for source in sources:
        sid = source.get_source_id()
        print(f"\n{'─' * 50}")
        print(f"Source: {sid}")
        print(f"{'─' * 50}")

        # 1. Fetch documents
        try:
            documents = source.fetch_documents()
        except Exception as e:
            print(f"[{sid}] FETCH ERROR: {e}")
            continue

        if not documents:
            print(f"[{sid}] No documents fetched.")
            continue

        print(f"[{sid}] Fetched {len(documents)} documents")

        # 2. Deduplicate
        if deduplicator:
            documents = deduplicator.filter_new(documents)
            print(f"[{sid}] After dedup: {len(documents)} new documents")

        if not documents:
            print(f"[{sid}] Nothing new to ingest.")
            continue

        # 3. Chunk
        all_chunks = []
        for doc in documents:
            chunks = chunker.chunk_document(doc)
            all_chunks.extend(chunks)
        print(f"[{sid}] Created {len(all_chunks)} chunks")

        if args.dry_run:
            print(f"[{sid}] DRY RUN — skipping embed + upsert")
            for chunk in all_chunks[:2]:
                print(f"  Sample chunk ID: {chunk['id']}")
                print(f"  Text preview: {chunk['text'][:120]}...")
            total_new_docs += len(documents)
            total_new_chunks += len(all_chunks)
            continue

        # 4. Embed
        print(f"[{sid}] Generating embeddings...")
        chunks_with_embeddings = embedder.embed_chunks(all_chunks)

        # 5. Upsert to Pinecone
        vector_store.add_chunks(chunks_with_embeddings)

        # 6. Update BM25 corpus
        bm25_index.add_chunks(all_chunks)

        # 7. Mark as ingested in deduplicator cache
        deduplicator.mark_ingested(documents)

        total_new_docs += len(documents)
        total_new_chunks += len(all_chunks)

        # Polite pause between sources
        time.sleep(1)

    # Save updated BM25 corpus
    if not args.dry_run and total_new_chunks > 0:
        bm25_index.save(bm25_corpus_path)

    print(f"\n{'=' * 60}")
    print(f"Ingestion complete")
    print(f"  New documents: {total_new_docs}")
    print(f"  New chunks:    {total_new_chunks}")
    if not args.dry_run and vector_store:
        after_count = vector_store.count()
        print(f"  Pinecone vectors: {before_count} → {after_count} (+{after_count - before_count})")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
