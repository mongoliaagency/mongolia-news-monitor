import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from bs4 import BeautifulSoup

with open("_sme.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Look for news patterns - focus on link groups
results = []

# Find all sections/divs that might be news lists
for tag_name in ["section", "div"]:
    for tag in soup.find_all(tag_name):
        cls = tag.get("class", [])
        cls_str = ".".join(cls) if cls else ""
        links = tag.find_all("a", href=True)
        # Filter meaningful links (not #, not javascript, has text)
        meaningful = [a for a in links if a.get_text(strip=True) and a['href'] not in ('#', 'javascript:void(0)') and len(a.get_text(strip=True)) > 10]
        if 5 <= len(meaningful) <= 50:
            results.append((len(meaningful), tag_name, cls_str, meaningful))

results.sort(key=lambda x: x[0], reverse=True)

with open("_sme_analysis.txt", "w", encoding="utf-8") as f:
    for count, tag_name, cls_str, links in results[:20]:
        f.write(f"\n{'='*60}\n")
        f.write(f"{tag_name}.{cls_str}: {count} meaningful links\n")
        for a in links[:5]:
            f.write(f"  [{a.get_text(strip=True)[:120]}]\n")
            f.write(f"  -> {a['href']}\n")
            # parent info
            parent = a.parent
            f.write(f"  parent: {parent.name}.{'.'.join(parent.get('class',[])[:3])}\n")
            f.write(f"\n")
    
    # Also search for specific section IDs
    f.write(f"\n{'='*60}\n")
    f.write("SEARCHING FOR NEWS SECTION\n")
    
    # Look for h4/h2 with date patterns nearby
    h4s = soup.find_all("h4")
    f.write(f"\nTotal h4 tags: {len(h4s)}\n")
    for h in h4s[:10]:
        f.write(f"  h4.{'.'.join(h.get('class',[]))}: [{h.get_text(strip=True)[:100]}]\n")
        parent = h.parent
        f.write(f"  parent: {parent.name}.{'.'.join(parent.get('class',[])[:5])}\n")
        # check for date
        for sibling in parent.find_all(["span", "small", "time", "p"]):
            text = sibling.get_text(strip=True)
            if any(c.isdigit() for c in text) and len(text) < 30:
                f.write(f"  possible date: [{text}] in {sibling.name}.{'.'.join(sibling.get('class',[])[:3])}\n")
