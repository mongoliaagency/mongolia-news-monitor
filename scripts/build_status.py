import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))

CATEGORY_ORDER = ["党政机关", "新闻媒体"]


def build_status():
    status_dir = Path("data/status")
    status_dir.mkdir(parents=True, exist_ok=True)

    # Load runtime status from main.py output
    runtime_file = status_dir / "runtime_status.json"
    runtime = {}
    if runtime_file.exists():
        try:
            runtime = json.loads(runtime_file.read_text(encoding="utf-8"))
        except Exception:
            runtime = {}

    status = {
        "updated_at": datetime.now(BJT).strftime("%Y-%m-%d %H:%M:%S"),
        "categories": {},
    }

    total_all = 0
    success_all = 0
    failed_all = 0

    for key in CATEGORY_ORDER:
        cat = runtime.get(key, {"total": 0, "success": 0, "failed": 0, "failed_list": []})
        cat_total = cat.get("total", 0)
        cat_success = cat.get("success", 0)
        cat_failed = cat.get("failed", 0)
        rate = round(cat_success * 100 / cat_total, 1) if cat_total > 0 else 0

        status["categories"][key] = {
            "label": key,
            "total": cat_total,
            "success": cat_success,
            "failed": cat_failed,
            "success_rate": rate,
            "failed_list": cat.get("failed_list", []),
        }

        total_all += cat_total
        success_all += cat_success
        failed_all += cat_failed

    status["total_sources"] = total_all
    status["success_sources"] = success_all
    status["failed_sources"] = failed_all
    status["success_rate"] = round(success_all * 100 / total_all, 1) if total_all > 0 else 0

    return status


def save_status_json(status):
    output_file = Path("data/status/status.json")
    output_file.write_text(
        json.dumps(status, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


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


def _build_nav_bar():
    return """<nav class="nav-bar">
    <div class="nav-inner">
        <a class="nav-brand" href="index.html">蒙古国新闻监控</a>
        <div class="nav-links">
            <a href="index.html">首页</a>
            <a href="sources.html">采集源</a>
            <a href="status.html" class="active">运行状态</a>
        </div>
    </div>
</nav>"""


def build_status_html(status):
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>采集状态</title>
<style>
body {{ font-family: 'Noto Sans', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 0 20px; color: #1f2937; background: #eef2f8; }}
{_nav_css()}
h1 {{ font-size: 1.8rem; margin-top: 28px; }}
h2 {{ font-size: 1.2rem; margin-top: 28px; color: #374151; }}
.cat-box {{ background: #f9fafb; border-radius: 12px; padding: 16px 20px; margin: 14px 0; border: 1px solid #e5e7eb; }}
.cat-box h3 {{ margin: 0 0 8px; }}
.fail {{ color: #b91c1c; }}
.ok {{ color: #15803d; }}
ul {{ padding-left: 20px; }}
</style>
</head>
<body>
{_build_nav_bar()}
<h1>采集状态</h1>
<p>更新时间：{status["updated_at"]}</p>
<p>新闻源总数：{status["total_sources"]} | 成功：<span class="ok">{status["success_sources"]}</span> | 失败：<span class="fail">{status["failed_sources"]}</span> | 成功率：{status["success_rate"]}%</p>
"""

    for key in CATEGORY_ORDER:
        cat = status.get("categories", {}).get(key, {})
        if not cat:
            continue
        html += f"""
<div class="cat-box">
<h3>{cat.get('label', key)}</h3>
<p>总计：{cat['total']} | 成功：<span class="ok">{cat['success']}</span> | 失败：<span class="fail">{cat['failed']}</span> | 成功率：{cat['success_rate']}%</p>
"""
        if cat.get("failed_list"):
            html += "<h4>失败源</h4><ul>"
            # Sort: '连接失败' before '0 articles'
            sorted_list = sorted(cat["failed_list"], key=lambda x: (0 if x.get("error") == "连接失败" else 1 if x.get("error") == "0 articles" else 2))
            for item in sorted_list:
                name = item.get("source", "")
                error = item.get("error", "")
                html += f"<li>{name} - {error}</li>"
            html += "</ul>"
        html += "</div>"

    html += """
</body>
</html>
"""
    return html


def save_status_html(content):
    output_file = Path("docs/status.html")
    output_file.write_text(content, encoding="utf-8")


def main():
    status = build_status()
    save_status_json(status)
    html = build_status_html(status)
    save_status_html(html)
    print("Status page generated.")


if __name__ == "__main__":
    main()
