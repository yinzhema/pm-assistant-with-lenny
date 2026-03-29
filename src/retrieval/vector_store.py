"""
ChromaDB vector store for transcript chunks.
"""
import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings


class VectorStore:
    """Manage ChromaDB vector store for transcript chunks."""
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        """
        Initialize ChromaDB client.
        
        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="lenny_transcripts",
            metadata={"description": "Lenny's Podcast transcript chunks"}
        )
    
    def add_chunks(self, chunks: List[Dict]) -> None:
        """
        Add chunks to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with embeddings
        """
        if not chunks:
            print("No chunks to add")
            return
        
        # Filter out chunks without embeddings
        valid_chunks = [c for c in chunks if c.get('embedding')]
        
        if not valid_chunks:
            print("No valid chunks with embeddings")
            return
        
        # Prepare data for ChromaDB
        ids = [chunk['id'] for chunk in valid_chunks]
        embeddings = [chunk['embedding'] for chunk in valid_chunks]
        documents = [chunk['text'] for chunk in valid_chunks]
        metadatas = [chunk['metadata'] for chunk in valid_chunks]
        
        # Convert list fields and dates to strings for ChromaDB
        for metadata in metadatas:
            if 'keywords' in metadata and isinstance(metadata['keywords'], list):
                metadata['keywords'] = ','.join(metadata['keywords'])
            if 'publish_date' in metadata and metadata['publish_date']:
                metadata['publish_date'] = str(metadata['publish_date'])
        
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            print(f"Added {len(valid_chunks)} chunks to vector store")
        except Exception as e:
            print(f"Error adding chunks to vector store: {e}")
    
    def search(self, query_embedding: List[float], n_results: int = 5,
               where: Optional[Dict] = None) -> Dict:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Search results with ids, documents, metadatas, and distances
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            return results
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    
    def get_by_id(self, chunk_id: str) -> Optional[Dict]:
        """Get a specific chunk by ID."""
        try:
            result = self.collection.get(ids=[chunk_id])
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'text': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
        except Exception as e:
            print(f"Error getting chunk by ID: {e}")
        return None
    
    def count(self) -> int:
        """Get total number of chunks in the store."""
        return self.collection.count()
    
    def delete_all(self) -> None:
        """Delete all chunks from the collection."""
        try:
            # Delete the collection
            self.client.delete_collection(name="lenny_transcripts")
            # Recreate it
            self.collection = self.client.get_or_create_collection(
                name="lenny_transcripts",
                metadata={"description": "Lenny's Podcast transcript chunks"}
            )
            print("Deleted all chunks from vector store")
        except Exception as e:
            print(f"Error deleting chunks: {e}")
    
    def get_all_episodes(self) -> List[str]:
        """Get list of all episode slugs in the store."""
        try:
            # Get all items (this might be slow for large collections)
            results = self.collection.get()
            episodes = set()
            for metadata in results['metadatas']:
                if 'episode_slug' in metadata:
                    episodes.add(metadata['episode_slug'])
            return sorted(list(episodes))
        except Exception as e:
            print(f"Error getting episodes: {e}")
            return []


if __name__ == "__main__":
    # Test the vector store
    store = VectorStore()
    
    print(f"Vector store initialized")
    print(f"Total chunks: {store.count()}")
    
    episodes = store.get_all_episodes()
    if episodes:
        print(f"Episodes in store: {len(episodes)}")
        print(f"First 5 episodes: {episodes[:5]}")

# Made with Bob
