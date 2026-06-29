import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from bs4 import BeautifulSoup

with open('_html/mongolianminingjournal_com.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Find all pages-item with full children
print("=" * 60)
print("1. Full pages-item HTML structure")
print("=" * 60)
pages = soup.select('.pages-item')
for i, page in enumerate(pages[:5]):
    print(f"\n--- pages-item [{i}] ---")
    print(str(page)[:800])
    print("...")

print("\n\n" + "=" * 60)
print("2. All <a> tags with /a/ pattern")
print("=" * 60)
a_tags = soup.select('a[href^="/a/"]')
for i, a in enumerate(a_tags[:15]):
    print(f"  [{i}] {a.get('href', 'N/A')}")
    print(f"       Text: {a.get_text(strip=True)[:80]}")
    print(f"       Parent classes: {a.parent.get('class', [])[:5] if a.parent else 'N/A'}")
    print()

print("\n" + "=" * 60)
print("3. sub-feature-item elements")
print("=" * 60)
subs = soup.select('.sub-feature-item')
for i, sub in enumerate(subs[:5]):
    link = sub.select_one('a[href]')
    date_el = sub.select_one('.sub-feature-item__date')
    title_el = sub.select_one('.sub-feature-item__name')
    print(f"  [{i}] Title: {title_el.get_text(strip=True)[:80] if title_el else 'N/A'}")
    print(f"       Date: {date_el.get_text(strip=True) if date_el else 'N/A'}")
    print(f"       Link: {link.get('href', 'N/A') if link else 'N/A'}")
    print(f"       HTML: {str(sub)[:400]}")
    print()

print("\n" + "=" * 60)
print("4. All date/time patterns in visible text")
print("=" * 60)
# Find dates in the HTML
dates = re.findall(r'(?:pages-item__time|sub-feature-item__date|article-date|post-date)[^>]*>([^<]+)<', html)
print(f"  pages-item__time / sub-feature-item__date dates: {dates[:20]}")
# Also find any date-like text
all_dates = re.findall(r'\d{4}[-/.]\d{2}[-/.]\d{2}', html)
print(f"  All YYYY-MM-DD dates: {sorted(set(all_dates))[:30]}")
