from bs4 import BeautifulSoup

with open("_energy.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Top-level structure
body = soup.body
lines = []
for child in body.find_all(recursive=False)[:30]:
    name = child.name or ""
    cls = " ".join(child.get("class", [])) if child.get("class") else ""
    ident = child.get("id", "")
    text_preview = child.get_text(strip=True)[:80]
    lines.append(f"<{name}> class='{cls}' id='{ident}' text='{text_preview}'")

with open("_energy_analysis.txt", "w", encoding="utf-8") as f:
    f.write("=== BODY DIRECT CHILDREN ===\n")
    f.write("\n".join(lines))

    # Search for news-like containers
    f.write("\n\n=== LOOKING FOR POSTS/CARDS/ARTICLES ===\n")
    
    # Try common patterns
    for sel in ["article", ".post", ".post-item", ".post-list .item", ".card", ".news-item", 
                ".entry", "[class*='post']", "[class*='news']", "[class*='list'] .item",
                ".row [class*='col']", ".blog-post", ".blog-item"]:
        items = soup.select(sel)
        if items:
            f.write(f"\n{sel}: {len(items)} items\n")
            for i, item in enumerate(items[:3]):
                cls = " ".join(item.get("class", []))
                text = item.get_text(strip=True)[:100]
                f.write(f"  [{i}] class='{cls}' text='{text}'\n")

    # Links with href
    f.write("\n\n=== SAMPLE LINKS (first 30) ===\n")
    links = soup.select("a[href]")
    for a in links[:30]:
        href = a.get("href", "")
        text = a.get_text(strip=True)[:60]
        cls = " ".join(a.get("class", []))
        f.write(f"  href='{href}' text='{text}' class='{cls}'\n")

    # Dates
    f.write("\n\n=== DATE PATTERNS ===\n")
    for sel in ["time", "[class*='date']", "[class*='time']", ".date", "time[datetime]", "span[class*='date']"]:
        items = soup.select(sel)
        if items:
            f.write(f"\n{sel}: {len(items)} items\n")
            for item in items[:5]:
                dt_attr = item.get("datetime", "")
                text = item.get_text(strip=True)[:60]
                f.write(f"  datetime='{dt_attr}' text='{text}'\n")

print("Analysis written to _energy_analysis.txt")
