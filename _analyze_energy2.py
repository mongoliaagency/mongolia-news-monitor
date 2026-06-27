from bs4 import BeautifulSoup

with open("_energy.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

items = soup.select(".post-item")
lines = []
for i, item in enumerate(items):
    lines.append(f"\n=== POST [{i}] ===")
    
    # Find all links inside
    for a in item.select("a[href]"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        cls = " ".join(a.get("class", []))
        lines.append(f"  LINK: href='{href}' text='{text}' class='{cls}'")
    
    # Find date element
    date_el = item.select_one("[class*='date']")
    if date_el:
        lines.append(f"  DATE: text='{date_el.get_text(strip=True)}' class='{' '.join(date_el.get('class', []))}'")
    
    # Find all direct child divs
    for child in item.find_all(recursive=False):
        cls = " ".join(child.get("class", []))
        text = child.get_text(strip=True)[:120]
        lines.append(f"  DIV: class='{cls}' text='{text}'")

with open("_energy_analysis2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Done. Written to _energy_analysis2.txt")
