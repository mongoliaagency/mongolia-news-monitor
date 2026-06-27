import requests
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

url = "https://mmra.gov.mn/?id=200008"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
resp = requests.get(url, headers=headers, timeout=30)
print(f"Status: {resp.status_code}, encoding: {resp.encoding}, len: {len(resp.text)}")

with open("_mmra.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("Saved to _mmra.html")
