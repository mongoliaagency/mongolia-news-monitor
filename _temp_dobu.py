import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_html/dobu_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f'Size: {len(html)} chars')

# Title
titles = re.findall(r'<title>([^<]+)</title>', html)
print(f'Title: {titles}')

# Unique links
links = re.findall(r'href="(/[^"]+)"', html)
urls = set()
for l in links:
    skip = any(l.startswith(p) for p in ['/cdn','/_next','/js','/css','/images','/wp-','/assets','/uploads','/themes','/lib','/media','/static','/fonts'])
    if not skip and len(l) > 2:
        urls.add(l)
print(f'Unique links ({len(urls)}):')
for u in sorted(urls)[:30]:
    print(f'  {u}')

# Date patterns
dates = re.findall(r'(\d{4}[-/.]\d{2}[-/.]\d{2})', html)
print(f'\nDate patterns ({len(dates)}):')
for d in list(set(dates))[:20]:
    print(f'  {d}')

# Relative dates
rel = re.findall(r'(\d+\s*(?:цаг|өдөр|мин|хоног|сар|жил|минут|цагийн|өдрийн|хоногийн|сарын|жилийн|минутын)\s*(?:өмнө|урьд)?)', html)
print(f'\nRelative dates ({len(rel)}):')
for r in list(set(rel))[:20]:
    print(f'  {r}')

# Class patterns for articles
classes = re.findall(r'class="([^"]{3,80})"', html)
article_classes = [c for c in classes if any(kw in c.lower() for kw in ['post','article','news','item','card','grid','list','entry','story','col-'])]
from collections import Counter
cls_counts = Counter(article_classes)
print(f'\nArticle-related classes (top 30):')
for c, n in cls_counts.most_common(30):
    print(f'  [{n:3d}] {c}')
