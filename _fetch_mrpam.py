import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = "https://mrpam.gov.mn/news/type/article"
try:
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60, verify=False)
    resp.encoding = resp.apparent_encoding
    print(f"Status: {resp.status_code}")
    print(f"Length: {len(resp.text)}")
    with open("_mrpam.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
    print("Saved to _mrpam.html via requests")
except Exception as e:
    print(f"requests failed: {e}")
    print("Trying playwright...")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-gpu','--no-sandbox','--disable-dev-shm-usage','--ignore-certificate-errors'])
        page = browser.new_page()
        page.goto(url, wait_until='load', timeout=60000)
        page.wait_for_timeout(3000)
        html = page.content()
        browser.close()
    print(f"Playwright Length: {len(html)}")
    with open("_mrpam.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved to _mrpam.html via playwright")
