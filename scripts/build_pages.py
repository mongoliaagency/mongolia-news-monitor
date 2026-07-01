import json
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

BJT = timezone(timedelta(hours=8))

NEWS_DIR = Path("data/news")
DOCS_DIR = Path("docs")
CONFIG_DIR = Path("config/sources")
STATUS_FILE = Path("data/status/status.json")

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

CATEGORY_ORDER = ["党政机关", "新闻媒体"]


def _mmdd(date_str):
    """Extract MM-DD from YYYY-MM-DD date string."""
    if date_str and len(date_str) >= 10 and date_str[4] == '-':
        return date_str[5:]
    return date_str


def _time_part(date_str):
    """Extract HH:MM from datetime string."""
    if date_str and len(date_str) >= 16:
        return date_str[11:16]
    return ""


def load_news_files():
    files = [
        f for f in NEWS_DIR.glob("*.json")
        if _DATE_PATTERN.match(f.stem)
    ]
    files.sort(reverse=True)
    return files


def _load_source_configs():
    """Load all source configuration files."""
    sources = []
    for f in sorted(CONFIG_DIR.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            cfg = json.load(fh)
            cfg["_file"] = f.stem
            sources.append(cfg)
    return sources


def _load_detailed_status():
    """Load detailed status from status.json to know per-source success/failure."""
    if not STATUS_FILE.exists():
        return {}
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Build lookup: source_name -> {"status": "failed", "error": "..."}
    lookup = {}
    for cat_key in CATEGORY_ORDER:
        cat = data.get("categories", {}).get(cat_key, {})
        for item in cat.get("failed_list", []):
            lookup[item["source"]] = {"status": "failed", "error": item.get("error", "")}
    # All other sources in that category are success (inferred)
    all_sources = _load_source_configs()
    for s in all_sources:
        name = s.get("name", "")
        if name not in lookup:
            is_active = s.get("status", "active") == "active"
            if is_active:
                lookup[name] = {"status": "success", "error": ""}
            else:
                lookup[name] = {"status": "paused", "error": ""}
    return lookup


def _load_today_news():
    """Load today's news articles."""
    today_str = datetime.now(BJT).strftime("%Y-%m-%d")
    today_file = NEWS_DIR / f"{today_str}.json"
    if not today_file.exists():
        return []
    with open(today_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_past_news(max_days=7):
    """Load past days' news (not including today), up to max_days."""
    today_str = datetime.now(BJT).strftime("%Y-%m-%d")
    past = []
    for f in sorted(NEWS_DIR.glob("*.json"), reverse=True):
        date_str = f.stem
        if not _DATE_PATTERN.match(date_str):
            continue
        if date_str >= today_str:
            continue
        with open(f, "r", encoding="utf-8") as fh:
            items = json.load(fh)
        for item in items:
            item["_date"] = date_str
        past.extend(items)
        # Limit to unique dates
        unique_dates = {it["_date"] for it in past}
        if len(unique_dates) >= max_days:
            break
    return past


# ====== NAVIGATION BAR ======


def _build_nav_bar(active_page=""):
    links = [
        ("index.html", "首页"),
        ("sources.html", "采集源"),
        ("status.html", "运行状态"),
    ]
    items = []
    for href, label in links:
        cls = ' class="active"' if href.startswith(active_page) else ""
        items.append(f'<a href="{href}"{cls}>{label}</a>')
    return f"""<nav class="nav-bar">
    <div class="nav-inner">
        <a class="nav-brand" href="index.html">蒙古国新闻监控</a>
        <div class="nav-links">{"".join(items)}</div>
    </div>
</nav>"""


def _nav_css():
    return """
.nav-bar {
    background: #1e3a5f;
    padding: 0 22px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}
.nav-inner {
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 28px;
    height: 52px;
}
.nav-brand {
    color: #fff;
    font-weight: 700;
    font-size: 1.05rem;
    text-decoration: none;
    white-space: nowrap;
}
.nav-links {
    display: flex;
    gap: 6px;
}
.nav-links a {
    color: rgba(255,255,255,0.75);
    text-decoration: none;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.92rem;
    transition: all 0.15s;
}
.nav-links a:hover,
.nav-links a.active {
    color: #fff;
    background: rgba(255,255,255,0.12);
}
"""


# ====== DAY PAGE (individual date page) ======


def build_day_page(date_str, news_list):
    party_gov = []
    media = []
    for item in news_list:
        cat = item.get("category", "党政机关")
        if cat == "新闻媒体":
            media.append(item)
        else:
            party_gov.append(item)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{date_str} - 蒙古国新闻</title>
<style>
:root {{
    color-scheme: light;
    font-family: 'Noto Sans', Arial, sans-serif;
    background: #f5f7fb;
    color: #202640;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 0; background: #f5f7fb; }}
{_nav_css()}
.container {{
    max-width: 1024px;
    margin: 0 auto;
    padding: 24px 20px 40px;
}}
header {{ margin-bottom: 24px; }}
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
a.home-link:hover {{ text-decoration: underline; }}
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
{_build_nav_bar("")}
<div class="container">
<header>
<h1>{date_str}</h1>
<p><a class="home-link" href="index.html">← 返回新闻列表</a></p>
<hr>
</header>"""

    if party_gov:
        html += "<h2>党政机关</h2>"
        for item in party_gov:
            html += f"""
<div class="news-item">
<a class="title-link" href="{item['url']}" target="_blank">{item['title']}</a>
<div class="news-meta">来源：{item['source']} | 时间：{_mmdd(item.get('publish_date', ''))}</div>
</div>"""

    if media:
        html += "<h2>新闻媒体</h2>"
        for item in media:
            html += f"""
<div class="news-item">
<a class="title-link" href="{item['url']}" target="_blank">{item['title']}</a>
<div class="news-meta">来源：{item['source']} | 时间：{_mmdd(item.get('publish_date', ''))}</div>
</div>"""

    html += """
</div>
</body>
</html>"""
    return html


# ====== INDEX PAGE (two-tab design) ======


def _index_css():
    return """
/* Tab bar */
.tab-bar {
    display: flex;
    gap: 0;
    margin-bottom: 24px;
    background: #fff;
    border-radius: 14px;
    padding: 5px;
    box-shadow: 0 4px 16px rgba(15,23,42,0.06);
}
.tab-btn {
    flex: 1;
    text-align: center;
    padding: 14px 20px;
    border: none;
    background: transparent;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    border-radius: 10px;
    color: #64748b;
    transition: all 0.2s;
    font-family: inherit;
}
.tab-btn.active {
    background: #1e3a5f;
    color: #fff;
    box-shadow: 0 4px 12px rgba(30,58,95,0.3);
}
.tab-btn:hover:not(.active) {
    background: #f1f5f9;
    color: #334155;
}
.tab-content { display: none; }
.tab-content.active { display: block; }

/* Update time */
.update-time {
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 20px;
    padding: 10px 16px;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* Quick stats */
.quick-stats {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}
.stat-card {
    background: #fff;
    padding: 14px 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    min-width: 100px;
}
.stat-num {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1e3a5f;
}
.stat-label {
    font-size: 0.8rem;
    color: #64748b;
}

/* Category heading */
.cat-heading {
    font-size: 1.4rem;
    margin: 28px 0 16px;
    color: #1e3a5f;
    border-bottom: 3px solid #3b82f6;
    padding-bottom: 8px;
    display: flex;
    align-items: baseline;
    gap: 10px;
}
.cat-count {
    font-size: 0.85rem;
    color: #6b7280;
    font-weight: 400;
}

/* Source block */
.source-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.source-block {
    background: #fff;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    overflow: hidden;
    transition: box-shadow 0.2s;
}
.source-block:hover {
    box-shadow: 0 6px 20px rgba(15,23,42,0.08);
}
.source-header {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    padding: 14px 18px;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
}
.source-name {
    font-weight: 700;
    font-size: 1.02rem;
    color: #1d4ed8;
    text-decoration: none;
    transition: color 0.15s;
}
.source-name:hover {
    color: #1e40af;
    text-decoration: underline;
}
.source-badges {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    margin-left: auto;
}

/* Badges */
.badge {
    font-size: 0.78rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    white-space: nowrap;
}
.badge-success { background: #dcfce7; color: #15803d; }
.badge-failed { background: #fee2e2; color: #b91c1c; }
.badge-conn-fail { background: #fef3c7; color: #92400e; }
.badge-zero { background: #f1f5f9; color: #64748b; }
.badge-paused { background: #e0e7ff; color: #4338ca; }
.tag {
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 6px;
    background: #f1f5f9;
    color: #64748b;
    white-space: nowrap;
}
.tag-browser { background: #fef3c7; color: #92400e; }
.tag-rss { background: #fce7f3; color: #9d174d; }
.article-count {
    font-size: 0.8rem;
    color: #6b7280;
    font-weight: 500;
}

/* News list in source */
.source-news-list {
    list-style: none;
    margin: 0;
    padding: 8px 0;
}
.source-news-list li {
    padding: 10px 18px;
    display: flex;
    align-items: baseline;
    gap: 10px;
    border-bottom: 1px solid #f1f5f9;
}
.source-news-list li:last-child { border-bottom: none; }
.source-news-list a {
    flex: 1;
    color: #1f2937;
    text-decoration: none;
    font-size: 0.95rem;
    line-height: 1.5;
    transition: color 0.15s;
}
.source-news-list a:hover { color: #3b5bdb; }
.news-time {
    font-size: 0.82rem;
    color: #9ca3af;
    white-space: nowrap;
}
.no-news {
    padding: 16px 18px;
    color: #9ca3af;
    font-size: 0.9rem;
}

/* Past news */
.date-subhead {
    font-size: 1.05rem;
    color: #374151;
    margin: 20px 0 10px;
    padding-left: 4px;
    font-weight: 600;
}
.past-news-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.past-news-list li {
    padding: 10px 16px;
    background: #fff;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: baseline;
    gap: 12px;
    transition: box-shadow 0.15s;
}
.past-news-list li:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.past-news-list a {
    flex: 1;
    color: #1f2937;
    text-decoration: none;
    font-size: 0.92rem;
    line-height: 1.5;
}
.past-news-list a:hover { color: #3b5bdb; }
.past-source {
    font-size: 0.8rem;
    color: #9ca3af;
    white-space: nowrap;
}

@media (max-width: 768px) {
    .source-header { flex-direction: column; align-items: flex-start; }
    .source-badges { margin-left: 0; }
    .tab-btn { font-size: 0.9rem; padding: 12px 14px; }
}
"""


def _build_source_card(cfg, status_info, news_items):
    """Build HTML for a single source block in the today tab."""
    name = cfg.get("name", "Unknown")
    homepage = cfg.get("homepage", "#")
    is_active = cfg.get("status", "active") == "active"
    browser = cfg.get("requires_browser", False)
    src_type = cfg.get("source_type", "html")

    # Status badge
    if not is_active:
        badge_html = '<span class="badge badge-paused">暂停</span>'
    elif status_info["status"] == "failed":
        err = status_info["error"]
        if "连接失败" in err:
            badge_html = '<span class="badge badge-conn-fail">连接失败</span>'
        elif "0 articles" in err:
            badge_html = '<span class="badge badge-zero">今日无文章</span>'
        else:
            badge_html = '<span class="badge badge-failed">失败</span>'
    else:
        badge_html = '<span class="badge badge-success">成功</span>'

    # Tech tags
    tags = []
    if browser:
        tags.append('<span class="tag tag-browser">🌐 浏览器</span>')
    if src_type == "rss":
        tags.append('<span class="tag tag-rss">RSS</span>')
    else:
        tags.append('<span class="tag">HTML</span>')

    html = f'''<div class="source-block">
    <div class="source-header">
        <a class="source-name" href="{homepage}" target="_blank" title="{homepage}">{name}</a>
        <div class="source-badges">
            {badge_html}
            {"".join(tags)}
            <span class="article-count">{len(news_items)} 篇</span>
        </div>
    </div>'''

    if news_items:
        html += '<ul class="source-news-list">'
        for item in news_items:
            title = item.get("title", "")
            url = item.get("url", "#")
            pub = _time_part(item.get("publish_date", ""))
            html += f'''<li>
                <a href="{url}" target="_blank">{title}</a>
                <span class="news-time">{pub}</span>
            </li>'''
        html += '</ul>'
    else:
        html += '<div class="no-news">暂无今日新闻</div>'

    html += '</div>'
    return html


def _build_today_tab(sources, source_status_lookup, news_by_source):
    """Build the '今日采集' tab HTML."""
    update_time = datetime.now(BJT).strftime("%Y-%m-%d %H:%M")
    today_str = datetime.now(BJT).strftime("%Y-%m-%d")

    html = f'<div id="tab-today" class="tab-content active">'
    html += f'<div class="update-time">📅 采集时间：{update_time} | 今日日期：{today_str}</div>'

    # Quick stats
    total_articles = sum(len(v) for v in news_by_source.values())
    total_sources = len(sources)
    active_sources = sum(1 for s in sources if s.get("status", "active") == "active")
    success_count = sum(1 for s in sources
                        if source_status_lookup.get(s.get("name", ""), {}).get("status") == "success")

    html += f'''<div class="quick-stats">
    <div class="stat-card"><span class="stat-num">{total_articles}</span><span class="stat-label">今日文章</span></div>
    <div class="stat-card"><span class="stat-num">{success_count}/{active_sources}</span><span class="stat-label">采集成功</span></div>
    <div class="stat-card"><span class="stat-num">{total_sources}</span><span class="stat-label">采集源总数</span></div>
</div>'''

    for cat in CATEGORY_ORDER:
        cat_sources = [s for s in sources if s.get("category") == cat]
        if not cat_sources:
            continue

        html += f'<h2 class="cat-heading">{cat}</h2>'
        html += '<div class="source-list">'

        for cfg in cat_sources:
            name = cfg.get("name", "")
            sinfo = source_status_lookup.get(name, {"status": "unknown", "error": ""})
            items = news_by_source.get(name, [])
            html += _build_source_card(cfg, sinfo, items)

        html += '</div>'

    html += '</div>'
    return html


def _build_past_tab(past_news):
    """Build the '往日采集（近七天）' tab HTML with aggregated past news."""
    html = '<div id="tab-past" class="tab-content">'

    if not past_news:
        html += '<p style="color:#9ca3af;text-align:center;padding:40px;">暂无往日采集数据</p>'
        html += '</div>'
        return html

    for cat in CATEGORY_ORDER:
        cat_items = [it for it in past_news if it.get("category") == cat]
        if not cat_items:
            continue

        # Sort by date desc
        cat_items.sort(key=lambda x: (x.get("_date", ""), x.get("source", "")), reverse=True)

        html += f'<h2 class="cat-heading">{cat} <span class="cat-count">{len(cat_items)} 篇</span></h2>'

        by_date = defaultdict(list)
        for item in cat_items:
            by_date[item["_date"]].append(item)

        for date_str in sorted(by_date.keys(), reverse=True):
            items = by_date[date_str]
            html += f'<h3 class="date-subhead">{date_str} ({len(items)} 篇)</h3>'
            html += '<ul class="past-news-list">'
            for item in items:
                title = item.get("title", "")
                url = item.get("url", "#")
                source = item.get("source", "")
                html += f'''<li>
                    <a href="{url}" target="_blank">{title}</a>
                    <span class="past-source">{source}</span>
                </li>'''
            html += '</ul>'

    html += '</div>'
    return html


def build_index_page(files):
    """Build the new two-tab index page."""
    sources = _load_source_configs()
    source_status_lookup = _load_detailed_status()
    today_news = _load_today_news()
    past_news = _load_past_news(max_days=7)

    # Group today's news by source name
    news_by_source = defaultdict(list)
    for item in today_news:
        src = item.get("source", "")
        news_by_source[src].append(item)

    # Keep daily date files for the daily pages (referenced elsewhere)
    # files param is still used in main() for individual day pages

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>蒙古国新闻监控</title>
<style>
:root {{
    color-scheme: light;
    font-family: 'Noto Sans', 'Microsoft YaHei', Arial, sans-serif;
    background: #eef2f8;
    color: #1f2937;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 0; background: #eef2f8; }}
{_nav_css()}
.container {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 24px 22px 40px;
}}
{_index_css()}
</style>
</head>
<body>
{_build_nav_bar("index")}
<div class="container">

<div class="tab-bar">
    <button class="tab-btn active" onclick="switchTab('today', this)">📰 今日采集</button>
    <button class="tab-btn" onclick="switchTab('past', this)">📅 往日采集（近七天）</button>
</div>

<script>
function switchTab(name, btn) {{
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + name).classList.add('active');
}}
</script>

{_build_today_tab(sources, source_status_lookup, news_by_source)}
{_build_past_tab(past_news)}

</div>
</body>
</html>"""

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

    print("Pages generated successfully.")


if __name__ == "__main__":
    main()
