import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from bs4 import BeautifulSoup

with open("_namem.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

items = soup.select(".list_item .item")

with open("_verify_namem.txt", "w", encoding="utf-8") as f:
    f.write(f"Total items: {len(items)}\n\n")
    for i, item in enumerate(items):
        title_node = item.select_one("h2 a.title")
        date_node = item.select_one(".text .date")
        
        title = title_node.get_text(strip=True) if title_node else None
        link = title_node.get("href") if title_node else None
        date = date_node.get_text(strip=True) if date_node else None
        
        if not title:
            f.write(f"[{i+1}] SKIP\n")
            continue
        
        f.write(f"[{i+1}] {title[:100]}\n")
        f.write(f"      Link: {link}\n")
        f.write(f"      Date: {date}\n\n")
