import sys
sys.stdout.reconfigure(encoding='utf-8')
import json, re
from bs4 import BeautifulSoup

with open('_html/newspress_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

result = {}
result['size'] = len(html)
result['title'] = soup.title.string.strip() if soup.title else 'N/A'

# Meta
metas = []
for meta in soup.find_all('meta'):
    name = meta.get('name', meta.get('property', ''))
    content = meta.get('content', '')
    if content:
        metas.append(f"{name}={content[:120]}")
result['metas'] = metas[:20]

# Scripts
scripts = [s.get('src', '')[:120] for s in soup.find_all('script', src=True) if s.get('src')]
result['scripts'] = scripts[:20]

# CSS
css = [c.get('href', '')[:120] for c in soup.find_all('link', rel='stylesheet') if c.get('href')]
result['css'] = css[:20]

# All unique hrefs
hrefs = sorted(set(re.findall(r'href="([^"]+)"', html) + re.findall(r"href='([^']+)'", html)))
# Filter interesting ones
interesting = [h for h in hrefs if h.startswith('/') and len(h) > 2 and not any(h.startswith(p) for p in ['/cdn','/wp-','/js/','/css/','/images/','/assets/','/img/','/static/','/themes/','/uploads/','/fonts/','/lib/','/dist/'])]
result['interesting_links'] = interesting[:60]

# Also full URL interesting ones
full_interesting = [h for h in hrefs if h.startswith('https://newspress.mn/') and len(h) > 25]
result['full_links'] = full_interesting[:60]

# All CSS classes
all_classes = set()
for tag in soup.find_all(True):
    if tag.get('class'):
        for c in tag.get('class'):
            all_classes.add(c)

# Article-related classes
article_related = sorted([c for c in all_classes if any(k in c.lower() for k in ['article', 'post', 'news', 'item', 'card', 'feature', 'slide', 'story', 'headline', 'list', 'content', 'title', 'entry', 'grid', 'row'])])
result['article_classes'] = article_related[:80]

print(json.dumps(result, ensure_ascii=False, indent=2))
