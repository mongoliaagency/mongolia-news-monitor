import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_html/eagle_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract card_wrapper sections with more context
cards = re.findall(r'(<div[^>]*class="[^"]*card_wrapper[^"]*"[^>]*>.*?</a>\s*</div>)', html, re.DOTALL)
print(f"Full card wrappers: {len(cards)}")
for i, card in enumerate(cards[:8]):
    print(f"\n{'='*60}")
    print(f"CARD {i}:")
    # Print cleaned version
    # Extract link
    links = re.findall(r'href="(/r/[^"]+)"', card)
    # Extract title
    titles = re.findall(r'class="[^"]*card_title[^"]*"[^>]*>(.*?)<', card)
    # Extract any date/time
    dates = re.findall(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})', card)
    # Extract category
    cats = re.findall(r'>([^<]{2,30})</(?:span|a|div)>', card)
    # Extract image
    imgs = re.findall(r'<img[^>]*src="([^"]+)"', card)
    print(f"  Link: {links}")
    print(f"  Title: {titles}")
    print(f"  Dates: {dates}")
    print(f"  Images: {imgs[:1]}")
    # Print raw HTML snippet (first 500 chars)
    print(f"  HTML snippet: {card[:500]}")

# Also look for the section headers / categories in cards
cat_spans = re.findall(r'<span[^>]*class="[^"]*(?:category|cat|badge|tag|label)[^"]*"[^>]*>(.*?)</span>', html, re.DOTALL)
print(f"\n\nCategory/badge spans: {len(cat_spans)}")
for c in list(set(cat_spans))[:20]:
    print(f"  {c}")

# Look for news section structure
sections = re.findall(r'<h[2-4][^>]*class="[^"]*(?:title|heading|section|category)[^"]*"[^>]*>(.*?)</h[2-4]>', html)
print(f"\nSection headers: {len(sections)}")
for s in list(set(sections))[:15]:
    print(f"  {s}")

# Look for the main layout
# Find what comes before card_wrapper - likely section headers
for m in re.finditer(r'(<h[2-4][^>]*>.*?</h[2-4]>).{0,500}card_wrapper', html):
    print(f"\nSection header near cards: {m.group(1)[:200]}")
    break

# Check for date in the rendered HTML near articles
# Look for patterns like: title + date + link in article context
article_blocks = re.findall(r'<div[^>]*class="[^"]*(?:col-lg-4|col-md-4|col-6)[^"]*"[^>]*>.*?href="(/r/[^"]+)".*?</div>\s*</div>\s*</div>', html, re.DOTALL)
print(f"\nArticle blocks (col-lg-4 + /r/ link): {len(article_blocks)}")
for i, block in enumerate(article_blocks[:5]):
    title = re.findall(r'>([^<]{10,80})<', block)
    date = re.findall(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})', block)
    rel = re.findall(r'(\d+\s*(?:цаг|өдөр|мин|хоног))', block)
    print(f"  Block {i}: title={title[:2]}, date={date[:2]}, rel={rel[:2]}")
