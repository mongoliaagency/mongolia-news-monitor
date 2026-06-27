from bs4 import BeautifulSoup, Tag
import json

with open("_mddic.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

articles = soup.select("article.eael-grid-post")

out_lines = []
out_lines.append(f"Total articles: {len(articles)}\n")

for i, article in enumerate(articles):
    title_el = article.select_one(".eael-entry-title")
    link_el = article.select_one(".eael-entry-overlay a")
    date_el = article.select_one(".eael-posted-on")

    title = title_el.get_text(strip=True) if title_el else "N/A"
    link = link_el.get("href", "") if link_el else "N/A"
    date = date_el.get_text(strip=True) if date_el else "N/A"

    out_lines.append(f"#{i+1}")
    out_lines.append(f"  Title: {title}")
    out_lines.append(f"  Link:  {link}")
    out_lines.append(f"  Date:  {date}")
    out_lines.append("")

with open("_verify_mddic.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print(f"Done - {len(articles)} articles verified")
