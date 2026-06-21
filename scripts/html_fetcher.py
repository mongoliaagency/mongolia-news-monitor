import json

import requests

from bs4 import BeautifulSoup

from datetime import datetime

def fetch_html(source_file):

```
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

response.encoding = response.apparent_encoding

soup = BeautifulSoup(
    response.text,
    "lxml"
)

news = []

items = soup.select(selector)

for item in items[:100]:

    title = item.get_text(
        strip=True
    )

    if not title:
        continue

    link = item.get(
        "href",
        ""
    )

    if not link:
        continue

    if link.startswith("/"):

        link = (
            source["homepage"].rstrip("/")
            + link
        )

    elif link.startswith("//"):

        link = (
            "https:"
            + link
        )

    elif not link.startswith("http"):

        link = (
            source["homepage"].rstrip("/")
            + "/"
            + link.lstrip("/")
        )

    news.append({

        "title": title,

        "publish_date":
        datetime.now().strftime(
            "%a, %d %b %Y 00:00:00 GMT"
        ),

        "source":
        source["name"],

        "url":
        link

    })

return news
