import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup

with open('_html/24tsag_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 60)
print("1. article-item raw HTML (first 5)")
print("=" * 60)
items = soup.select('.article-item')
for i, item in enumerate(items[:5]):
    print(f"\n--- article-item [{i}] ---")
    print(str(item)[:600])
    print("...")

print("\n\n" + "=" * 60)
print("2. featured-item raw HTML (first 3)")
print("=" * 60)
items = soup.select('.featured-item')
for i, item in enumerate(items[:3]):
    print(f"\n--- featured-item [{i}] ---")
    print(str(item)[:600])
    print("...")

print("\n\n" + "=" * 60)
print("3. Swiper slide raw HTML (first 2)")
print("=" * 60)
slides = soup.select('.swiper-slide')
for i, slide in enumerate(slides[:2]):
    print(f"\n--- swiper-slide [{i}] ---")
    print(str(slide)[:800])
    print("...")

print("\n\n" + "=" * 60)
print("4. ALL /a/ links with date context")
print("=" * 60)
seen = set()
for a in soup.select('a[href^="/a/"]'):
    url = a.get('href', '')
    if url in seen:
        continue
    seen.add(url)
    
    # Check parent hierarchy for date
    date = 'NO_DATE'
    for p in a.parents:
        pclass = ' '.join(p.get('class', []))
        # Look for date element in siblings or children
        date_el = p.select_one('.article-item-date, .featured-item__date, [class*="date"]')
        if date_el:
            date = date_el.get_text(strip=True)
            break
        # Also check if parent itself is an article-item with date
        if 'article-item' in pclass:
            date_el = p.select_one('.article-item-date')
            if date_el:
                date = date_el.get_text(strip=True)
            break
    
    title = a.get_text(strip=True)[:80] if a.get_text(strip=True) else '(empty)'
    
    # Determine type
    atype = 'unknown'
    for p in a.parents:
        pclass = ' '.join(p.get('class', []))
        if 'featured-item' in pclass: atype = 'featured-item'; break
        if 'article-item' in pclass: atype = 'article-item'; break
        if 'feature-main' in pclass: atype = 'feature-main'; break
        if 'feature-sub' in pclass: atype = 'feature-sub'; break
        if 'feature-top' in pclass: atype = 'feature-top'; break
        if 'swiper' in pclass: atype = 'swiper'; break
        if 'publicist' in pclass: atype = 'publicist'; break
    
    print(f"  [{atype:15s}] {date:25s} {url:12s} {title}")

print(f"\nTotal unique articles: {len(seen)}")
