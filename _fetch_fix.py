"""Download pages for mod, nema, parliament to analyze selectors."""
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

sources = {
    'mod': 'https://mod.gov.mn/?cat=23',
    'nema': 'https://nema.gov.mn/posts',
    'parliament': 'https://www.parliament.mn/nc/340/',
}

for name, url in sources.items():
    try:
        req = urllib.request.Request(url, headers=headers)
        r = urllib.request.urlopen(req, timeout=60)
        html = r.read().decode('utf-8', errors='ignore')
        with open(f'_fix_{name}.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'{name}: Status={r.status}, Length={len(html)}')
    except Exception as e:
        print(f'{name}: ERROR: {e}')
