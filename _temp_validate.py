import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from pathlib import Path

sources_dir = Path("config/sources")
errors = []
warnings = []

for f in sorted(sources_dir.glob("*.json")):
    try:
        with open(f, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
    except json.JSONDecodeError as e:
        errors.append(f"{f.name}: JSON syntax error - {e}")
        continue

    name = data.get('name', 'UNKNOWN')
    
    # Check critical field: source_type
    st = data.get('source_type')
    if not st:
        errors.append(f"{f.name} [{name}]: MISSING source_type")
    elif st not in ('html', 'rss', 'api', 'sitemap'):
        errors.append(f"{f.name} [{name}]: INVALID source_type='{st}'")
    
    # Check old incorrect field
    if 'type' in data and not st:
        errors.append(f"{f.name} [{name}]: uses 'type' instead of 'source_type'")
    
    # Check homepage
    hp = data.get('homepage')
    url = data.get('url')
    if not hp and not url:
        errors.append(f"{f.name} [{name}]: MISSING homepage")
    elif url and not hp:
        errors.append(f"{f.name} [{name}]: uses 'url' instead of 'homepage'")
    
    # Check status
    if not data.get('status'):
        errors.append(f"{f.name} [{name}]: MISSING status")
    
    # Check news_url for html type
    if st == 'html':
        if not data.get('news_url') and not data.get('date_url_template'):
            errors.append(f"{f.name} [{name}]: MISSING news_url (html type)")
        if 'requires_browser' not in data:
            warnings.append(f"{f.name} [{name}]: MISSING requires_browser (defaults to False)")
    
    # Check rss_url for rss type
    if st == 'rss':
        if not data.get('rss_url'):
            errors.append(f"{f.name} [{name}]: MISSING rss_url (rss type)")
    
    # Check api_url for api type
    if st == 'api':
        if not data.get('api_url'):
            errors.append(f"{f.name} [{name}]: MISSING api_url (api type)")

print(f"Total files: {len(list(sources_dir.glob('*.json')))}")
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")
print()

if errors:
    print("=== ERRORS ===")
    for e in errors:
        print(f"  ❌ {e}")
    print()

if warnings:
    print("=== WARNINGS ===")
    for w in warnings:
        print(f"  ⚠️ {w}")
    print()

if not errors and not warnings:
    print("✅ All files pass validation!")
elif not errors:
    print("✅ No critical errors found (warnings only)")
