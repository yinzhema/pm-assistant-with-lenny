"""
RSS/Atom feed ingestion source.
Handles Substack newsletters, blog RSS feeds, etc.
"""
import time
import re
from typing import List, Optional
from datetime import datetime

import feedparser
import requests
from bs4 import BeautifulSoup

from .base import BaseSource, RawDocument


class RSSSource(BaseSource):
    """Ingest any RSS/Atom feed (Substack, blogs)."""

    def __init__(
        self,
        source_id: str,
        source_name: str,
        feed_url: str,
        credibility_tier: int,
        source_type: str = "newsletter",
        author_override: Optional[str] = None,
        max_articles: int = 100,
    ):
        self.source_id = source_id
        self.source_name = source_name
        self.feed_url = feed_url
        self.credibility_tier = credibility_tier
        self.source_type = source_type
        self.author_override = author_override
        self.max_articles = max_articles
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "AskProduct/2.0 (PM knowledge aggregator; contact@askproduct.ai)"
        })

    def get_source_id(self) -> str:
        return self.source_id

    def fetch_documents(self) -> List[RawDocument]:
        print(f"[{self.source_id}] Fetching RSS feed: {self.feed_url}")
        feed = feedparser.parse(self.feed_url)

        if feed.bozo and not feed.entries:
            print(f"[{self.source_id}] Feed parse error: {feed.bozo_exception}")
            return []

        documents = []
        for entry in feed.entries[: self.max_articles]:
            try:
                doc = self._process_entry(entry)
                if doc and len(doc.text) > 200:
                    documents.append(doc)
                time.sleep(0.3)  # polite crawl delay
            except Exception as e:
                print(f"[{self.source_id}] Error processing entry '{entry.get('title', '?')}': {e}")

        print(f"[{self.source_id}] Fetched {len(documents)} documents")
        return documents

    def _process_entry(self, entry) -> Optional[RawDocument]:
        title = entry.get("title", "").strip()
        url = entry.get("link", "").strip()
        if not url:
            return None

        # Try to get full article HTML from entry content first
        content_html = ""
        if "content" in entry and entry["content"]:
            content_html = entry["content"][0].get("value", "")
        elif "summary" in entry:
            content_html = entry["summary"]

        # If content is too short, try fetching the full article
        text = self._clean_html(content_html)
        if len(text) < 500:
            text = self._fetch_article_text(url)

        if not text:
            return None

        author = self.author_override or self._extract_author(entry)
        publish_date = self._extract_date(entry)

        return RawDocument(
            title=title,
            text=text,
            url=url,
            author=author,
            publish_date=publish_date,
            source_name=self.source_name,
            source_id=self.source_id,
            source_type=self.source_type,
            credibility_tier=self.credibility_tier,
        )

    def _fetch_article_text(self, url: str) -> str:
        try:
            resp = self._session.get(url, timeout=15)
            resp.raise_for_status()
            return self._clean_html(resp.text)
        except Exception as e:
            print(f"[{self.source_id}] Could not fetch {url}: {e}")
            return ""

    def _clean_html(self, html: str) -> str:
        if not html:
            return ""
        soup = BeautifulSoup(html, "lxml")

        # Remove boilerplate elements
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "aside", "form", "noscript", "iframe", "figure"]):
            tag.decompose()

        # Extract meaningful text
        paragraphs = []
        for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "li", "blockquote"]):
            text = tag.get_text(separator=" ", strip=True)
            if len(text) > 40:
                paragraphs.append(text)

        text = "\n\n".join(paragraphs)
        # Collapse excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _extract_author(self, entry) -> str:
        if "author" in entry:
            return entry["author"].strip()
        if "authors" in entry and entry["authors"]:
            return entry["authors"][0].get("name", "").strip()
        return ""

    def _extract_date(self, entry) -> Optional[str]:
        for field in ("published_parsed", "updated_parsed"):
            parsed = entry.get(field)
            if parsed:
                try:
                    return datetime(*parsed[:3]).strftime("%Y-%m-%d")
                except Exception:
                    pass
        return None
