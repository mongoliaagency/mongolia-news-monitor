import json
from pathlib import Path

from rss_fetcher import fetch_rss
from html_fetcher import fetch_html
from api_fetcher import fetch_api

from news_storage import save_news

from build_pages import main as build_pages
from build_status import main as build_status

def load_sources():
    sources_dir = Path("config/sources")

    source_files = list(sources_dir.glob("*.json"))

    return source_files

def save_runtime_status(status):
    output = Path("data/status/runtime_status.json")

    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

CATEGORY_ORDER = ["党政机关", "新闻媒体"]

def _init_category_status():
    return {
        "total": 0,
        "success": 0,
        "failed": 0,
        "failed_list": []
    }

def collect_news():
    all_news = []

    status = {k: _init_category_status() for k in CATEGORY_ORDER}

    source_files = load_sources()

    for source_file in source_files:
        source = None
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                source = json.load(f)

            if source.get("status") != "active":
                continue

            category = source.get("category", "党政机关")
            cat_status = status.setdefault(category, _init_category_status())
            cat_status["total"] += 1

            source_type = source.get("source_type")

            if source_type == "rss":
                news = fetch_rss(source_file)
            elif source_type == "html":
                news = fetch_html(source_file)
            elif source_type == "api":
                news = fetch_api(source_file)
            else:
                cat_status["failed"] += 1
                cat_status["failed_list"].append({
                    "source": source.get("name", source_file.name),
                    "homepage": source.get("homepage", "#"),
                    "error": "未知源类型"
                })
                print(f"ERROR: {source.get('name', source_file.name)} — 未知源类型")
                continue

            all_news.extend(news)

            if len(news) > 0:
                cat_status["success"] += 1
            else:
                cat_status["failed"] += 1
                cat_status["failed_list"].append({
                    "source": source["name"],
                    "homepage": source.get("homepage", "#"),
                    "error": "0 articles"
                })
                print(f"ERROR: {source['name']} — 无近期文章")

        except Exception as e:
            cat_status = status.get(source.get("category", "党政机关") if source else "党政机关", status["党政机关"])
            cat_status["failed"] += 1
            source_name = source_file.name
            source_homepage = "#"
            if source is not None:
                source_name = source.get("name", source_file.name)
                source_homepage = source.get("homepage", "#")
            cat_status["failed_list"].append({
                "source": source_name,
                "homepage": source_homepage,
                "error": "连接失败"
            })

            print(f"ERROR: {source_name} — 连接失败")

    return all_news, status

def main():
    all_news, status = collect_news()

    save_runtime_status(status)
    save_news(all_news)

    build_pages()
    build_status()

    print(f"Total articles: {len(all_news)}")
    print("HTML and status generated successfully.")


if __name__ == "__main__":
    main()
