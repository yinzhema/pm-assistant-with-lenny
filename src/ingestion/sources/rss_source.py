"""
RSS/Atom feed ingestion source.
Uses requests + stdlib xml.etree.ElementTree (no feedparser dependency).
"""
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseSource, RawDocument

# XML namespaces commonly used in RSS/Atom feeds
_NS = {
    "atom":    "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc":      "http://purl.org/dc/elements/1.1/",
    "media":   "http://search.yahoo.com/mrss/",
}


class RSSSource(BaseSource):
    """Ingest any RSS 2.0 or Atom feed."""

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
            "User-Agent": "AskProduct/2.0 (PM knowledge aggregator)"
        })

    def get_source_id(self) -> str:
        return self.source_id

    def fetch_documents(self) -> List[RawDocument]:
        print(f"[{self.source_id}] Fetching RSS feed: {self.feed_url}")
        try:
            resp = self._session.get(self.feed_url, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            print(f"[{self.source_id}] Failed to fetch feed: {e}")
            return []

        try:
            root = ET.fromstring(resp.content)
        except ET.ParseError as e:
            print(f"[{self.source_id}] XML parse error: {e}")
            return []

        # Detect format: RSS vs Atom
        tag = root.tag.lower()
        if "feed" in tag or root.tag == f"{{{_NS['atom']}}}feed":
            entries = self._parse_atom(root)
        else:
            entries = self._parse_rss(root)

        documents = []
        for entry in entries[: self.max_articles]:
            try:
                doc = self._process_entry(entry)
                if doc and len(doc.text) > 200:
                    documents.append(doc)
                time.sleep(0.3)
            except Exception as e:
                print(f"[{self.source_id}] Error on entry: {e}")

        print(f"[{self.source_id}] Fetched {len(documents)} documents")
        return documents

    # ── Format parsers ────────────────────────────────────────────────────────

    def _parse_rss(self, root: ET.Element) -> List[dict]:
        """Parse RSS 2.0 items."""
        entries = []
        for item in root.iter("item"):
            entry = {
                "title":   _text(item, "title"),
                "url":     _text(item, "link") or _text(item, "guid"),
                "date":    _text(item, "pubDate"),
                "author":  _text(item, f"{{{_NS['dc']}}}creator") or _text(item, "author"),
                "content": (
                    _text(item, f"{{{_NS['content']}}}encoded")
                    or _text(item, "description")
                    or ""
                ),
            }
            entries.append(entry)
        return entries

    def _parse_atom(self, root: ET.Element) -> List[dict]:
        """Parse Atom 1.0 entries."""
        entries = []
        ns = _NS["atom"]
        for entry in root.iter(f"{{{ns}}}entry"):
            link_el = entry.find(f"{{{ns}}}link[@rel='alternate']") or entry.find(f"{{{ns}}}link")
            url = link_el.get("href", "") if link_el is not None else ""

            content_el = entry.find(f"{{{ns}}}content") or entry.find(f"{{{ns}}}summary")
            content = content_el.text or "" if content_el is not None else ""

            author_el = entry.find(f"{{{ns}}}author/{{{ns}}}name")
            author = author_el.text or "" if author_el is not None else ""

            date_el = entry.find(f"{{{ns}}}published") or entry.find(f"{{{ns}}}updated")
            date = date_el.text or "" if date_el is not None else ""

            entries.append({
                "title":   (_text(entry, f"{{{ns}}}title") or ""),
                "url":     url,
                "date":    date,
                "author":  author,
                "content": content,
            })
        return entries

    # ── Document processing ───────────────────────────────────────────────────

    def _process_entry(self, entry: dict) -> Optional[RawDocument]:
        url = entry.get("url", "").strip()
        title = entry.get("title", "").strip()
        if not url:
            return None

        # Try embedded content first; fall back to fetching the full article
        text = self._clean_html(entry.get("content", ""))
        if len(text) < 500:
            text = self._fetch_article_text(url)

        if not text:
            return None

        author = self.author_override or entry.get("author", "").strip()
        publish_date = self._parse_date(entry.get("date", ""))

        return RawDocument(
            title=title or url,
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
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "aside", "form", "noscript", "iframe"]):
            tag.decompose()
        paragraphs = []
        for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "li", "blockquote"]):
            text = tag.get_text(separator=" ", strip=True)
            if len(text) > 40:
                paragraphs.append(text)
        text = "\n\n".join(paragraphs)
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    def _parse_date(self, raw: str) -> Optional[str]:
        if not raw:
            return None
        # ISO 8601 (Atom)
        if "T" in raw:
            return raw[:10]
        # RFC 2822 (RSS pubDate)
        try:
            return parsedate_to_datetime(raw).strftime("%Y-%m-%d")
        except Exception:
            pass
        return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _text(el: ET.Element, tag: str) -> str:
    """Safely get text from a child element."""
    child = el.find(tag)
    return (child.text or "").strip() if child is not None else ""
