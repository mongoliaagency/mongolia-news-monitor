# -*- coding: utf-8 -*-
"""Final comprehensive test for IMEDEE."""
import sys, io, json
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup
from date_utils import parse_date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('_html/imedee_com.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Use article.post as items (the actual article posts, 27 of them)
# But .type-post includes some non-article wrappers
# Let's check: which selector gives best results?

# Test: article.post as items, h3 a as title, .mh-meta-date as date
items = soup.select('article.post')
print(f"article.post: {len(items)}")

success = 0
fail = 0
fail_details = []
seen_urls = set()

for i, item in enumerate(items):
    title_el = item.select_one('h3 a')
    date_el = item.select_one('.mh-meta-date')
    
    title = title_el.get_text(strip=True) if title_el else None
    href = title_el.get('href', '') if title_el else ''
    raw_date = date_el.get_text(strip=True) if date_el else None
    
    if not title:
        fail += 1
        fail_details.append(f"Item {i}: no title")
        continue
    
    if href in seen_urls:
        continue
    seen_urls.add(href)
    
    if not raw_date:
        fail += 1
        fail_details.append(f"Item {i} '{title[:50]}': no date")
        continue
    
    parsed = parse_date(raw_date)
    if parsed:
        success += 1
    else:
        fail += 1
        fail_details.append(f"Item {i} '{title[:50]}': date '{raw_date}' failed")

print(f"Unique articles: {len(seen_urls)}")
print(f"Results: {success} success, {fail} fail")
if fail_details:
    print("Failures:")
    for d in fail_details:
        print(f"  {d}")

# Also test with .type-post (43 items)
print(f"\n=== Also test .type-post ===")
items2 = soup.select('.type-post')
print(f".type-post: {len(items2)}")
seen2 = set()
s2, f2 = 0, 0
for i, item in enumerate(items2):
    title_el = item.select_one('h3 a')
    date_el = item.select_one('.mh-meta-date')
    title = title_el.get_text(strip=True) if title_el else None
    href = title_el.get('href', '') if title_el else ''
    raw_date = date_el.get_text(strip=True) if date_el else None
    if not title or not raw_date:
        continue
    if href in seen2:
        continue
    seen2.add(href)
    if parse_date(raw_date):
        s2 += 1
    else:
        f2 += 1
print(f".type-post unique: {len(seen2)}, success={s2}, fail={f2}")

# Sample
print("\n=== Sample results (article.post) ===")
for i, item in enumerate(items[:5]):
    title_el = item.select_one('h3 a')
    date_el = item.select_one('.mh-meta-date')
    title = title_el.get_text(strip=True) if title_el else 'N/A'
    raw_date = date_el.get_text(strip=True) if date_el else 'N/A'
    parsed = parse_date(raw_date)
    print(f"  [{title[:70]}] | {raw_date} -> {parsed}")
