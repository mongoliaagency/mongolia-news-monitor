import json
from lxml import html

with open("_mmra.html", "r", encoding="utf-8") as f:
    page = f.read()

tree = html.fromstring(page)

items = tree.cssselect("div.blog.list-view div.post")
results = []

for item in items:
    title_el = item.cssselect("h3.post-title a")
    date_el = item.cssselect("div.meta span.date")
    
    title = title_el[0].text_content().strip() if title_el else ""
    href = title_el[0].get("href", "") if title_el else ""
    url = "https://mmra.gov.mn" + href if href else ""
    date_str = date_el[0].text_content().strip() if date_el else ""
    
    results.append({
        "title": title[:80],
        "url": url,
        "date": date_str
    })

with open("_mmra_verify.txt", "w", encoding="utf-8") as f:
    f.write(json.dumps(results, ensure_ascii=False, indent=2))
    f.write(f"\n\nTotal: {len(results)} articles\n")
    if results:
        f.write(f"Latest: {results[0]['date']}\n")
        f.write(f"Earliest: {results[-1]['date']}\n")

print(f"Verified {len(results)} articles")
