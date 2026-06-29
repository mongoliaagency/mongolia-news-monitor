import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup

with open('_html/24tsag_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# The "unknown" articles with 58 мин - find their actual structure
# Find one that we know has date 58 мин and title is empty
print("=" * 60)
print("1. 'unknown' type article raw HTML samples")
print("=" * 60)
seen_unknown = 0
for a in soup.select('a[href^="/a/"]'):
    url = a.get('href', '')
    # Check if this is an "unknown" type
    atype = 'unknown'
    for p in a.parents:
        pclass = ' '.join(p.get('class', []))
        for t in ['featured-item','article-item','feature-main','feature-sub','feature-top','swiper','publicist']:
            if t in pclass:
                atype = t
                break
        if atype != 'unknown':
            break
    
    if atype == 'unknown' and seen_unknown < 5:
        # Find the parent container
        for p in a.parents:
            pclass = ' '.join(p.get('class', []))
            if pclass.strip() and p.name not in ('body', 'html', '[document]'):
                print(f"\n--- {p.name}.{pclass[:80]} ---")
                print(str(p)[:700])
                print("...")
                seen_unknown += 1
                break

print("\n\n" + "=" * 60)
print("2. Most recent / most visible article items (re-date only)")
print("=" * 60)
# Focus on items with article-item-date or featured-item__date
items_with_date = soup.select('.article-item')
print(f"article-item count: {len(items_with_date)}")
for i, item in enumerate(items_with_date[:15]):
    link = item.select_one('a.article-item-title')
    date_el = item.select_one('.article-item-date span')
    url = link.get('href', 'N/A') if link else 'N/A'
    date = date_el.get_text(strip=True) if date_el else 'NO_DATE'
    title = link.get_text(strip=True)[:80] if link else 'N/A'
    print(f"  [{i:2d}] {date:25s} {url:12s} {title}")

print(f"\nfeatured-item count: {len(soup.select('.featured-item'))}")

# Get the main containers to understand layout
print("\n\n" + "=" * 60)
print("3. Main page containers")
print("=" * 60)
for tag_name in ['div', 'section']:
    for tag in soup.find_all(tag_name):
        tclass = ' '.join(tag.get('class', []))
        if any(kw in tclass for kw in ['container', 'wrapper', 'main', 'content', 'body', 'page', 'row']):
            if len(tclass) < 100:
                children = len(list(tag.children))
                if children > 1:
                    print(f"  <{tag.name} class='{tclass}'> ({children} children)")

print("\n\n" + "=" * 60)
print("4. All unique date values (article-item-date)")
print("=" * 60)
date_values = set()
for date_el in soup.select('.article-item-date span'):
    date_values.add(date_el.get_text(strip=True))
for date_el in soup.select('.featured-item__date'):
    date_values.add(date_el.get_text(strip=True))
for d in sorted(date_values):
    print(f"  {d}")
