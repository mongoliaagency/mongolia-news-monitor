#!/usr/bin/env python3
"""Final validation: title extraction for all .post types."""
import sys
import io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open("_html/newmm_mn.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Examine different post types for title extraction
print("=" * 60)
print("TITLE EXTRACTION BY POST TYPE")
print("=" * 60)

# Type 1: hero-post / post-overlay (carousel)
hero = soup.select(".hero-post")
if hero:
    p = hero[0]
    print("\n1. hero-post / post-overlay:")
    print(f"   a[href*='/n/'] -> {p.select_one('a[href*=\"/n/\"]').get_text(strip=True)[:80]}")
    print(f"   .title a -> {p.select_one('.title a').get_text(strip=True)[:80] if p.select_one('.title a') else 'N/A'}")

# Type 2: post-small / post-list
small = soup.select(".post-small")
if small:
    p = small[0]
    print("\n2. post-small / post-list:")
    a = p.select_one("a[href*='/n/']")
    print(f"   a[href*='/n/'] -> '{a.get_text(strip=True)[:80]}'")
    print(f"   .title a -> '{p.select_one('.title a').get_text(strip=True)[:80] if p.select_one('.title a') else 'N/A'}'")

# Type 3: feature-post with post-separator-border
feature = soup.select(".feature-post")
if feature:
    p = feature[0]
    print("\n3. feature-post:")
    a = p.select_one("a[href*='/n/']")
    print(f"   a[href*='/n/'] -> '{a.get_text(strip=True)[:80]}'")
    print(f"   .title a -> '{p.select_one('.title a').get_text(strip=True)[:80] if p.select_one('.title a') else 'N/A'}'")

# Type 4: popular-post-slider (no date)
popular = soup.select(".popular-post")
if popular:
    p = popular[0]
    print("\n4. popular-post (no date):")
    a = p.select_one("a[href*='/n/']")
    print(f"   a[href*='/n/'] -> '{a.get_text(strip=True)[:80]}'")
    print(f"   .title a -> '{p.select_one('.title a').get_text(strip=True)[:80] if p.select_one('.title a') else 'N/A'}'")

# =========================================================
print("\n" + "=" * 60)
print("FULL EXTRACTION WITH PROPER TITLE SELECTORS")
print("=" * 60)

posts = soup.select(".post")
articles = []
seen_urls = set()

for post in posts:
    # Title: try .title a first, then a[href*='/n/']
    title_el = post.select_one(".title a") or post.select_one("a[href*='/n/']")
    if not title_el:
        continue
    
    link = title_el.get("href", "").strip()
    title = title_el.get_text(strip=True)
    
    if not title or not link:
        continue
    
    if link.startswith("/"):
        link = "https://www.newmm.mn" + link
    
    if link in seen_urls:
        continue
    seen_urls.add(link)
    
    # Date
    date_el = post.select_one(".meta-item.date")
    date_text = date_el.get_text(strip=True) if date_el else ""
    
    articles.append((title, link, date_text))

# Add breaking news ticker
ticker_links = soup.select(".breaking-news-ticker a[href*='/n/']")
for a in ticker_links:
    link = a.get("href", "").strip()
    title = a.get_text(strip=True)
    if not title or not link:
        continue
    if link.startswith("/"):
        link = "https://www.newmm.mn" + link
    if link in seen_urls:
        continue
    seen_urls.add(link)
    articles.append((title, link, ""))

print(f"\nTotal: {len(articles)} unique articles")
with_date = sum(1 for _, _, d in articles if d)
without_date = sum(1 for _, _, d in articles if not d)
print(f"With date: {with_date}")
print(f"Without date: {without_date}")

# Show all
for i, (title, link, date_text) in enumerate(articles):
    d = date_text if date_text else "(no date)"
    print(f"\n  [{i+1}] {d} | {title[:80]}")
    print(f"       {link}")

# =========================================================
print("\n" + "=" * 60)
print("DATE FORMAT TEST")
print("=" * 60)
sys.path.insert(0, '.')
from scripts.date_utils import parse_date
for _, _, d in articles:
    if d:
        result = parse_date(d)
        print(f"  '{d}' => {result}")
        break
