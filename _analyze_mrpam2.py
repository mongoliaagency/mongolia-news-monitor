from bs4 import BeautifulSoup

with open("_mrpam.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")
items = soup.select("article.post.post-medium")

with open("_mrpam_analysis2.txt", "w", encoding="utf-8") as f:
    for i, item in enumerate(items):
        f.write(f"\n=== POST [{i}] ===\n")
        
        # All links
        for a in item.select("a[href]"):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            cls = " ".join(a.get("class", []))
            f.write(f"  LINK: href='{href}' text='{text[:80]}' class='{cls}'\n")
        
        # Date elements
        for el in item.select("[class*='date'], time"):
            dt = el.get("datetime", "")
            text = el.get_text(strip=True)
            cls = " ".join(el.get("class", []))
            f.write(f"  DATE_EL: datetime='{dt}' text='{text}' class='{cls}'\n")
        
        # Direct children
        for child in item.find_all(recursive=False):
            cls = " ".join(child.get("class", []))
            tag = child.name
            text = child.get_text(strip=True)[:150]
            f.write(f"  <{tag}> class='{cls}' text='{text}'\n")
        
        # Look for date text at the start of each post
        full_text = item.get_text(strip=True)
        f.write(f"  FULL_TEXT (first 200): '{full_text[:200]}'\n")

    f.write(f"\n=== TOTAL POSTS: {len(items)} ===\n")

    # Pagination
    pagination = soup.select("[class*='pagination'] a, a[rel='next'], a[rel='prev']")
    f.write("\n=== PAGINATION ===\n")
    for a in pagination[:10]:
        href = a.get("href", "")
        text = a.get_text(strip=True)
        f.write(f"  href='{href}' text='{text}'\n")

print("Done. Written to _mrpam_analysis2.txt")
