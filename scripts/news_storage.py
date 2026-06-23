import json

from pathlib import Path

from datetime import datetime
from datetime import timedelta


NEWS_DIR = Path("data/news")


def ensure_dir():

    NEWS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def save_news(news_list):

    ensure_dir()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    output_file = (
        NEWS_DIR /
        f"{today}.json"
    )

    output_file.write_text(

        json.dumps(
            news_list,
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

        except Exception:

            print(
                f"Skip: {file.name}"
            )
