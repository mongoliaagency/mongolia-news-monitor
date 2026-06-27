from bs4 import BeautifulSoup

with open("_mrpam.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")
items = soup.select("article.post.post-medium")

lines = []
for i, item in enumerate(items):
    title_el = item.select_one(".post-content h4 a")
    date_el = item.select_one("a.bg-tertiary")
    link_el = item.select_one("a.bg-tertiary")
    
    title = title_el.get_text(strip=True) if title_el else "NONE"
    date = date_el.get_text(strip=True) if date_el else "NONE"
    link = link_el.get("href", "") if link_el else "NONE"
    
    if link.startswith("/"):
        link = "https://mrpam.gov.mn" + link
    
    lines.append(f"[{i}] {date} | {title[:80]} | {link}")

with open("_verify_mrpam.txt", "w", encoding="utf-8") as f:
    f.write(f"Total items: {len(items)}\n\n")
    f.write("\n".join(lines))

print(f"Verified {len(items)} items.")
