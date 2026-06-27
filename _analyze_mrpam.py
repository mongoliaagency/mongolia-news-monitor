from bs4 import BeautifulSoup

with open("_mrpam.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

with open("_mrpam_analysis.txt", "w", encoding="utf-8") as f:
    # Body direct children
    f.write("=== BODY DIRECT CHILDREN ===\n")
    for child in soup.body.find_all(recursive=False)[:30]:
        name = child.name or ""
        cls = " ".join(child.get("class", [])) if child.get("class") else ""
        ident = child.get("id", "")
        text_preview = child.get_text(strip=True)[:80]
        f.write(f"<{name}> class='{cls}' id='{ident}' text='{text_preview}'\n")

    # Search for news-like containers
    f.write("\n=== LOOKING FOR NEWS CONTAINERS ===\n")
    for sel in ["article", ".post", ".post-item", ".card", ".news-item", ".entry",
                "[class*='post']", "[class*='news']", "[class*='article']",
                ".list-item", ".blog-post", ".blog-item", ".col-lg-", ".col-md-"]:
        items = soup.select(sel)
        if items:
            f.write(f"\n{sel}: {len(items)} items\n")
            for i, item in enumerate(items[:3]):
                cls = " ".join(item.get("class", []))
                text = item.get_text(strip=True)[:100]
                f.write(f"  [{i}] class='{cls}' text='{text}'\n")

    # Links with href
    f.write("\n=== SAMPLE LINKS (first 50) ===\n")
    links = soup.select("a[href]")
    for a in links[:50]:
        href = a.get("href", "")
        text = a.get_text(strip=True)[:80]
        cls = " ".join(a.get("class", []))
        f.write(f"  href='{href}' text='{text}' class='{cls}'\n")

    # Dates
    f.write("\n=== DATE PATTERNS ===\n")
    for sel in ["time", "[class*='date']", "[class*='time']", ".date", "time[datetime]", "span[class*='date']"]:
        items = soup.select(sel)
        if items:
            f.write(f"\n{sel}: {len(items)} items\n")
            for item in items[:5]:
                dt_attr = item.get("datetime", "")
                text = item.get_text(strip=True)[:60]
                f.write(f"  datetime='{dt_attr}' text='{text}'\n")

    # Look for table/rows
    f.write("\n=== TABLE/ROW STRUCTURES ===\n")
    for sel in ["table", ".table", "tr", "[class*='row']", "[class*='list']", ".news-list", ".article-list"]:
        items = soup.select(sel)
        if items:
            f.write(f"\n{sel}: {len(items)} items\n")
            for item in items[:3]:
                cls = " ".join(item.get("class", []))
                text = item.get_text(strip=True)[:100]
                f.write(f"  class='{cls}' text='{text}'\n")

print("Done. Written to _mrpam_analysis.txt")
