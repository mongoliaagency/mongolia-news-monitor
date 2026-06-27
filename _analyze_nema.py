"""Analyze nema.gov.mn/posts HTML to find news selectors."""
from bs4 import BeautifulSoup
import re

with open('_fix_nema.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# Search for post-item patterns
print("=== NEMA: Post items ===")
for el in soup.select('article, .post-item, .news-item, [class*="post"], [class*="news"]'):
    txt = el.get_text(strip=True)[:120]
    cls = el.get('class', [])
    if len(txt) > 20:
        print(f'  <{el.name} class="{cls}"> "{txt}"')
        # Find title link inside
        for a in el.find_all('a', href=True):
            a_txt = a.get_text(strip=True)
            href = a.get('href', '')
            if len(a_txt) > 10:
                print(f'    → <a href="{href}">{a_txt[:80]}</a>')
        # Find date
        for d in el.find_all(['time', 'span', 'div', 'p', 'small']):
            d_txt = d.get_text(strip=True)
            if re.search(r'\d{4}', d_txt) and len(d_txt) < 40:
                d_cls = d.get('class', '')
                print(f'    → date: <{d.name} class="{d_cls}">{d_txt[:50]}</d>')
        print()
        if len([x for x in dir() if x]) > 20:
            break

print("\n=== NEMA: Date elements ===")
for tag in soup.find_all(['time', 'span', 'div', 'p', 'small']):
    txt = tag.get_text(strip=True)
    if re.search(r'\d{4}', txt) and len(txt) < 50:
        cls = tag.get('class', '')
        parent = tag.parent
        p_cls = parent.get('class', '') if parent else ''
        print(f'  <{tag.name} class="{cls}"> "{txt}" in <{parent.name if parent else ""} class="{p_cls}">')

print("\n=== NEMA: Title links ===")
for a in soup.find_all('a', href=True):
    txt = a.get_text(strip=True)
    href = a.get('href', '')
    if len(txt) > 15 and '/post/' in href:
        cls = a.get('class', '')
        h_tag = a.find_parent(['h1','h2','h3','h4','h5','h6'])
        parent_info = f'in <{h_tag.name}>' if h_tag else f'in <{a.parent.name} class={a.parent.get("class","")}>'
        print(f'  <a class="{cls}" href="{href}"> {txt[:80]} </a> {parent_info}')
        if h_tag:
            # Look for date in parent container
            container = h_tag.parent
            for _ in range(3):
                if container:
                    for d in container.find_all(['time', 'span', 'small', 'div']):
                        d_txt = d.get_text(strip=True)
                        if re.search(r'\d{4}', d_txt) and len(d_txt) < 30:
                            print(f'    → date nearby: <{d.name} class="{d.get("class","")}"> "{d_txt}"')
                    container = container.parent
            break
