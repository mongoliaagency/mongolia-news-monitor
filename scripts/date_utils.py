"""Shared date parsing and filtering utilities for all fetchers."""
from datetime import datetime


def parse_date(raw_date):
    """Try to parse a raw date string into a datetime object. Returns None on failure."""
    if not raw_date:
        return None

    raw_date = str(raw_date).strip()

    # Remove common prefixes
    for prefix in ['far fa-clock', 'fa fa-clock']:
        if raw_date.lower().startswith(prefix.lower()):
            raw_date = raw_date[len(prefix):].strip()

    formats = [
        # ISO / standard
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        # Mongolian common
        "%Y.%m.%d",
        "%Y/%m/%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
        # RSS/HTTP date formats
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%a, %d %b %Y %H:%M:%S",
        "%a, %d %b %Y",
        "%Y-%m-%dT%H:%M:%S%z",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw_date, fmt)
        except Exception:
            continue

    return None


def format_date(dt):
    """Format datetime to standard publish_date string for storage."""
    return dt.strftime("%a, %d %b %Y 00:00:00 GMT")


def is_today(raw_date):
    """Check if the raw date string represents today's date."""
    dt = parse_date(raw_date)
    if dt is None:
        return False
    return dt.date() == datetime.now().date()
