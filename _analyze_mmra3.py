from lxml import html

with open("_mmra.html", "r", encoding="utf-8") as f:
    page = f.read()

tree = html.fromstring(page)

posts = tree.cssselect("div.blog.list-view div.post")

with open("_mmra_analysis.txt", "w", encoding="utf-8") as out:
    # Show full HTML of first post
    out.write("=== Post 0 FULL HTML ===\n")
    out.write(html.tostring(posts[0], encoding='unicode'))
    
    out.write("\n\n=== Post 1 FULL HTML ===\n")
    out.write(html.tostring(posts[1], encoding='unicode'))
