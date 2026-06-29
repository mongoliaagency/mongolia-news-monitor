import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

from bs4 import BeautifulSoup

with open('_html/chig_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

result = {}
result['size'] = len(html)
result['title'] = soup.title.string.strip() if soup.title else 'N/A'

# Meta
metas = []
for meta in soup.find_all('meta'):
    name = meta.get('name', '')
    content = meta.get('content', '')
    metas.append(f"{name}={content[:100]}")
result['metas'] = metas

# Scripts
scripts = [s.get('src', '')[:120] for s in soup.find_all('script', src=True)]
result['scripts'] = scripts

# CSS
css = [c.get('href', '')[:120] for c in soup.find_all('link', rel='stylesheet')]
result['css'] = css

# All unique internal href
import re
links = sorted(set(re.findall(r'href="(/[^"]+)"', html)))
interesting = [l for l in links if not any(l.startswith(p) for p in ['/cdn', '/wp-', '/js/', '/css/', '/images/', '/assets/', '/img/', '/static/', '/themes/', '/uploads/', '/fonts/']) and len(l) > 2]
result['interesting_links'] = interesting[:60]

# Find article containers
body = soup.find('body')
all_classes = set()
for tag in body.find_all(True):
    if tag.get('class'):
        for c in tag.get('class'):
            all_classes.add(c)

article_related = sorted([c for c in all_classes if any(k in c.lower() for k in ['article', 'post', 'news', 'item', 'card', 'feature', 'slide', 'story', 'headline', 'list'])])
result['article_classes'] = article_related[:60]

# All unique CSS classes
result['all_classes'] = sorted(all_classes)[:80]

print(json.dumps(result, ensure_ascii=False, indent=2))
