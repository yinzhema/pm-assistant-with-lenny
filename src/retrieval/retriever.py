"""
Retrieval system for finding relevant transcript chunks.
"""
from typing import List, Dict, Optional
from .vector_store import VectorStore
from ..ingestion.embedder import EmbeddingGenerator


class Retriever:
    """Retrieve relevant chunks for queries."""
    
    def __init__(self, vector_store: VectorStore, embedder: EmbeddingGenerator):
        """
        Initialize retriever.
        
        Args:
            vector_store: VectorStore instance
            embedder: EmbeddingGenerator instance
        """
        self.vector_store = vector_store
        self.embedder = embedder
    
    def retrieve(self, query: str, n_results: int = 5, 
                 filters: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User query
            n_results: Number of results to return
            filters: Optional metadata filters (e.g., {'guest': 'Brian Chesky'})
            
        Returns:
            List of relevant chunks with metadata and similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_embedding(query)
        
        if not query_embedding:
            print("Failed to generate query embedding")
            return []
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            where=filters
        )
        
        # Format results
        chunks = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                chunk = {
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                }
                chunks.append(chunk)
        
        return chunks
    
    def retrieve_with_context(self, query: str, n_results: int = 5) -> Dict:
        """
        Retrieve chunks and format them for LLM context.
        
        Args:
            query: User query
            n_results: Number of results to return
            
        Returns:
            Dictionary with formatted context and source information
        """
        chunks = self.retrieve(query, n_results)
        
        if not chunks:
            return {
                'context': "No relevant information found.",
                'sources': []
            }
        
        # Format context
        context_parts = []
        sources = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk['metadata']
            
            # Format chunk with citation
            context_parts.append(
                f"[Source {i}] From {metadata.get('guest', 'Unknown')} - "
                f"{metadata.get('title', 'Unknown Episode')} "
                f"(Timestamp: {metadata.get('timestamp', 'N/A')}):\n"
                f"{chunk['text']}\n"
            )
            
            # Collect source info
            sources.append({
                'number': i,
                'guest': metadata.get('guest', 'Unknown'),
                'title': metadata.get('title', 'Unknown Episode'),
                'timestamp': metadata.get('timestamp', 'N/A'),
                'youtube_url': metadata.get('youtube_url', ''),
                'similarity_score': chunk['similarity_score']
            })
        
        context = "\n---\n".join(context_parts)
        
        return {
            'context': context,
            'sources': sources
        }
    
    def retrieve_by_topic(self, topic: str, n_results: int = 10) -> List[Dict]:
        """
        Retrieve chunks by topic keyword.
        
        Args:
            topic: Topic keyword (e.g., 'product-management')
            n_results: Number of results to return
            
        Returns:
            List of chunks matching the topic
        """
        # For topic-based retrieval, we'll use a semantic search
        # with the topic as the query
        query = f"insights about {topic.replace('-', ' ')}"
        return self.retrieve(query, n_results)


if __name__ == "__main__":
    # Test the retriever
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found")
        exit(1)
    
    vector_store = VectorStore()
    embedder = EmbeddingGenerator()
    retriever = Retriever(vector_store, embedder)
    
    # Test query
    query = "How do I find product-market fit?"
    print(f"\nQuery: {query}")
    print(f"Total chunks in store: {vector_store.count()}")
    
    if vector_store.count() > 0:
        result = retriever.retrieve_with_context(query, n_results=3)
        
        print(f"\nFound {len(result['sources'])} relevant sources")
        print("\nSources:")
        for source in result['sources']:
            print(f"  {source['number']}. {source['guest']} - {source['title']}")
            print(f"     Similarity: {source['similarity_score']:.3f}")
    else:
        print("\nVector store is empty. Run ingestion first.")

# Made with Bob
