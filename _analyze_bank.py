"""分析 mongolbank.mn 页面结构"""
import re, sys
from lxml import html
sys.stdout.reconfigure(encoding='utf-8')

with open("_bank_page.html", "r", encoding="utf-8") as f:
    content = f.read()

tree = html.fromstring(content)

# 1. 找新闻相关容器
lines = []
for tag in ['ul', 'div', 'section', 'article']:
    elems = tree.cssselect(tag)
    for e in elems:
        cls = e.get('class', '')
        if any(kw in cls.lower() for kw in ['news', 'article', 'post', 'blog', 'list', 'item', 'press', 'release', 'announce']):
            child_count = len(e.cssselect('*'))
            link_count = len(e.cssselect('a'))
            lines.append(f"<{tag} class='{cls}'> children:{child_count}, links:{link_count}")

# 2. 找 class 分布
class_counts = {}
for e in tree.iter():
    cls = e.get('class', '')
    if cls:
        class_counts[cls] = class_counts.get(cls, 0) + 1

# 3. 找看起来像新闻链接的
links = tree.cssselect('a[href]')
news_links = []
for a in links:
    href = a.get('href', '')
    text = (a.text_content() or '').strip()
    if href and len(text) > 15 and not href.startswith('#') and not href.startswith('javascript'):
        if any(kw in href.lower() for kw in ['news', 'article', 'press', 'release', 'detail', 'post', 'announce']):
            news_links.append((href, text[:100]))

with open("_bank_analysis.txt", "w", encoding="utf-8") as f:
    f.write("=== Possible news containers ===\n")
    f.write("\n".join(lines))
    f.write(f"\n\n=== Total <a> tags: {len(links)}\n")
    f.write(f"=== News-related links: {len(news_links)}\n")
    for href, text in news_links[:30]:
        f.write(f"  {href} | {text}\n")
    f.write("\n=== Top class names ===\n")
    for cls, cnt in sorted(class_counts.items(), key=lambda x: -x[1])[:30]:
        f.write(f"  {cls}: {cnt}\n")

print("Done. See _bank_analysis.txt")
