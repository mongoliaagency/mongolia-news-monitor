import sys
sys.stdout.reconfigure(encoding='utf-8')

from bs4 import BeautifulSoup

with open('_html/newspress_mn.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("1. body 全部内容 (去 script/style)")
print("=" * 80)
body = soup.find('body')
if body:
    for script in body.find_all(['script', 'style']):
        script.decompose()
    text = body.get_text('\n', strip=True)
    print(text[:3000])

print("\n" + "=" * 80)
print("2. 所有 Vue 组件标签")
print("=" * 80)
import re
vue_tags = set(re.findall(r'<([a-z]+-[a-z]+[^>]*)', html))
for t in sorted(vue_tags):
    print(f"  <{t}")

print("\n" + "=" * 80)
print("3. 所有 div class 含内容的结构")
print("=" * 80)
for tag in soup.find_all('div'):
    cls = ' '.join(tag.get('class', []))
    if cls:
        text = tag.get_text(strip=True)[:80]
        if text and len(text) > 5:
            print(f"  div.{cls}: {text}")

print("\n" + "=" * 80)
print("4. 所有链接 (a tags)")
print("=" * 80)
for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(strip=True)[:80]
    if text and not href.startswith('javascript'):
        print(f"  {href:60s} -> {text}")

print("\n" + "=" * 80)
print("5. HTML 尾部 (最后 2000 字符)")
print("=" * 80)
print(html[-2000:])
