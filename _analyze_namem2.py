import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from bs4 import BeautifulSoup

with open("_namem.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

with open("_namem_analysis.txt", "w", encoding="utf-8") as f:
    items = soup.select("div.list_item")
    f.write(f"Total div.list_item: {len(items)}\n\n")
    
    for i, item in enumerate(items[:5]):
        f.write(f"=== Item {i+1} ===\n")
        f.write(str(item)[:1200])
        f.write("\n\n")
    
    # Also try to get news from /c/news page
    f.write("\n=== ALSO CHECK: section.top.btm structure ===\n")
    section = soup.select_one("section.top.btm")
    if section:
        f.write(str(section)[:800])
        f.write("\n\n")
        # show children
        for ch in section.find_all(recursive=False):
            cls = ".".join(ch.get("class", [])[:3])
            f.write(f"  {ch.name}.{cls}\n")
    
    # Look for date patterns
    f.write("\n=== DATE PATTERNS in list_items ===\n")
    for i, item in enumerate(soup.select("div.list_item")[:5]):
        h2 = item.select_one("h2 a")
        title = h2.get_text(strip=True) if h2 else "NONE"
        link = h2.get("href") if h2 else "NONE"
        
        # search for date
        import re
        date_found = "NONE"
        for tag in item.find_all(["span", "small", "time", "div", "p", "i"]):
            text = tag.get_text(strip=True)
            if re.search(r'\d{4}[-./]\d{1,2}[-./]\d{1,2}', text):
                date_found = text
                break
            if re.search(r'\d{1,2}[-./]\d{1,2}[-./]\d{4}', text):
                date_found = text
                break
        
        f.write(f"\n[{i+1}] {title[:100]}\n")
        f.write(f"    Link: {link}\n")
        f.write(f"    Date: {date_found}\n")
