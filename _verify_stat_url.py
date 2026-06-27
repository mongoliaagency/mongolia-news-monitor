"""确认 1212.mn 文章详情页 URL"""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

base = "https://www.1212.mn"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 尝试各种可能的文章 URL 模式
article_id = "102923438"
urls = [
    f"{base}/mn/about-us/news/{article_id}",
    f"{base}/mn/about-us/news/detail/{article_id}",
    f"{base}/mn/about-us/news/latest/{article_id}",
    f"{base}/api/articles/{article_id}",
]

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        print(f"{url}: {r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) < 500:
            print(f"  Content: {r.text[:300]}")
    except Exception as e:
        print(f"{url}: ERROR - {e}")

# 检查 RSC 中的页面链接
rsc_resp = requests.get(f"{base}/mn/about-us/news/latest", 
    headers={**headers, "RSC": "1", "Accept": "text/x-component",
             "Next-Url": "/mn/about-us/news/latest"}, 
    timeout=15, verify=False)
rsc_text = rsc_resp.text

# 在 RSC 中找链接
import re
links = re.findall(r'"([^"]*(?:news|articles|detail)[^"]*)"', rsc_text)
print(f"\n=== Links in RSC response ===")
for l in links[:20]:
    print(f"  {l}")

# 也在 JSON 中找 slug
import json
with open("_stat_api.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 检查 slug 是否用于构造 URL
for a in data['data'][:3]:
    print(f"\nid={a['id']}, slug={a.get('slug')}, news_type={a.get('news_type')}")
