# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

with open("_mcud.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

items = soup.select("#listTarget > div")
lines = [f"找到 {len(items)} 个项目\n"]
count = 0
for item in items:
    title_el = item.select_one(".article-list-item__name")
    if not title_el: continue
    title = title_el.get_text(strip=True)
    if not title: continue
    link_el = item.select_one("a.video-list-item")
    link = link_el.get("href", "") if link_el else ""
    date_el = item.select_one(".video-list-item__published")
    date_text = date_el.get_text(strip=True) if date_el else "无日期"
    count += 1
    lines.append(f"  [{count}] {date_text} | {title[:60]}")
    lines.append(f"       链接: https://mcud.gov.mn{link}\n")

lines.append(f"有效新闻: {count} 条")

with open("_verify_mcud.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
