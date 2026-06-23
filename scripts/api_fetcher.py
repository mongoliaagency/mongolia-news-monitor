import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime


def fetch_api(source_file):
    with open(source_file, 'r', encoding='utf-8') as f:
        source = json.load(f)

    api_url = source.get('api_url')
    if not api_url:
        raise ValueError('api_url is required for api source_type')

    response = requests.get(api_url, headers={
        'User-Agent': 'Mozilla/5.0'
    }, timeout=30)
    response.raise_for_status()

    data = response.json()
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

        publish_date = item.get('createdDateText') or item.get('createdDate') or ''

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
            'publish_date': publish_date,
            'source': source.get('name'),
            'url': link,
            'summary': summary
        })

    return items
