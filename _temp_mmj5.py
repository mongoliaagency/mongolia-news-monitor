import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from bs4 import BeautifulSoup

with open('_html/mongolianminingjournal_com.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 60)
print("1. Swiper main feature slides (dates)")
print("=" * 60)
slides = soup.select('.swiper.mainFeature .swiper-slide')
for i, slide in enumerate(slides):
    date_el = slide.select_one('.feature-content__date')
    title_el = slide.select_one('.feature-content__name a')
    desc_el = slide.select_one('.main-feature-desc')
    link = title_el.get('href', 'N/A') if title_el else 'N/A'
    date = date_el.get_text(strip=True) if date_el else 'NO_DATE'
    title = title_el.get_text(strip=True)[:80] if title_el else 'N/A'
    print(f"  [{i}] Date: {date}")
    print(f"       Title: {title}")
    print(f"       Link: {link}")
    print()

print("=" * 60)
print("2. home-section-grid full structure (each grid)")
print("=" * 60)
grids = soup.select('.home-section-grid')
for gi, grid in enumerate(grids):
    print(f"\n--- Grid [{gi}] ---")
    # Section name
    sname = grid.select_one('.section-name-home')
    if sname:
        print(f"  Section name: {sname.get_text(strip=True)}")
    
    # Find all article items within this grid
    for tag in grid.select('a[href^="/a/"]'):
        url = tag.get('href', '')
        title = tag.get_text(strip=True)[:80]
        
        # Find date in parent hierarchy
        date = 'NO_DATE'
        for p in tag.parents:
            if p == grid:
                break
            date_el = p.select_one('.pages-item__time, .sub-feature-item__date, [class*="date"]')
            if date_el:
                date = date_el.get_text(strip=True)
                break
        
        # Check if it's a pages-item (the a itself)
        if 'pages-item' in ' '.join(tag.get('class', [])):
            date_el = tag.select_one('.pages-item__time')
            if date_el:
                date = date_el.get_text(strip=True)
        
        print(f"  URL: {url}")
        print(f"  Title: {title}")
        print(f"  Date: {date}")
        print(f"  Tag classes: {' '.join(tag.get('class', []))[:100]}")
        print()

print("=" * 60)
print("3. home-article-item__title parent full HTML")
print("=" * 60)
items = soup.select('.home-article-item__title')
for i, item in enumerate(items[:3]):
    # Find the closest ancestor that might contain a date
    # Go up to home-section-grid
    ancestor = None
    for p in item.parents:
        pclass = ' '.join(p.get('class', []))
        if 'home-section-grid' in pclass or 'uk-card' in pclass:
            ancestor = p
            break
    
    if ancestor:
        print(f"\n--- home-article-item [{i}] ancestor ---")
        print(str(ancestor)[:1000])
        print("...")

print("\n\n" + "=" * 60)
print("4. ALL unique /a/ URLs with dates and types")
print("=" * 60)

# Comprehensive scan
all_articles = []
seen = set()
for a in soup.select('a[href^="/a/"]'):
    url = a.get('href', '')
    if url in seen:
        continue
    seen.add(url)
    
    title = a.get_text(strip=True)[:80]
    
    # Determine type
    article_type = 'unknown'
    date = 'NO_DATE'
    
    # Check if the a tag itself is a card
    aclass = ' '.join(a.get('class', []))
    if 'pages-item' in aclass:
        article_type = 'pages-item'
        date_el = a.select_one('.pages-item__time span')
        if date_el:
            date = date_el.get_text(strip=True)
    elif 'sub-feature-item' in aclass:
        article_type = 'sub-feature-item'
        date_el = a.select_one('.sub-feature-item__date span')
        if date_el:
            date = date_el.get_text(strip=True)
    else:
        # Look at parent
        for p in a.parents:
            pclass = ' '.join(p.get('class', []))
            if 'feature-content__name' in pclass:
                article_type = 'swiper-feature'
                # Find sibling feature-content__date
                fc = p.parent
                if fc:
                    date_el = fc.select_one('.feature-content__date')
                    if date_el:
                        date = date_el.get_text(strip=True)
                break
            elif 'home-article-item__title' in aclass:
                article_type = 'home-article-item'
                break
            elif 'section-box' in pclass:
                article_type = 'section-box'
                break
            elif 'mobile-pad' in pclass:
                article_type = 'home-article-item-list'
                break
    
    all_articles.append((url, title, date, article_type))

print(f"Total unique articles: {len(all_articles)}")
for url, title, date, atype in all_articles:
    print(f"  [{atype:25s}] {date:12s} {url:10s} {title}")
