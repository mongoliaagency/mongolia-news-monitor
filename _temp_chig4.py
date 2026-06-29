import sys
sys.stdout.reconfigure(encoding='utf-8')

from bs4 import BeautifulSoup

with open('_html/chig_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("1. today_news_content1 完整列表 (所有 li)")
print("=" * 80)
for i, el in enumerate(soup.find_all(class_='today_news_content1')[:1]):
    for j, li in enumerate(el.find_all('li')[:20]):
        a = li.find('a', href=True)
        img = li.find('img')
        print(f"\n  li#{j+1}:")
        print(f"    link: {a['href'] if a else 'N/A'}")
        print(f"    text: {li.get_text(strip=True)[:120]}")
        if img:
            print(f"    img: {img.get('src', 'N/A')[:100]}")

print("\n" + "=" * 80)
print("2. owl-carousel (轮播区) 所有 items")
print("=" * 80)
for carousel in soup.find_all(class_='owl-carousel'):
    items = carousel.find_all(class_='item')
    print(f"\nCarousel items: {len(items)}")
    for i, item in enumerate(items[:5]):
        fr_news = item.find(class_='fr_news')
        fr_title = item.find(class_='fr_title')
        a = item.find('a', href=True)
        span = item.find('span')
        bg = item.get('style', '')
        print(f"\n  item#{i+1}:")
        print(f"    background: {bg[:100]}")
        if fr_title:
            print(f"    fr_title: {fr_title.get_text(strip=True)}")
        if fr_news:
            print(f"    fr_news text: {fr_news.get_text(strip=True)[:100]}")
            if a:
                print(f"    link: {a['href']}")
        if span and not fr_news:
            print(f"    span: {span.get_text(strip=True)[:100]}")

print("\n" + "=" * 80)
print("3. front_1 / front_2 / front_live 区域")
print("=" * 80)
for cls in ['front_1', 'front_2', 'front_live']:
    els = soup.find_all(class_=cls)
    print(f"\n  {cls}: {len(els)} elements")
    for el in els[:3]:
        links = el.find_all('a', href=True)
        for a in links[:5]:
            href = a.get('href', '')
            if '/single/' in href:
                print(f"    article: {href} -> {a.get_text(strip=True)[:100]}")

print("\n" + "=" * 80)
print("4. section_item_left 区域")
print("=" * 80)
for el in soup.find_all(class_='section_item_left')[:3]:
    a = el.find('a', href=True)
    img = el.find('img')
    print(f"  link: {a['href'] if a else 'N/A'}")
    print(f"  text: {el.get_text(strip=True)[:150]}")
    if img:
        print(f"  img: {img.get('src', 'N/A')[:100]}")

print("\n" + "=" * 80)
print("5. 页面主要区域概览 (查找所有包含 single 链接的区域)")
print("=" * 80)
import re
# Find all sections with single links grouped
sections = {}
for tag in soup.find_all(True):
    links_in_tag = tag.find_all('a', href=re.compile(r'/single/\d+'))
    if links_in_tag:
        parent_cls = ' '.join(tag.get('class', []))
        for a in links_in_tag:
            key = parent_cls if parent_cls else tag.name
            if key not in sections:
                sections[key] = []
            sections[key].append({
                'link': a['href'],
                'text': a.get_text(strip=True)[:100],
                'tag': tag.name
            })

for section, items in sections.items():
    print(f"\n  [{section}] ({len(items)} articles)")
    for item in items[:5]:
        print(f"    {item['link']} -> {item['text'][:80]}")

print("\n" + "=" * 80)
print("6. 页面布局 body 直接子元素")
print("=" * 80)
body = soup.find('body')
if body:
    for child in body.find_all(True, recursive=False)[:20]:
        cls = ' '.join(child.get('class', []))
        name = child.name
        print(f"  <{name} class='{cls}'>")
