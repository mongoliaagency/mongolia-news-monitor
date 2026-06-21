from news_storage import save_news

import json
from pathlib import Path

from rss_fetcher import fetch_rss
from html_fetcher import fetch_html

from build_html import build_html
from build_html import save_html

def load_sources():

```
sources_dir = Path("config/sources")

source_files = list(
    sources_dir.glob("*.json")
)

return source_files
```

def collect_news():

```
all_news = []

status = {

    "total": 0,

    "success": 0,

    "failed": 0,

    "failed_list": []
}

source_files = load_sources()

for source_file in source_files:

    try:

        with open(
            source_file,
            "r",
            encoding="utf-8"
        ) as f:

            source = json.load(f)

        if source.get("status") != "active":
            continue

        source_type = source.get(
            "source_type"
        )

        if source_type == "rss":

            news = fetch_rss(
                source_file
            )

        elif source_type == "html":

            news = fetch_html(
                source_file
            )

        else:

            continue

        all_news.extend(news)

        print(
            f"SUCCESS: {source['name']} "
            f"{len(news)} articles"
        )

    except Exception as e:

        print(
            f"ERROR: {source_file.name}"
        )

        print(e)

return all_news
```

def main():

```
all_news = collect_news()

save_news(all_news)

html = build_html(all_news)

save_html(html)

print(
    f"Total articles: {len(all_news)}"
)

print(
    "HTML generated successfully."
)
```

if **name** == "**main**":
main()
