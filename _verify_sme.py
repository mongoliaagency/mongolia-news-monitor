import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from bs4 import BeautifulSoup

with open("_sme.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

items = soup.select(".entry.col-12.pb-2")

with open("_verify_sme.txt", "w", encoding="utf-8") as f:
    f.write(f"Total items: {len(items)}\n\n")
    for i, item in enumerate(items):
        title_node = item.select_one("h4 a")
        date_node = item.select_one(".entry-meta li.sme-custom-blue:last-child")
        
        title = title_node.get_text(strip=True) if title_node else None
        link = title_node.get("href") if title_node else None
        date = date_node.get_text(strip=True) if date_node else None
        
        # Skip Twitter/Facebook entries (no title)
        if not title:
            f.write(f"[{i+1}] SKIP (no h4 a)\n")
            continue
        
        f.write(f"[{i+1}] {title[:80]}\n")
        f.write(f"      Link: {link}\n")
        f.write(f"      Date: {date}\n\n")
