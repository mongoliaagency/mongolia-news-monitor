import re

with open('_html/eagle_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract the big RSC push #235
pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', html, re.DOTALL)
big = pushes[235]
print(f"Push #235 length: {len(big)}")

# Find published_at dates in the big payload
dates = re.findall(r'published_at.{0,3}"([^"]+)"', big)
print(f"\npublished_at dates: {len(dates)}")
for d in list(set(dates))[:20]:
    print(f"  {d}")

# Find created_at dates
dates2 = re.findall(r'created_at.{0,3}"([^"]+)"', big)
print(f"\ncreated_at dates: {len(dates2)}")
for d in list(set(dates2))[:20]:
    print(f"  {d}")

# Find titles in the big payload
titles = re.findall(r'title.{0,3}"([^"]{10,100})"', big)
print(f"\nTitle samples from big payload:")
for t in list(set(titles))[:20]:
    print(f"  {t}")

# Find all object_type patterns
obj_types = re.findall(r'"object_type":"([^"]+)"', big)
print(f"\nObject types: {set(obj_types)}")

# Find post entries with title and slug
posts = re.findall(r'"object_type":"post".*?"title":"([^"]+)".*?"slug":"([^"]+)"', big)
print(f"\nPost entries (title + slug): {len(posts)}")
for t, s in posts[:10]:
    print(f"  {t[:60]} -> {s}")

# Now analyze the rendered HTML portion (not RSC)
# Find article cards in the HTML
card_pattern = re.findall(r'<div[^>]*class="[^"]*card_wrapper[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
print(f"\nCard wrappers in HTML: {len(card_pattern)}")
for i, c in enumerate(card_pattern[:5]):
    # Extract link and title
    link = re.findall(r'href="(/r/[^"]+)"', c)
    title = re.findall(r'class="[^"]*card_title[^"]*"[^>]*>(.*?)<', c)
    print(f"  Card {i}: link={link}, title={title[:80] if title else 'N/A'}")

# Also look for col-md-4 mb-4 patterns (article grid items)  
grid_items = re.findall(r'<div class="col-md-4 mb-4">(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
print(f"\nGrid items (col-md-4 mb-4): {len(grid_items)}")
for i, item in enumerate(grid_items[:10]):
    link = re.findall(r'href="(/r/[^"]+)"', item)
    title = re.findall(r'>([^<]{10,80})<', item)
    img = re.findall(r'<img[^>]*src="([^"]+)"', item)
    print(f"  Item {i}: link={link}, img={'Y' if img else 'N'}")

# Check for date in card context
date_in_card = re.findall(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})', html)
print(f"\nDates in HTML: {len(date_in_card)}")
for d in list(set(date_in_card))[:15]:
    print(f"  {d}")

# Look for relative dates in Mongolian
rel_dates = re.findall(r'(\d+\s*(?:цаг|өдөр|мин|хоног|сар|жил))', html)
print(f"\nRelative dates in Mongolian: {len(rel_dates)}")
for d in list(set(rel_dates))[:15]:
    print(f"  {d}")
