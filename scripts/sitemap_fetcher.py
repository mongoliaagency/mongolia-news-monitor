"""
Sitemap-based news fetcher for Next.js SSR sites.
Strategy:
  1. Fetch sitemap XML (e.g. /sitemap/0)
  2. Extract article URLs with lastmod dates
  3. Filter by recent dates
  4. Fetch each article page (SSR)
  5. Extract JSON-LD NewsArticle metadata
"""
import json
import logging
import re

import requests
from bs4 import BeautifulSoup
from date_utils import parse_date, format_date, is_within_days

logger = logging.getLogger(__name__)


def fetch_sitemap(source_file):
    """Fetch news from a sitemap-based source."""
    source = json.loads(open(source_file, 'r', encoding='utf-8').read())
    source_name = source.get('name', 'Unknown')
    category = source.get('category', '党政机关')
    max_days = source.get('sitemap_max_days', 1)
    max_articles = source.get('sitemap_max_articles', 100)
    timeout = source.get('timeout', 20)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    all_articles = []

    # Step 1: Fetch sitemap index pages to discover article URLs
    sitemap_urls = source.get('sitemap_urls', [])
    if not sitemap_urls:
        logger.warning(f"[{source_name}] No sitemap_urls configured")
        return []

    article_candidates = []  # (url, lastmod_str)

    for sitemap_url in sitemap_urls:
        try:
            logger.info(f"[{source_name}] Fetching sitemap: {sitemap_url}")
            resp = requests.get(sitemap_url, headers=headers, timeout=timeout)
            resp.raise_for_status()

            # Parse XML sitemap
            urls = re.findall(r'<loc>([^<]+)</loc>', resp.text)
            lastmods = re.findall(r'<lastmod>([^<]+)</lastmod>', resp.text)

            # Get article URL pattern from config
            article_pattern = source.get('sitemap_article_pattern', '/article/')

            for url, lm in zip(urls, lastmods):
                if article_pattern in url:
                    article_candidates.append((url, lm))

        except Exception as e:
            logger.error(f"[{source_name}] Error fetching sitemap {sitemap_url}: {e}")

    logger.info(f"[{source_name}] Found {len(article_candidates)} total article URLs in sitemaps")

    # Step 2: Filter by recency using lastmod dates
    recent_articles = []

    for url, lm_str in article_candidates:
        if is_within_days(lm_str, days=max_days):
            recent_articles.append((url, lm_str))

    logger.info(f"[{source_name}] {len(recent_articles)} articles within {max_days} days")

    # Step 3: Limit articles
    recent_articles = recent_articles[:max_articles]

    # Step 4: Fetch each article page and extract JSON-LD
    for url, sitemap_date in recent_articles:
        try:
            logger.debug(f"[{source_name}] Fetching article: {url}")
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()

            article = _extract_article_from_html(resp.text, url, source_name, category)
            if article:
                all_articles.append(article)

        except Exception as e:
            logger.error(f"[{source_name}] Error fetching article {url}: {e}")

    logger.info(f"[{source_name}] Successfully extracted {len(all_articles)} articles")
    return all_articles


def _extract_article_from_html(html, url, source_name, category):
    """Extract article metadata from HTML using JSON-LD and meta tags."""
    soup = BeautifulSoup(html, 'lxml')

    # Method 1: JSON-LD structured data (preferred)
    ld_scripts = soup.find_all('script', type='application/ld+json')
    for script in ld_scripts:
        try:
            ld_data = json.loads(script.string)
            if isinstance(ld_data, dict) and ld_data.get('@type') == 'NewsArticle':
                return _from_jsonld(ld_data, url, source_name, category)
        except (json.JSONDecodeError, TypeError, AttributeError):
            continue

    # Method 2: Fallback to meta tags
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ''
    # Remove site name suffix
    title = re.sub(r'\s*\|\s*DNN\.mn\s*$', '', title)

    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc.get('content', '') if meta_desc else ''

    pub_meta = soup.find('meta', attrs={'property': 'article:published_time'})
    pub_date = pub_meta.get('content', '') if pub_meta else ''

    if not title or not pub_date:
        return None

    try:
        parsed = parse_date(pub_date)
        if not parsed or not is_within_days(pub_date, days=1):
            return None
        formatted_date = format_date(parsed)
    except Exception:
        return None

    return {
        'title': title,
        'publish_date': formatted_date,
        'source': source_name,
        'url': url,
        'summary': description,
        'category': category,
    }


def _from_jsonld(ld, url, source_name, category):
    """Build article dict from JSON-LD NewsArticle data."""
    title = ld.get('headline', '')
    description = ld.get('description', '')
    pub_date = ld.get('datePublished', '')

    if not title or not pub_date:
        return None

    try:
        parsed = parse_date(pub_date)
        if not parsed or not is_within_days(pub_date, days=1):
            return None
        formatted_date = format_date(parsed)
    except Exception:
        return None

    return {
        'title': title,
        'publish_date': formatted_date,
        'source': source_name,
        'url': url,
        'summary': description,
        'category': category,
    }


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config/sources/dnn_mn.json'
    articles = fetch_sitemap(config_path)
    for a in articles:
        print(f"[{a['publish_date']}] {a['title'][:80]}")
        print(f"  {a['url']}")
        print(f"  {a.get('summary', '')[:100]}")
        print()
    print(f"Total: {len(articles)}")
