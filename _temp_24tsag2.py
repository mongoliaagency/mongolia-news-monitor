import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup

with open('_html/24tsag_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 60)
print("1. featured-items / featured-item structure")
print("=" * 60)
items = soup.select('.featured-item')
for i, item in enumerate(items[:8]):
    link = item.select_one('a[href]')
    date_el = item.select_one('.featured-item__date')
    title_el = item.select_one('.featured-item__title-text, .article-item-title')
    img_el = item.select_one('img')
    url = link.get('href', 'N/A') if link else 'N/A'
    date = date_el.get_text(strip=True) if date_el else 'NO_DATE'
    title = title_el.get_text(strip=True)[:80] if title_el else 'N/A'
    img = img_el.get('src', 'N/A')[:80] if img_el else 'N/A'
    print(f"  [{i}] URL: {url}")
    print(f"       Title: {title}")
    print(f"       Date: {date}")
    print(f"       Img: {img}")
    print()

print("\n" + "=" * 60)
print("2. article-item structure")
print("=" * 60)
items = soup.select('.article-item')
for i, item in enumerate(items[:10]):
    link = item.select_one('a[href]')
    date_el = item.select_one('.article-item-date, [class*="date"]')
    title_el = item.select_one('.article-item-title, a')
    url = link.get('href', 'N/A') if link else 'N/A'
    date = date_el.get_text(strip=True) if date_el else 'NO_DATE'
    title = title_el.get_text(strip=True)[:80] if title_el else 'N/A'
    print(f"  [{i}] URL: {url}")
    print(f"       Title: {title}")
    print(f"       Date: {date}")
    print(f"       Classes: {' '.join(item.get('class', []))[:80]}")
    print()

print("\n" + "=" * 60)
print("3. feature-main / feature-sub structure")
print("=" * 60)
for sel in ['.feature-main', '.feature-sub', '.feature-top']:
    items = soup.select(sel)
    if items:
        print(f"\n  {sel} ({len(items)} items):")
        for i, item in enumerate(items[:5]):
            link = item.select_one('a[href]')
            date_el = item.select_one('[class*="date"]')
            title_el = item.select_one('[class*="title"], [class*="text"], [class*="name"]')
            url = link.get('href', 'N/A') if link else 'N/A'
            date = date_el.get_text(strip=True) if date_el else 'NO_DATE'
            title = title_el.get_text(strip=True)[:80] if title_el else 'N/A'
            print(f"    [{i}] URL: {url} | Date: {date}")
            print(f"         Title: {title}")

print("\n" + "=" * 60)
print("4. Swiper slides")
print("=" * 60)
slides = soup.select('.swiper-slide')
for i, slide in enumerate(slides[:10]):
    link = slide.select_one('a[href]')
    date_el = slide.select_one('[class*="date"]')
    title_el = slide.select_one('[class*="title"], [class*="text"]')
    url = link.get('href', 'N/A') if link else 'N/A'
    date = date_el.get_text(strip=True) if date_el else 'NO_DATE'
    title = title_el.get_text(strip=True)[:80] if title_el else 'N/A'
    print(f"  [{i}] URL: {url} | Date: {date}")
    print(f"       Title: {title}")

print("\n" + "=" * 60)
print("5. publicist-item structure")
print("=" * 60)
items = soup.select('.publicist-item')
for i, item in enumerate(items[:5]):
    link = item.select_one('a[href]')
    date_el = item.select_one('[class*="date"]')
    title_el = item.select_one('.publicist-item-title, .publicist-item-name')
    url = link.get('href', 'N/A') if link else 'N/A'
    date = date_el.get_text(strip=True) if date_el else 'NO_DATE'
    title = title_el.get_text(strip=True)[:80] if title_el else 'N/A'
    print(f"  [{i}] URL: {url} | Date: {date}")
    print(f"       Title: {title}")
