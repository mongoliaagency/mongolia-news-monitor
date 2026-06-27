# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup

with open("_mocsty.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# 1. 寻找新闻列表容器
candidates = []
for tag in soup.find_all(["div", "section", "ul", "article", "main"]):
    links = tag.find_all("a", href=True)
    if len(links) >= 3:
        cls = tag.get("class", [])
        tid = tag.get("id", "")
        candidates.append((tag.name, tid, " ".join(cls), len(links)))

candidates.sort(key=lambda x: -x[3])
for c in candidates[:20]:
    print(f"[{c[0]}#{c[1]}.{c[2]}] links={c[3]}")

print("\n=== 寻找 a 标签模式 ===")
a_samples = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)
    if len(text) > 10 and ("news" in href.lower() or "/" in href):
        a_samples.append((text[:60], href[:80]))

for text, href in a_samples[:30]:
    print(f"  [{text}] -> {href}")

print("\n=== 寻找日期元素 ===")
for tag in soup.find_all(["time", "span", "div", "p"]):
    txt = tag.get_text(strip=True)
    if any(c.isdigit() for c in txt) and len(txt) >= 6 and len(txt) <= 30:
        cls = tag.get("class", [])
        print(f"  <{tag.name} class=\"{' '.join(cls)}\"> {txt[:60]}")
