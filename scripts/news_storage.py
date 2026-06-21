import json
from pathlib import Path
from datetime import datetime


def get_today_file():

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    news_dir = Path(
        "data/news"
    )

    news_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return news_dir / f"{today}.json"


def save_news(news_list):

    output_file = get_today_file()

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
