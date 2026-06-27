"""全面验证项目文件"""
import json, os, sys, glob
from collections import defaultdict

ROOT = r"C:\Users\VictorXu\Documents\GitHub\mongolia-news-monitor"
errors = []
warnings = []

# ========== 1. 验证所有 JSON 配置文件 ==========
print("=" * 60)
print("1. Check config/sources/*.json")
print("=" * 60)

json_files = glob.glob(os.path.join(ROOT, "config", "sources", "*.json"))
required_fields = {"name", "url", "category", "items_selector", "title_selector",
                   "link_selector", "date_selector", "date_format", "source_type"}

for jf in sorted(json_files):
    try:
        with open(jf, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"[JSON Error] {os.path.basename(jf)}: {e}")
        continue
    
    basename = os.path.basename(jf)
    
    # Check required fields
    missing = required_fields - set(data.keys())
    if missing:
        errors.append(f"[Missing Field] {basename}: missing {missing}")
    
    # Check source_type valid
    valid_types = {"html", "api", "rss", "sitemap", "custom"}
    st = data.get("source_type")
    if st not in valid_types:
        warnings.append(f"[Unknown source_type] {basename}: '{st}'")
    
    # API source must have api_url
    if st == "api" and "api_url" not in data:
        errors.append(f"[API Missing api_url] {basename}")
    
    # Check items_selector
    if "items_selector" in data and not data["items_selector"]:
        warnings.append(f"[Empty items_selector] {basename}")
    
    # Check empty name
    if not data.get("name", "").strip():
        errors.append(f"[Empty Name] {basename}")
    
    # Check empty url
    if not data.get("url", "").strip():
        errors.append(f"[Empty URL] {basename}")
    
    # Check date_format
    if "date_format" not in data:
        warnings.append(f"[Missing date_format] {basename}")
    
    # Check date_attr for html sources
    if st == "html" and "date_attr" not in data:
        warnings.append(f"[HTML without date_attr] {basename}")

print(f"  JSON files: {len(json_files)}")
json_err_count = len([e for e in errors if 'JSON Error' in e or 'Missing Field' in e or 'API Missing' in e or 'Empty' in e or 'Missing date' in e])
print(f"  Errors: {json_err_count}")
print(f"  Warnings: {len(warnings)}")

# ========== 2. 检查 Python 脚本语法 ==========
print("\n" + "=" * 60)
print("2. Check Python Script Syntax")
print("=" * 60)

script_files = glob.glob(os.path.join(ROOT, "scripts", "*.py"))
root_py = glob.glob(os.path.join(ROOT, "_*.py"))
all_py = sorted(script_files + root_py)
py_errors = []

for pf in all_py:
    try:
        with open(pf, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, pf, 'exec')
    except SyntaxError as e:
        py_errors.append(f"[Python Syntax Error] {os.path.basename(pf)}: {e}")
    except Exception as e:
        py_errors.append(f"[Read Error] {os.path.basename(pf)}: {e}")

print(f"  Python files: {len(all_py)}")
print(f"  Syntax errors: {len(py_errors)}")
for pe in py_errors:
    print(f"    ERROR: {pe}")

errors.extend(py_errors)

# ========== 3. 检查根目录异常文件 ==========
print("\n" + "=" * 60)
print("3. Check Anomalous Files")
print("=" * 60)

root_files = os.listdir(ROOT)
for f in root_files:
    fpath = os.path.join(ROOT, f)
    if f == "$null":
        errors.append(f"[Anomalous File] '$null' exists in root - should be deleted")
        print(f"  WARN: Found $null empty file in root")
    # Check for non-underscore root py files (not standard in this project)
    if f.endswith(".py") and not f.startswith("_") and f not in ["requirements.txt", "README.md", ".gitignore"]:
        if not os.path.isdir(fpath):
            pass  # Not a warning - requirements.txt etc are fine

# ========== 4. 详细检查每个 config/sources JSON 内容 ==========
print("\n" + "=" * 60)
print("4. Detailed Config Review")
print("=" * 60)

