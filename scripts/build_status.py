import json
from pathlib import Path
from datetime import datetime


def build_status():

    status_dir = Path("data/status")

    status_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    status = {

        "updated_at":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "total_sources": 0,

        "success_sources": 0,

        "failed_sources": 0,

        "success_rate": 0,

        "failed_list": []
    }

    return status

def scan_sources():

    sources_dir = Path(
        "config/sources"
    )

    source_files = list(
        sources_dir.glob("*.json")
    )

    total = len(source_files)

    success = 0

    failed = 0

    failed_list = []

    for file in source_files:

        try:

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:

                source = json.load(f)

            if (
                source.get("status")
                == "active"
            ):

                success += 1

        except Exception:

            failed += 1

            failed_list.append(
                file.name
            )

    return (
        total,
        success,
        failed,
        failed_list
    )

def save_status_json(status):

    output_file = Path(
        "data/status/status.json"
    )

    output_file.write_text(

        json.dumps(
            status,
            ensure_ascii=False,
            indent=2
        ),

        encoding="utf-8"
    )

def build_status_html(status):

    html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="utf-8">

<title>采集状态</title>

</head>

<body>

<h1>采集状态</h1>

<p>
更新时间：
{status["updated_at"]}
</p>

<p>
新闻源总数：
{status["total_sources"]}
</p>

<p>
成功：
{status["success_sources"]}
</p>

<p>
失败：
{status["failed_sources"]}
</p>

<p>
成功率：
{status["success_rate"]}%
</p>

<h2>失败新闻源</h2>

<ul>
"""

    for item in status["failed_list"]:

        html += f"<li>{item}</li>"

    html += """

</ul>

</body>

</html>
"""

    return html

def save_status_html(content):

    output_file = Path(
        "docs/status.html"
    )

    output_file.write_text(

        content,

        encoding="utf-8"
    )

def main():

    status = build_status()

    (
        total,
        success,
        failed,
        failed_list
    ) = scan_sources()

    status["total_sources"] = total

    status["success_sources"] = success

    status["failed_sources"] = failed

    status["failed_list"] = failed_list

    if total > 0:

        status["success_rate"] = round(
            success * 100 / total,
            2
        )

    save_status_json(status)

    html = build_status_html(
        status
    )

    save_status_html(html)

    print(
        "Status page generated."
    )


if __name__ == "__main__":

    main()
