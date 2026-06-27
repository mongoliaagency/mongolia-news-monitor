import requests

url = "https://moh.gov.mn/index.php/news/t/1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}
resp = requests.get(url, headers=headers, timeout=30)
print(f"Status: {resp.status_code}")
print(f"Length: {len(resp.text)}")
with open("_moh.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("Saved to _moh.html")
