from bs4 import BeautifulSoup
import json

with open("_energy.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")
items = soup.select(".post-item")

lines = []
for i, item in enumerate(items):
    title_el = item.select_one("a.text-dark-emphasis")
    date_el = item.select_one(".post-date")
    
    title = title_el.get_text(strip=True) if title_el else "NONE"
    link = title_el.get("href", "") if title_el else "NONE"
    date = date_el.get_text(strip=True) if date_el else "NONE"
    
    if link.startswith("/"):
        link = "https://energy.gov.mn" + link
    
    lines.append(f"[{i}] {date} | {title[:60]} | {link}")

# Check for pagination
next_page = soup.select_one("a[rel='next'], .pagination .next a, [class*='pagination'] a[class*='next']")
pagination_links = soup.select("[class*='pagination'] a")
page_urls = [a.get("href", "") for a in pagination_links[:10]]

with open("_verify_energy.txt", "w", encoding="utf-8") as f:
    f.write(f"Total items: {len(items)}\n\n")
    f.write("\n".join(lines))
    f.write(f"\n\nPagination links: {page_urls}")
    if next_page:
        f.write(f"\nNext page: {next_page.get('href', '')}")

print(f"Verified {len(items)} items. Output to _verify_energy.txt")
