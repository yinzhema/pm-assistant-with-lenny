"""
Central registry of all web ingestion sources for AskProduct v2.

To add a new source: instantiate it here and append to SOURCES.
To disable a source: comment it out.
"""
from .rss_source import RSSSource
from .html_scraper import HTMLScraperSource

SOURCES = [
    # ── Tier 1: Highest credibility ─────────────────────────────────────────

    HTMLScraperSource(
        source_id="svpg",
        source_name="Silicon Valley Product Group",
        index_url="https://svpg.com/articles/",
        article_link_selector="h2.entry-title a, h1.entry-title a, .entry-title a",
        credibility_tier=1,
        author="Marty Cagan",
        base_url="https://svpg.com",
        source_type="blog",
        content_selector="article",
    ),

    RSSSource(
        source_id="lenny-newsletter",
        source_name="Lenny's Newsletter",
        feed_url="https://www.lennysnewsletter.com/feed",
        credibility_tier=1,
        source_type="newsletter",
    ),

    RSSSource(
        source_id="stratechery",
        source_name="Stratechery",
        feed_url="https://stratechery.com/feed/",
        credibility_tier=1,
        source_type="blog",
        author_override="Ben Thompson",
    ),

    HTMLScraperSource(
        source_id="intercom-blog",
        source_name="Inside Intercom",
        index_url="https://www.intercom.com/blog/product/",
        article_link_selector="a.blog-post__link, h2 a, h3 a, .post-title a",
        credibility_tier=1,
        author="",
        base_url="https://www.intercom.com",
        source_type="blog",
        content_selector="article",
    ),

    # ── Tier 2: High credibility ─────────────────────────────────────────────

    RSSSource(
        source_id="product-growth",
        source_name="Product Growth",
        feed_url="https://www.productgrowth.com/feed",
        credibility_tier=2,
        source_type="newsletter",
    ),

    RSSSource(
        source_id="product-compass",
        source_name="Product Compass",
        feed_url="https://www.productcompass.pm/feed",
        credibility_tier=2,
        source_type="newsletter",
    ),
]
