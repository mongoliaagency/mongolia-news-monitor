#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify selectors against downloaded HTML for mod, nema, parliament."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from bs4 import BeautifulSoup
import re
from datetime import datetime

def test_source(name, html_file, items_sel, title_sel, link_sel, date_sel):
    print(f"\n{'='*50}")
    print(f"  TEST: {name}")
    print(f"  items: {items_sel}")
    print(f"  title: {title_sel}")
    print(f"  link:  {link_sel}")
    print(f"  date:  {date_sel}")
    print(f"{'='*50}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    
    items = soup.select(items_sel) if items_sel else []
    print(f"  Matched items: {len(items)}")
    
    if not items and title_sel:
        items = soup.select(title_sel)
        print(f"  Fallback to title_selector: {len(items)} items")
    
    found = 0
    for item in items[:20]:
        try:
            # Try with items_selector context
            if items_sel:
                title_node = item.select_one(title_sel) if title_sel else item
                link_node = item.select_one(link_sel) if link_sel else title_node
            else:
                title_node = item
                link_node = item
            
            title = title_node.get_text(strip=True) if title_node else ''
            if not title or len(title) < 10:
                continue
            
            href = link_node.get('href', '') if link_node else ''
            if not href:
                continue
            
            date_str = ''
            if date_sel:
                date_node = item.select_one(date_sel)
                if date_node:
                    raw = date_node.get_text(strip=True)
                    m = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', raw)
                    if m:
                        date_str = m.group(1)
            
            found += 1
            print(f"  [{found}] {title[:60]}")
            print(f"       href: {href[:80]}")
            print(f"       date: {date_str}")
        except Exception as e:
            print(f"  Error: {e}")
    
    if found == 0:
        print("  *** NO VALID ITEMS FOUND - SELECTORS MAY BE WRONG ***")
    else:
        print(f"\n  Total valid items: {found}")

test_source(
    'mod.gov.mn', '_fix_mod.html',
    '.td-block-span12, [class*="td_module"]',
    '.entry-title a, h3 a[href*="?p="]',
    '.entry-title a, h3 a[href*="?p="]',
    'time.entry-date'
)

test_source(
    'nema.gov.mn', '_fix_nema.html',
    'article.post-item, div.posts-detail',
    'h6 a[href^="/post/"]',
    'h6 a[href^="/post/"]',
    'div.post-date-category, div.post-date-category p'
)

test_source(
    'parliament.mn', '_fix_parliament.html',
    'div.col-md-8',
    'h3 a[href^="/nn/"]',
    'h3 a[href^="/nn/"]',
    'div.entry-meta'
)
