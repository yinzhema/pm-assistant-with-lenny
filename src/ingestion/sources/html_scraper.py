"""
Static HTML scraper for blogs that don't provide RSS
or need direct scraping (svpg.com, intercom.com/blog, etc.).
"""
import time
import re
from typing import List, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .base import BaseSource, RawDocument


class HTMLScraperSource(BaseSource):
    """
    Ingest static HTML blogs by crawling an index page to discover
    article URLs, then scraping each article individually.
    """

    def __init__(
        self,
        source_id: str,
        source_name: str,
        index_url: str,
        article_link_selector: str,
        credibility_tier: int,
        author: str = "",
        base_url: str = "",
        source_type: str = "blog",
        content_selector: str = "article",
        max_articles: int = 100,
    ):
        self.source_id = source_id
        self.source_name = source_name
        self.index_url = index_url
        self.article_link_selector = article_link_selector
        self.credibility_tier = credibility_tier
        self.default_author = author
        self.base_url = base_url.rstrip("/")
        self.source_type = source_type
        self.content_selector = content_selector
        self.max_articles = max_articles
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "AskProduct/2.0 (PM knowledge aggregator; contact@askproduct.ai)"
        })

    def get_source_id(self) -> str:
        return self.source_id

    def fetch_documents(self) -> List[RawDocument]:
        print(f"[{self.source_id}] Crawling index: {self.index_url}")
        urls = self._get_article_urls()
        print(f"[{self.source_id}] Found {len(urls)} article URLs")

        documents = []
        for url in urls[: self.max_articles]:
            try:
                doc = self._scrape_article(url)
                if doc and len(doc.text) > 200:
                    documents.append(doc)
                time.sleep(0.5)  # polite crawl delay
            except Exception as e:
                print(f"[{self.source_id}] Error scraping {url}: {e}")

        print(f"[{self.source_id}] Scraped {len(documents)} documents")
        return documents

    def _get_article_urls(self) -> List[str]:
        try:
            resp = self._session.get(self.index_url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            urls = []
            for a in soup.select(self.article_link_selector):
                href = a.get("href", "").strip()
                if not href:
                    continue
                if href.startswith("http"):
                    urls.append(href)
                elif href.startswith("/"):
                    urls.append(self.base_url + href)

            # Deduplicate while preserving order
            seen = set()
            unique = []
            for u in urls:
                if u not in seen:
                    seen.add(u)
                    unique.append(u)
            return unique
        except Exception as e:
            print(f"[{self.source_id}] Could not crawl index page: {e}")
            return []

    def _scrape_article(self, url: str) -> Optional[RawDocument]:
        resp = self._session.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Title
        title_tag = soup.find("h1") or soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else url

        # Author
        author = self._extract_author(soup)

        # Date
        publish_date = self._extract_date(soup)

        # Content
        text = self._extract_text(soup)
        if not text:
            return None

        return RawDocument(
            title=title,
            text=text,
            url=url,
            author=author or self.default_author,
            publish_date=publish_date,
            source_name=self.source_name,
            source_id=self.source_id,
            source_type=self.source_type,
            credibility_tier=self.credibility_tier,
        )

    def _extract_text(self, soup: BeautifulSoup) -> str:
        # Remove boilerplate
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "aside", "form", "noscript", "iframe"]):
            tag.decompose()

        # Try content selector first, fall back to body
        container = soup.select_one(self.content_selector) or soup.body
        if not container:
            return ""

        paragraphs = []
        for tag in container.find_all(["p", "h1", "h2", "h3", "h4", "li", "blockquote"]):
            text = tag.get_text(separator=" ", strip=True)
            if len(text) > 40:
                paragraphs.append(text)

        text = "\n\n".join(paragraphs)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _extract_author(self, soup: BeautifulSoup) -> str:
        # Try common author meta patterns
        for selector in [
            'meta[name="author"]',
            '[rel="author"]',
            ".author-name",
            ".byline",
            '[class*="author"]',
        ]:
            el = soup.select_one(selector)
            if el:
                val = el.get("content") or el.get_text(strip=True)
                if val:
                    return val.strip()
        return self.default_author

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        # Try <time> tags and meta tags
        for selector in ['time[datetime]', 'meta[property="article:published_time"]',
                         'meta[name="publish-date"]']:
            el = soup.select_one(selector)
            if el:
                raw = el.get("datetime") or el.get("content", "")
                if raw:
                    try:
                        return raw[:10]  # YYYY-MM-DD
                    except Exception:
                        pass
        return None
