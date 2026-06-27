"""下载 1212.mn 新闻列表页面"""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.1212.mn/mn/about-us/news/latest"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

resp = requests.get(url, headers=headers, timeout=30, verify=False)
resp.encoding = 'utf-8'

with open("_stat_news.html", "w", encoding="utf-8") as f:
    f.write(resp.text)

print(f"Status: {resp.status_code}")
print(f"Length: {len(resp.text)}")

# 快速找关键结构
import re
# 找 RSC payload 或 news items
if '__NEXT_DATA__' in resp.text:
    print("Found __NEXT_DATA__")
if 'rsc' in resp.text[:500]:
    print("RSC response")
# 找所有链接
links = re.findall(r'href="([^"]+)"', resp.text)
news_links = [l for l in links if '/news/' in l or '/about-us/' in l]
print(f"\nNews-related links: {news_links[:20]}")
