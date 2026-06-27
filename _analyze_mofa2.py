# -*- coding: utf-8 -*-
import re
with open("_mofa.html", "r", encoding="utf-8") as f:
    html = f.read()

lines = []

# 搜索 __NEXT_DATA__ 或 JSON 数据
lines.append(f"=== 页面长度: {len(html)} 字符 ===")

# 搜索 JSON 结构
match = re.search(r'__NEXT_DATA__\s*=\s*({.*?})', html, re.DOTALL)
if match:
    import json
    data = json.loads(match.group(1))
    lines.append(f"=== __NEXT_DATA__ 找到 ===")
    lines.append(str(data)[:3000])
else:
    # 查找所有 script 标签
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script"):
        text = script.get_text()
        if "pageProps" in text or "news" in text.lower():
            lines.append(f"=== Script 含 news/pageProps (前1000字符) ===")
            lines.append(text[:1000])
            lines.append("")
    
    # 搜索可能的 API 端点
    lines.append("=== 搜索 API URL ===")
    for m in re.finditer(r'(https?://[^\s"\']*api[^\s"\']*)', html):
        lines.append(f"  {m.group(1)[:100]}")
    for m in re.finditer(r'(https?://[^\s"\']*/news[^\s"\']*)', html):
        lines.append(f"  {m.group(1)[:100]}")

# 直接打印 body 内容
lines.append("")
lines.append(f"=== 完整 body 文本 ===")
text = soup.get_text() if 'soup' in dir() else ""
lines.append(text[:2000])

with open("_mofa_analysis2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done")
