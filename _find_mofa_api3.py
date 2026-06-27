# -*- coding: utf-8 -*-
import requests, re

headers = {"User-Agent": "Mozilla/5.0"}

# 在 _app.js 中搜索 fetchList 的完整实现
r = requests.get("https://mofa.gov.mn/_next/static/chunks/pages/_app-05525bbe7a3e899d36cd.js", headers=headers, timeout=10)
app_js = r.text

lines = [f"_app.js: {len(app_js)} chars\n"]

# 搜索 fetchList 函数体，找 axios/get/post 调用
# 先找一个 fetchList 的完整实现
idx = app_js.find(',{key:"fetchList"')
while idx > 0:
    # 取前后 500 字符
    start = max(0, idx - 50)
    end = min(len(app_js), idx + 500)
    snippet = app_js[start:end]
    
    # 只保留有 URL 的
    if any(kw in snippet for kw in ['/api', 'http', 'axios', 'get(', 'post(', 'request(']):
        lines.append(f"  === fetchList at {idx} ===\n  {snippet[:400]}\n")
    
    idx = app_js.find(',{key:"fetchList"', idx + 1)

# 也搜索 axios.create
for m in re.finditer(r'(axios\.create\s*\([^)]{0,200})', app_js):
    lines.append(f"  AXIOS: {m.group(0)[:200]}")

# 搜索 url: 或 baseURL: 附近
for m in re.finditer(r'(url\s*:\s*["\'][^"\']{3,80}["\'])', app_js):
    lines.append(f"  URL_CONFIG: {m.group(1)}")

# 搜索 /api/sa
for m in re.finditer(r'["\'](/api/sa[A-Za-z/]{3,60})["\']', app_js):
    lines.append(f"  API_SA: {m.group(1)}")

# 搜索 ${baseURL} 或 ${apiUrl}
for m in re.finditer(r'(\$\{[a-zA-Z]+\}[^"\']{0,80})', app_js):
    val = m.group(1)
    if any(kw in val.lower() for kw in ['/api', '/sa', '/list', '/news', '/content']):
        lines.append(f"  TEMPLATE: {val[:150]}")

# 搜索 get( 或 post( 调用带 URL 的
for m in re.finditer(r'([gG]et|[pP]ost)\s*\(\s*["\'][^"\']{5,80}["\']', app_js):
    lines.append(f"  REQ_CALL: {m.group(0)[:150]}")

with open("_mofa_api3.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
