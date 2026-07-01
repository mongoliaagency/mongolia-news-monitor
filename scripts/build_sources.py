"""Generate docs/sources.html — a page listing all configured news sources."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

BJT = timezone(timedelta(hours=8))
SOURCES_DIR = Path("config/sources")
DOCS_DIR = Path("docs")
CATEGORY_ORDER = ["党政机关", "新闻媒体"]
TYPE_LABELS = {
    "html": "网页抓取",
    "rss": "RSS订阅",
    "api": "API接口",
}

_SOURCE_HTML_ESC = str.maketrans({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"})


def _escape(text):
    return str(text).translate(_SOURCE_HTML_ESC)


def load_all_sources():
    """Read all source JSON files and return them grouped by category."""
    result = {key: [] for key in CATEGORY_ORDER}
    if not SOURCES_DIR.exists():
        return result

    for src_file in sorted(SOURCES_DIR.glob("*.json")):
        try:
            with open(src_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            continue

        name = cfg.get("name", src_file.stem)
        category = cfg.get("category", "党政机关")
        if category not in result:
            category = "党政机关"

        source_type = cfg.get("source_type", "html")
        result[category].append({
            "filename": src_file.stem,
            "name": name,
            "homepage": cfg.get("homepage", ""),
            "news_url": cfg.get("news_url", cfg.get("rss_url", cfg.get("api_url", ""))),
            "source_type": source_type,
            "type_label": TYPE_LABELS.get(source_type, source_type),
            "status": cfg.get("status", "active"),
            "requires_browser": cfg.get("requires_browser", False),
        })

    return result


def build_sources_page():
    all_sources = load_all_sources()
    update_time = datetime.now(BJT).strftime("%Y-%m-%d %H:%M")

    total_count = sum(len(v) for v in all_sources.values())

    # Generate source list HTML by category
    sections_html = ""
    for cat in CATEGORY_ORDER:
        items = all_sources.get(cat, [])
        if not items:
            continue

        active_count = sum(1 for s in items if s["status"] == "active")
        inactive_count = len(items) - active_count

        items_html = ""
        for s in items:
            status_badge = "active" if s["status"] == "active" else "inactive"
            status_text = "启用" if s["status"] == "active" else "停用"
            browser_badge = ""
            if s["requires_browser"]:
                browser_badge = '<span class="tag tag-browser">🖥 浏览器</span>'

            items_html += f"""
                <div class="source-card" data-status="{status_badge}">
                    <div class="source-header">
                        <span class="source-name">{_escape(s['name'])}</span>
                        <span class="badge badge-{status_badge}">{status_text}</span>
                        {browser_badge}
                    </div>
                    <div class="source-body">
                        <span class="source-type">{s['type_label']}</span>
                        <a class="source-url" href="{_escape(s['homepage'])}" target="_blank" rel="noopener">
                            {_escape(s['homepage'])}
                        </a>
                    </div>
                </div>"""

        sections_html += f"""
            <section class="cat-section">
                <h2 class="cat-title">
                    {cat}
                    <span class="cat-count">{len(items)}个源<span class="count-detail">（{active_count}启用 / {inactive_count}停用）</span></span>
                </h2>
                <div class="source-grid">
                    {items_html}
                </div>
            </section>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>采集源列表 - 蒙古国新闻监控</title>
<style>
:root {{
    color-scheme: light;
    font-family: 'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    background: #eef2f8;
    color: #1f2937;
}}
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    padding: 0;
    background: #eef2f8;
}}
.container {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 28px 22px 50px;
}}

/* ---- Navigation ---- */
.nav-bar {{
    background: #1e3a5f;
    padding: 0 22px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}}
.nav-inner {{
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 28px;
    height: 52px;
}}
.nav-brand {{
    color: #fff;
    font-weight: 700;
    font-size: 1.05rem;
    text-decoration: none;
    white-space: nowrap;
}}
.nav-links {{
    display: flex;
    gap: 6px;
}}
.nav-links a {{
    color: rgba(255,255,255,0.75);
    text-decoration: none;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.92rem;
    transition: all 0.15s;
}}
.nav-links a:hover,
.nav-links a.active {{
    color: #fff;
    background: rgba(255,255,255,0.12);
}}

/* ---- Page header ---- */
.page-header {{
    margin-bottom: 24px;
    padding-top: 8px;
}}
h1 {{
    margin: 0 0 8px;
    font-size: 2rem;
    letter-spacing: 0.02em;
}}
.page-meta {{
    color: #6b7280;
    font-size: 0.9rem;
    margin-top: 4px;
}}
.page-meta strong {{
    color: #1e3a5f;
}}

/* ---- Filter bar ---- */
.filter-bar {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 22px;
    align-items: center;
}}
.filter-bar input {{
    flex: 1;
    min-width: 200px;
    max-width: 400px;
    padding: 10px 16px;
    border: 1px solid #d1d5db;
    border-radius: 12px;
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.15s;
}}
.filter-bar input:focus {{
    border-color: #3b5bdb;
    box-shadow: 0 0 0 3px rgba(59,91,219,0.12);
}}
.filter-bar .filter-btn {{
    padding: 10px 18px;
    border: 1px solid #d1d5db;
    border-radius: 12px;
    font-size: 0.9rem;
    cursor: pointer;
    background: #fff;
    color: #374151;
    transition: all 0.15s;
}}
.filter-bar .filter-btn:hover {{
    background: #f1f5f9;
}}
.filter-bar .filter-btn.active-filter {{
    background: #1e3a5f;
    color: #fff;
    border-color: #1e3a5f;
}}

