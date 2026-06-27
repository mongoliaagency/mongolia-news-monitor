from lxml import html

with open("_iaac.html", "r", encoding="utf-8") as f:
    page = f.read()

tree = html.fromstring(page)

# blog_box items
boxes = tree.cssselect("div.blog_box.type_two")

with open("_iaac_analysis.txt", "w", encoding="utf-8") as out:
    out.write(f"=== blog_box count: {len(boxes)} ===\n\n")
    
    # Show first 3 full HTML
    for i, box in enumerate(boxes[:3]):
        out.write(f"\n--- Box {i} FULL HTML ---\n")
        out.write(html.tostring(box, encoding='unicode'))
        out.write("\n")
        
    # Also check blog_inner
    inners = tree.cssselect("div.blog_inner")
    out.write(f"\n=== blog_inner count: {len(inners)} ===\n")
    for i, inner in enumerate(inners[:2]):
        out.write(f"\n--- Inner {i} FULL HTML ---\n")
        out.write(html.tostring(inner, encoding='unicode'))
        out.write("\n")
