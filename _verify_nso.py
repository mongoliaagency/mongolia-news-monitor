"""验证统计局 API 抓取"""
import sys, json
sys.path.insert(0, 'scripts')
from api_fetcher import fetch_api

result = fetch_api("config/sources/nso_mn.json")

print(f"Total articles (today only): {len(result)}")
for i, item in enumerate(result[:5]):
    print(f"\n--- Article {i+1} ---")
    for k, v in item.items():
        if isinstance(v, str) and len(v) > 100:
            v = v[:100] + "..."
        print(f"  {k}: {v}")

# 输出到文件
with open("_nso_verify.txt", "w", encoding="utf-8") as f:
    f.write(f"Total articles (today only): {len(result)}\n\n")
    for i, item in enumerate(result):
        f.write(f"--- Article {i+1} ---\n")
        for k, v in item.items():
            f.write(f"  {k}: {v}\n")
        f.write("\n")
