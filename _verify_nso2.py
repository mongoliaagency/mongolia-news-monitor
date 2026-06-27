"""验证统计局 API - 不过滤日期"""
import sys, json, requests
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'scripts')
from date_utils import parse_date, format_date

resp = requests.get("https://www.1212.mn/api/articles", 
    headers={"User-Agent": "Mozilla/5.0"}, verify=False)
data = resp.json()
articles = data.get('data', [])

print(f"Total articles: {len(articles)}")
print(f"Pagination: {data.get('pagination')}")

for i, a in enumerate(articles):
    title = a.get('name', '')
    pub_date = a.get('published_date', '')
    dt = parse_date(pub_date)
    print(f"  [{i+1}] {dt.date() if dt else '???'} | {title[:80]}")

# 检查是否有今天的文章
from datetime import datetime
today = datetime.now().date()
today_articles = [a for a in articles if parse_date(a.get('published_date', '')) and parse_date(a.get('published_date', '')).date() == today]
print(f"\nToday's articles ({today}): {len(today_articles)}")
