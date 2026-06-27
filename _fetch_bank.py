"""下载 mongolbank.mn 首页HTML"""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.mongolbank.mn/mn/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

resp = requests.get(url, headers=headers, timeout=30)
resp.encoding = 'utf-8'

with open("_bank_page.html", "w", encoding="utf-8") as f:
    f.write(resp.text)

print(f"Status: {resp.status_code}")
print(f"Length: {len(resp.text)}")
