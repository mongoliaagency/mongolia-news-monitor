import json
import feedparser
import requests
from pathlib import Path


def _is_cloudflare_challenge(content, status_code=None):
    if not content:
        return True

    if status_code in {403, 429, 503, 520, 521, 522, 523, 524}:
        return True

    lower = content[:2000].lower()
    challenge_keywords = [
        b"just a moment",
        b"cf-chl-bypass",
        b"cf-browser-verification",
        b"cloudflare",
        b"attention required",
        b"please enable javascript",
        b"captcha",
    ]
    return any(keyword in lower for keyword in challenge_keywords)


def _fetch_with_cloudscraper(url, headers=None, timeout=30):
    try:
        import cloudscraper
        scraper = cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "mobile": False,
            }
        )
        if headers:
            scraper.headers.update(headers)
        return scraper.get(url, timeout=timeout)
    except Exception:
        return None


def _fetch_with_requests(url, headers=None, timeout=30):
    try:
        return requests.get(url, headers=headers, timeout=timeout)
    except Exception:
        return None


def _fetch_with_playwright(url, timeout=60000):
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return None

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=[
                '--disable-gpu',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ])
            page = browser.new_page()
            page.set_extra_http_headers({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            })
            page.goto(url, wait_until="load", timeout=timeout)
            page.wait_for_timeout(2000)
            content = page.content()
            browser.close()
            return content.encode("utf-8")
    except Exception:
        return None


def fetch_rss(source_file):
    with open(source_file, "r", encoding="utf-8") as f:
        source = json.load(f)

    rss_url = source["rss_url"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    content = None
    resp = _fetch_with_cloudscraper(rss_url, headers=headers, timeout=30)
    if resp is not None and resp.status_code == 200 and not _is_cloudflare_challenge(resp.content, resp.status_code):
        content = resp.content
    elif resp is not None and resp.content and not _is_cloudflare_challenge(resp.content, resp.status_code):
        content = resp.content

    if content is None:
        resp = _fetch_with_requests(rss_url, headers=headers, timeout=30)
        if resp is not None and resp.status_code == 200 and not _is_cloudflare_challenge(resp.content, resp.status_code):
            content = resp.content
        elif resp is not None and resp.content and not _is_cloudflare_challenge(resp.content, resp.status_code):
            content = resp.content

    if content is None or _is_cloudflare_challenge(content, getattr(resp, 'status_code', None)):
        playwright_content = _fetch_with_playwright(rss_url, timeout=60000)
        if playwright_content:
            content = playwright_content

    if content is None:
        print(f"  {source['name']}: All fetch methods returned None")
        return []

    feed = feedparser.parse(content)

    if feed.bozo:
        print(f"  {source['name']}: XML parse warning — {feed.bozo_exception}")

    if len(feed.entries) == 0:
        # Diagnostic: log content preview to help debug
        preview = (content[:500] if isinstance(content, bytes) else str(content)[:500])
        preview = preview.replace('\n', ' ').replace('\r', '')
        print(f"  {source['name']}: 0 entries in feed. Content preview: {preview}")

    news = []
    for entry in feed.entries:
        item = {
            "title": entry.get("title", ""),
            "publish_date": entry.get("published", ""),
            "source": source["name"],
            "url": entry.get("link", ""),
        }
        news.append(item)

    return news



