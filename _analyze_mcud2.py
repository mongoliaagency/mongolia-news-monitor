# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

with open("_mcud.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

lines = []

# 分析 card__body card_body__stories 结构
stories = soup.find("div", class_="card_body__stories")
if stories:
    lines.append(f"=== card_body__stories 子元素: {len(list(stories.children))} ===\n")
    for child in stories.find_all(recursive=False)[:3]:
        lines.append(f"  <{child.name} class=\"{' '.join(child.get('class',[]))}\">")
        lines.append(f"  {str(child)[:500]}")
        lines.append("")
else:
    lines.append("未找到 card_body__stories")

# 找所有 card 内的链接
lines.append("=== card 内链接 ===")
cards = soup.find_all("div", class_="card")
for card in cards[:3]:
    for a in card.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if len(text) > 5:
            lines.append(f"  [{text[:50]}] -> {href}")
    lines.append("  ---")

# 寻找主要新闻列表区的直接结构
lines.append("=== uk-width-2-3 主内容区 ===")
main_area = soup.select_one(".uk-width-2-3\\@m")
if main_area:
    lines.append(str(main_area)[:3000])

with open("_mcud_analysis2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
