import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_html/eagle_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the "Шинэ мэдээ" section and extract article items
shine_start = html.find('Шинэ мэдээ')
if shine_start > 0:
    context = html[shine_start:shine_start+8000]
    print("=== ШИНЭ МЭДЭЭ SECTION (first 8000 chars) ===")
    print(context[:8000])

print("\n\n" + "="*80)

# Find the section with "col-md-9" (main content) to see article structure
# Look for the grid of articles with col-md-4
main_start = html.find('col-md-9')
if main_start > 0:
    # Find the article grid after the main content area
    context = html[main_start:main_start+15000]
    # Find all article-like blocks
    # Each article has: image, category, title, link
    print("=== MAIN CONTENT SECTION (first 5000 chars) ===")
    print(context[:5000])

print("\n\n" + "="*80)

# Let's look at the full HTML structure around the card_wrapper elements
# Find the section containing cards
card_start = html.find('card_wrapper')
if card_start > 0:
    # Go back to find the section header
    section_start = max(0, card_start - 3000)
    section = html[section_start:card_start + 5000]
    print("=== CARD SECTION CONTEXT ===")
    print(section[:5000])

print("\n\n" + "="*80)

# Check if there is a date near any article title in the visible HTML
# Look for patterns like: title + date within same parent div
# Try to find the closest date to each /r/ link in visible HTML
for m in re.finditer(r'<a[^>]*href="(/r/[a-zA-Z0-9]+)"[^>]*>(.*?)</a>', html):
    link = m.group(1)
    title = m.group(2)
    # Look backwards up to 500 chars for a date
    before = html[max(0, m.start()-500):m.start()]
    dates_before = re.findall(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})', before)
    if dates_before:
        print(f"Date BEFORE link: {dates_before[-1]} -> {link} ({title[:40]})")
    # Look forwards up to 200 chars for a date
    after = html[m.end():m.end()+200]
    dates_after = re.findall(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})', after)
    if dates_after:
        print(f"Date AFTER link: {dates_after[0]} -> {link} ({title[:40]})")

print("\n\n" + "="*80)

# Also look for "time" elements or any dedicated date container
time_elements = re.findall(r'<(?:time|span)[^>]*datetime="([^"]+)"[^>]*>', html)
print(f"Time/datetime elements: {len(time_elements)}")
for t in time_elements[:10]:
    print(f"  {t}")

# Look for any span/div with date-related class
date_containers = re.findall(r'<([a-z]+)[^>]*class="[^"]*(?:date|time|published|created)[^"]*"[^>]*>(.*?)</\1>', html, re.DOTALL)
print(f"\nDate containers: {len(date_containers)}")
for tag, content in date_containers[:10]:
    print(f"  <{tag}> {content[:100]}")
