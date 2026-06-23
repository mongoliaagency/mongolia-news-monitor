import json
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def fetch_parliament(config_path='config/sources/parliament_mn.json', out_path='data/news/parliament_mn.json'):
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    page_url = cfg.get('page_url')
    resp = requests.get(page_url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'lxml')

    items = []
    # listing page may not contain full article markup; collect article links like /nn/<id>/
    import re
    anchors = soup.select('a')
    links = []
    for a in anchors:
        href = a.get('href')
        if not href:
            continue
        m = re.match(r'^/nn/\d+/', href)
        if m:
            links.append(href)

    # unique preserve order
    seen = set()
    uniq_links = []
    for h in links:
        if h not in seen:
            seen.add(h)
            uniq_links.append(h)

    # fetch each article page to extract title and date
    for rel in uniq_links:
        art_url = urljoin(cfg.get('homepage'), rel)
        try:
            r2 = requests.get(art_url, timeout=20)
            r2.raise_for_status()
            s2 = BeautifulSoup(r2.text, 'lxml')
            # title
            title_tag = s2.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else ''
            # date
            date_tag = s2.find('time') or s2.select_one('.entry-meta span')
            pub_date = date_tag.get_text(strip=True) if date_tag else ''
            # summary: first paragraph in article container
            article_container = s2.find('article') or s2.find('div', class_='article') or s2.find('div', id='content')
            summary = ''
            if article_container:
                p = article_container.find('p')
                if p: summary = p.get_text(strip=True)
        except Exception:
            title = ''
            pub_date = ''
            summary = ''

        items.append({
            'title': title,
            'url': art_url,
            'publish_date': pub_date,
            'summary': summary,
            'source': cfg.get('name')
        })

    out = {
        'name': cfg.get('name'),
        'homepage': cfg.get('homepage'),
        'fetched_at': datetime.utcnow().isoformat() + 'Z',
        'items': items
    }

    # ensure output dir exists
    from pathlib import Path
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    return out_path, len(items)


if __name__ == '__main__':
    path, count = fetch_parliament()
    print('wrote', path, 'items', count)
