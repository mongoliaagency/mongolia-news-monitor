import json
import time

import requests

from bs4 import BeautifulSoup

from datetime import datetime

from playwright.sync_api import sync_playwright


def _fetch_with_retry(url, requires_browser=False, max_retries=3, timeout=45):
    """Fetch URL with retry logic for connection timeouts."""
    last_error = None
    for attempt in range(max_retries):
        try:
            if requires_browser:
                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()
                    page.goto(url, wait_until='networkidle', timeout=timeout * 1000)
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
                print(f"  Retry {attempt + 1}/{max_retries} for {url} in {wait}s: {e}")
                time.sleep(wait)
            else:
                raise last_error


def parse_publish_date(raw_date):
    if not raw_date:
        return None

    raw_date = raw_date.strip()
    
    # Remove common date prefixes/icons
    if raw_date.startswith('far fa-clock'):
        raw_date = raw_date.replace('far fa-clock', '').strip()

    formats = [
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%d-%m-%Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(raw_date, fmt)
            return dt.strftime("%a, %d %b %Y 00:00:00 GMT")
        except Exception:
            continue

    return None


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
            # Fallback: try with Playwright browser rendering
            print(f"  Falling back to Playwright for {url}: {e}")
            try:
                html_content = _fetch_with_retry(url, requires_browser=True)
            except Exception as e2:
                raise Exception(f"All fetch methods failed for {url}: {e2}")
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
    date_selector = source.get("date_selector")

    if items_selector:
        items = soup.select(items_selector)
    elif title_selector:
        items = soup.select(title_selector)
    else:
        source_name = source.get("name", source_file)
        print(f"  WARNING: {source_name} is missing both 'items_selector' and 'title_selector' in config, returning 0 articles")
        items = []

    for item in items[:100]:

        if items_selector:
            title_node = item.select_one(title_selector) if title_selector else item
            link_node = item.select_one(link_selector) if link_selector else title_node
        else:
            title_node = item
            link_node = item

        title = title_node.get_text(strip=True) if title_node else ""

        if not title:
            continue

        link = link_node.get("href", "") if link_node else ""

        if not link:
            continue

        if link.startswith("/"):
            link = source["homepage"].rstrip("/") + link
        elif link.startswith("//"):
            link = "https:" + link
        elif not link.startswith("http"):
            link = source["homepage"].rstrip("/") + "/" + link.lstrip("/")

        publish_date = None
        if date_selector:
            date_node = item.select_one(date_selector)
            if date_node:
                publish_date = parse_publish_date(date_node.get_text(strip=True))

        if not publish_date:
            publish_date = datetime.now().strftime(
                "%a, %d %b %Y 00:00:00 GMT"
            )

        news.append({
            "title": title,
            "publish_date": publish_date,
            "source": source["name"],
            "url": link
        })

    return news
