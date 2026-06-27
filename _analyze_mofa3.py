# -*- coding: utf-8 -*-
import re
with open("_mofa.html", "r", encoding="utf-8") as f:
    html = f.read()

lines = []
# 搜索 JS 文件中的 API 路径
for m in re.finditer(r'["\']([^"\']*api[^"\']*)["\']', html):
    lines.append(f"  API: {m.group(1)[:120]}")
for m in re.finditer(r'["\']([^"\']*list[^"\']*)["\']', html):
    lines.append(f"  LIST: {m.group(1)[:120]}")
for m in re.finditer(r'(/_next/[^"\']*)', html):
    lines.append(f"  NEXT: {m.group(1)[:120]}")
for m in re.finditer(r'(https?://[^\s"\'<>]+)', html):
    url = m.group(1)
    if any(kw in url.lower() for kw in ['api', 'content', 'news', 'mofa.gov']):
        lines.append(f"  URL: {url[:120]}")

# 搜索 fetch/axios 调用
for m in re.finditer(r'(fetch|axios|get)\s*\([^)]+', html):
    lines.append(f"  REQ: {m.group(0)[:120]}")

# 尝试直接访问可能的 API
lines.append("")
lines.append("=== 尝试直接 API ===")
import requests
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
apis = [
    "https://mofa.gov.mn/api/news/list",
    "https://mofa.gov.mn/api/content/list",
    "https://mofa.gov.mn/api/news?limit=20",
    "https://api.mofa.gov.mn/news/list",
]
for api in apis:
    try:
        r = requests.get(api, headers=headers, timeout=10)
        lines.append(f"  {api}: {r.status_code} {len(r.text)} chars")
        if r.status_code == 200:
            lines.append(f"  {r.text[:500]}")
    except Exception as e:
        lines.append(f"  {api}: ERROR {e}")

with open("_mofa_analysis3.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
