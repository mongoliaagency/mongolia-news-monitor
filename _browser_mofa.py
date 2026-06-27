# -*- coding: utf-8 -*-
"""用 seleniumwire 或直接监控网络请求找到 API"""
# 先尝试用 requests + 模拟 GraphQL 或 REST 模式

import requests, json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://mofa.gov.mn/news/time",
    "Origin": "https://mofa.gov.mn",
}

lines = []

# 尝试常见的 Next.js API routes 模式
# mofa.gov.mn 的 API 模式
api_base = "https://mofa.gov.mn/api"

# 尝试各种 path
paths = [
    "/saContent/list",
    "/content/list", 
    "/news/list",
    "/article/list",
    "/sa/list",
    "/list",
    "/saNews/list",
    "/saContent/news/list",
    "/content/news/list",
]

for path in paths:
    url = f"{api_base}{path}"
    # GET with params
    for params in [
        {"limit": 20},
        {"limit": 20, "type": "TIME"},
        {"limit": 20, "currentPage": 1, "pageSize": 6},
        {"limit": 20, "page": 1, "pageSize": 6},
        {"type": "TIME", "page": 1, "limit": 6},
    ]:
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
            if r.status_code == 200 and len(r.text) > 100:
                lines.append(f"GET {url}?{params}")
                lines.append(f"  STATUS: {r.status_code} SIZE: {len(r.text)}")
                lines.append(f"  {r.text[:400]}")
                lines.append("")
        except:
            pass
        
        # POST
        try:
            r = requests.post(url, json=params, headers=headers, timeout=10)
            if r.status_code == 200 and len(r.text) > 100:
                lines.append(f"POST {url} {params}")
                lines.append(f"  STATUS: {r.status_code} SIZE: {len(r.text)}")
                lines.append(f"  {r.text[:400]}")
                lines.append("")
        except:
            pass

# 也试试不带 /api 前缀
for path in paths:
    url = f"https://mofa.gov.mn{path}"
    try:
        r = requests.get(url, params={"limit": 20}, headers=headers, timeout=10)
        if r.status_code == 200 and len(r.text) > 100:
            lines.append(f"DIRECT GET {url}: {r.status_code} {len(r.text)}")
            lines.append(f"  {r.text[:400]}")
            lines.append("")
    except:
        pass

with open("_mofa_api_final.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
