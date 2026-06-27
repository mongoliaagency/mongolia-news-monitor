from bs4 import BeautifulSoup
import json, re
from datetime import datetime

with open("_html/president_mn.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

print("=" * 60)
print("总统办公厅 HTML 页面分析")
print("=" * 60)

# Check if it's WordPress
is_wp = bool(soup.select('link[rel="pingback"]') or soup.select('meta[name="generator"][content*="WordPress"]'))
print(f"WordPress: {is_wp}")

# Try to find article items - WordPress typically uses various classes
selectors_to_try = [
    "article", "article.post", ".post", ".post-item", ".post-box",
    ".news-item", ".grid-item", ".blog-post", ".entry", ".type-post",
    ".col-md-4", ".col-md-6", ".archive-item", ".list-item",
    ".news-block", ".medee-item", ".card", ".news-card",
    "[class*='post-']", "[class*='news']"
]

print("\n--- Try common selectors ---")
for sel in selectors_to_try:
    items = soup.select(sel)
    if items:
        print(f"  {sel}: {len(items)} items")

# Check for specific patterns
print("\n--- Check href patterns ---")
for pat in ["/medee/", "/news/", "/post/", "/archives/", "/category/"]:
    matches = soup.select(f'a[href*="{pat}"]')
    print(f"  a[href*='{pat}']: {len(matches)}")

# Check for date patterns
print("\n--- Date patterns ---")
for cls in ["date", "time", "posted-on", "entry-date", "entry-time", "published", "post-date", "meta"]:
    matches = soup.select(f'[class*="{cls}"]')
    print(f"  [class*='{cls}']: {len(matches)}")

# Check for time elements
times = soup.select('time')
print(f"  <time>: {len(times)}")

# Check body structure
body = soup.body
if body:
    # Look for main content area
    main = soup.select_one('main, #main, .content, .site-content, #content, .page-content')
    if main:
        print(f"\n--- Main content area: {main.get('id', '')} {main.get('class', '')}")

    # Check all links that look like article links
    all_links = soup.select('a[href]')
    article_links = []
    for a in all_links:
        href = a.get('href', '')
        # Try to find links that look like individual posts
        if re.search(r'/medee/\d{4}|/news/\d{4}|/archives/\d+|/\?p=\d+', href):
            article_links.append(a)
    
    if article_links:
        print(f"\n--- Potential article links: {len(article_links)} ---")
        for a in article_links[:5]:
            print(f"  {a.get_text(strip=True)[:60]} -> {a.get('href', '')}")

# Search for common WP REST API link
rest_link = soup.select('link[rel="alternate"][type="application/json"]')
print(f"\nREST API links: {len(rest_link)}")

# Check Yoast SEO structured data
yoast = soup.select('script[type="application/ld+json"]')
print(f"Yoast schema: {len(yoast)}")

# Dump first 5 date-like texts found
print("\n--- Date-like text samples ---")
date_pattern = re.compile(r'\d{4}[./-]\d{2}[./-]\d{2}')
texts_with_dates = []
for elem in soup.find_all(text=True):
    if date_pattern.search(elem):
        texts_with_dates.append((elem.parent.name, elem.parent.get('class', []), elem.strip()[:80]))

for name, cls, txt in texts_with_dates[:10]:
    print(f"  <{name} class={cls}> {txt}")
