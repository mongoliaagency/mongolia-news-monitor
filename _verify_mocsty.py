# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

with open("_mocsty.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

items_selector = ".grid.grid-cols-3 article"
title_selector = "h4.article-title"
link_selector = "a[href^=\"/news/\"]"
date_selector = "span.text-xs"

items = soup.select(items_selector)
lines = [f"选择器: {items_selector}", f"找到 {len(items)} 个 article 元素\n"]
count = 0
for item in items:
    title_el = item.select_one(title_selector)
    if not title_el: continue
    title = title_el.get_text(strip=True)
    if not title: continue
    link_el = item.select_one(link_selector)
    link = link_el.get("href", "") if link_el else ""
    date_el = item.select_one(date_selector)
    date_text = date_el.get_text(strip=True) if date_el else "无日期"
    count += 1
    lines.append(f"  [{count}] {date_text} | {title[:60]}")
    lines.append(f"       链接: https://mocsty.gov.mn{link}\n")

lines.append(f"有效新闻: {count} 条")

with open("_verify_mocsty.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done, check _verify_mocsty.txt")
