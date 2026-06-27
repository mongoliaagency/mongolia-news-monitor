from bs4 import BeautifulSoup
import re

with open("_moh.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

rows = soup.select(".standart-news-listpage .row.clearfix")

out_lines = []
out_lines.append(f"Total rows: {len(rows)}\n")

valid_count = 0
for i, row in enumerate(rows):
    title_el = row.select_one(".entry-title h4 a")
    date_el = row.select_one("p")

    if not title_el:
        continue  # skip non-news rows like pagination

    title = title_el.get_text(strip=True)
    link = title_el.get("href", "")
    if link.startswith("/"):
        link = "https://moh.gov.mn" + link

    date_text = date_el.get_text(strip=True) if date_el else ""
    date_match = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', date_text)
    date = date_match.group(0) if date_match else date_text

    valid_count += 1
    out_lines.append(f"#{valid_count}")
    out_lines.append(f"  Title: {title}")
    out_lines.append(f"  Link:  {link}")
    out_lines.append(f"  Date:  {date}")
    out_lines.append("")

out_lines.insert(1, f"Valid news items: {valid_count}\n")

with open("_verify_moh.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print(f"Done - {valid_count} valid news out of {len(rows)} rows")
