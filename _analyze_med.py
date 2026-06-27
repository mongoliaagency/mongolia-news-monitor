from bs4 import BeautifulSoup, Tag
import re

with open("_med.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

out_lines = []

def p(s=""):
    out_lines.append(s)

p("=== TITLE ===")
p(soup.title.text.strip() if soup.title else "NO TITLE")

# 找所有 article
articles = soup.find_all("article")
p(f"\n=== ARTICLE tags: {len(articles)} ===")
for i, a in enumerate(articles[:3]):
    p(f"\n--- article #{i} ---")
    p(str(a)[:1000])

# 找 class 含 news/post/card/item/entry/list 的元素
for cls_pat in ["news", "post", "card", "item", "entry", "list", "article", "blog"]:
    elems = soup.find_all(class_=re.compile(cls_pat, re.I))
    if elems:
        p(f"\n=== class~{cls_pat}: {len(elems)} elems ===")
        for e in elems[:3]:
            tag = e.name
            cls = e.get("class", [])
            p(f"  <{tag} class={cls}> text: {e.get_text(strip=True)[:150]}")

# 找含 posts/ 的链接
links = soup.find_all("a", href=True)
post_links = [l for l in links if re.search(r'/posts/', l["href"])]
p(f"\n=== /posts/ links: {len(post_links)} ===")
for l in post_links[:15]:
    p(f"  {l['href']} -> {l.get_text(strip=True)[:100]}")

# 统计
for tag in ["div", "section", "article", "li", "a"]:
    p(f"\n<{tag}>: {len(soup.find_all(tag))}")

# 深度分析 article 内部
def walk(el, depth=0):
    if depth > 5:
        return
    for child in el.children:
        if not isinstance(child, Tag):
            continue
        tag = child.name
        cls = ".".join(child.get("class", [])) if child.get("class") else ""
        text = child.get_text(strip=True)[:120]
        indent = "  " * depth
        p(f"{indent}<{tag} class='{cls}'> {text}")
        if tag == "a" and child.get("href"):
            p(f"{indent}  href={child['href']}")
        if tag in ("div", "header", "footer", "section", "li"):
            walk(child, depth + 1)

if articles:
    p("\n=== First article detailed ===")
    walk(articles[0])

# 日期模式
for pat in [r'\d{4}\.\d{2}\.\d{2}', r'\d{4}-\d{2}-\d{2}', r'\d{4}/\d{2}/\d{2}', r'\d{4}\s+\d{2}\s+\d{2}']:
    matches = re.findall(pat, html)
    if matches:
        p(f"\nDate pattern '{pat}': {len(matches)} matches, first 5: {matches[:5]}")

with open("_med_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print("Done")
