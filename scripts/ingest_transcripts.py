"""
Script to ingest all transcripts into the vector store.
Run this once to populate the database.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.parser import TranscriptParser
from src.ingestion.chunker import TranscriptChunker
from src.ingestion.embedder import EmbeddingGenerator
from src.retrieval.vector_store import VectorStore
from dotenv import load_dotenv

load_dotenv()


def ingest_all_transcripts(episodes_dir: str = "episodes", 
                          chunk_size: int = 800,
                          chunk_overlap: int = 100,
                          batch_size: int = 10):
    """
    Ingest all transcripts into the vector store.
    
    Args:
        episodes_dir: Directory containing episode transcripts
        chunk_size: Size of chunks in tokens
        chunk_overlap: Overlap between chunks in tokens
        batch_size: Number of episodes to process at once
    """
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment")
        print("Please create a .env file with your OpenAI API key")
        return
    
    print("=" * 60)
    print("PM Assistant - Transcript Ingestion")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing components...")
    parser = TranscriptParser(episodes_dir)
    chunker = TranscriptChunker(chunk_size, chunk_overlap)
    embedder = EmbeddingGenerator()
    vector_store = VectorStore()
    
    # Check if vector store already has data
    existing_count = vector_store.count()
    if existing_count > 0:
        print(f"\nWarning: Vector store already contains {existing_count} chunks")
        response = input("Do you want to delete existing data and re-ingest? (yes/no): ")
        if response.lower() == 'yes':
            vector_store.delete_all()
            print("Deleted existing data")
        else:
            print("Keeping existing data. Will add new chunks.")
    
    # Parse all episodes
    print("\n2. Parsing transcripts...")
    episodes = parser.parse_all_episodes()
    
    if not episodes:
        print("No episodes found to ingest")
        return
    
    print(f"Found {len(episodes)} episodes to process")
    
    # Process in batches
    total_chunks = 0
    
    for i in range(0, len(episodes), batch_size):
        batch = episodes[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(episodes) + batch_size - 1) // batch_size
        
        print(f"\n3. Processing batch {batch_num}/{total_batches} ({len(batch)} episodes)...")
        
        # Chunk episodes
        print("   - Chunking transcripts...")
        chunks = chunker.chunk_multiple_episodes(batch)
        print(f"   - Created {len(chunks)} chunks")
        
        # Generate embeddings
        print("   - Generating embeddings...")
        embedded_chunks = embedder.embed_chunks(chunks)
        
        # Add to vector store
        print("   - Adding to vector store...")
        vector_store.add_chunks(embedded_chunks)
        
        total_chunks += len(chunks)
        print(f"   ✓ Batch {batch_num} complete")
    
    # Summary
    print("\n" + "=" * 60)
    print("Ingestion Complete!")
    print("=" * 60)
    print(f"Total episodes processed: {len(episodes)}")
    print(f"Total chunks created: {total_chunks}")
    print(f"Chunks in vector store: {vector_store.count()}")
    print(f"\nYou can now run the Streamlit app: streamlit run app.py")


def ingest_single_episode(episode_slug: str):
    """
    Ingest a single episode (useful for testing or updates).
    
    Args:
        episode_slug: Episode directory name (e.g., 'brian-chesky')
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found")
        return
    
    print(f"Ingesting episode: {episode_slug}")
    
    parser = TranscriptParser()
    chunker = TranscriptChunker()
    embedder = EmbeddingGenerator()
    vector_store = VectorStore()
    
    # Parse episode
    episode = parser.get_episode_by_slug(episode_slug)
    if not episode:
        print(f"Episode '{episode_slug}' not found")
        return
    
    print(f"Episode: {episode['metadata']['title']}")
    
    # Chunk
    chunks = chunker.chunk_episode(episode)
    print(f"Created {len(chunks)} chunks")
    
    # Embed
    embedded_chunks = embedder.embed_chunks(chunks)
    
    # Store
    vector_store.add_chunks(embedded_chunks)
    
    print(f"✓ Successfully ingested {episode_slug}")
    print(f"Total chunks in store: {vector_store.count()}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest Lenny's Podcast transcripts")
    parser.add_argument('--episode', type=str, help='Ingest a single episode by slug')
    parser.add_argument('--batch-size', type=int, default=10, 
                       help='Number of episodes to process at once (default: 10)')
    parser.add_argument('--chunk-size', type=int, default=800,
                       help='Chunk size in tokens (default: 800)')
    parser.add_argument('--chunk-overlap', type=int, default=100,
                       help='Chunk overlap in tokens (default: 100)')
    
    args = parser.parse_args()
    
    if args.episode:
        ingest_single_episode(args.episode)
    else:
        ingest_all_transcripts(
            batch_size=args.batch_size,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )

# Made with Bob
