"""通过 Next.js RSC 协议获取 1212.mn 新闻数据"""
import requests, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

base = "https://www.1212.mn"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/x-component",
    "Next-Router-State-Tree": "%5B%22%22%2C%7B%22children%22%3A%5B%22mn%22%2C%7B%22children%22%3A%5B%22about-us%22%2C%7B%22children%22%3A%5B%22news%22%2C%7B%22children%22%3A%5B%22latest%22%2C%7B%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D",
    "Next-Url": "/mn/about-us/news/latest",
    "RSC": "1",
}

# Try RSC fetch
resp = requests.get(f"{base}/mn/about-us/news/latest", headers=headers, timeout=30, verify=False)
resp.encoding = 'utf-8'

with open("_stat_rsc.txt", "w", encoding="utf-8") as f:
    f.write(resp.text)

print(f"Status: {resp.status_code}")
print(f"Length: {len(resp.text)}")
print(f"\nFirst 2000 chars:")
print(resp.text[:2000])

# 尝试 API endpoint
print("\n\n=== Trying API endpoints ===")
api_urls = [
    f"{base}/api/news",
    f"{base}/api/news/latest",
    f"{base}/api/articles",
    f"{base}/mn/api/news",
]
for api_url in api_urls:
    try:
        r = requests.get(api_url, headers={"User-Agent": headers["User-Agent"]}, timeout=15, verify=False)
        print(f"{api_url}: {r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 50:
            print(f"  First 500: {r.text[:500]}")
    except Exception as e:
        print(f"{api_url}: ERROR - {e}")
