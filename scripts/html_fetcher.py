import json

import requests

from bs4 import BeautifulSoup


def fetch_html(source_file):

    with open(
        source_file,
        "r",
        encoding="utf-8"
    ) as f:

        source = json.load(f)

    url = source["news_url"]

    selector = source["title_selector"]

    response = requests.get(

        url,

        headers={
            "User-Agent":
            "Mozilla/5.0"
        },

        timeout=30
    )

    soup = BeautifulSoup(
        response.text,
        "lxml"
    )

    news = []

    items = soup.select(
        selector
    )

    for item in items[:100]:

        title = item.get_text(
            strip=True
        )

        link = item.get(
            "href",
            ""
        )

        if link.startswith("/"):

            link = (
                source["homepage"]
                + link
            )

        news.append({

            "title": title,

            "publish_date": "",

            "source": source["name"],

            "url": link

        })

    return news
