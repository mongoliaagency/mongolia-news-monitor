from lxml import html
import re

with open("_iaac.html", "r", encoding="utf-8") as f:
    page = f.read()

tree = html.fromstring(page)

with open("_iaac_analysis.txt", "w", encoding="utf-8") as out:
    # 1. News containers
    out.write("=== 常见新闻容器 ===\n")
    for sel in [".news-list", ".list-news", ".article-list", ".post", ".item", ".entry",
                "article", ".card", ".row", ".news-item", ".news_item",
                "[class*='news']", "[class*='list']", "[class*='article']", "[class*='post']",
                "table", "tr", "li", ".blog", ".content", ".page-content"]:
        els = tree.cssselect(sel)
        if els:
            out.write(f"\n{sel}: {len(els)} elements\n")

    # 2. Links
    out.write("\n\n=== href 模式统计 ===\n")
    href_patterns = {}
    for a in tree.cssselect("a[href]"):
        href = a.get("href", "")
        if "/news/" in href or "/post/" in href or "/article/" in href or "news" in href.lower():
            href_patterns[href] = href_patterns.get(href, 0) + 1
    for k, v in sorted(href_patterns.items(), key=lambda x: -x[1])[:30]:
        out.write(f"  {k}: {v}\n")

    # 3. Dates
    out.write("\n\n=== 日期模式 ===\n")
    text = tree.text_content()
    date_patterns = re.findall(r'\d{4}[./-]\d{2}[./-]\d{2}', text)
    if date_patterns:
        out.write(f"  Found {len(date_patterns)} dates, samples: {date_patterns[:10]}\n")

    # 4. All elements with class containing news/list/article/post
    out.write("\n\n=== 新闻相关class元素 ===\n")
    for el in tree.cssselect("[class]"):
        cls = el.get("class", "")
        if any(k in cls.lower() for k in ['news', 'list', 'item', 'article', 'post', 'blog']):
            tag = el.tag
            text = (el.text_content() or "").strip()[:150]
            if len(text) > 10:
                out.write(f"  <{tag} class=\"{cls}\"> {text}\n")

    # 5. Tables
    out.write("\n\n=== Table结构 ===\n")
    tables = tree.cssselect("table")
    for i, table in enumerate(tables):
        rows = table.cssselect("tr")
        out.write(f"\nTable {i}: {len(rows)} rows\n")
        for j, tr in enumerate(rows[:3]):
            tds = tr.cssselect("td, th")
            td_texts = [td.text_content().strip()[:60] for td in tds]
            out.write(f"  Row {j}: {td_texts}\n")

    out.write(f"\n\n=== 总元素数: {len(tree.cssselect('*'))} ===\n")