/* ---- Category sections ---- */
.cat-section {{
    margin-bottom: 30px;
}}
.cat-title {{
    font-size: 1.25rem;
    color: #1e3a5f;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 8px;
    margin: 0 0 14px;
    display: flex;
    align-items: baseline;
    gap: 10px;
}}
.cat-count {{
    font-size: 0.85rem;
    font-weight: 400;
    color: #6b7280;
}}
.count-detail {{
    color: #9ca3af;
}}
.source-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 12px;
}}

/* ---- Source card ---- */
.source-card {{
    background: #fff;
    border-radius: 14px;
    padding: 16px 18px;
    border: 1px solid #e5e7eb;
    transition: transform 0.15s, box-shadow 0.15s;
}}
.source-card:hover {{
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(15,23,42,0.08);
}}
.source-card.inactive-card {{
    opacity: 0.55;
}}
.source-header {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}}
.source-name {{
    font-weight: 600;
    font-size: 1rem;
    color: #1f2937;
}}
.badge {{
    font-size: 0.75rem;
    padding: 2px 10px;
    border-radius: 999px;
    font-weight: 500;
}}
.badge-active {{
    background: #dcfce7;
    color: #15803d;
}}
.badge-inactive {{
    background: #f3f4f6;
    color: #6b7280;
}}
.tag {{
    font-size: 0.73rem;
    padding: 2px 8px;
    border-radius: 999px;
    background: #ede9fe;
    color: #6d28d9;
}}
.tag-rss {{
    background: #fef3c7;
    color: #92400e;
}}
.tag-api {{
    background: #dbeafe;
    color: #1e40af;
}}
.source-body {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
}}
.source-type {{
    font-size: 0.8rem;
    padding: 2px 8px;
    border-radius: 6px;
    background: #f1f5f9;
    color: #475569;
    white-space: nowrap;
}}
.source-url {{
    font-size: 0.82rem;
    color: #3b5bdb;
    text-decoration: none;
    word-break: break-all;
    line-height: 1.4;
}}
.source-url:hover {{
    text-decoration: underline;
}}

/* ---- Footer ---- */
.page-footer {{
    margin-top: 40px;
    text-align: center;
    color: #9ca3af;
    font-size: 0.85rem;
}}

/* ---- Hidden utility ---- */
.hidden {{ display: none !important; }}
</style>
</head>
<body>

<nav class="nav-bar">
    <div class="nav-inner">
        <a class="nav-brand" href="index.html">📡 蒙古国新闻监控</a>
        <div class="nav-links">
            <a href="index.html">首页</a>
            <a href="sources.html" class="active">采集源</a>
            <a href="status.html">运行状态</a>
        </div>
    </div>
</nav>

<div class="container">
    <section class="page-header">
        <h1>采集源列表</h1>
        <div class="page-meta">
            共 <strong>{total_count}</strong> 个采集源 · 更新时间：{update_time}
        </div>
    </section>

    <div class="filter-bar">
        <input type="text" id="searchInput" placeholder="🔍 搜索采集源名称或网址…" oninput="applyFilters()">
        <button class="filter-btn active-filter" onclick="setFilter(this, 'all')">全部</button>
        <button class="filter-btn" onclick="setFilter(this, 'active')">仅启用</button>
        <button class="filter-btn" onclick="setFilter(this, '党政机关')">党政机关</button>
        <button class="filter-btn" onclick="setFilter(this, '新闻媒体')">新闻媒体</button>
        <button class="filter-btn" onclick="setFilter(this, 'html')">网页抓取</button>
        <button class="filter-btn" onclick="setFilter(this, 'rss')">RSS</button>
    </div>

    {sections_html}

    <div class="page-footer">
        采集源配置变更后，页面将在下一次采集任务执行时自动更新
    </div>
</div>

<script>
let currentFilter = 'all';

function applyFilters() {{
    const query = document.getElementById('searchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.source-card');
    const catSections = document.querySelectorAll('.cat-section');

    cards.forEach(card => {{
        const text = card.textContent.toLowerCase();
        const status = card.dataset.status;
        const catSection = card.closest('.cat-section');
        const catName = catSection ? catSection.querySelector('.cat-title').textContent.trim() : '';
        const matchSearch = !query || text.includes(query);
        const matchStatus = currentFilter === 'all' ||
            (currentFilter === 'active' && status === 'active') ||
            (currentFilter === '党政机关' && catName.startsWith('党政机关')) ||
            (currentFilter === '新闻媒体' && catName.startsWith('新闻媒体')) ||
            (currentFilter === 'html' && text.includes('网页抓取')) ||
            (currentFilter === 'rss' && text.includes('rss'));

        if (matchSearch && matchStatus) {{
            card.classList.remove('hidden');
        }} else {{
            card.classList.add('hidden');
        }}
    }});

    // Hide empty category sections
    catSections.forEach(section => {{
        const visible = section.querySelectorAll('.source-card:not(.hidden)');
        if (visible.length === 0) {{
            section.classList.add('hidden');
        }} else {{
            section.classList.remove('hidden');
        }}
    }});
}}

function setFilter(btn, filter) {{
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active-filter'));
    btn.classList.add('active-filter');
    applyFilters();
}}
</script>
</body>
</html>"""

    return html


def save_page(filename, content):
    DOCS_DIR.mkdir(exist_ok=True)
    output = DOCS_DIR / filename
    output.write_text(content, encoding="utf-8")


def main():
    html = build_sources_page()
    save_page("sources.html", html)
    print("sources.html generated.")


if __name__ == "__main__":
    main()
