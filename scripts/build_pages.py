import json

from pathlib import Path

from datetime import datetime


NEWS_DIR = Path("data/news")

DOCS_DIR = Path("docs")


def load_news_files():

    files = list(
        NEWS_DIR.glob("*.json")
    )

    files.sort(
        reverse=True
    )

    return files


def build_day_page(
    date_str,
    news_list
):

    html = f"""
<!DOCTYPE html>
<html>

<head>

<meta charset="utf-8">

<title>{date_str}</title>

<style>

body {{
    font-family: Arial;
    max-width: 1200px;
    margin: auto;
    padding: 20px;
}}

.news {{
    margin-bottom: 12px;
}}

.date {{
    color: gray;
}}

</style>

</head>

<body>

<h1>{date_str}</h1>

<p>
<a href="index.html">
返回首页
</a>
</p>

<hr>

"""

    for item in news_list:

        html += f"""
<div class="news">

<a href="{item['url']}"
target="_blank">

{item['title']}

</a>

<br>

<span class="date">

[{item['source']}]

</span>

</div>
"""

    html += """

</body>

</html>

"""

    return html


def build_index_page(files):

    update_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    html = f"""
<!DOCTYPE html>
<html>

<head>

<meta charset="utf-8">

<title>
蒙古国新闻标题列表
</title>

<style>

body {{
    font-family: Arial;
    max-width: 1200px;
    margin: auto;
    padding: 20px;
}}

.day-link {{
    margin: 10px 0;
    font-size: 20px;
}}

</style>

</head>

<body>

<h1>
蒙古国新闻标题列表
</h1>

<p>
更新时间：
{update_time}
</p>

<hr>

"""

    for file in files:

        date_str = file.stem

        html += f"""

<div class="day-link">

<a href="{date_str}.html">

{date_str}

</a>

</div>

"""

    html += """

</body>

</html>

"""

    return html


def save_page(
    filename,
    content
):

    DOCS_DIR.mkdir(
        exist_ok=True
    )

    output = (
        DOCS_DIR /
        filename
    )

    output.write_text(
        content,
        encoding="utf-8"
    )


def main():

    files = load_news_files()

    for file in files:

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

            news_list = json.load(f)

        html = build_day_page(
            file.stem,
            news_list
        )

        save_page(
            f"{file.stem}.html",
            html
        )

    index_html = build_index_page(
        files
    )

    save_page(
        "index.html",
        index_html
    )

    print(
        "7 day pages generated."
    )


if __name__ == "__main__":

    main()
