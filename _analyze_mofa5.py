# -*- coding: utf-8 -*-
import requests, re, json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 下载 main.js 并搜索 API URL
r = requests.get("https://mofa.gov.mn/_next/static/chunks/main-7d91e7686bd8b97b8c95.js", headers=headers, timeout=10)
main = r.text

lines = [f"Main JS: {len(main)} chars\n"]

# 搜索 fetchList 相关
for m in re.finditer(r'fetchList[^;]{0,200}', main):
    lines.append(f"  fetchList: {m.group(0)[:200]}")
for m in re.finditer(r'baseUrl[^,;]{0,100}', main):
    lines.append(f"  baseUrl: {m.group(0)[:150]}")
for m in re.finditer(r'BASE_URL[^,;]{0,100}', main):
    lines.append(f"  BASE_URL: {m.group(0)[:150]}")
for m in re.finditer(r'(https?://[^\s"\'<>]{5,80})', main):
    url = m.group(1)
    if any(kw in url.lower() for kw in ['mofa', 'api', '808', ':80', ':300', '/sa']):
        lines.append(f"  URL: {url}")

# 也尝试所有 JS chunk
for chunk_name in ["7315-a5a58f0278399c155558.js", "5839-36959a35cc615d3a6944.js", "5026-b9b1f046f915d656943f.js", "1232-d6a2dcd462e2523d40e3.js", "6068-b2012793fa71d31a999e.js", "5247-c64e32b43970163844f2.js"]:
    url = f"https://mofa.gov.mn/_next/static/chunks/{chunk_name}"
    r2 = requests.get(url, headers=headers, timeout=10)
    js = r2.text
    for m in re.finditer(r'(https?://[^\s"\'<>]{5,80})', js):
        url_found = m.group(1)
        if any(kw in url_found.lower() for kw in ['mofa', 'api', '808', ':80', ':300', '/sa', 'content', 'news/list']):
            lines.append(f"  [{chunk_name}] URL: {url_found}")

# 尝试直接猜 API 路径
lines.append("\n=== 尝试猜 API ===")
for path in [
    "https://mofa.gov.mn/saContent/list?limit=20",
    "https://mofa.gov.mn:8085/saContent/list?limit=20",
    "https://mofa.gov.mn/saContent/list?type=TIME&limit=20",
    "https://mofa.gov.mn/api/saContent/list?limit=20",
]:
    try:
        r3 = requests.get(path, headers=headers, timeout=10)
        lines.append(f"  {path}: {r3.status_code} {len(r3.text)} chars")
        if r3.status_code == 200 and len(r3.text) > 50:
            try:
                data = json.loads(r3.text)
                lines.append(f"  JSON keys: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}")
                lines.append(str(data)[:500])
            except:
                lines.append(f"  {r3.text[:300]}")
    except Exception as e:
        lines.append(f"  {path}: ERROR {e}")

with open("_mofa_analysis5.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
