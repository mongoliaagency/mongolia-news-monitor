import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from bs4 import BeautifulSoup

with open('_html/24tsag_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f'File size: {len(html)} chars')
soup = BeautifulSoup(html, 'html.parser')

# Find all links
links = set()
for a in soup.select('a[href]'):
    href = a.get('href', '')
    if href.startswith('/') and not any(href.startswith(p) for p in ['/cdn','/wp-','/js','/css','/images','/assets','/img','/static']):
        if len(href) > 2:
            links.add(href)

print(f'\nUnique links ({len(links)}):')
for l in sorted(links)[:40]:
    print(f'  {l}')

# Find article-related classes
print('\n' + '=' * 60)
print('Article-related classes:')
classes = re.findall(r'class="([^"]{0,100})"', html)
article_classes = set()
for c in classes:
    if any(kw in c.lower() for kw in ['post','article','news','item','card','story','grid','list','row','col','thumb','img','cover','feature','slide','swiper']):
        article_classes.add(c[:120])
for c in sorted(article_classes)[:50]:
    print(f'  {c}')

# Find date patterns
print('\n' + '=' * 60)
print('Date patterns:')
dates = re.findall(r'\d{4}[-/.]\d{2}[-/.]\d{2}', html)
print(f'  YYYY-MM-DD ({len(set(dates))} unique): {sorted(set(dates))[:20]}')
rel_dates = re.findall(r'\d+\s*(?:мин|цаг|өд|сар|жил|хоног)', html)
print(f'  Relative ({len(set(rel_dates))} unique): {sorted(set(rel_dates))[:20]}')
