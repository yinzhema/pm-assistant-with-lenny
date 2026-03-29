"""
Semantic chunking for transcript content.
Chunks dialogue into meaningful segments for embedding.
"""
import re
from typing import List, Dict


class TranscriptChunker:
    """Chunk transcripts into semantic segments."""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target size in tokens (approximate)
            chunk_overlap: Overlap between chunks in tokens (approximate)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Approximate: 1 token ≈ 4 characters for English text
        self.chars_per_token = 4
    
    def count_tokens(self, text: str) -> int:
        """
        Approximate token count based on character length.
        This is a simple approximation: 1 token ≈ 4 characters.
        """
        return len(text) // self.chars_per_token
    
    def chunk_episode(self, episode: Dict) -> List[Dict]:
        """
        Chunk an episode into semantic segments.
        
        Args:
            episode: Parsed episode dictionary from TranscriptParser
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        dialogue = episode['dialogue']
        metadata = episode['metadata']
        episode_slug = episode['episode_slug']
        
        if not dialogue:
            return chunks
        
        # Group dialogue entries into chunks
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        
        for i, entry in enumerate(dialogue):
            entry_text = f"{entry['speaker']}: {entry['text']}"
            entry_tokens = self.count_tokens(entry_text)
            
            # If adding this entry exceeds chunk size, save current chunk
            if current_tokens + entry_tokens > self.chunk_size and current_chunk:
                chunk_text = self._format_chunk(current_chunk)
                chunks.append(self._create_chunk_dict(
                    chunk_text, 
                    current_chunk[0],  # First entry for timestamp
                    metadata, 
                    episode_slug, 
                    chunk_index
                ))
                
                # Start new chunk with overlap
                overlap_entries = self._get_overlap_entries(current_chunk, self.chunk_overlap)
                current_chunk = overlap_entries
                current_tokens = sum(self.count_tokens(f"{e['speaker']}: {e['text']}") 
                                   for e in current_chunk)
                chunk_index += 1
            
            current_chunk.append(entry)
            current_tokens += entry_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = self._format_chunk(current_chunk)
            chunks.append(self._create_chunk_dict(
                chunk_text, 
                current_chunk[0], 
                metadata, 
                episode_slug, 
                chunk_index
            ))
        
        return chunks
    
    def _format_chunk(self, dialogue_entries: List[Dict]) -> str:
        """Format dialogue entries into readable chunk text."""
        lines = []
        for entry in dialogue_entries:
            lines.append(f"{entry['speaker']}: {entry['text']}")
        return "\n\n".join(lines)
    
    def _get_overlap_entries(self, entries: List[Dict], overlap_tokens: int) -> List[Dict]:
        """Get last few entries that fit within overlap token limit."""
        overlap_entries = []
        tokens = 0
        
        for entry in reversed(entries):
            entry_tokens = self.count_tokens(f"{entry['speaker']}: {entry['text']}")
            if tokens + entry_tokens > overlap_tokens:
                break
            overlap_entries.insert(0, entry)
            tokens += entry_tokens
        
        return overlap_entries
    
    def _create_chunk_dict(self, text: str, first_entry: Dict, 
                          metadata: Dict, episode_slug: str, 
                          chunk_index: int) -> Dict:
        """Create chunk dictionary with all metadata."""
        return {
            'id': f"{episode_slug}-chunk-{chunk_index:03d}",
            'text': text,
            'metadata': {
                'episode_slug': episode_slug,
                'guest': metadata.get('guest', ''),
                'title': metadata.get('title', ''),
                'youtube_url': metadata.get('youtube_url', ''),
                'timestamp': first_entry['timestamp'],
                'keywords': metadata.get('keywords', []),
                'publish_date': metadata.get('publish_date', ''),
                'chunk_index': chunk_index,
                'token_count': self.count_tokens(text)
            }
        }
    
    def chunk_multiple_episodes(self, episodes: List[Dict]) -> List[Dict]:
        """
        Chunk multiple episodes.
        
        Args:
            episodes: List of parsed episode dictionaries
            
        Returns:
            List of all chunks from all episodes
        """
        all_chunks = []
        
        for episode in episodes:
            chunks = self.chunk_episode(episode)
            all_chunks.extend(chunks)
        
        return all_chunks


if __name__ == "__main__":
    # Test the chunker
    from parser import TranscriptParser
    
    parser = TranscriptParser()
    chunker = TranscriptChunker(chunk_size=800, chunk_overlap=100)
    
    # Test with Brian Chesky episode
    episode = parser.get_episode_by_slug("brian-chesky")
    if episode:
        chunks = chunker.chunk_episode(episode)
        print(f"\nChunked episode into {len(chunks)} chunks")
        
        if chunks:
            print(f"\nFirst chunk:")
            print(f"  ID: {chunks[0]['id']}")
            print(f"  Tokens: {chunks[0]['metadata']['token_count']}")
            print(f"  Timestamp: {chunks[0]['metadata']['timestamp']}")
            print(f"  Text preview: {chunks[0]['text'][:200]}...")
            
            if len(chunks) > 1:
                print(f"\nSecond chunk:")
                print(f"  ID: {chunks[1]['id']}")
                print(f"  Tokens: {chunks[1]['metadata']['token_count']}")
                print(f"  Timestamp: {chunks[1]['metadata']['timestamp']}")

# Made with Bob
