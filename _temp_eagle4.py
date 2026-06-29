import re
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_html/eagle_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract push #235 - the big one with siteData
pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', html, re.DOTALL)
big = pushes[235]

# The big push is JSON-escaped. Try to find post data within it
# Look for the structure: "value":[{...post data...}]
# First, let's see what keys exist at the top level
top_keys = re.findall(r'"([a-z_]+)":', big)
from collections import Counter
key_counts = Counter(top_keys)
print("Top keys in big push:")
for k, v in key_counts.most_common(30):
    print(f"  {k}: {v}")

# Look for post list data - find arrays of posts
# Posts have "object_type":"post"
post_pattern = re.findall(r'\{"id":"[^"]+","object_type":"post"[^}]*?\}', big)
print(f"\nPost objects: {len(post_pattern)}")

# Look for post objects with more context
posts_extended = re.findall(r'\{(?:\\"[^\\]+\\":\\"[^\\]+\\",?){2,30}\}', big)
print(f"\nExtended objects: {len(posts_extended)}")

# Instead, find the section that has the posts array
# The pattern in Next.js RSC is typically: "value":[{posts}]
# Look for array of posts by finding the boundary
post_start = big.find('"object_type":"post"')
if post_start > 0:
    # Go back to find the array start
    context = big[max(0,post_start-500):post_start+2000]
    print(f"\nContext around first post object:")
    print(context[:2000])
else:
    print("\nNo 'object_type:post' found in big push")
    # Try unescaped version
    post_start2 = big.find('object_type')
    print(f"\nFirst 'object_type' at position: {post_start2}")
    if post_start2 > 0:
        print(big[post_start2:post_start2+500])

# The data might be double-escaped. Let's try to decode
# Look for JSON string within the push
try:
    # The RSC push data uses \n as newlines and \" for quotes
    # Try to find JSON arrays
    json_arrays = re.findall(r'\[({.*?})\](?:,|$)', big)
    print(f"\nJSON arrays found: {len(json_arrays)}")
except:
    pass

# Alternative: look for the actual page HTML (not RSC) that contains article lists
# Find sections between <script> tags
# The rendered HTML is the actual visible content
visible_start = html.find('<div class="container">')
if visible_start > 0:
    visible_html = html[visible_start:visible_start+20000]
    print(f"\n\n=== VISIBLE HTML (first 5000 chars) ===")
    print(visible_html[:5000])

# Also look for the section with "Шинэ" or "Онцлох" headers
for keyword in ['Шинэ', 'Онцлох', 'Мэдээ', 'Сүүлд', 'Хамгийн']:
    idx = visible_html.find(keyword)
    if idx > 0:
        print(f"\nFound '{keyword}' at position {idx} in visible HTML:")
        print(visible_html[max(0,idx-100):idx+200])
