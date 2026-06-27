from bs4 import BeautifulSoup
import json

with open("_med.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

items = soup.select(".entry.post-list-item")

out_lines = []
out_lines.append(f"Total items: {len(items)}\n")

for i, item in enumerate(items):
    title_el = item.select_one(".entry-title h2 a")
    date_el = item.select_one(".entry-meta li:first-child")

    title = title_el.get_text(strip=True) if title_el else "N/A"
    link = title_el.get("href", "") if title_el else "N/A"
    # 补全完整URL
    if link.startswith("/"):
        link = "https://med.gov.mn" + link
    date_text = date_el.get_text(strip=True) if date_el else "N/A"
    # 从 "2026-06-26" 这样的文本提取日期
    import re
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_text)
    date = date_match.group(0) if date_match else date_text

    out_lines.append(f"#{i+1}")
    out_lines.append(f"  Title: {title}")
    out_lines.append(f"  Link:  {link}")
    out_lines.append(f"  Date:  {date}")
    out_lines.append("")

with open("_verify_med.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print(f"Done - {len(items)} items verified")
