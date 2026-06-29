import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

with open('_html/mongolianminingjournal_com.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f'File size: {len(html)} chars')

# Title
title = re.findall(r'<title>([^<]+)</title>', html)
print(f'\nTitle: {title}')

# Find all unique links
links = re.findall(r'href="(/[^"]+)"', html)
unique_links = set()
for l in links:
    if not any(l.startswith(p) for p in ['/cdn', '/wp-', '/js', '/css', '/images', '/assets']):
        if len(l) > 2:
            unique_links.add(l)

print(f'\nUnique links ({len(unique_links)}):')
for l in sorted(unique_links)[:40]:
    print(f'  {l}')

# Look for article-related classes
article_classes = re.findall(r'class="([^"]{0,80}(?:post|article|news|item|card|story|grid|list|row|col|thumb|img|cover)[^"]{0,80})"', html, re.IGNORECASE)
print(f'\nArticle-related classes ({len(set(article_classes))} unique):')
for c in sorted(set(article_classes))[:40]:
    print(f'  {c[:100]}')
