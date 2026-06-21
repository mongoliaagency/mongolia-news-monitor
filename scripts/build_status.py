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
