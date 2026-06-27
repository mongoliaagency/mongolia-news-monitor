"""Analyze parliament.mn HTML to find news selectors."""
from bs4 import BeautifulSoup
import re

with open('_fix_parliament.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# Search for link patterns to /nn/
print("=== PARLIAMENT: Title links to /nn/ ===")
count = 0
for a in soup.find_all('a', href=True):
    href = a.get('href', '')
    txt = a.get_text(strip=True)
    if len(txt) > 10 and '/nn/' in href:
        count += 1
        cls = a.get('class', '')
        parent = a.parent
        gparent = parent.parent if parent else None
        p_cls = parent.get('class', '') if parent else ''
        gp_cls = gparent.get('class', '') if gparent else ''
        print(f'  [{count}] <a class="{cls}" href="{href}"> {txt[:80]} </a>')
        print(f'       parent: <{parent.name} class="{p_cls}">')
        print(f'       grandparent: <{gparent.name} class="{gp_cls}">' if gparent else '')
        
        # Search for date in ancestors
        for ancestor in [parent, gparent] + ([gparent.parent] if gparent else []):
            if ancestor:
                for d in ancestor.find_all(['time', 'span', 'div', 'p', 'small']):
                    d_txt = d.get_text(strip=True)
                    if re.search(r'\d{4}', d_txt) and len(d_txt) < 50 and '202' in d_txt:
                        print(f'       → date: <{d.name} class="{d.get("class","")}"> "{d_txt}"')
                # Also check text of ancestor
                ancestor_txt = ancestor.get_text(strip=True)
                dates = re.findall(r'\d{4}[./-]\d{1,2}[./-]\d{1,2}', ancestor_txt)
                if dates:
                    print(f'       → date in text: {dates[0]}')
        
        if count >= 5:
            break

print("\n=== PARLIAMENT: Date-containing elements ===")
for tag in soup.find_all(['time', 'span', 'div', 'p', 'small', 'li', 'td']):
    txt = tag.get_text(strip=True)
    if re.search(r'\d{4}', txt) and len(txt) < 60 and '202' in txt:
        cls = tag.get('class', '')
        print(f'  <{tag.name} class="{cls}"> "{txt}"')

print("\n=== PARLIAMENT: List/container structures ===")
for el in soup.select('ul, ol, .list, .news-list, [class*="list"], [class*="news"], .article-list, table'):
    cls = el.get('class', [])
    children = el.find_all('li', recursive=False) or el.find_all('div', recursive=False) or el.find_all('tr', recursive=False)
    if len(children) >= 2:
        print(f'  <{el.name} class="{cls}"> with {len(children)} children')
        first = children[0]
        print(f'    first child: <{first.name} class="{first.get("class","")}"> text: "{first.get_text(strip=True)[:100]}"')
        break
