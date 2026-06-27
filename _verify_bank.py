"""验证央行抓取"""
import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'scripts')
from html_fetcher import fetch_html
from date_utils import parse_date
import requests
from lxml import html

output_lines = []

result = fetch_html("config/sources/mongolbank_mn.json")
output_lines.append(f"Total articles (today only): {len(result)}")
for i, item in enumerate(result):
    output_lines.append(f"\n--- Article {i+1} ---")
    for k, v in item.items():
        output_lines.append(f"  {k}: {v}")

resp = requests.get("https://www.mongolbank.mn/mn/", headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
resp.encoding = resp.apparent_encoding
tree = html.fromstring(resp.text)
items = tree.cssselect('div.row.home-news1.my-3')

output_lines.append(f"\n=== All articles on page ({len(items)}) ===")
for i, item in enumerate(items):
    date_div = item.cssselect('.home-news1-date')
    title_a = item.cssselect('h5.home-news1-title a')
    date_text = ''
    title = ''
    if date_div:
        date_text = re.sub(r'\s+', ' ', date_div[0].text_content().strip())
        dt = parse_date(date_text)
        date_text = f"{date_text} -> {dt.date() if dt else 'FAIL'}"
    if title_a:
        title = title_a[0].text_content().strip()
    output_lines.append(f"  [{i+1}] {date_text}")
    output_lines.append(f"       {title[:100]}")

with open("_bank_verify.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print("Done. See _bank_verify.txt")
