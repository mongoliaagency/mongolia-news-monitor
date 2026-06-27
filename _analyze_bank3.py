"""验证 mongolbank.mn 日期文本组合"""
import re, sys
from lxml import html
sys.stdout.reconfigure(encoding='utf-8')

with open("_bank_page.html", "r", encoding="utf-8") as f:
    content = f.read()

tree = html.fromstring(content)

items = tree.cssselect('div.row.home-news1.my-3')
for i, item in enumerate(items):
    date_div = item.cssselect('.home-news1-date')
    if date_div:
        full_text = date_div[0].text_content().strip()
        # clean up whitespace
        full_text = re.sub(r'\s+', ' ', full_text)
        print(f"[{i+1}] date text: '{full_text}'")
    
    title_a = item.cssselect('h5.home-news1-title a')
    if title_a:
        print(f"    title: {title_a[0].text_content().strip()[:80]}")
        print(f"    link: {title_a[0].get('href')}")
    print()
