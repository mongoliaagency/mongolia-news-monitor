import sys
sys.stdout.reconfigure(encoding='utf-8')

from bs4 import BeautifulSoup

with open('_html/chig_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("1. fr_news 精选新闻 HTML 结构")
print("=" * 80)
for i, el in enumerate(soup.find_all(class_='fr_news')[:3]):
    print(f"\n--- fr_news #{i+1} ---")
    print(str(el)[:800])
    print("...")

print("\n" + "=" * 80)
print("2. today_news1 区域")
print("=" * 80)
for i, el in enumerate(soup.find_all(class_='today_news1')[:3]):
    print(f"\n--- today_news1 #{i+1} ---")
    print(str(el)[:600])
    print("...")

print("\n" + "=" * 80)
print("3. v_list 区域")
print("=" * 80)
for i, el in enumerate(soup.find_all(class_='v_list')[:3]):
    print(f"\n--- v_list #{i+1} ---")
    print(str(el)[:600])
    print("...")

print("\n" + "=" * 80)
print("4. news 类区域")
print("=" * 80)
news_els = soup.find_all(class_='news')
print(f"Count: {len(news_els)}")
for i, el in enumerate(news_els[:5]):
    print(f"\n--- news #{i+1} ---")
    print(str(el)[:500])
    print("...")

print("\n" + "=" * 80)
print("5. small_list 区域")
print("=" * 80)
for i, el in enumerate(soup.find_all(class_='small_list')[:3]):
    print(f"\n--- small_list #{i+1} ---")
    print(str(el)[:600])
    print("...")

print("\n" + "=" * 80)
print("6. 所有 article 详情链接 (single/xxxxx)")
print("=" * 80)
import re
single_links = set(re.findall(r'https://chig\.mn/news/\d+/single/\d+', html))
for l in sorted(single_links):
    print(f"  {l}")

print(f"\nTotal single article links: {len(single_links)}")
