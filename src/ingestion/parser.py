"""
Parser for Lenny's Podcast transcripts.
Extracts YAML frontmatter and dialogue content.
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import yaml


class TranscriptParser:
    """Parse transcript markdown files with YAML frontmatter."""
    
    def __init__(self, episodes_dir: str = "episodes"):
        self.episodes_dir = Path(episodes_dir)
    
    def parse_file(self, filepath: Path) -> Optional[Dict]:
        """
        Parse a single transcript file.
        
        Args:
            filepath: Path to transcript.md file
            
        Returns:
            Dictionary with metadata and content, or None if parsing fails
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
            if not frontmatter_match:
                print(f"Warning: No frontmatter found in {filepath}")
                return None
            
            frontmatter_str, transcript_content = frontmatter_match.groups()
            metadata = yaml.safe_load(frontmatter_str)
            
            # Parse dialogue
            dialogue = self._parse_dialogue(transcript_content)
            
            # Get episode slug from directory name
            episode_slug = filepath.parent.name
            
            return {
                'episode_slug': episode_slug,
                'metadata': metadata,
                'dialogue': dialogue,
                'raw_content': transcript_content
            }
            
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None
    
    def _parse_dialogue(self, content: str) -> List[Dict]:
        """
        Parse dialogue from transcript content.
        
        Format: Speaker (timestamp):\nContent
        
        Returns:
            List of dialogue entries with speaker, timestamp, and text
        """
        dialogue = []
        
        # Pattern: Speaker (HH:MM:SS):
        pattern = r'^([^(]+)\s+\((\d{2}:\d{2}:\d{2})\):\n(.*?)(?=\n\n[^(]+\s+\(\d{2}:\d{2}:\d{2}\):|$)'
        
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            speaker = match.group(1).strip()
            timestamp = match.group(2).strip()
            text = match.group(3).strip()
            
            dialogue.append({
                'speaker': speaker,
                'timestamp': timestamp,
                'text': text
            })
        
        return dialogue
    
    def parse_all_episodes(self) -> List[Dict]:
        """
        Parse all transcript files in the episodes directory.
        
        Returns:
            List of parsed episode dictionaries
        """
        episodes = []
        
        # Find all transcript.md files
        transcript_files = list(self.episodes_dir.glob("*/transcript.md"))
        
        print(f"Found {len(transcript_files)} transcript files")
        
        for filepath in transcript_files:
            parsed = self.parse_file(filepath)
            if parsed:
                episodes.append(parsed)
        
        print(f"Successfully parsed {len(episodes)} episodes")
        return episodes
    
    def get_episode_by_slug(self, slug: str) -> Optional[Dict]:
        """Get a specific episode by its slug."""
        filepath = self.episodes_dir / slug / "transcript.md"
        if filepath.exists():
            return self.parse_file(filepath)
        return None


if __name__ == "__main__":
    # Test the parser
    parser = TranscriptParser()
    
    # Test with Brian Chesky episode
    episode = parser.get_episode_by_slug("brian-chesky")
    if episode:
        print(f"\nEpisode: {episode['metadata']['title']}")
        print(f"Guest: {episode['metadata']['guest']}")
        print(f"Keywords: {episode['metadata'].get('keywords', [])}")
        print(f"Dialogue entries: {len(episode['dialogue'])}")
        if episode['dialogue']:
            print(f"\nFirst dialogue entry:")
            print(f"  Speaker: {episode['dialogue'][0]['speaker']}")
            print(f"  Timestamp: {episode['dialogue'][0]['timestamp']}")
            print(f"  Text preview: {episode['dialogue'][0]['text'][:100]}...")

# Made with Bob
