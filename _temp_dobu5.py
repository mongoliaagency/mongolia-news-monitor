import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_html/dobu_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all article blocks with their full structure
# Pattern: each article is in a grid row with:
# col-span-3 (image) + col-span-4 (title + date + author)
# OR a standalone card with image + title + date

# Let me find all article blocks by looking for the complete pattern
# Type 1: grid-cols-7 articles (side list with small thumbnails)
type1_articles = re.findall(
    r'<div class="text-black md:text-white grid grid-cols-7 gap-4 text-sm">'
    r'\s*<a class="col-span-3"[^>]*href="(/news/\d+)"[^>]*>.*?</a>'
    r'\s*<div class="col-span-4 flex flex-col gap-2 justify-between">'
    r'\s*<p class="[^"]*"><a[^>]*href="(/news/\d+)"[^>]*>(.*?)</a></p>'
    r'\s*<div class="undefined flex justify-between gap-4 text-xs">'
    r'\s*<p>(.*?)</p>'
    r'\s*<p class="text-\[#35CBF5\]">(.*?)</p>'
    r'\s*</div>',
    html, re.DOTALL
)
print(f"Type 1 (grid-cols-7 list) articles: {len(type1_articles)}")
for link1, link2, title, date, author in type1_articles[:5]:
    print(f'  {link1} -> {title[:60]} | Date: {date} | Author: {author}')

# Type 2: large cards (hero/first article)
# Type 3: swiper carousel cards
# Type 4: 3-column grid cards

# Let me find ALL article patterns comprehensively
print("\n=== FINDING ALL ARTICLE PATTERNS ===")

# Find sections with multiple /news/ links
# The main structure appears to be:
# 1. Hero section (1 big article)
# 2. Swiper carousel (3 articles)  
# 3. List section with thumbnails (grid-cols-7)
# 4. Bottom grid with 3-column layout

# Find hero section
hero_links = re.findall(r'absolute inset-0 text-white[^>]*>.*?href="(/news/\d+)".*?>(.*?)</a>.*?<div[^>]*flex justify-between[^>]*>\s*<p>([^<]+)</p>', html, re.DOTALL)
print(f"Hero articles: {len(hero_links)}")
for link, title, date in hero_links[:3]:
    print(f'  {link} -> {title[:60]} | {date}')

# Find all date+author patterns near /news/ links
print("\n=== DATE+ARTICLE PAIRS ===")
for m in re.finditer(r'href="(/news/\d+)"[^>]*>(.*?)</a>.*?<p>([^<]+)</p>\s*<p[^>]*>([^<]+)</p>', html, re.DOTALL):
    link = m.group(1)
    title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    date = m.group(3).strip()
    author = m.group(4).strip()
    if any(kw in date for kw in ['цаг','өдөр','мин','хоног','сар','өмнө']):
        print(f'  {link} -> {title[:50]} | {date} | {author}')

# Find all article containers with their class names
print("\n=== ARTICLE CONTAINER CLASSES ===")
# Look for patterns: class + /news/ link
container_patterns = re.findall(r'class="([^"]+)"[^>]*>.*?href="(/news/\d+)"', html)
for cls, link in container_patterns[:20]:
    if any(kw in cls for kw in ['col-span','grid','flex','card','item']):
        print(f'  {cls[:80]} -> {link}')

# Now let me just print the raw HTML structure (first 8000 chars after body)
body_start = html.find('<body')
if body_start > 0:
    main = html[body_start:body_start+10000]
    print("\n\n=== RAW HTML STRUCTURE (body first 10000) ===")
    # Print only structural elements
    tags = re.findall(r'<(div|section|main|article|header|nav|a)[^>]*class="([^"]*)"[^>]*>', main)
    for tag, cls in tags:
        print(f'  <{tag} class="{cls[:100]}">')

# Find section-like structures
sections = re.findall(r'<(div|section)[^>]*class="([^"]*)"[^>]*>', html)
print(f"\n\n=== ALL SECTION-LIKE DIVS ===")
for tag, cls in sections:
    if any(kw in cls for kw in ['container','section','wrapper','main','content','grid','flex','row','layout']):
        print(f'  <{tag} class="{cls[:100]}">')
