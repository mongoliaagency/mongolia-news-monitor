import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from bs4 import BeautifulSoup

with open('_html/mongolianminingjournal_com.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 60)
print("1. Page structure overview - main containers")
print("=" * 60)

# Find major structural elements
for tag in soup.select('.header, .uk-container, .home-section-grid, [class*="section"], [class*="feature"], [class*="swiper"]'):
    tag_class = ' '.join(tag.get('class', []))
    if len(tag_class) < 100:
        # Count children
        child_count = len(list(tag.children))
        if child_count > 1 or 'section' in tag_class.lower() or 'feature' in tag_class.lower() or 'swiper' in tag_class.lower():
            tag_id = tag.get('id', '')
            id_str = f' #{tag_id}' if tag_id else ''
            print(f"  <{tag.name} class='{tag_class}'{id_str}> ({child_count} children)")

print("\n\n" + "=" * 60)
print("2. ALL article items (with links and dates)")
print("=" * 60)

# Find all a tags that link to /a/ and extract their full context
all_a = soup.select('a[href^="/a/"]')
seen_urls = set()
for i, a in enumerate(all_a):
    url = a.get('href', '')
    if url in seen_urls:
        continue
    seen_urls.add(url)
    
    # Find date in parent chain
    parent_card = None
    for p in a.parents:
        pclass = ' '.join(p.get('class', [])) if p.name != '[document]' else ''
        if any(c in pclass for c in ['pages-item', 'post-card', 'sub-feature-item', 'section-box', 'feature-content', 'home-article-item', 'mobile-pad', 'pl-20']):
            parent_card = p
            break
    
    # Extract date from parent or sibling
    date = 'NO_DATE'
    if parent_card:
        date_el = parent_card.select_one('.pages-item__time, .sub-feature-item__date, time, [class*="date"], [class*="time"]')
        if date_el:
            date = date_el.get_text(strip=True)
    
    title = a.get_text(strip=True)[:80]
    
    # Determine card type
    card_class = ' '.join(parent_card.get('class', [])) if parent_card else 'N/A'
    
    print(f"  [{i:2d}] URL: {url}")
    print(f"        Title: {title}")
    print(f"        Date: {date}")
    print(f"        Card type: {card_class[:100]}")
    print()

print("\n\n" + "=" * 60)
print("3. Unique card types summary")
print("=" * 60)
card_types = {}
for a in soup.select('a[href^="/a/"]'):
    url = a.get('href', '')
    for p in a.parents:
        pclass = ' '.join(p.get('class', [])) if p.name != '[document]' else ''
        for ct in ['pages-item', 'sub-feature-item', 'section-box', 'feature-content', 'home-article-item']:
            if ct in pclass:
                card_types[ct] = card_types.get(ct, 0) + 1
                break
        else:
            continue
        break

for ct, count in sorted(card_types.items()):
    print(f"  {ct}: {count} articles")
