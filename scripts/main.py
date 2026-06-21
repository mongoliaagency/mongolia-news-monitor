import json
from pathlib import Path

from rss_fetcher import fetch_rss
from html_fetcher import fetch_html

from news_storage import save_news

from build_html import build_html
from build_html import save_html


def load_sources():

    sources_dir = Path("config/sources")

    source_files = list(
        sources_dir.glob("*.json")
    )

    return source_files


def save_runtime_status(status):

    output = Path(
        "data/status/runtime_status.json"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            status,
            f,
            ensure_ascii=False,
            indent=2
        )


def collect_news():

    all_news = []

    status = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "failed_list": []
    }

    source_files = load_sources()

    for source_file in source_files:

        status["total"] += 1

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

            if len(news) > 0:

                status["success"] += 1

            else:

                status["failed"] += 1

                status["failed_list"].append({
                    "source": source["name"],
                    "error": "0 articles"
                })

            print(
                f"SUCCESS: {source['name']} "
                f"{len(news)} articles"
            )

        except Exception as e:

            status["failed"] += 1

            status["failed_list"].append({
                "source": source_file.name,
                "error": str(e)
            })

            print(
                f"ERROR: {source_file.name}"
            )

            print(e)

    return all_news, status


def main():

    all_news, status = collect_news()

    save_runtime_status(status)

    save_news(all_news)

    html = build_html(all_news)

    save_html(html)

    print(
        f"Total articles: {len(all_news)}"
    )

    print(
        "HTML generated successfully."
    )


if __name__ == "__main__":
    main()
