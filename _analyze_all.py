#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analyze mod.gov.mn, nema.gov.mn, parliament.mn HTML structures."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from bs4 import BeautifulSoup
import re

def analyze(name, html_file, patterns):
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')

    print(f"\n{'='*60}")
    print(f"  ANALYSIS: {name}")
    print(f"{'='*60}")

    for label, selector in patterns:
        print(f"\n--- {label} ---")
        try:
            els = soup.select(selector)
            for el in els[:8]:
                txt = el.get_text(strip=True)[:100]
                cls = el.get('class', '')
                href = el.get('href', '')
                print(f"  <{el.name} class='{cls}' href='{href}'> {txt}")
        except Exception as e:
            print(f"  Error: {e}")

    # Always show title links
    print("\n--- Title links ---")
    for a in soup.find_all('a', href=True):
        txt = a.get_text(strip=True)
        href = a.get('href', '')
        if len(txt) > 10 and any(kw in href for kw in ['post', 'news', 'article', '/nn/', '/i/', 'entry', 'detail']):
            parent = a.parent
            gp = parent.parent if parent else None
            print(f"  <a class='{a.get('class','')}' href='{href}'> {txt[:70]} </a>")
            print(f"    parent: <{parent.name} class='{parent.get('class','')}'>")
            if gp:
                print(f"    grandparent: <{gp.name} class='{gp.get('class','')}'>")

    # Date elements
    print("\n--- Date elements ---")
    for tag in soup.find_all(['time', 'span', 'div', 'p', 'small']):
        txt = tag.get_text(strip=True)
        if re.search(r'\d{4}[-./]\d{1,2}[-./]\d{1,2}', txt) and len(txt) < 60:
            print(f"  <{tag.name} class='{tag.get('class','')}'> '{txt}'")
            if len([x for x in dir()]) > 5:
                print(f"    parent: <{tag.parent.name} class='{tag.parent.get('class','')}'>")

    # Item containers
    print("\n--- List/container structures ---")
    for el in soup.select('[class*="list"], [class*="news"], [class*="post"], [class*="article"], article, ul, ol'):
        children = list(el.find_all(['li', 'div', 'article'], recursive=False))
        if 2 <= len(children) <= 30:
            cls = el.get('class', [])
            print(f"  <{el.name} class='{cls}'> has {len(children)} children")
            first = children[0]
            f_txt = first.get_text(strip=True)[:120]
            print(f"    1st child <{first.name} class='{first.get('class','')}'>: {f_txt}")
            # Find date in first child
            for d in first.find_all(['time', 'span', 'small', 'div', 'p']):
                dt = d.get_text(strip=True)
                if re.search(r'\d{4}', dt) and len(dt) < 40:
                    print(f"      date: <{d.name} class='{d.get('class','')}'> '{dt}'")
            break  # Just show the first matching container


# MOD
analyze('mod.gov.mn', '_fix_mod.html', [
    ('Article elements', 'article, [class*="post"], [class*="entry"]'),
    ('Headings with links', 'h1 a, h2 a, h3 a, h4 a'),
    ('Date-class elements', '[class*="date"], [class*="time"], [class*="meta"], time'),
])

# NEMA
analyze('nema.gov.mn', '_fix_nema.html', [
    ('Article elements', 'article, [class*="post"], [class*="news"]'),
    ('Headings with links', 'h1 a, h2 a, h3 a, h4 a, h5 a, h6 a'),
    ('Date-class elements', '[class*="date"], [class*="time"], [class*="meta"], time'),
])

# PARLIAMENT
analyze('parliament.mn', '_fix_parliament.html', [
    ('Article elements', 'article, [class*="post"], [class*="news"], [class*="list"]'),
    ('Headings with links', 'h1 a, h2 a, h3 a, h4 a, h5 a'),
    ('Date-class elements', '[class*="date"], [class*="time"], [class*="meta"], time'),
])
