import json
import feedparser
from pathlib import Path


def fetch_rss(source_file):

    with open(source_file, "r", encoding="utf-8") as f:
        source = json.load(f)

    rss_url = source["rss_url"]

    feed = feedparser.parse(rss_url)

    news = []

    for entry in feed.entries:

        item = {
            "title": entry.get("title", ""),
            "publish_date": entry.get("published", ""),
            "source": source["name"],
            "url": entry.get("link", "")
        }

        news.append(item)

    return news


if __name__ == "__main__":

    print(
        "rss_fetcher.py should be called by main.py"
    )
