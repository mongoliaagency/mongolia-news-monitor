# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

with open("_mcud.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# 寻找新闻列表容器
candidates = []
for tag in soup.find_all(["div", "section", "ul", "article", "main"]):
    links = tag.find_all("a", href=True)
    if len(links) >= 3:
        cls = tag.get("class", [])
        tid = tag.get("id", "")
        candidates.append((tag.name, tid, " ".join(cls), len(links)))

candidates.sort(key=lambda x: -x[3])
lines = ["=== 候选容器 ===\n"]
for c in candidates[:15]:
    lines.append(f"  [{c[0]}#{c[1]}.{c[2]}] links={c[3]}")

# 找 /as/news/ 或 /news/ 链接模式
lines.append("")
lines.append("=== 新闻链接模式 ===")
news_links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)
    if len(text) > 10 and ("/news" in href.lower() or "/as/" in href.lower()):
        if not href.endswith((".pdf", ".xlsx", ".jpg", ".png")):
            news_links.append((text[:60], href[:80]))

for text, href in news_links[:30]:
    lines.append(f"  [{text}] -> {href}")

# 寻找日期元素
lines.append("")
lines.append("=== 日期元素 ===")
seen = set()
for tag in soup.find_all(["time", "span", "div", "p"]):
    txt = tag.get_text(strip=True)
    if any(c.isdigit() for c in txt) and 6 <= len(txt) <= 30:
        cls = " ".join(tag.get("class", []))
        key = f"<{tag.name} class=\"{cls}\"> {txt[:40]}"
        if key not in seen:
            seen.add(key)
            lines.append(f"  {key}")

# 检查是否是 JS 渲染
lines.append("")
lines.append("=== 静态内容检查 ===")
body = soup.get_text()
for kw in ["Мэдээ", "шийдвэр", "барилга"]:
    lines.append(f"  '{kw}': {body.count(kw)} 次")

with open("_mcud_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
