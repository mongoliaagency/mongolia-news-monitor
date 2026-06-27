import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from bs4 import BeautifulSoup

with open("_sme.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

with open("_sme_analysis.txt", "w", encoding="utf-8") as f:
    # 1. Look at the news tab entries
    f.write("NEWS TAB (.entry.col-12.mb-3):\n")
    entries = soup.select(".entry.col-12.mb-3")
    f.write(f"Count: {len(entries)}\n")
    for i, entry in enumerate(entries[:5]):
        title = entry.select_one("h6 a")
        date = entry.select_one(".entry-meta li")
        f.write(f"  [{i+1}] Title: {title.get_text(strip=True) if title else 'NONE'}\n")
        f.write(f"      Link: {title.get('href') if title else 'NONE'}\n")
        f.write(f"      Date: {date.get_text(strip=True) if date else 'NONE'}\n")
        f.write(f"      HTML: {str(entry)[:500]}\n\n")
    
    # 2. Look at the old tab entries with absolute dates
    f.write("\n" + "="*60 + "\n")
    f.write("OLD TAB (.entry.col-12.pb-2):\n")
    entries = soup.select(".entry.col-12.pb-2")
    f.write(f"Count: {len(entries)}\n")
    for i, entry in enumerate(entries[:5]):
        title = entry.select_one("h4 a")
        date = entry.select_one("li.sme-custom-blue:last-child")
        f.write(f"  [{i+1}] Title: {title.get_text(strip=True) if title else 'NONE'}\n")
        f.write(f"      Link: {title.get('href') if title else 'NONE'}\n")
        f.write(f"      Date: {date.get_text(strip=True) if date else 'NONE'}\n")
        f.write(f"      HTML: {str(entry)[:500]}\n\n")
    
    # 3. Look at all .entry containers with actual news links
    f.write("\n" + "="*60 + "\n")
    f.write("ALL .entry WITH /news/ LINKS:\n")
    all_entries = soup.select(".entry")
    count = 0
    for entry in all_entries:
        news_link = entry.select_one("a[href*='/news/']")
        if news_link:
            count += 1
            if count <= 5:
                date_el = entry.select_one("li.sme-custom-blue")
                # get all li
                lis = entry.select("li")
                date_texts = [li.get_text(strip=True) for li in lis]
                cls = ".".join(entry.get("class", []))
                f.write(f"  [{count}] classes={cls}\n")
                f.write(f"      Title: {news_link.get_text(strip=True)[:100]}\n")
                f.write(f"      Link: {news_link.get('href')}\n")
                f.write(f"      LI texts: {date_texts}\n\n")
    f.write(f"Total .entry with /news/ links: {count}\n")
