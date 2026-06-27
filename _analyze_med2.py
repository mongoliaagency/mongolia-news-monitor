from bs4 import BeautifulSoup, Tag
import re

with open("_med.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

out_lines = []
def p(s=""):
    out_lines.append(s)

# 找所有 .entry.post-list-item
items = soup.select(".entry.post-list-item")
p(f"=== .entry.post-list-item: {len(items)} ===\n")

for i, item in enumerate(items[:5]):
    p(f"--- Item #{i+1} ---")
    p(str(item)[:1500])
    p("")

# 深入分析第一个 item 内部结构
if items:
    p("=== First item walk ===")
    def walk(el, depth=0):
        if depth > 5:
            return
        for child in el.children:
            if not isinstance(child, Tag):
                continue
            tag = child.name
            cls = ".".join(child.get("class", [])) if child.get("class") else ""
            text = child.get_text(strip=True)[:150]
            indent = "  " * depth
            p(f"{indent}<{tag} class='{cls}'> {text}")
            if tag == "a" and child.get("href"):
                p(f"{indent}  href={child['href']}")
            if tag in ("div", "header", "ul", "li"):
                walk(child, depth + 1)
    walk(items[0])

# 查找含 /post/ 的链接
links = soup.find_all("a", href=True)
post_links = [l for l in links if re.search(r'/post/', l["href"])]
p(f"\n=== /post/ links: {len(post_links)} ===")
for l in post_links[:15]:
    p(f"  {l['href']} -> {l.get_text(strip=True)[:100]}")

# 找日期模式周边文本
dates_html = re.findall(r'\d{4}-\d{2}-\d{2}', html)
p(f"\nDate YYYY-MM-DD matches: {len(dates_html)}, first 10: {dates_html[:10]}")

# 查看 entry-meta 相关
metas = soup.select(".entry-meta, .post-date, .entry-date, time")
p(f"\n=== Date-related elements: {len(metas)} ===")
for m in metas[:10]:
    p(f"  <{m.name} class={m.get('class', [])}> {m.get_text(strip=True)[:100]}")

# 看是否有分页
pagers = soup.select(".pagination, .page-numbers, .pager")
p(f"\n=== Pagination elements: {len(pagers)} ===")
for pg in pagers[:3]:
    p(str(pg)[:500])

with open("_med_analysis2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print("Done")
