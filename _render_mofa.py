# -*- coding: utf-8 -*-
"""用 requests + 分析 XHR 请求找到 mofa API"""
import requests, re, json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://mofa.gov.mn/news/time",
}

lines = []

# 尝试各种可能的 API URL 模式
apis = [
    # 常见的蒙古政府网站 API 模式
    ("https://mofa.gov.mn/api/saContent/list", {"limit": 20, "type": "TIME"}),
    ("https://mofa.gov.mn/api/news", {"limit": 20, "category": "time"}),
    ("https://mofa.gov.mn/api/news/list", {"limit": 20}),
    ("https://mofa.gov.mn/api/content", {"limit": 20, "type": "TIME"}),
    ("https://mofa.gov.mn/api/article/list", {"limit": 20, "category": "TIME"}),
    # 带端口
    ("https://mofa.gov.mn:8085/saContent/list", {"limit": 20}),
    # 直接路径
    ("https://mofa.gov.mn/api/v1/news", {"limit": 20}),
    ("https://mofa.gov.mn/api/v1/content/list", {"limit": 20}),
]

for api_url, params in apis:
    try:
        r = requests.get(api_url, params=params, headers=headers, timeout=15)
        lines.append(f"{api_url}?{params}: {r.status_code} {len(r.text)} chars")
        if r.status_code == 200 and len(r.text) > 50:
            lines.append(f"  Content-Type: {r.headers.get('Content-Type', '')}")
            lines.append(f"  {r.text[:600]}")
    except Exception as e:
        lines.append(f"{api_url}?{params}: ERROR {str(e)[:80]}")

# 也试 POST
post_apis = [
    ("https://mofa.gov.mn/api/saContent/list", {"limit": 20, "type": "TIME", "page": 1}),
    ("https://mofa.gov.mn/api/news", {"limit": 20, "category": "time", "page": 1}),
]
lines.append("")
lines.append("=== POST 尝试 ===")
for api_url, data in post_apis:
    try:
        r = requests.post(api_url, json=data, headers=headers, timeout=15)
        lines.append(f"POST {api_url}: {r.status_code} {len(r.text)} chars")
        if r.status_code == 200 and len(r.text) > 50:
            lines.append(f"  {r.text[:600]}")
    except Exception as e:
        lines.append(f"POST {api_url}: ERROR {str(e)[:80]}")

with open("_mofa_api.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
