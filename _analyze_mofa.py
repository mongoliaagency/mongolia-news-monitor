# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

with open("_mofa.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

lines = []

# 候选容器
candidates = []
for tag in soup.find_all(["div", "section", "ul", "article", "main", "table", "tbody"]):
    links = tag.find_all("a", href=True)
    if len(links) >= 2:
        cls = tag.get("class", [])
        tid = tag.get("id", "")
        candidates.append((tag.name, tid, " ".join(cls), len(links)))

candidates.sort(key=lambda x: -x[3])
lines.append("=== 候选容器 ===")
for c in candidates[:15]:
    lines.append(f"  [{c[0]}#{c[1]}.{c[2]}] links={c[3]}")

# 新闻链接
lines.append("")
lines.append("=== 新闻链接 ===")
for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)
    if len(text) > 10 and "/news/" in href and not href.endswith((".pdf", ".xlsx", ".jpg", ".png")):
        lines.append(f"  [{text[:60]}] -> {href}")

# 日期
lines.append("")
lines.append("=== 日期元素 ===")
seen = set()
for tag in soup.find_all(["time", "span", "div", "p", "td"]):
    txt = tag.get_text(strip=True)
    if any(c.isdigit() for c in txt) and 6 <= len(txt) <= 20:
        cls = " ".join(tag.get("class", []))
        key = f"<{tag.name} class=\"{cls}\"> {txt[:40]}"
        if key not in seen:
            seen.add(key)
            lines.append(f"  {key}")

# 页面概览
lines.append("")
lines.append(f"=== 页面字符数: {len(soup.get_text())} ===")
lines.append(f"  body: {str(soup.body)[:2000] if soup.body else 'no body'}")

with open("_mofa_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