# Read all configs and cross-check
for jf in sorted(json_files):
    with open(jf, 'r', encoding='utf-8') as f:
        data = json.load(f)
    basename = os.path.basename(jf)
    name = data.get("name", "")
    url = data.get("url", "")
    cat = data.get("category", "")
    st = data.get("source_type", "")
    
    # Check name existence
    if len(name) < 2:
        errors.append(f"[Short Name] {basename}: '{name}'")
    
    # Check category values
    valid_cats = {"党政机关", "新闻媒体", "金融机构", "能源", "其他"}
    if cat and cat not in valid_cats:
        warnings.append(f"[Unusual Category] {basename}: '{cat}'")
    
    # Print summary
    print(f"  {basename:30s} name={name:20s} type={st:10s} cat={cat:8s}")

# ========== 5. 检查 data/ 文件 ==========
print("\n" + "=" * 60)
print("5. Check data/ files")
print("=" * 60)

# Status files
status_dir = os.path.join(ROOT, "data", "status")
if os.path.exists(status_dir):
    for sf in os.listdir(status_dir):
        if sf.endswith(".json"):
            try:
                with open(os.path.join(status_dir, sf), 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"  OK: data/status/{sf}")
            except:
                errors.append(f"[JSON Error] data/status/{sf}")

# News files
news_dir = os.path.join(ROOT, "data", "news")
if os.path.exists(news_dir):
    for nf in sorted(os.listdir(news_dir)):
        if nf == ".gitkeep":
            continue
        fpath = os.path.join(news_dir, nf)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            if content.strip() == "" or content.strip() == "{}" or content.strip() == "[]":
                if nf not in ["parliament_mn.json", "nema_mn.json", "ulaanbaatar_mn.json"]:
                    warnings.append(f"[Empty/Small] data/news/{nf}")
                else:
                    print(f"  INFO: data/news/{nf} is intentionally empty/small (API-backed)")
            else:
                json.loads(content)
                # Check if it's a list of news items
                data = json.loads(content)
                if isinstance(data, list):
                    print(f"  OK: data/news/{nf} ({len(data)} items)")
                elif isinstance(data, dict):
                    print(f"  OK: data/news/{nf} (dict with {len(data)} keys)")
        except json.JSONDecodeError as e:
            errors.append(f"[JSON Error] data/news/{nf}: {e}")
        except Exception as e:
            errors.append(f"[Read Error] data/news/{nf}: {e}")

# ========== 6. Check docs HTML structure ==========
print("\n" + "=" * 60)
print("6. Check docs/ HTML files")
print("=" * 60)

html_files = glob.glob(os.path.join(ROOT, "docs", "*.html"))
for hf in sorted(html_files):
    try:
        with open(hf, 'r', encoding='utf-8') as f:
            content = f.read()
        if "</html>" not in content:
            warnings.append(f"[HTML incomplete] docs/{os.path.basename(hf)}: missing </html>")
        elif "<html" not in content.lower():
            warnings.append(f"[HTML incomplete] docs/{os.path.basename(hf)}: missing <html>")
        else:
            pass  # OK
    except Exception as e:
        errors.append(f"[Read Error] docs/{os.path.basename(hf)}: {e}")

print(f"  HTML files: {len(html_files)}")
html_warns = len([w for w in warnings if 'HTML incomplete' in w])
print(f"  HTML warnings: {html_warns}")

# ========== 汇总 ==========
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if errors:
    print(f"\n[FAIL] {len(errors)} error(s) found:")
    for i, e in enumerate(errors, 1):
        print(f"  {i}. {e}")
else:
    print("\n[OK] No errors found")

if warnings:
    print(f"\n[WARN] {len(warnings)} warning(s):")
    for i, w in enumerate(warnings, 1):
        print(f"  {i}. {w}")
else:
    print("[OK] No warnings")

print(f"\nTotal: {len(errors)} errors, {len(warnings)} warnings")
