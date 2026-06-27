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


def _parse_date_from_item(item):
    """Extract date string (YYYY-MM-DD) from a news item's publish_date field."""
    publish_date = item.get("publish_date", "")
    if not publish_date:
        return None

    # Use the same robust parser as the fetchers to handle all formats:
    # "%a, %d %b %Y %H:%M:%S %z" (+0800), "%a, %d %b %Y %H:%M:%S %Z" (GMT),
    # "%a, %d %b %Y 00:00:00 GMT", and ISO variants
    from date_utils import parse_date as date_parse
    dt = date_parse(publish_date)
    if dt:
        return dt.strftime("%Y-%m-%d")

    return None


def save_news(news_list):

    ensure_dir()

    today_str = datetime.now().strftime("%Y-%m-%d")

    # Group articles by their publish_date (YYYY-MM-DD)
    grouped = {}
    for item in news_list:
        date_key = _parse_date_from_item(item)
        if date_key is None:
            date_key = today_str
        grouped.setdefault(date_key, []).append(item)

    # Merge with existing files to preserve articles from previous runs
    for date_key in grouped:
        output_file = NEWS_DIR / f"{date_key}.json"
        existing = []
        if output_file.exists():
            try:
                existing = json.loads(output_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []

        # Deduplicate: normalized title
        def normalize_title(t):
            if not t:
                return ""
            s = t.strip().lower()
            return " ".join(s.split())

        seen = set()
        for item in existing:
            key = normalize_title(item.get("title", ""))
            seen.add(key)

        new_items = []
        for item in grouped[date_key]:
            key = normalize_title(item.get("title", ""))
            if key in seen:
                continue
            seen.add(key)
            new_items.append(item)

        merged = existing + new_items
        output_file.write_text(
            json.dumps(merged, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"Saved: {output_file} ({len(new_items)} new, {len(merged)} total)")

    cleanup_old_files()


def cleanup_old_files():

    today = datetime.now().date()

    cutoff = today - timedelta(days=7)

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
