from bs4 import BeautifulSoup, Tag
import re

with open("_moh.html", "r", encoding="utf-8") as f:
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

# 找 class 含 news/post/card/item/entry/list 的元素
for cls_pat in ["news", "post", "card", "item", "entry", "list", "article", "blog", "row"]:
    elems = soup.find_all(class_=re.compile(cls_pat, re.I))
    if elems:
        p(f"\n=== class~{cls_pat}: {len(elems)} elems ===")
        for e in elems[:3]:
            tag = e.name
            cls = e.get("class", [])
            p(f"  <{tag} class={cls}> text: {e.get_text(strip=True)[:150]}")

# 找含 /news/ 的链接
links = soup.find_all("a", href=True)
news_links = [l for l in links if re.search(r'/news/', l["href"])]
p(f"\n=== /news/ links: {len(news_links)} ===")
for l in news_links[:15]:
    p(f"  {l['href']} -> {l.get_text(strip=True)[:100]}")

# 统计
for tag in ["div", "section", "article", "li", "a"]:
    p(f"\n<{tag}>: {len(soup.find_all(tag))}")

# 日期模式
for pat in [r'\d{4}\.\d{2}\.\d{2}', r'\d{4}-\d{2}-\d{2}', r'\d{4}/\d{2}/\d{2}', r'\d{4}\s+\d{2}\s+\d{2}']:
    matches = re.findall(pat, html)
    if matches:
        p(f"\nDate pattern '{pat}': {len(matches)} matches, first 5: {matches[:5]}")

# 找特定结构：看 class 含 news 的最外层容器
news_containers = soup.find_all(class_=re.compile(r'news', re.I))
p(f"\n=== news* containers: {len(news_containers)} ===")
for nc in news_containers[:3]:
    p(f"\n  <{nc.name} class={nc.get('class', [])}>")
    p(f"  {str(nc)[:800]}")

with open("_moh_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print("Done")
