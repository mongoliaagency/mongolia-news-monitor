import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from bs4 import BeautifulSoup

with open('_html/mongolianminingjournal_com.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Find all article items
print("=" * 60)
print("1. home-article-item elements")
print("=" * 60)
items = soup.select('.home-article-item__title')
for i, item in enumerate(items[:10]):
    link = item.find('a') if item.name != 'a' else item
    if link and link.name == 'a':
        print(f"  [{i}] Title: {link.get_text(strip=True)[:80]}")
        print(f"       Link: {link.get('href', 'N/A')}")

# Find parent structure
print("\n" + "=" * 60)
print("2. home-article-item parent structure")
print("=" * 60)
parents = soup.select('.home-article-item__desc')
for i, p in enumerate(parents[:3]):
    parent = p.parent
    if parent:
        print(f"  [{i}] Parent classes: {parent.get('class', [])}")
        print(f"       Parent HTML (first 500 chars):")
        print(f"       {str(parent)[:500]}")
        print()

print("\n" + "=" * 60)
print("3. post-card elements")
print("=" * 60)
cards = soup.select('.post-card')
for i, card in enumerate(cards[:5]):
    title_el = card.select_one('.pages-item__desc, .home-article-item__title, a')
    time_el = card.select_one('.pages-item__time, .sub-feature-item__date')
    link_el = card.select_one('a[href]')
    title = title_el.get_text(strip=True)[:80] if title_el else 'N/A'
    time_text = time_el.get_text(strip=True) if time_el else 'N/A'
    link = link_el.get('href', 'N/A') if link_el else 'N/A'
    print(f"  [{i}] Title: {title}")
    print(f"       Date: {time_text}")
    print(f"       Link: {link}")
    print(f"       Card classes: {card.get('class', [])}")
    print()

print("\n" + "=" * 60)
print("4. pages-item elements (full)")
print("=" * 60)
pages = soup.select('.pages-item')
for i, page in enumerate(pages[:8]):
    title_el = page.select_one('.pages-item__desc, a')
    time_el = page.select_one('.pages-item__time')
    link_el = page.select_one('a[href]')
    img_el = page.select_one('.pages-item__img img, .pages-item__img')
    title = title_el.get_text(strip=True)[:80] if title_el else 'N/A'
    time_text = time_el.get_text(strip=True) if time_el else 'N/A'
    link = link_el.get('href', 'N/A') if link_el else 'N/A'
    img = img_el.get('src', img_el.get('data-src', 'N/A')) if img_el else 'N/A'
    print(f"  [{i}] Title: {title}")
    print(f"       Date: {time_text}")
    print(f"       Link: {link}")
    print(f"       Img: {img[:80] if img else 'N/A'}")
    print(f"       Classes: {page.get('class', [])}")
    print()
