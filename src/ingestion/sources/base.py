"""
Base classes for all ingestion sources.
"""
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RawDocument:
    """Normalized document before chunking."""
    title: str
    text: str                   # clean plain text
    url: str
    author: str
    publish_date: Optional[str] # YYYY-MM-DD or None
    source_name: str
    source_id: str              # e.g. 'svpg', 'lenny-newsletter'
    source_type: str            # 'blog' | 'newsletter' | 'podcast'
    credibility_tier: int       # 1 = highest signal
    content_hash: str = field(init=False)

    def __post_init__(self):
        self.content_hash = "sha256:" + hashlib.sha256(self.text.encode()).hexdigest()


class BaseSource(ABC):
    """Abstract base for all web ingestion sources."""

    @abstractmethod
    def fetch_documents(self) -> List[RawDocument]:
        """Fetch and return all new/updated documents from this source."""
        ...

    @abstractmethod
    def get_source_id(self) -> str:
        """Short machine-readable identifier used in vector ID prefix."""
        ...
