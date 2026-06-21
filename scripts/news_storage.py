import json

from pathlib import Path

from datetime import datetime
from datetime import timedelta

from email.utils import parsedate_to_datetime


NEWS_DIR = Path("data/news")


def ensure_dir():

    NEWS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def parse_publish_date(date_str):

    try:

        dt = parsedate_to_datetime(
            date_str
        )

        return dt.strftime(
            "%Y-%m-%d"
        )

    except:

        return None


def save_news(news_list):

    ensure_dir()

    grouped = {}

    today = datetime.now().date()

    cutoff = today - timedelta(days=6)

    for item in news_list:

        publish_date = parse_publish_date(
            item["publish_date"]
        )

        if not publish_date:
            continue

        news_day = datetime.strptime(
            publish_date,
            "%Y-%m-%d"
        ).date()

        if news_day < cutoff:
            continue

        grouped.setdefault(
            publish_date,
            []
        ).append(item)

    for date_key, items in grouped.items():

        output_file = (
            NEWS_DIR /
            f"{date_key}.json"
        )

        output_file.write_text(

            json.dumps(
                items,
                ensure_ascii=False,
                indent=2
            ),

            encoding="utf-8"
        )

        print(
            f"Saved: {output_file}"
        )

    cleanup_old_files()


def cleanup_old_files():

    today = datetime.now().date()

    cutoff = today - timedelta(days=6)

    for file in NEWS_DIR.glob("*.json"):

        try:

            file_date = datetime.strptime(
                file.stem,
                "%Y-%m-%d"
            ).date()

            if file_date < cutoff:

                file.unlink()

                print(
                    f"Deleted: {file.name}"
                )

        except:

            pass
