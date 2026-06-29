import re, json

with open('_html/eagle_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f'File size: {len(html)} chars')

# Find all self.__next_f.push calls containing data
# Look for 'published_at' or 'created_at' patterns
dates = re.findall(r'"(?:published_at|created_at)":"([^"]+)"', html)
print(f'\nDate samples (published_at/created_at):')
for d in list(set(dates))[:20]:
    print(f'  {d}')

# Look for post/article title patterns
titles = re.findall(r'"title":"([^"]{10,80})"', html)
print(f'\nTitle samples:')
for t in list(set(titles))[:15]:
    print(f'  {t}')

# Look for slug patterns (URL paths)
slugs = re.findall(r'"slug":"([^"]+)"', html)
print(f'\nSlug samples:')
for s in list(set(slugs))[:15]:
    print(f'  {s}')

# Look for Next.js link patterns
links = re.findall(r'href="(/[^"]+)"', html)
print(f'\nLink samples (href):')
for l in list(set(links))[:30]:
    print(f'  {l}')

# Look for "post" related class names
post_classes = re.findall(r'class="([^"]*post[^"]*)"', html)
print(f'\nPost class samples:')
for c in list(set(post_classes))[:20]:
    print(f'  {c}')

# Look for article card patterns  
card_classes = re.findall(r'class="([^"]*card[^"]*)"', html)
print(f'\nCard class samples:')
for c in list(set(card_classes))[:20]:
    print(f'  {c}')

# Look for col-md patterns (likely article grid items)
col_patterns = re.findall(r'<div class="([^"]*col[^"]*)"[^>]*>.*?<a[^>]*href="(/[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
print(f'\nColumn + link patterns:')
for c in col_patterns[:15]:
    print(f'  {c[0]} -> {c[1]}')

# Extract Next.js RSC payload - look for the actual page data
# The data is in self.__next_f.push([1, "...json_escaped..."])
rsc_pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', html)
print(f'\nRSC push count: {len(rsc_pushes)}')

# Look for the large payload
for idx, push in enumerate(rsc_pushes):
    print(f'\nRSC push #{idx} length: {len(push)}')
    if len(push) > 50000:
        # Try to find structured data
        if 'siteData' in push or 'organization' in push:
            print('  Contains siteData/organization')
        # Extract post list data
        posts = re.findall(r'"object_type":"post","[^}]*"title":"([^"]+)"', push)
        print(f'  Post titles in this push: {len(posts)}')
        for t in posts[:5]:
            print(f'    {t}')
