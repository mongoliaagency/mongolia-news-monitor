# -*- coding: utf-8 -*-
"""Comprehensive test for ISEE news source."""
import sys, io, json
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup
from date_utils import parse_date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('config/sources/isee_mn.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

with open('_html/isee_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

items = soup.select(config['items_selector'])
print(f"Items found: {len(items)}")

success = 0
fail = 0
fail_details = []

for i, item in enumerate(items):
    title_el = item.select_one(config['title_selector'])
    date_el = item.select_one(config['date_selector'])
    
    title = title_el.get_text(strip=True) if title_el else None
    raw_date = date_el.get_text(strip=True) if date_el else None
    
    if not title:
        fail += 1
        fail_details.append(f"Item {i}: no title")
        continue
    
    if not raw_date:
        fail += 1
        fail_details.append(f"Item {i} '{title[:50]}': no date")
        continue
    
    parsed = parse_date(raw_date)
    if parsed:
        success += 1
        # print(f"  OK: '{title[:60]}' | {raw_date} -> {parsed}")
    else:
        fail += 1
        fail_details.append(f"Item {i} '{title[:50]}': date '{raw_date}' failed to parse")

print(f"\nResults: {success} success, {fail} fail")
if fail_details:
    print("Failures:")
    for d in fail_details:
        print(f"  {d}")

# Show a few samples
print("\n=== Sample results ===")
for i, item in enumerate(items[:5]):
    title_el = item.select_one(config['title_selector'])
    date_el = item.select_one(config['date_selector'])
    title = title_el.get_text(strip=True) if title_el else 'N/A'
    raw_date = date_el.get_text(strip=True) if date_el else 'N/A'
    parsed = parse_date(raw_date)
    print(f"  [{title[:60]}] | {raw_date} -> {parsed}")
