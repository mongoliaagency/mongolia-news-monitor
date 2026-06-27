"""下载 1212.mn/mn 统计局新闻页面HTML"""
import requests

url = "https://www.1212.mn/mn"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

resp = requests.get(url, headers=headers, timeout=30, verify=False)
resp.encoding = 'utf-8'

with open("_stat_page.html", "w", encoding="utf-8") as f:
    f.write(resp.text)

print(f"Status: {resp.status_code}")
print(f"Length: {len(resp.text)}")
