import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

from bs4 import BeautifulSoup

with open('_html/chig_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

result = {}

# Find all links
all_links = []
for a in soup.find_all('a', href=True):
    href = a['href']
    if href.startswith('http://') or href.startswith('https://'):
        all_links.append(href)
    elif href.startswith('/'):
        all_links.append(href)
result['total_links'] = len(all_links)
result['sample_links'] = list(set(all_links))[:80]

# Article containers: fr_news, news, today_news1, v_list, section_item_left, item
article_classes = ['fr_news', 'news', 'today_news1', 'today_news_content1', 'v_list', 'section_item_left', 'small_list', 'item']
for cls in article_classes:
    els = soup.find_all(class_=cls)
    if els:
        result[f'{cls}_count'] = len(els)
        sample = []
        for el in els[:5]:
            # get inner HTML snippet
            sample.append(str(el)[:500])
        result[f'{cls}_samples'] = sample

# Look for all links in news-related areas
# Find all href patterns
import re
hrefs = re.findall(r'href="([^"]+)"', html)
unique_hrefs = sorted(set(hrefs))
result['unique_hrefs'] = unique_hrefs[:100]

# Check for specific URL patterns
news_links = [h for h in unique_hrefs if '/news/' in h or '/article/' in h or '/read/' in h or '/detail/' in h or 'id=' in h or '/view/' in h]
result['news_pattern_links'] = news_links[:40]

# Check all / links
slash_links = [h for h in unique_hrefs if h.startswith('/') and len(h) > 3]
result['slash_links'] = slash_links[:60]

print(json.dumps(result, ensure_ascii=False, indent=2))
