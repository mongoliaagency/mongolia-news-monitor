import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from bs4 import BeautifulSoup

with open("_sme.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Focus on the first .entry.col-12.pb-2
entry = soup.select_one(".entry.col-12.pb-2")
if entry:
    with open("_sme_analysis.txt", "w", encoding="utf-8") as f:
        f.write("FIRST ENTRY HTML:\n")
        f.write(str(entry)[:3000])
        f.write("\n\n" + "="*60 + "\n")
        
        # Show all children recursively
        f.write("\nCHILDREN STRUCTURE:\n")
        def show_tree(el, indent=0):
            for child in el.find_all(recursive=False):
                cls = ".".join(child.get("class", []))
                text = child.get_text(strip=True)[:80]
                f.write(f"{'  '*indent}{child.name}.{cls}: [{text}]\n")
                show_tree(child, indent+1)
        show_tree(entry)
        
        # Look for dates in first 5 entries
        f.write("\n\n" + "="*60 + "\n")
        f.write("DATES IN FIRST 5 ENTRIES:\n")
        for i, entry in enumerate(soup.select(".entry.col-12.pb-2")[:5]):
            f.write(f"\n--- Entry {i+1} ---\n")
            # search for date patterns
            for tag in entry.find_all(["span", "li", "small", "time", "div", "p"]):
                text = tag.get_text(strip=True)
                cls = ".".join(tag.get("class", []))
                # Look for anything that might be a date
                import re
                if re.search(r'\d{4}', text) and len(text) < 50:
                    f.write(f"  {tag.name}.{cls}: [{text}]\n")
            
            # also check entry-meta
            meta = entry.select(".entry-meta li")
            for m in meta:
                f.write(f"  meta: [{m.get_text(strip=True)}]\n")
        
        # Look for the news section's specific structure
        f.write("\n\n" + "="*60 + "\n")
        f.write("TAB-CONTENT STRUCTURE:\n")
        tab = soup.select_one(".tab-content")
        if tab:
            # show first 2000 chars
            f.write(str(tab)[:2000])
