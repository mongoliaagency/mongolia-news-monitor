import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = "https://sme.gov.mn/index"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

try:
    r = requests.get(url, headers=headers, timeout=30, verify=False)
    with open("_sme.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print(f"OK: {len(r.text)} bytes, status={r.status_code}")
except Exception as e:
    print(f"FAIL: {e}")
    # fallback to playwright
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30000)
        html = page.content()
        with open("_sme.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"OK via playwright: {len(html)} bytes")
        browser.close()
