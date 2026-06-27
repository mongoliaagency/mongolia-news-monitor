import json
import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime
from date_utils import parse_date, format_date, is_today


def _fetch_api_with_retry(api_url, max_retries=3, timeout=45):
    """Fetch API endpoint with retry logic for connection timeouts."""
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, headers={
                'User-Agent': 'Mozilla/5.0'
            }, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = (attempt + 1) * 10
                time.sleep(wait)
            else:
                raise last_error


def fetch_api(source_file):
    with open(source_file, 'r', encoding='utf-8') as f:
        source = json.load(f)

    api_url = source.get('api_url')
    if not api_url:
        raise ValueError('api_url is required for api source_type')

    # Try primary URL first, then fallback URLs
    urls_to_try = [api_url] + source.get('api_fallback_urls', [])
    data = None
    last_error = None
    for url in urls_to_try:
        try:
            data = _fetch_api_with_retry(url, max_retries=2, timeout=30)
            break
        except Exception as e:
            last_error = e

    if data is None:
        raise last_error
    items = []

    raw_list = []
    if isinstance(data, dict):
        raw_list = data.get('data', {}).get('list', [])
    elif isinstance(data, list):
        raw_list = data

    for item in raw_list:
        title = item.get('title', '').strip()
        if not title:
            continue

        url_id = item.get('urlId') or item.get('id')
        if url_id is None:
            continue

        link = urljoin(source.get('homepage', ''), f'/news/{url_id}')

        publish_date_raw = item.get('createdDateText') or item.get('createdDate') or ''
        dt = parse_date(publish_date_raw)
        if not dt or dt.date() != datetime.now().date():
            continue  # only keep today's articles

        summary = item.get('shortContent') or ''
        if not summary:
            content_html = item.get('content') or ''
            try:
                soup = BeautifulSoup(content_html, 'lxml')
            except Exception:
                soup = BeautifulSoup(content_html, 'html.parser')
            summary = soup.get_text(strip=True)[:300]

        items.append({
            'title': title,
            'publish_date': format_date(dt),
            'source': source.get('name'),
            'url': link,
            'summary': summary
        })

    return items
