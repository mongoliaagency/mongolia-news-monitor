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

    # 去重：按照归一化后的标题保留首条记录，确保不同来源的重复标题只保留一次
    def normalize_title(t):
        if not t:
            return ""
        # 小写并去除首尾空白
        s = t.strip().lower()
        # 合并连续空白为单个空格
        s = " ".join(s.split())
        return s

    seen = set()
    unique_news = []
    for item in news_list:
        title = item.get("title", "")
        key = normalize_title(title)
        if key in seen:
            continue
        seen.add(key)
        unique_news.append(item)

    news_list = unique_news

    output_file = (
        NEWS_DIR /
        f"{today}.json"
    )

    output_file.write_text(json.dumps(news_list, ensure_ascii=False, indent=2), encoding="utf-8")

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
