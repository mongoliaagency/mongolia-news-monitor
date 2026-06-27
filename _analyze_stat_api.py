"""深入分析 1212.mn /api/articles API"""
import requests, sys, json
sys.stdout.reconfigure(encoding='utf-8')

base = "https://www.1212.mn"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 获取完整 articles
resp = requests.get(f"{base}/api/articles", headers=headers, timeout=30, verify=False)
data = resp.json()

print(f"Status: {resp.status_code}")
print(f"Status field: {data.get('status')}")
print(f"Total articles: {len(data.get('data', []))}")

articles = data.get('data', [])

with open("_stat_api.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 分析前3条
print("\n=== First 3 articles ===")
for i, a in enumerate(articles[:3]):
    print(f"\n--- Article {i+1} ---")
    for k, v in a.items():
        if isinstance(v, str) and len(v) > 200:
            v = v[:200] + "..."
        print(f"  {k}: {v}")

# 找日期字段
print("\n=== All keys in first article ===")
if articles:
    print(list(articles[0].keys()))

# 分页信息
print(f"\n=== Pagination info ===")
for k in data:
    if k != 'data':
        print(f"  {k}: {data[k]}")
