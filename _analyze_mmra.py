from lxml import html
import re

with open("_mmra.html", "r", encoding="utf-8") as f:
    page = f.read()

tree = html.fromstring(page)

# Print structure summary
with open("_mmra_analysis.txt", "w", encoding="utf-8") as out:
    # 1. Look for news list containers
    out.write("=== 常见新闻容器 ===\n")
    for sel in [".news-list", ".list-news", ".article-list", ".post", ".item", ".entry",
                "article", ".card", ".row", ".col", ".news-item", ".news_item",
                "[class*='news']", "[class*='list']", "[class*='article']", "[class*='post']",
                "table", "tr", "li"]:
        els = tree.cssselect(sel)
        if els:
            out.write(f"\n{sel}: {len(els)} elements\n")

    # 2. Look for links with potential news patterns
    out.write("\n\n=== 链接模式 ===\n")
    links = tree.cssselect("a[href]")
    for a in links[:50]:
        href = a.get("href", "")
        text = (a.text_content() or "").strip()
        if len(text) > 10:
            out.write(f"  [{href}] {text[:100]}\n")

    # 3. All <a> href patterns
    out.write("\n\n=== href 模式统计 ===\n")
    href_patterns = {}
    for a in links:
        href = a.get("href", "")
        if href.startswith("/"):
            prefix = "/" + href.split("/")[1] if len(href.split("/")) > 1 else "/"
        elif "?" in href:
            prefix = href.split("?")[0]
        else:
            prefix = href[:30]
        href_patterns[prefix] = href_patterns.get(prefix, 0) + 1
    for k, v in sorted(href_patterns.items(), key=lambda x: -x[1])[:20]:
        out.write(f"  {k}: {v}\n")

    # 4. Look for date patterns
    out.write("\n\n=== 日期模式 ===\n")
    text = tree.text_content()
    date_patterns = re.findall(r'\d{4}[./-]\d{2}[./-]\d{2}', text)
    if date_patterns:
        out.write(f"  Found {len(date_patterns)} dates, samples: {date_patterns[:10]}\n")

    # 5. All div/li with class containing 'news' or 'list' or 'item' or 'article'
    out.write("\n\n=== 新闻相关class元素 ===\n")
    for el in tree.cssselect("[class]"):
        cls = el.get("class", "")
        if any(k in cls.lower() for k in ['news', 'list', 'item', 'article', 'post']):
            tag = el.tag
            text = (el.text_content() or "").strip()[:120]
            if len(text) > 10:
                out.write(f"  <{tag} class=\"{cls}\"> {text}\n")

    # 6. Tables
    out.write("\n\n=== Table结构 ===\n")
    tables = tree.cssselect("table")
    for i, table in enumerate(tables):
        rows = table.cssselect("tr")
        out.write(f"\nTable {i}: {len(rows)} rows\n")
        for j, tr in enumerate(rows[:5]):
            tds = tr.cssselect("td, th")
            td_texts = [td.text_content().strip()[:60] for td in tds]
            out.write(f"  Row {j}: {td_texts}\n")

    out.write(f"\n\n=== 总元素数: {len(tree.cssselect('*'))} ===\n")
