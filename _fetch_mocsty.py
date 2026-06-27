import requests
resp = requests.get("https://mocsty.gov.mn/news", headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}, timeout=30)
with open("_mocsty.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print(f"OK: {len(resp.text)} chars")
