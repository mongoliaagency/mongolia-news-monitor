# -*- coding: utf-8 -*-
"""下载更多 JS chunk 找到 API endpoint"""
import requests, re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 从 HTML 中提取所有 chunk URL
with open("_mofa.html", "r", encoding="utf-8") as f:
    html = f.read()

chunks = re.findall(r'/_next/static/chunks/[^"]+\.js', html)
lines = [f"找到 {len(chunks)} 个 JS chunk\n"]

for chunk_url in chunks:
    url = f"https://mofa.gov.mn{chunk_url}"
    r = requests.get(url, headers=headers, timeout=10)
    js = r.text
    # 搜索 API 相关的关键字
    patterns = [
        r'["\']([^"\']*(?:saContent|saNews|saArticle|/api/|fetchList|getNews|getList)[^"\']*)["\']',
        r'(baseUrl\s*[:=]\s*["\'][^"\']+["\'])',
        r'(apiUrl\s*[:=]\s*["\'][^"\']+["\'])',
        r'(https?://[^\s"\'<>]{5,80})',
        r'(["\'][^"\']{3,50}:[^"\']{3,50}["\'])',  # host:port 模式
    ]
    found = False
    for pat in patterns:
        for m in re.finditer(pat, js):
            val = m.group(1)
            if len(val) > 3 and val not in ['"use client"', '"use strict"']:
                if not found:
                    lines.append(f"\n--- {chunk_url} ({len(js)} chars) ---")
                    found = True
                lines.append(f"  {val[:150]}")

with open("_mofa_api2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
