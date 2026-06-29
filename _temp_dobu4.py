import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_html/dobu_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the "flex justify-between gap-4 text-xs" section - this is where dates appear
# Let me extract the full parent div containing multiple articles with dates
idx = html.find('flex justify-between gap-4 text-xs')
if idx > 0:
    # Find the enclosing div
    # Go back to find the opening div
    start = html.rfind('<div', 0, idx)
    # Find the matching closing div (rough)
    depth = 0
    end = start
    for i in range(start, min(start + 30000, len(html))):
        if html[i:i+4] == '<div':
            depth += 1
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                end = i + 6
                break
    
    section = html[start:end]
    print(f"=== SECTION WITH DATES (len={len(section)}) ===")
    # Print first 3000 chars
    print(section[:3000])
    print("...")
    print(section[-1000:])

# Also look at one specific article block that has a date (e.g. /news/8078)
print("\n\n=== SPECIFIC ARTICLE: /news/8078 ===")
idx2 = html.find('/news/8078')
if idx2 > 0:
    # Go back 500 chars, forward 800 chars
    snippet = html[max(0,idx2-500):idx2+800]
    print(snippet)

# Look at /news/8077 which has '1 цаг'
print("\n\n=== SPECIFIC ARTICLE: /news/8077 ===")
idx3 = html.find('/news/8077')
if idx3 > 0:
    snippet = html[max(0,idx3-500):idx3+800]
    print(snippet)

# Find what element contains the date text directly
# Search for patterns like ">1 цаг<" or ">2 цаг<"
date_raw = re.findall(r'>(\d+\s*(?:цаг|өдөр|мин|хоног|сар))<', html)
print(f"\n\n=== RAW DATE PATTERNS ===")
for d in list(set(date_raw))[:15]:
    print(f'  {d}')

# Find dates with surrounding tag context
date_with_tag = re.findall(r'(<[^>]*>)\s*(\d+\s*(?:цаг|өдөр|мин|хоног|сар))\s*(</[^>]*>)', html)
print(f'\n=== DATES WITH TAGS ===')
for before, date, after in date_with_tag[:15]:
    print(f'  {before} {date} {after}')

# Find dates in any element  
date_anywhere = re.findall(r'(<[^>]{0,30}>\s*\d+\s*(?:цаг|өдөр|мин|хоног|сар)\s*</[^>]{0,30}>)', html)
print(f'\n=== DATES IN ANY ELEMENT ===')
for d in date_anywhere[:15]:
    print(f'  {d[:100]}')
