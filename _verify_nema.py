"""Verify nema.gov.mn HTML structure"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import json
from bs4 import BeautifulSoup

sys.path.insert(0, 'scripts')
from date_utils import parse_date, format_date

with open('_html/nema_gov_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

with open('config/sources/nema_mn.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

print(f"=== Config ===")
print(f"Name: {config['name']}")
print(f"News URL: {config['news_url']}")
print(f"Items: {config['items_selector']}")
print(f"Title: {config['title_selector']}")
print(f"Link: {config['link_selector']}")
print(f"Date: {config['date_selector']}")

items = soup.select(config['items_selector'])
print(f"\n=== Items found: {len(items)} ===")

# Check the element types
article_count = sum(1 for i in items if i.name == 'article')
div_count = sum(1 for i in items if i.name == 'div' and 'posts-detail' in (i.get('class') or []))
print(f"article.post-item: {article_count}")
print(f"div.posts-detail: {div_count}")

seen_urls = set()
success = 0
fail = 0

for i, item in enumerate(items):
    elem_type = item.name
    elem_classes = ' '.join(item.get('class', []))
    
    title_el = item.select_one(config['title_selector'])
    title = title_el.get_text(strip=True) if title_el else "NO TITLE"
    
    link_el = item.select_one(config['link_selector'])
    link = link_el.get('href', '') if link_el else ""
    
    if link in seen_urls:
        print(f"  [{i}] DUPLICATE: {link}")
        continue
    seen_urls.add(link)
    
    date_el = item.select_one(config['date_selector'])
    raw_date = date_el.get_text(strip=True) if date_el else ""
    
    dt = parse_date(raw_date)
    if dt:
        date_str = format_date(dt)
        success += 1
        print(f"  [{i}] OK  date={date_str}  type={elem_type}  title={title[:55]}")
    else:
        fail += 1
        print(f"  [{i}] FAIL raw='{raw_date}'  type={elem_type}  title={title[:55]}")
    
    if i < 4:
        print(f"       link={link}")
        print(f"       raw_date='{raw_date}'")

print(f"\n=== Results ===")
print(f"Unique articles: {len(seen_urls)}")
print(f"Date success: {success}")
print(f"Date fail: {fail}")
pct = 100*success/(success+fail) if success+fail > 0 else 0
print(f"Success rate: {success}/{success+fail} = {pct:.0f}%")
