import json
import re
from pathlib import Path
from datetime import datetime

NEWS_DIR = Path("data/news")
DOCS_DIR = Path("docs")

STATUS_FILE = Path("data/status/runtime_status.json")

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def _mmdd(date_str):
    """Extract MM-DD from YYYY-MM-DD date string."""
    if date_str and len(date_str) >= 10 and date_str[4] == '-':
        return date_str[5:]  # return "MM-DD"
    return date_str

CATEGORY_ORDER = ["党政机关", "新闻媒体"]


def load_news_files():
    files = [
        f for f in NEWS_DIR.glob("*.json")
        if _DATE_PATTERN.match(f.stem)
    ]
    files.sort(reverse=True)
    return files


def load_status():
    default_status = {k: {"total": 0, "success": 0, "failed": 0, "failed_list": []} for k in CATEGORY_ORDER}
    if not STATUS_FILE.exists():
        return default_status

    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_day_page(date_str, news_list):
    # Group by category
    party_gov = []
    media = []
    for item in news_list:
        cat = item.get("category", "党政机关")
        if cat == "新闻媒体":
            media.append(item)
        else:
            party_gov.append(item)

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{date_str} - 蒙古国新闻</title>
<style>
::root {{
    color-scheme: light;
    font-family: 'Noto Sans', Arial, sans-serif;
    background: #f5f7fb;
    color: #202640;
}}
* {{
    box-sizing: border-box;
}}
body {{
    margin: 0;
    padding: 0;
    background: #f5f7fb;
}}
.container {{
    max-width: 1024px;
    margin: 0 auto;
    padding: 24px 20px 40px;
}}
header {{
    margin-bottom: 24px;
}}
h1 {{
    margin: 0 0 12px;
    font-size: 2rem;
    letter-spacing: 0.02em;
}}
h2 {{
    margin: 28px 0 14px;
    font-size: 1.3rem;
    color: #374151;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 6px;
}}
a.home-link {{
    display: inline-block;
    margin-top: 8px;
    color: #3b5bdb;
    text-decoration: none;
    font-weight: 500;
}}
a.home-link:hover {{
    text-decoration: underline;
}}
.news-item {{
    padding: 18px 18px 16px;
    border-radius: 16px;
    background: #ffffff;
    box-shadow: 0 14px 30px rgba(24, 37, 77, 0.08);
    margin-bottom: 14px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.news-item:hover {{
    transform: translateY(-2px);
    box-shadow: 0 18px 34px rgba(24, 37, 77, 0.12);
}}
.news-item a.title-link {{
    color: #171f36;
    font-size: 1.1rem;
    font-weight: 600;
    line-height: 1.5;
    text-decoration: none;
}}
.news-item a.title-link:hover {{
    color: #3b5bdb;
    text-decoration: underline;
}}
.news-meta {{
    margin-top: 10px;
    color: #6b7280;
    font-size: 0.95rem;
}}
</style>
</head>
<body>
<div class="container">
<header>
<h1>{date_str}</h1>
<p><a class="home-link" href="index.html">← 返回新闻列表</a></p>
<hr>
</header>
"""

    if party_gov:
        html += "<h2>党政机关</h2>"
        for item in party_gov:
            html += f"""
<div class="news-item">
<a class="title-link" href="{item['url']}" target="_blank">{item['title']}</a>
<div class="news-meta">来源：{item['source']} | 时间：{_mmdd(item.get('publish_date', ''))}</div>
</div>
"""

    if media:
        html += "<h2>新闻媒体</h2>"
        for item in media:
            html += f"""
<div class="news-item">
<a class="title-link" href="{item['url']}" target="_blank">{item['title']}</a>
<div class="news-meta">来源：{item['source']} | 时间：{_mmdd(item.get('publish_date', ''))}</div>
</div>
"""

    html += """
</div>
</body>
</html>
"""

    return html


def _build_category_summary(status):
    """Build HTML summary rows for each category."""
    parts = []
    for key in CATEGORY_ORDER:
        cat = status.get(key, {"total": 0, "success": 0, "failed": 0, "failed_list": []})
        parts.append(
            f"<div class=\"cat-group\">"
            f"<div class=\"cat-label\">{key}</div>"
            f"<span>总计：{cat['total']}</span>"
            f"<span class=\"ok\">成功：{cat['success']}</span>"
            f"<span class=\"fail\">失败：{cat['failed']}</span>"
            f"</div>"
        )
    return "\n".join(parts)


def _sort_failed_list(failed_list):
    """Sort failed_list so '连接失败' comes before '0 articles'."""
    connection_failures = [item for item in failed_list if item.get('error') == '连接失败']
    zero_articles = [item for item in failed_list if item.get('error') == '0 articles']
    others = [item for item in failed_list if item.get('error') not in ('连接失败', '0 articles')]
    return connection_failures + zero_articles + others


def _build_failures(status):
    """Build failure list HTML, grouped by category."""
    html = ""
    for key in CATEGORY_ORDER:
        cat = status.get(key, {"total": 0, "success": 0, "failed": 0, "failed_list": []})
        if cat["failed"] == 0:
            continue
        html += f"<div class=\"cat-fail\"><strong>{key}失败源：</strong><br>"
        sorted_list = _sort_failed_list(cat["failed_list"])
        for item in sorted_list:
            homepage = item.get('homepage', '#') or '#'
            display = f"{item.get('source', '')} - {item.get('error', '')}"
            html += f"<a href=\"{homepage}\" target=\"_blank\">{display}</a><br>"
        html += "</div>"
    return html


def build_index_page(files):
    status = load_status()
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>蒙古国新闻标题列表</title>
<style>
::root {{
    color-scheme: light;
    font-family: 'Noto Sans', Arial, sans-serif;
    background: #eef2f8;
    color: #1f2937;
}}
* {{
    box-sizing: border-box;
}}
body {{
    margin: 0;
    padding: 0;
    background: #eef2f8;
}}
.container {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 28px 22px 40px;
}}
.page-header {{
    margin-bottom: 22px;
}}
h1 {{
    margin: 0;
    font-size: 2.2rem;
    letter-spacing: 0.03em;
}}
.summary {{
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 14px;
    color: #4b5563;
}}
.cat-group {{
    background: #ffffff;
    padding: 12px 16px;
    border-radius: 14px;
    box-shadow: 0 10px 18px rgba(15, 23, 42, 0.06);
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
}}
.cat-label {{
    font-weight: 700;
    font-size: 1rem;
    color: #1e3a5f;
    margin-right: 4px;
}}
.cat-group span {{
    font-size: 0.92rem;
    padding: 4px 10px;
    border-radius: 999px;
    background: #f1f5f9;
}}
.cat-group span.ok {{
    color: #15803d;
    background: #dcfce7;
}}
.cat-group span.fail {{
    color: #b91c1c;
    background: #fee2e2;
}}
.all-total {{
    background: #1e3a5f;
    color: #fff;
    padding: 12px 18px;
    border-radius: 14px;
    font-weight: 600;
}}
.failures {{
    margin: 18px 0 28px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}}
.cat-fail {{
    padding: 18px;
    border-radius: 16px;
    background: #fff1f2;
    color: #b91c1c;
    border: 1px solid #fca5a5;
}}
.cat-fail a {{
    color: #991b1b;
    text-decoration: underline;
}}
.day-list {{
    display: grid;
    gap: 14px;
}}
.day-card {{
    background: #ffffff;
    padding: 18px 20px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    transition: transform 0.2s ease, border-color 0.2s ease;
}}
.day-card:hover {{
    transform: translateY(-2px);
    border-color: #c7d2fe;
}}
.day-card a {{
    color: #1d4ed8;
    font-size: 1.05rem;
    font-weight: 600;
    text-decoration: none;
}}
.day-card a:hover {{
    text-decoration: underline;
}}
</style>
</head>
<body>
<div class="container">
<section class="page-header">
<h1>蒙古国新闻标题列表</h1>
<div class="summary">
<span class="all-total">采集时间：{update_time}</span>
{_build_category_summary(status)}
</div>
</section>
"""

    failure_html = _build_failures(status)
    if failure_html:
        html += f"<section class=\"failures\">{failure_html}</section>"

    html += "<section class=\"day-list\">"

    for file in files:
        date_str = file.stem
        html += f"""
<div class=\"day-card\">
<a href=\"{date_str}.html\">{date_str}</a>
</div>
"""

    html += "</section>"
    html += "</div>"
    html += "</body>\n</html>"

    return html


def save_page(filename, content):
    DOCS_DIR.mkdir(exist_ok=True)
    output = DOCS_DIR / filename
    output.write_text(content, encoding="utf-8")


def main():
    files = load_news_files()
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            news_list = json.load(f)

        html = build_day_page(file.stem, news_list)
        save_page(f"{file.stem}.html", html)

    index_html = build_index_page(files)
    save_page("index.html", index_html)

    print("7 day pages generated.")


if __name__ == "__main__":
    main()
