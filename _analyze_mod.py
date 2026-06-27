"""Analyze mod.gov.mn HTML to find news selectors."""
from bs4 import BeautifulSoup
import re

with open('_fix_mod.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# Search for news/article patterns
print("=== MOD: Looking for articles/news entries ===")
for tag in ['article', 'div', 'li', 'section']:
    for cls in ['post', 'entry', 'news', 'article', 'item', 'list']:
        for el in soup.select(f'{tag}[class*="{cls}"]')[:3]:
            txt = el.get_text(strip=True)[:150]
            cls_val = el.get('class', [])
            print(f'  {tag}.{el.get("class")} -> "{txt}"')
            break

# Search for title links
print("\n=== MOD: Title link patterns ===")
links = soup.find_all('a', href=True)
for a in links[:50]:
    href = a.get('href', '')
    txt = a.get_text(strip=True)
    if len(txt) > 10 and ('post' in href.lower() or 'entry' in href.lower() or 'news' in href.lower() or '?p=' in href or '&p=' in href or 'article' in href.lower() or txt):
        parent = a.parent
        parent_info = f"  in <{parent.name} class={parent.get('class','')}>"
        date_el = None
        # Search nearby for dates
        for dtag in ['time', 'span', 'small', 'div', 'p']:
            for dcls in ['date', 'time', 'published', 'posted', 'meta']:
                found = parent.find_all(dtag, class_=re.compile(dcls, re.I))
                if found:
                    date_el = found
                    break
            if date_el:
                break
        if date_el:
            print(f'  <a href="{href}"> {txt[:60]}... </a>{parent_info}')
            for d in date_el[:2]:
                print(f'    date element: <{d.name} class={d.get("class","")}> "{d.get_text(strip=True)[:40]}"')
            print()
            break

# Search for date patterns
print("\n=== MOD: Date-containing elements ===")
for tag in soup.find_all(['time', 'span', 'div', 'p', 'small']):
    txt = tag.get_text(strip=True)
    if re.search(r'\d{4}', txt) and len(txt) < 50:
        cls = tag.get('class', '')
        parent_cls = tag.parent.get('class', '') if tag.parent else ''
        print(f'  <{tag.name} class="{cls}"> "{txt}" parent=<{tag.parent.name if tag.parent else ""} class="{parent_cls}">')

# Search for entry-title, post-title classes
print("\n=== MOD: Entry/post title class elements ===")
for el in soup.select('[class*="entry-title"], [class*="post-title"], [class*="entry-title"], h2 a, h3 a'):
    txt = el.get_text(strip=True)
    if len(txt) > 10:
        cls = el.get('class', '')
        href = el.get('href', '')
        print(f'  <{el.name} class="{cls}" href="{href}"> "{txt[:80]}"')
        break

# Dump first 5000 chars to see structure
print("\n=== MOD: Body structure (first 3000 chars) ===")
body = soup.find('body')
if body:
    for child in body.find_all(['article', 'div'], recursive=True, limit=3):
        if child.get('class'):
            inner = str(child)[:500]
            print(f'  <{child.name} class="{child.get("class")}">: {inner[:200]}')
