"""深入分析 mongolbank.mn 新闻条目结构"""
import re, sys
from lxml import html
sys.stdout.reconfigure(encoding='utf-8')

with open("_bank_page.html", "r", encoding="utf-8") as f:
    content = f.read()

tree = html.fromstring(content)

# 找新闻容器
news_items = tree.cssselect('div.row.home-news1.my-3')
print(f"Found {len(news_items)} news items")

output_lines = []
for i, item in enumerate(news_items):
    output_lines.append(f"\n{'='*60}")
    output_lines.append(f"ITEM {i+1}")
    output_lines.append(f"{'='*60}")
    
    # 日期部分
    year_el = item.cssselect('.home-news1-year')
    month_el = item.cssselect('.home-news1-month')
    day_el = item.cssselect('.home-news1-day')
    year = year_el[0].text_content().strip() if year_el else ''
    month = month_el[0].text_content().strip() if month_el else ''
    day = day_el[0].text_content().strip() if day_el else ''
    output_lines.append(f"Date: {year}-{month}-{day}")
    
    # 标题和链接
    links = item.cssselect('a[href]')
    for a in links:
        href = a.get('href', '')
        text = a.text_content().strip()
        if text and len(text) > 5:
            output_lines.append(f"Link: {href}")
            output_lines.append(f"Text: {text[:150]}")
    
    # 类别
    cat_el = item.cssselect('.home-news1-cat')
    if cat_el:
        output_lines.append(f"Category: {cat_el[0].text_content().strip()[:100]}")

    # 完整 HTML
    raw_html = html.tostring(item, encoding='unicode')
    output_lines.append(f"\nFull HTML ({len(raw_html)} chars):")
    output_lines.append(raw_html[:800])

with open("_bank_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print("Done")
