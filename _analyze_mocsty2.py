# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup

with open("_mocsty.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# 找新闻列表区域
section = soup.find("section", id="recent-news")
if section:
    print("=== recent-news section 结构 (前2000字符) ===")
    print(str(section)[:3000])
else:
    print("未找到 section#recent-news")

# 找所有 /news/XXX 链接
print("\n=== /news/ 模式链接 ===")
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/news/" in href and not href.endswith((".pdf", ".xlsx")):
        # 找父元素看日期
        parent = a.parent
        for _ in range(4):
            if parent is None: break
            date_span = parent.find("span", class_="text-xs")
            if date_span:
                print(f"  标题: {a.get_text(strip=True)[:60]}")
                print(f"  链接: {href}")
                print(f"  日期: {date_span.get_text(strip=True)}")
                print(f"  父元素: {parent.name}.{' '.join(parent.get('class',[]))}")
                print()
                break
            parent = parent.parent

# 检查静态HTML中是否有新闻内容
print("\n=== 检查是否Js渲染 ===")
body_text = soup.get_text()
keywords = ["Соёл", "спорт", "залуучууд"]
for kw in keywords:
    count = body_text.count(kw)
    print(f"  '{kw}': {count} 次")

# 检查是否有 <div class="grid grid-cols-3 gap-14 mt-10">
grid = soup.find("div", class_="grid")
if grid:
    print(f"\n=== grid 子元素数: {len(grid.find_all(recursive=False))} ===")
    for child in grid.find_all(recursive=False)[:3]:
        print(f"  {child.name}.{' '.join(child.get('class',[]))}")
        print(f"  {child.get_text(strip=True)[:100]}")
        print()
