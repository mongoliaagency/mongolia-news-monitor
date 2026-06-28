import json
import re
import time
from datetime import datetime, timedelta

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


def _parse_articles(soup, source, override_date=None):
    """Extract articles from a parsed BeautifulSoup object.
    If override_date is provided, use it as the publish_date for all articles.
    Supports detail_page_date: when True, fetches each article's detail page
    to extract the publish date via detail_date_pattern regex.
    Supports group_date_selector: when items are grouped under date headers,
    each item inherits the date from its nearest preceding group header.
    """
    items_selector = source.get("items_selector")
    title_selector = source.get("title_selector")
    link_selector = source.get("link_selector", title_selector)
    title_attr = source.get("title_attr")
    date_selector = source.get("date_selector")
    date_attr = source.get("date_attr")
    exclude_urls = source.get("exclude_urls", [])
    detail_date = source.get("detail_date", False)
    detail_date_pattern = source.get("detail_date_pattern")
    requires_browser = source.get("requires_browser", False)
    group_date_selector = source.get("group_date_selector")
    group_date_pattern = source.get("group_date_pattern")

    # Build a group-date map when group_date_selector is configured.
    # Maps each item element to the date of its nearest preceding group-date header.
    group_date_map = {}
    if group_date_selector and items_selector:
        group_headers = soup.select(group_date_selector)
        item_elements = soup.select(items_selector)
        if group_headers and item_elements:
            # Gather all relevant elements (headers + items) in document order
            all_elements = [(el, 'group') for el in group_headers] + \
                           [(el, 'item') for el in item_elements]
            all_elements.sort(key=lambda x: x[0].sourceline if hasattr(x[0], 'sourceline') and x[0].sourceline else 0)
            current_date = None
            for el, el_type in all_elements:
                if el_type == 'group':
                    raw_date = el.get_text(strip=True)
                    if group_date_pattern:
                        m = re.search(group_date_pattern, raw_date)
                        if m:
                            raw_date = m.group(1)
                    dt = parse_date(raw_date)
                    if dt:
                        current_date = format_date(dt)
                elif el_type == 'item':
                    if current_date:
                        group_date_map[el] = current_date

    if items_selector:
        items = soup.select(items_selector)
    elif title_selector:
        items = soup.select(title_selector)
    else:
        items = []

    articles = []
    pending_for_detail = []  # articles that need detail page date fetch

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

        # Date extraction
        publish_date_str = None

        if override_date:
            # When using date_url_template, the date is known from the URL
            publish_date_str = override_date
        elif date_selector:
            date_node = item.select_one(date_selector)
            if date_node:
                if date_attr:
                    raw_date = date_node.get(date_attr, '')
                    if '%' in raw_date:
                        from urllib.parse import unquote
                        raw_date = unquote(raw_date)
                else:
                    raw_date = date_node.get_text(strip=True)
                dt = parse_date(raw_date)
                if dt:
                    publish_date_str = format_date(dt)
        elif source.get("date_from_item_text", False):
            dt = parse_date(item.get_text(strip=True))
            if dt:
                publish_date_str = format_date(dt)

        # Group-date fallback: use date from nearest preceding group header
        if not publish_date_str and not override_date and group_date_selector:
            mapped_date = group_date_map.get(item)
            if mapped_date:
                publish_date_str = mapped_date

        # Fallback: try alt date selector when primary date_selector didn't yield a date
        if not publish_date_str and not override_date:
            date_alt_selector = source.get("date_alt_selector")
            if date_alt_selector:
                date_alt_node = item.select_one(date_alt_selector)
                if date_alt_node:
                    raw_date_alt = date_alt_node.get_text(strip=True)
                    dt = parse_date(raw_date_alt)
                    if dt:
                        publish_date_str = format_date(dt)

        # Fallback: extract date from item's full text when date_selector didn't yield a date
        if not publish_date_str and not override_date and source.get("date_from_item_text") and date_selector:
            dt = parse_date(item.get_text(strip=True))
            if dt:
                publish_date_str = format_date(dt)

        article_entry = {
            "title": title,
            "publish_date": publish_date_str,
            "source": source["name"],
            "url": link,
            "category": source.get("category", "党政机关"),
        }

        if not publish_date_str and detail_date and detail_date_pattern:
            pending_for_detail.append(article_entry)
        elif publish_date_str:
            articles.append(article_entry)
        # else: skip articles without date (and without detail_date config)

    # Fetch detail pages for articles that need date extraction
    if pending_for_detail:
        for entry in pending_for_detail:
            try:
                detail_html = _fetch_with_retry(entry["url"], requires_browser=requires_browser, timeout=30)
                match = re.search(detail_date_pattern, detail_html)
                if match:
                    raw_date = match.group(1)
                    dt = parse_date(raw_date)
                    if dt:
                        entry["publish_date"] = format_date(dt)
                        articles.append(entry)
            except Exception:
                pass  # Skip this article if detail page fetch fails

    # Deduplicate by URL when configured (e.g. same article appears in multiple layouts)
    if source.get("deduplicate_urls"):
        seen = set()
        deduped = []
        for entry in articles:
            if entry["url"] not in seen:
                seen.add(entry["url"])
                deduped.append(entry)
        return deduped

    return articles


def _fetch_and_parse(url, source, requires_browser, override_date=None):
    """Fetch a URL and parse articles from it. Optionally override the publish date."""
    try:
        html_content = _fetch_with_retry(url, requires_browser=requires_browser)
    except Exception:
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

    return _parse_articles(soup, source, override_date=override_date)


def fetch_html(source_file):

    with open(
        source_file,
        "r",
        encoding="utf-8"
    ) as f:

        source = json.load(f)

    requires_browser = source.get("requires_browser", False)

    date_url_template = source.get("date_url_template")

    if date_url_template:
        # Fetch per-day archive pages for the last 7 days
        all_news = []
        today = datetime.now().date()
        for days_ago in range(7):
            d = today - timedelta(days=days_ago)
            url = date_url_template.format(
                year=d.year,
                month=f"{d.month:02d}",
                day=f"{d.day:02d}"
            )
            override_date = format_date(datetime(d.year, d.month, d.day))
            try:
                news = _fetch_and_parse(url, source, requires_browser,
                                        override_date=override_date)
                all_news.extend(news)
            except Exception as e:
                # Log but continue with other days
                print(f"WARN: {source.get('name')} date={d} — {e}")
        return all_news
    else:
        url = source["news_url"]
        news = _fetch_and_parse(url, source, requires_browser)

        # Filter: only articles from the last 7 days
        return [item for item in news if is_within_days(item["publish_date"], days=7)]
