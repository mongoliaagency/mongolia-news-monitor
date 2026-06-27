import json
from lxml import html

with open("_iaac.html", "r", encoding="utf-8") as f:
    page = f.read()

tree = html.fromstring(page)

items = tree.cssselect("div.blog_box.type_two")
results = []

for item in items:
    title_el = item.cssselect("h4.title_16 a")
    date_el = item.cssselect("time.date.published")
    
    title = title_el[0].text_content().strip() if title_el else ""
    href = title_el[0].get("href", "") if title_el else ""
    url = "https://iaac.mn/" + href if href else ""
    date_str = date_el[0].text_content().strip() if date_el else ""
    
    results.append({
        "title": title[:80],
        "url": url,
        "date": date_str
    })

with open("_iaac_verify.txt", "w", encoding="utf-8") as f:
    f.write(json.dumps(results[:10], ensure_ascii=False, indent=2))
    f.write(f"\n\nTotal: {len(results)} articles\n")
    if results:
        f.write(f"Latest: {results[0]['date']}\n")
        f.write(f"Earliest: {results[-1]['date']}\n")

print(f"Verified {len(results)} articles")
