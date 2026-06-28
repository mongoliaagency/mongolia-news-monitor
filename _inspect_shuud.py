# -*- coding: utf-8 -*-
"""SHUUD: Verify uniqueness and test 'Уржигдар' date parsing."""
import sys, io, json
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup
from date_utils import parse_date, format_date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('config/sources/shuud_mn.json', 'r', encoding='utf-8') as f:
    source = json.load(f)

with open('_html/shuud_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

items = soup.select(source["items_selector"])

articles = []
seen_urls = set()
seen_titles = set()

for item in items:
    title_node = item.select_one(source["title_selector"])
    if not title_node:
        continue
    title = title_node.get_text(strip=True)
    link_node = item.select_one(source.get("link_selector", source["title_selector"]))
    link = link_node.get("href", "") if link_node else ""
    if not title or len(title) < 5 or not link:
        continue
    if link in seen_urls:
        continue
    seen_urls.add(link)
    
    publish_date_str = None
    date_node = item.select_one(source["date_selector"])
    if date_node:
        raw = date_node.get(source["date_attr"], '') if source.get("date_attr") else date_node.get_text(strip=True)
        dt = parse_date(raw)
        if dt:
            publish_date_str = format_date(dt)
    
    if not publish_date_str and source.get("date_alt_selector"):
        alt_node = item.select_one(source["date_alt_selector"])
        if alt_node:
            raw = alt_node.get_text(strip=True)
            dt = parse_date(raw)
            if dt:
                publish_date_str = format_date(dt)
    
    if not publish_date_str:
        continue
    
    articles.append({"title": title, "date": publish_date_str})

print(f"Total unique articles: {len(articles)}")

# Check how many are within 7 days
from date_utils import is_within_days
recent = sum(1 for a in articles if is_within_days(a['date'], 7))
print(f"Within 7 days: {recent}")

# Verify Уржигдар parsing
print(f"\n=== Уржигдар test ===")
from datetime import datetime
test = parse_date("Уржигдар 17 цаг 36 мин")
print(f"  'Уржигдар 17 цаг 36 мин' -> {test}")
test2 = parse_date("Өчигдөр 10 цаг 15 мин")
print(f"  'Өчигдөр 10 цаг 15 мин' -> {test2}")
