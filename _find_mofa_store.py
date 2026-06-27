# -*- coding: utf-8 -*-
"""在 _app.js 中搜索 store 定义，找到 API URL"""
import re

with open("_mofa.html", "r", encoding="utf-8") as f:
    html = f.read()

# 搜索 articleStore 相关
chunks_in_html = re.findall(r'/_next/static/chunks/[^"]+\.js', html)

# 重点下载 _app.js 并搜索
import requests
headers = {"User-Agent": "Mozilla/5.0"}

# 在 _app.js 中找 store 定义
r = requests.get("https://mofa.gov.mn/_next/static/chunks/pages/_app-05525bbe7a3e899d36cd.js", headers=headers, timeout=10)
app_js = r.text
lines = [f"_app.js: {len(app_js)} chars\n"]

# 搜索 store 相关
for m in re.finditer(r'(articleStore|newsStore|fetchList|getNews|newsList)[^;]{0,300}', app_js):
    val = m.group(0)
    if 'api' in val.lower() or 'url' in val.lower() or 'fetch' in val.lower() or 'http' in val.lower():
        lines.append(f"  STORE: {val[:200]}")
        lines.append("")

# 搜索 http 或 api URL
for m in re.finditer(r'(https?://[^\s"\'<>]{5,100})', app_js):
    url = m.group(1)
    if 'mofa' in url and ('api' in url or '808' in url or '/sa' in url):
        lines.append(f"  URL: {url}")

# 搜索 /api/ 模式
for m in re.finditer(r'["\'](/api/[^"\']{3,80})["\']', app_js):
    lines.append(f"  API_PATH: {m.group(1)}")

# 搜索 fetch 或 axios 请求
for m in re.finditer(r'(axios|fetch|request)\s*\(\s*["\'][^"\']{5,100}["\']', app_js):
    lines.append(f"  REQUEST: {m.group(0)[:150]}")

# 搜索 baseURL
for m in re.finditer(r'(baseURL|BASE_URL|apiUrl|API_URL|baseUrl)\s*[:=]\s*["\'][^"\']{3,100}["\']', app_js):
    lines.append(f"  CONFIG: {m.group(0)[:150]}")

# 也检查 articleStore 的创建
for m in re.finditer(r'new\s+\w+Store[^;]{0,200}', app_js):
    lines.append(f"  NEW_STORE: {m.group(0)[:200]}")
for m in re.finditer(r'createStore[^;]{0,200}', app_js):
    lines.append(f"  CREATE_STORE: {m.group(0)[:200]}")

# 找 list 端点
for m in re.finditer(r'["\'][^"\']{3,60}/list[^"\']{0,30}["\']', app_js):
    lines.append(f"  LIST_ENDPOINT: {m.group(0)}")

with open("_mofa_store.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
