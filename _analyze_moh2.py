from bs4 import BeautifulSoup, Tag
import re

with open("_moh.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

out_lines = []
def p(s=""):
    out_lines.append(s)

# 找 .standart-news-listpage 下的所有 .row.clearfix
container = soup.select_one(".standart-news-listpage")
if container:
    rows = container.select(".row.clearfix")
    p(f"=== .row.clearfix in news list: {len(rows)} ===\n")

    for i, row in enumerate(rows[:3]):
        p(f"--- Row #{i+1} ---")
        p(str(row)[:1200])
        p("")

    # 详细走第一个
    if rows:
        p("=== First row detailed walk ===")
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
                if tag in ("div", "header", "ul", "li", "h4"):
                    walk(child, depth + 1)
        walk(rows[0])

# 查看所有 /news/ 数字链接
news_detail_links = soup.find_all("a", href=re.compile(r'/news/\d+'))
p(f"\n=== /news/NNN links: {len(news_detail_links)} ===")
for l in news_detail_links[:15]:
    p(f"  {l['href']} -> {l.get_text(strip=True)[:120]}")

# 日期：找 2026-06-26 05:00:00 这类
datetime_pattern = r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}'
dt_matches = re.findall(datetime_pattern, html)
p(f"\nDatetime matches: {len(dt_matches)}, first 10: {dt_matches[:10]}")

# 看日期在 row 内的位置
if rows:
    row_html = str(rows[0])
    dt_in_row = re.findall(datetime_pattern, row_html)
    p(f"\nDatetime in first row: {dt_in_row}")

    # 搜索日期前后的上下文
    for m in re.finditer(datetime_pattern, row_html):
        start = max(0, m.start()-50)
        end = min(len(row_html), m.end()+50)
        p(f"  Context: ...{row_html[start:end]}...")

with open("_moh_analysis2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print("Done")
