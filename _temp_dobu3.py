import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_html/dobu_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the main article blocks - look for swiper-slide articles
print("=== SWIPER ARTICLES ===")
swiper_slides = re.findall(r'<div[^>]*class="[^"]*swiper-slide[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*</div>', html, re.DOTALL)
print(f'Swiper slides: {len(swiper_slides)}')
for i, slide in enumerate(swiper_slides[:5]):
    links = re.findall(r'href="(/news/\d+)"', slide)
    titles = re.findall(r'alt="([^"]+)"', slide)
    rel_dates = re.findall(r'(\d+\s*(?:цаг|өдөр|мин|хоног|сар)\s*(?:өмнө|урьд)?)', slide)
    print(f'  Slide {i}: link={links}, title={titles[0][:50] if titles else "N/A"}, dates={rel_dates}')

# Find the main news grid (the large one with multiple /news/ links)
print("\n=== MAIN NEWS GRID ===")
# Look for sections with multiple /news/ links in a grid
# Find the "Онцлох мэдээ" or similar section header
for kw in ['Онцлох', 'Шинэ', 'Мэдээ', 'Сүүлийн', 'Бусад', 'Дэлгэрэнгүй']:
    idx = html.find(kw)
    if idx > 0:
        context = html[max(0,idx-100):idx+100]
        print(f"  '{kw}' found at {idx}: ...{context}...")

# Look for all <a> tags with /news/ links and extract their full parent context
print("\n=== ALL /news/ ARTICLES WITH CONTEXT ===")
seen = set()
for m in re.finditer(r'<a[^>]*href="(/news/\d+)"[^>]*>(.*?)</a>', html, re.DOTALL):
    link = m.group(1)
    if link in seen:
        continue
    seen.add(link)
    
    inner = m.group(2)
    # Extract title from alt or inner text
    title = ''
    alt_match = re.search(r'alt="([^"]+)"', inner)
    if alt_match:
        title = alt_match.group(1)
    else:
        title = re.sub(r'<[^>]+>', '', inner).strip()[:60]
    
    # Look at surrounding context (before + after)
    ctx_start = max(0, m.start() - 500)
    ctx_end = min(len(html), m.end() + 300)
    ctx = html[ctx_start:ctx_end]
    
    # Find dates in context
    abs_dates = re.findall(r'(\d{4}-\d{2}-\d{2})', ctx)
    rel_dates = re.findall(r'(\d+\s*(?:цаг|өдөр|мин|хоног|сар)\s*(?:өмнө|урьд)?)', ctx)
    
    # Find the parent container classes (the div wrapping the article)
    # Look backwards for opening div tags
    parent_classes = re.findall(r'class="([^"]+)"', ctx[:400])
    
    all_dates = abs_dates + rel_dates
    if title:
        print(f'  {link}')
        print(f'    Title: {title[:70]}')
        print(f'    Dates: {all_dates}')
        if parent_classes:
            # Show the most specific class (likely the article wrapper)
            for pc in parent_classes[-3:]:
                if any(kw in pc for kw in ['flex','grid','col-span','gap','justify','item']):
                    print(f'    Class: {pc[:80]}')
        print()

# Now find the date elements specifically
print("\n=== DATE SPAN ELEMENTS ===")
date_spans = re.findall(r'<span[^>]*>(\d+\s*(?:цаг|өдөр|мин|хоног|сар)\s*(?:өмнө|урьд)?)</span>', html)
print(f'Date spans: {len(date_spans)}')
for d in list(set(date_spans))[:15]:
    print(f'  {d}')

# Also find date in div
date_divs = re.findall(r'<div[^>]*>(\d+\s*(?:цаг|өдөр|мин|хоног|сар)\s*(?:өмнө|урьд)?)</div>', html)
print(f'Date divs: {len(date_divs)}')
for d in list(set(date_divs))[:15]:
    print(f'  {d}')

# Find time elements
time_els = re.findall(r'<time[^>]*>([^<]+)</time>', html)
print(f'Time elements: {len(time_els)}')
for t in time_els[:10]:
    print(f'  {t}')

# Look for published/date related class names  
date_class_spans = re.findall(r'<(span|div|time|p)[^>]*class="([^"]*)"[^>]*>(.*?)</\1>', html, re.DOTALL)
for tag, cls, content in date_class_spans:
    if any(kw in cls.lower() for kw in ['date','time','published','created','ago']):
        print(f'  <{tag} class="{cls[:60]}"> {content[:60]}')
