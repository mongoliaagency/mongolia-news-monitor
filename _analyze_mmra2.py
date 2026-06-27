from lxml import html

with open("_mmra.html", "r", encoding="utf-8") as f:
    page = f.read()

tree = html.fromstring(page)

# Focus on div.blog.list-view > div.post items
posts = tree.cssselect("div.blog.list-view div.post")

with open("_mmra_analysis.txt", "w", encoding="utf-8") as out:
    out.write(f"=== 总共 post 条目: {len(posts)} ===\n\n")
    
    for i, post in enumerate(posts[:15]):
        out.write(f"\n--- Post {i} ---\n")
        out.write(f"HTML snippet:\n{html.tostring(post, encoding='unicode')[:800]}\n")
        
        # Title
        title_el = post.cssselect("h3.post-title a")
        if title_el:
            out.write(f"Title: {title_el[0].text_content().strip()}\n")
            out.write(f"Link: {title_el[0].get('href', '')}\n")
        
        # Date - look for various patterns
        text = post.text_content()
        out.write(f"Full text: {text[:500]}\n")
        
        # Check entry-meta, date classes
        for sel in [".entry-meta", ".post-meta", ".date", "[class*='date']", 
                    ".meta", ".posted-on", ".time", "small", "span"]:
            els = post.cssselect(sel)
            for el in els:
                t = el.text_content().strip()
                if t:
                    out.write(f"  {sel}: {t[:120]}\n")
