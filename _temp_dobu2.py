import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_html/dobu_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the main content area with articles
# Look for /news/ links and the surrounding HTML structure
for m in re.finditer(r'(.{0,600})<a[^>]*href="(/news/\d+)"[^>]*>(.*?)</a>(.{0,400})', html, re.DOTALL):
    link = m.group(2)
    title = m.group(3).strip()
    before = m.group(1)
    after = m.group(4)
    
    # Find date in the surrounding context
    full_context = before + after
    dates_abs = re.findall(r'(\d{4}-\d{2}-\d{2})', full_context)
    dates_rel = re.findall(r'(\d+\s*(?:цаг|өдөр|мин|хоног|сар|жил|минут|цагийн|өдрийн|хоногийн|сарын|жилийн|минутын)\s*(?:өмнө|урьд)?)', full_context)
    
    print(f'Link: {link}')
    print(f'Title: {title[:80]}')
    print(f'Abs dates: {dates_abs}')
    print(f'Rel dates: {dates_rel}')
    
    # Extract the parent div class
    parent_divs = re.findall(r'<div[^>]*class="([^"]+)"[^>]*>', before[-400:])
    if parent_divs:
        print(f'Parent classes: {parent_divs[-3:]}')
    print('---')
    
    # Limit to first 15
    if len([1]) > 14:
        break

# Now a different approach: find the article grid pattern
# Look for grid with /news/ links
print('\n\n=== GRID SECTIONS ===')
grid_sections = re.findall(r'(<div[^>]*class="[^"]*grid[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>)', html, re.DOTALL)
print(f'Grid sections: {len(grid_sections)}')

# Find sections with multiple /news/ links
news_sections = re.findall(r'((?:.*?/news/\d+.*?){3,})', html)
print(f'News-dense sections: {len(news_sections)}')

# Find the main article list by looking for repeated patterns
# Each article: image + title + date + link
article_pattern = re.findall(r'<a[^>]*href="(/news/\d+)"[^>]*>(?:<img[^>]*>|)([^<]{5,100})</a>', html)
print(f'\nArticle links with text: {len(article_pattern)}')
for link, title in article_pattern[:15]:
    print(f'  {link} -> {title[:70]}')

# Check what comes before/after the link to find date
print('\n\n=== CONTEXT AROUND ARTICLES ===')
for m in re.finditer(r'(.{0,200})<a[^>]*href="(/news/\d+)"[^>]*>(.{0,100})</a>(.{0,200})', html, re.DOTALL):
    before = m.group(1)
    link = m.group(2)
    title_inner = m.group(3)
    after = m.group(4)
    full = before + after
    
    # Look for date patterns near the link
    date_abs = re.findall(r'(\d{4}-\d{2}-\d{2})', full)
    date_rel = re.findall(r'(\d+\s*(?:цаг|өдөр|мин|хоног|сар)\s*(?:өмнө|урьд)?)', full)
    
    # Look for the containing element class
    containers = re.findall(r'class="([^"]+)"', before[-300:])
    
    print(f'  Link: {link}')
    print(f'  Title: {title_inner[:60]}')
    print(f'  Abs: {date_abs}, Rel: {date_rel}')
    if containers:
        print(f'  Classes: {containers[-2:]}')
    print()
    if len([1 for _ in [1]]) > 9:
        break
