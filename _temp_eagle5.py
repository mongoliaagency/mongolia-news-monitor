import re
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_html/eagle_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract push #235
pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', html, re.DOTALL)
big = pushes[235]

# The RSC data is escaped. Let's try to find post objects with published_at
# Pattern: published_at field followed by ISO date
pub_dates = re.findall(r'published_at\\":\\"([^\\]+)', big)
print(f"published_at dates: {len(pub_dates)}")
for d in list(set(pub_dates))[:15]:
    print(f"  {d}")

# Extract full post objects
# Post objects start with {"id":"..." and contain "object_type":"post"
# In escaped form: \{"id\":\"...\",\"object_type\":\"post\"
post_objects = re.findall(r'\{(?:\\"[^\\]+\\":(?:\{[^}]*\}|\[[^\]]*\]|\\"[^\\]*\\"|null|\d+),?)+\}', big)
print(f"\nTotal JSON-like objects: {len(post_objects)}")

# Find posts with title and published_at
posts_with_data = []
for obj in post_objects:
    if 'object_type\\\":\\\"post\\\"' in obj:
        title_match = re.search(r'title\\\":\\\"([^\\]+)', obj)
        slug_match = re.search(r'slug\\\":\\\"([^\\]+)', obj)
        date_match = re.search(r'published_at\\\":\\\"([^\\]+)', obj)
        excerpt_match = re.search(r'excerpt\\\":\\\"([^\\]+)', obj)
        if title_match and slug_match:
            posts_with_data.append({
                'title': title_match.group(1),
                'slug': slug_match.group(1),
                'date': date_match.group(1) if date_match else 'N/A',
                'excerpt': excerpt_match.group(1)[:50] if excerpt_match else 'N/A'
            })

print(f"\nPosts with data: {len(posts_with_data)}")
for p in posts_with_data[:15]:
    print(f"  [{p['date'][:19] if len(p['date'])>19 else p['date']}] {p['title'][:60]}")
    print(f"    URL: /r/{p['slug']}")

# Now let's look at the visible HTML for any dates near articles
# Search for date patterns near /r/ links in visible HTML
visible = html
# Find patterns like: some text + date + /r/ link
date_near_link = re.findall(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})[^/]{0,200}?(/r/[a-zA-Z0-9]+)', visible)
print(f"\nDate near /r/ links in HTML: {len(date_near_link)}")
for d, link in date_near_link[:15]:
    print(f"  {d} -> {link}")

# Also look for the small article list items (sidebar / list view)
# These might have dates
small_items = re.findall(r'<div[^>]*class="[^"]*(?:smallPost|small_post|listItem|list_item|sidePost|side_post)[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', visible, re.DOTALL)
print(f"\nSmall post items: {len(small_items)}")

# Look for the "Шинэ мэдээ" (latest news) section
for m in re.finditer(r'(Шинэ мэдээ|Хамгийн их|Онцлох|Сүүлийн|Шинээр).{0,2000}', visible):
    context = m.group(0)
    # Find dates in context
    dates = re.findall(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}|\d+\s*(?:цаг|өдөр|мин|хоног))', context)
    links = re.findall(r'href="(/r/[^"]+)"', context)
    print(f"\nSection '{m.group(1)}': dates={dates[:5]}, links={links[:5]}")

# Final: find date near any visible article link
# Look at all /r/ links and what's near them
for m in re.finditer(r'(.{0,300})href="(/r/[a-zA-Z0-9]+)"(.{0,100})', visible):
    context = m.group(0)
    dates = re.findall(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})', context)
    if dates:
        print(f"\nLink with date: {m.group(2)} -> {dates[0]}")
        if len([d for d in dates]) > 5:
            break
