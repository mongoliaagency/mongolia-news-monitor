import json
import feedparser
import requests
from pathlib import Path


def fetch_rss(source_file):

    with open(source_file, "r", encoding="utf-8") as f:
        source = json.load(f)

    rss_url = source["rss_url"]
    # Try to fetch the feed with cloudscraper to bypass Cloudflare; fall back to requests
    content = None
    resp = None
    try:
        import cloudscraper

        scraper = cloudscraper.create_scraper()
        resp = scraper.get(rss_url, timeout=15)
        # do not raise here; capture whatever the server returned
        if resp is not None and getattr(resp, 'status_code', None) == 200:
            content = resp.content
        else:
            content = getattr(resp, 'content', None)
    except Exception:
        # fallback: use requests with a browser-like User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        }
        try:
            resp = requests.get(rss_url, headers=headers, timeout=15)
            if resp is not None and resp.status_code == 200:
                content = resp.content
            else:
                content = getattr(resp, 'content', None)
        except Exception:
            resp = None
            content = None

    # If the response looks like a Cloudflare challenge page, try rendering with Playwright (if installed)
    try_playwright = False
    if content is None:
        try_playwright = True
    else:
        lower = content[:2000].lower()
        if b"just a moment" in lower or b"cf-chl-bypass" in lower or b"cf-browser-verification" in lower:
            try_playwright = True

    if try_playwright:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(rss_url, wait_until="networkidle", timeout=30000)
                html = page.content()
                content = html.encode("utf-8")
                browser.close()
        except Exception:
            # if Playwright isn't available or fails, continue with whatever content we have
            pass

    feed = feedparser.parse(content)

    news = []

    for entry in feed.entries:

        item = {
            "title": entry.get("title", ""),
            "publish_date": entry.get("published", ""),
            "source": source["name"],
            "url": entry.get("link", "")
        }

        news.append(item)

    return news



