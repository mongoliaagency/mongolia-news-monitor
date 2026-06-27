"""深入分析 1212.mn - 找JS bundle和API端点"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open("_stat_page.html", "r", encoding="utf-8") as f:
    content = f.read()

# 找所有 script src
scripts = re.findall(r'<script[^>]*src="([^"]+)"', content)
print("=== Script sources ===")
for s in scripts[:20]:
    print(f"  {s}")

# 找可能的 API URL
apis = re.findall(r'(?:api|fetch|url|href|endpoint)[\'"]?\s*[:=]\s*[\'"]([^\'"]+)[\'"]', content)
print(f"\n=== Possible API URLs ===")
for a in apis[:20]:
    print(f"  {a}")

# 找 news/latest 相关的所有内容
news_refs = re.findall(r'.{0,100}news.{0,100}', content, re.IGNORECASE)
print(f"\n=== News references ({len(news_refs)}) ===")
for n in news_refs[:10]:
    print(f"  {n}")

# 找 main.js 或 chunk
print("\n=== All script tags content ===")
for m in re.finditer(r'<script[^>]*>(.*?)</script>', content, re.DOTALL):
    s = m.group(1).strip()
    if s:
        print(f"  Inline script length: {len(s)}")

# 找 __NEXT_DATA__ 或类似
for pattern in ['__NEXT_DATA__', '__NUXT__', 'window.__', '__INITIAL_STATE__']:
    idx = content.find(pattern)
    if idx >= 0:
        print(f"\n=== {pattern} found at {idx} ===")
        print(content[idx:idx+500])
