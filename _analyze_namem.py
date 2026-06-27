import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from bs4 import BeautifulSoup

with open("_namem.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

with open("_namem_analysis.txt", "w", encoding="utf-8") as f:
    # Look for news sections
    f.write("=== TOP-LEVEL STRUCTURE ===\n")
    body = soup.body
    if body:
        for child in body.find_all(recursive=False):
            if child.name:
                cls = ".".join(child.get("class", [])[:3])
                f.write(f"  {child.name}.{cls}\n")
    
    # Common news selectors
    for selector in [".news", ".post", ".article", ".card", ".list-item", ".entry", ".blog", ".content", "article", ".news-item"]:
        items = soup.select(selector)
        if items:
            f.write(f"\n{selector}: {len(items)} items\n")
    
    # Look for link groups
    f.write("\n=== LINK GROUPS ===\n")
    count = 0
    for tag in soup.find_all(["ul", "ol", "div", "section"]):
        links = [a for a in tag.find_all("a", href=True) 
                if a.get_text(strip=True) and a['href'] not in ('#', 'javascript:void(0)') and len(a.get_text(strip=True)) > 8]
        if 5 <= len(links) <= 50:
            count += 1
            cls = ".".join(tag.get("class", [])[:3])
            f.write(f"\n{tag.name}.{cls}: {len(links)} links\n")
            for a in links[:3]:
                f.write(f"  [{a.get_text(strip=True)[:100]}] -> {a['href']}\n")
            if count >= 15:
                break
    
    # Look for divs with repeating children of similar classes
    from collections import Counter
    f.write("\n=== REPEATING DIVS ===\n")
    for selector in ["div.row", "div.grid", "div.list", "div.items", "div.news-list", "div.card-deck"]:
        containers = soup.select(selector)
        for c in containers[:5]:
            children = [ch for ch in c.find_all(recursive=False) if ch.name]
            if 3 <= len(children) <= 30:
                cls = ".".join(c.get("class", [])[:3])
                child_classes = Counter()
                for ch in children:
                    child_classes[".".join(ch.get("class", [])[:2])] += 1
                f.write(f"\n{selector} '{cls}': {len(children)} children\n")
                for cc, cnt in child_classes.most_common(5):
                    f.write(f"  {cc}: {cnt}\n")
    
    # search h4, h3, h2 - news titles
    f.write("\n=== H4/H3/H2 SAMPLE ===\n")
    for tag_name in ["h4", "h3", "h2"]:
        tags = soup.find_all(tag_name)
        news_tags = [t for t in tags if t.find("a") and t.find("a").get("href") and "/news/" in t.find("a").get("href", "")]
        f.write(f"\n{tag_name} with /news/ link: {len(news_tags)}\n")
        if news_tags:
            parent_cls = Counter()
            for t in news_tags[:3]:
                a = t.find("a")
                f.write(f"  [{a.get_text(strip=True)[:100]}] -> {a['href']}\n")
                p = t.parent
                parent_cls[f"{p.name}.{'.'.join(p.get('class',[])[:3])}"] += 1
            f.write(f"  Parents: {parent_cls.most_common(3)}\n")
