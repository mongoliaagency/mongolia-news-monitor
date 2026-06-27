"""分析 1212.mn/mn 页面结构"""
from lxml import html
import re

with open("_stat_page.html", "r", encoding="utf-8") as f:
    content = f.read()

tree = html.fromstring(content)

# 输出关键结构
lines = []

# 1. 找出所有可能的新闻容器
for tag in ['ul', 'div', 'section', 'article']:
    elems = tree.cssselect(tag)
    for e in elems:
        cls = e.get('class', '')
        if any(kw in cls.lower() for kw in ['news', 'article', 'post', 'blog', 'list', 'item', 'content']):
            child_count = len(e.cssselect('*'))
            link_count = len(e.cssselect('a'))
            lines.append(f"Possible container: <{tag} class='{cls}'> - children:{child_count}, links:{link_count}")

# 2. 找所有 a 标签的 pattern
links = tree.cssselect('a[href]')
lines.append(f"\nTotal <a> tags: {len(links)}")
# 找看起来像新闻链接的
news_links = []
for a in links:
    href = a.get('href', '')
    text = (a.text_content() or '').strip()
    if href and len(text) > 10 and not href.startswith('#') and not href.startswith('javascript'):
        news_links.append((href, text[:80]))

lines.append(f"Links with >10 char text: {len(news_links)}")
lines.append("\n--- First 30 candidate links ---")
for href, text in news_links[:30]:
    lines.append(f"  {href} | {text}")

# 3. 找 class 名分布
class_counts = {}
for e in tree.iter():
    cls = e.get('class', '')
    if cls:
        class_counts[cls] = class_counts.get(cls, 0) + 1

lines.append("\n--- Top class names ---")
for cls, cnt in sorted(class_counts.items(), key=lambda x: -x[1])[:30]:
    lines.append(f"  {cls}: {cnt}")

with open("_stat_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Done. See _stat_analysis.txt")
