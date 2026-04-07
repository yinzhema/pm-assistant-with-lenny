"""
Ingestion sources package for AskProduct v2.
"""
from .base import RawDocument, BaseSource
from .rss_source import RSSSource
from .html_scraper import HTMLScraperSource

__all__ = ["RawDocument", "BaseSource", "RSSSource", "HTMLScraperSource"]
