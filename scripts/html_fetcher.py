import json
import time

import requests

from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright

from date_utils import parse_date, format_date, is_within_days


def _fetch_with_retry(url, requires_browser=False, max_retries=3, timeout=60):
    """Fetch URL with retry logic for connection timeouts."""
    last_error = None
    for attempt in range(max_retries):
        try:
            if requires_browser:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, args=[
                        '--disable-gpu',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ])
                    page = browser.new_page()
                    page.set_extra_http_headers({
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "mn-MN,en-US;q=0.9",
                    })
                    # Use 'load' instead of 'networkidle' — Mongolian servers often
                    # keep long-lived connections open, causing networkidle to timeout.
                    page.goto(url, wait_until='load', timeout=timeout * 1000)
                    # Give the page a little extra time to render dynamic content
                    page.wait_for_timeout(2000)
                    html_content = page.content()
                    browser.close()
                return html_content
            else:
                response = requests.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=timeout
                )
                response.encoding = response.apparent_encoding
                return response.text
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = (attempt + 1) * 10
                time.sleep(wait)
            else:
                raise last_error


def fetch_html(source_file):

    with open(
        source_file,
        "r",
        encoding="utf-8"
    ) as f:

        source = json.load(f)

    url = source["news_url"]
    requires_browser = source.get("requires_browser", False)

    try:
        html_content = _fetch_with_retry(url, requires_browser=requires_browser)
    except Exception as e:
        if not requires_browser:
            try:
                html_content = _fetch_with_retry(url, requires_browser=True)
            except Exception:
                raise
        else:
            raise

    try:
        soup = BeautifulSoup(html_content, "lxml")
    except Exception:
        soup = BeautifulSoup(html_content, "html.parser")

    news = []

    items_selector = source.get("items_selector")
    title_selector = source.get("title_selector")
    link_selector = source.get("link_selector", title_selector)
    title_attr = source.get("title_attr")  # e.g. "alt" to read title from img alt
    date_selector = source.get("date_selector")
    date_attr = source.get("date_attr")  # e.g. "src" to read date from img src
    exclude_urls = source.get("exclude_urls", [])  # URL substrings to skip (e.g. static pages)

    if items_selector:
        items = soup.select(items_selector)
    elif title_selector:
        items = soup.select(title_selector)
    else:
        items = []

    for item in items[:100]:

        if items_selector:
            title_node = item.select_one(title_selector) if title_selector else item
            link_node = item.select_one(link_selector) if link_selector else title_node
        else:
            title_node = item
            link_node = item

        if title_attr and title_node:
            title = title_node.get(title_attr, '').strip()
        else:
            title = title_node.get_text(strip=True) if title_node else ""

        if not title:
            continue

        link = link_node.get("href", "") if link_node else ""

        # Fallback: if link_node didn't yield a href, try the item itself
        if not link and item.name == 'a':
            link = item.get("href", "")

        if not link:
            continue

        if link.startswith("/"):
            link = source["homepage"].rstrip("/") + link
        elif link.startswith("//"):
            link = "https:" + link
        elif not link.startswith("http"):
            link = source["homepage"].rstrip("/") + "/" + link.lstrip("/")

        # Skip excluded URLs (e.g. static pages, navigation links)
        if exclude_urls:
            link_lower = link.lower()
            skip = False
            for pattern in exclude_urls:
                if pattern.lower() in link_lower:
                    skip = True
                    break
            if skip:
                continue

        publish_date_str = None
        date_from_text_fallback = source.get("date_from_item_text", False)

        if date_selector:
            date_node = item.select_one(date_selector)
            if date_node:
                if date_attr:
                    raw_date = date_node.get(date_attr, '')
                    # URL-decode if needed (e.g. Next.js image src with %2F)
                    if '%' in raw_date:
                        from urllib.parse import unquote
                        raw_date = unquote(raw_date)
                else:
                    raw_date = date_node.get_text(strip=True)
                dt = parse_date(raw_date)
                if dt:
                    publish_date_str = format_date(dt)
        elif date_from_text_fallback:
            # No date_selector configured, extract from item text
            dt = parse_date(item.get_text(strip=True))
            if dt:
                publish_date_str = format_date(dt)

        # Fallback: extract date from item's full text when date_selector didn't yield a date
        if not publish_date_str and date_from_text_fallback and date_selector:
            dt = parse_date(item.get_text(strip=True))
            if dt:
                publish_date_str = format_date(dt)

        # Only keep articles with a parsed date matching today
        if not publish_date_str:
            continue

        news.append({
            "title": title,
            "publish_date": publish_date_str,
            "source": source["name"],
            "url": link,
            "category": source.get("category", "党政机关"),
        })

    # Filter: only articles from the last 7 days
    filtered_news = [item for item in news if is_within_days(item["publish_date"], days=7)]

    return filtered_news
