"""
Pinecone vector store for transcript chunks.
"""
import os
import unicodedata
from typing import List, Dict, Optional
from pinecone import Pinecone


def _ascii_id(s: str) -> str:
    """Convert a string to an ASCII-safe ID (Pinecone requirement)."""
    normalized = unicodedata.normalize('NFKD', s)
    return normalized.encode('ascii', 'ignore').decode('ascii')


class VectorStore:
    """Manage Pinecone vector store for transcript chunks."""

    def __init__(self):
        """Initialize Pinecone client and connect to index."""
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME", os.getenv("PINECONE_INDEX", "lenny-podcast"))

        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables.")

        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)

    def add_chunks(self, chunks: List[Dict]) -> None:
        """
        Upsert chunks into Pinecone.

        Args:
            chunks: List of chunk dicts with 'id', 'embedding', 'text', 'metadata'
        """
        if not chunks:
            print("No chunks to add")
            return

        valid_chunks = [c for c in chunks if c.get('embedding')]
        if not valid_chunks:
            print("No valid chunks with embeddings")
            return

        vectors = []
        for chunk in valid_chunks:
            metadata = dict(chunk['metadata'])
            # Flatten list fields for Pinecone (metadata values must be scalar/list of strings)
            if 'keywords' in metadata and isinstance(metadata['keywords'], list):
                metadata['keywords'] = ','.join(metadata['keywords'])
            if 'publish_date' in metadata and metadata['publish_date']:
                metadata['publish_date'] = str(metadata['publish_date'])
            if 'chunk_index' in metadata:
                metadata['chunk_index'] = int(metadata['chunk_index'])
            if 'token_count' in metadata:
                metadata['token_count'] = int(metadata['token_count'])
            # Store document text inside metadata so we can retrieve it
            metadata['text'] = chunk['text']

            vectors.append({
                'id': _ascii_id(chunk['id']),
                'values': chunk['embedding'],
                'metadata': metadata,
            })

        # Pinecone recommends upserting in batches of ≤100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)

        print(f"Upserted {len(valid_chunks)} chunks to Pinecone")

    def search(self, query_embedding: List[float], n_results: int = 5,
               where: Optional[Dict] = None) -> Dict:
        """
        Search for similar chunks.

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter (Pinecone filter dict)

        Returns:
            Results dict matching ChromaDB format:
            {'ids': [[...]], 'documents': [[...]], 'metadatas': [[...]], 'distances': [[...]]}
        """
        try:
            kwargs = {
                'vector': query_embedding,
                'top_k': n_results,
                'include_metadata': True,
            }
            if where:
                kwargs['filter'] = where

            response = self.index.query(**kwargs)
            matches = response.get('matches', [])

            ids = [[m['id'] for m in matches]]
            documents = [[m['metadata'].get('text', '') for m in matches]]
            row = []
            for m in matches:
                meta = dict(m['metadata'])
                meta.pop('text', None)  # Remove text from metadata (it's in documents)
                row.append(meta)
            metadatas = [row]
            distances = [[1 - m['score'] for m in matches]]  # Convert similarity → distance

            return {
                'ids': ids,
                'documents': documents,
                'metadatas': metadatas,
                'distances': distances,
            }
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}

    def get_by_id(self, chunk_id: str) -> Optional[Dict]:
        """Get a specific chunk by ID."""
        try:
            result = self.index.fetch(ids=[_ascii_id(chunk_id)])
            vectors = result.get('vectors', {})
            if chunk_id in vectors:
                v = vectors[chunk_id]
                meta = dict(v['metadata'])
                text = meta.pop('text', '')
                return {'id': chunk_id, 'text': text, 'metadata': meta}
        except Exception as e:
            print(f"Error getting chunk by ID: {e}")
        return None

    def count(self) -> int:
        """Get total number of vectors in the index."""
        try:
            stats = self.index.describe_index_stats()
            return stats.get('total_vector_count', 0)
        except Exception as e:
            print(f"Error getting count: {e}")
            return 0

    def delete_all(self) -> None:
        """Delete all vectors from the index."""
        try:
            self.index.delete(delete_all=True)
            print("Deleted all vectors from Pinecone index")
        except Exception as e:
            print(f"Error deleting vectors: {e}")

    def get_all_episodes(self) -> List[str]:
        """Get list of all unique episode slugs (derived from vector IDs)."""
        try:
            episodes = set()
            for ids_page in self.index.list():
                for vid in ids_page:
                    # IDs are formatted as "{episode_slug}-chunk-{index}"
                    parts = vid.rsplit('-chunk-', 1)
                    if len(parts) == 2:
                        episodes.add(parts[0])
            return sorted(list(episodes))
        except Exception as e:
            print(f"Error getting episodes: {e}")
            return []
