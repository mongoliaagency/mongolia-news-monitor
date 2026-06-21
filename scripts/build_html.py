from pathlib import Path
from datetime import datetime


def build_html(news_data):

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">

<head>

<meta charset="utf-8">

<title>蒙古国新闻标题列表</title>

<style>

body {{
    font-family: Arial, sans-serif;
    max-width: 1200px;
    margin: 30px auto;
    padding: 20px;
    line-height: 1.6;
}}

h1 {{
    margin-bottom: 10px;
}}

.update-time {{
    color: #666;
    margin-bottom: 20px;
}}

.news {{
    border-bottom: 1px solid #dddddd;
    padding: 15px 0;
}}

.title {{
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 8px;
}}

.source {{
    color: #666666;
    font-size: 14px;
}}

a {{
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

</style>

</head>

<body>

<h1>蒙古国新闻标题列表</h1>

<div class="update-time">
更新时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
</div>

<hr>

"""

    for item in news_data:

        html += f"""
<div class="news">

<div class="title">
<a href="{item['url']}" target="_blank">
{item['title']}
</a>
</div>

<div class="source">
来源：{item['source']}
<br>
发布日期：{item['publish_date']}
</div>

</div>
"""

    html += """

</body>

</html>

"""

    return html


def save_html(content):

    output_dir = Path("docs")

    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "index.html"

    output_file.write_text(
        content,
        encoding="utf-8"
    )


if __name__ == "__main__":

    sample_news = [

        {
            "title": "测试新闻标题1",
            "publish_date": "2026-06-21",
            "source": "Montsame",
            "url": "https://montsame.mn"
        },

        {
            "title": "测试新闻标题2",
            "publish_date": "2026-06-21",
            "source": "Montsame",
            "url": "https://montsame.mn"
        },

        {
            "title": "测试新闻标题3",
            "publish_date": "2026-06-21",
            "source": "News.mn",
            "url": "https://news.mn"
        }

    ]

    html = build_html(sample_news)

    save_html(html)

    print("HTML generated successfully.")
