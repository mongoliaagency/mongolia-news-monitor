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

def load_today_news():

    output_file = get_today_file()

    if not output_file.exists():

        return []

    return json.loads(

        output_file.read_text(
            encoding="utf-8"
        )
    )
