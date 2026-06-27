# -*- coding: utf-8 -*-
import requests, re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 下载新闻页面的 JS chunk
js_url = "https://mofa.gov.mn/_next/static/chunks/pages/news/%5Bcategory%5D-7b213567a3a86bf40833.js"
r = requests.get(js_url, headers=headers, timeout=10)
js = r.text
print(f"JS chunk: {len(js)} chars")

# 搜索 API URL
lines = [f"JS chunk: {len(js)} chars\n"]
for m in re.finditer(r'["\']([^"\']*api[^"\']*)["\']', js):
    lines.append(f"  API: {m.group(1)}")
for m in re.finditer(r'["\']([^"\']*/news[^"\']*)["\']', js):
    lines.append(f"  NEWS: {m.group(1)}")
for m in re.finditer(r'["\']([^"\']*content[^"\']*)["\']', js):
    lines.append(f"  CONTENT: {m.group(1)}")
for m in re.finditer(r'["\']([^"\']*fetch[^"\']*)["\']', js):
    lines.append(f"  FETCH: {m.group(1)}")
for m in re.finditer(r'["\']([^"\']*/sa[A-Z][^"\']*)["\']', js):
    lines.append(f"  SA: {m.group(1)}")
for m in re.finditer(r'(["\']/(api|sa|v1|v2)/[^"\']*["\'])', js):
    lines.append(f"  PATH: {m.group(1)}")
for m in re.finditer(r'(https?://[^\s"\'<>]+mofa[^\s"\'<>]+)', js):
    lines.append(f"  URL: {m.group(1)}")
for m in re.finditer(r'(baseURL|apiUrl|API_URL|api_url|endpoint|ENDPOINT)[^,;]*', js):
    lines.append(f"  CONFIG: {m.group(0)[:150]}")

# 也下载 main chunk
main_js = "https://mofa.gov.mn/_next/static/chunks/main-7d91e7686bd8b97b8c95.js"
r2 = requests.get(main_js, headers=headers, timeout=10)
main = r2.text
lines.append(f"\nMain JS: {len(main)} chars")
for m in re.finditer(r'(["\']/(api|sa|v1|v2)/[^"\']*["\'])', main):
    lines.append(f"  PATH: {m.group(1)}")
for m in re.finditer(r'(baseURL|apiUrl|API_URL|api_url)[^,;]*', main):
    lines.append(f"  CONFIG: {m.group(0)[:150]}")

# 搜索所有可能的 API 模式
for m in re.finditer(r'(["\'][^"\']{2,50}/(sa[A-Za-z]+|newslist|newsList|getNews|getContent|listNews)[^"\']*["\'])', main):
    lines.append(f"  API_CALL: {m.group(1)}")

with open("_mofa_analysis4.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
