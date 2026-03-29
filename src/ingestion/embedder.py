"""
Generate embeddings for transcript chunks using OpenAI.
"""
import os
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()


class EmbeddingGenerator:
    """Generate embeddings using OpenAI API."""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize embedding generator.
        
        Args:
            model: OpenAI embedding model to use
        """
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.batch_size = 100  # OpenAI allows up to 2048 inputs per request
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                print(f"Generated embeddings for batch {i//self.batch_size + 1} "
                      f"({len(batch)} texts)")
                
                # Rate limiting - be nice to the API
                if i + self.batch_size < len(texts):
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"Error generating embeddings for batch {i//self.batch_size + 1}: {e}")
                # Add empty embeddings for failed batch
                embeddings.extend([[] for _ in batch])
        
        return embeddings
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Add embeddings to chunk dictionaries.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Chunks with embeddings added
        """
        print(f"Generating embeddings for {len(chunks)} chunks...")
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding
        
        # Count successful embeddings
        successful = sum(1 for chunk in chunks if chunk.get('embedding'))
        print(f"Successfully generated {successful}/{len(chunks)} embeddings")
        
        return chunks


if __name__ == "__main__":
    # Test the embedder
    from parser import TranscriptParser
    from chunker import TranscriptChunker
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment")
        print("Please create a .env file with your OpenAI API key")
        exit(1)
    
    parser = TranscriptParser()
    chunker = TranscriptChunker(chunk_size=800, chunk_overlap=100)
    embedder = EmbeddingGenerator()
    
    # Test with Brian Chesky episode (just first 3 chunks)
    episode = parser.get_episode_by_slug("brian-chesky")
    if episode:
        chunks = chunker.chunk_episode(episode)
        
        # Test with just first 3 chunks
        test_chunks = chunks[:3]
        print(f"\nTesting with {len(test_chunks)} chunks...")
        
        embedded_chunks = embedder.embed_chunks(test_chunks)
        
        if embedded_chunks and embedded_chunks[0].get('embedding'):
            print(f"\nFirst chunk embedding:")
            print(f"  Dimension: {len(embedded_chunks[0]['embedding'])}")
            print(f"  First 5 values: {embedded_chunks[0]['embedding'][:5]}")

# Made with Bob
