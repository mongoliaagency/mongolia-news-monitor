"""Shared date parsing and filtering utilities for all fetchers."""
import re
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

    # Roman numeral months (e.g. "2026 VI сар 26" from mongolbank.mn)
    # Order: longest first to avoid partial matches (e.g. "viii" before "iii")
    ROMAN_MONTHS = [
        ('viii сар', 8), ('vii сар', 7), ('iii сар', 3), ('xii сар', 12),
        ('xiii сар', 13), ('xi сар', 11), ('xii сар', 12), ('ix сар', 9),
        ('iv сар', 4), ('vi сар', 6), ('ii сар', 2), ('v сар', 5),
        ('x сар', 10), ('i сар', 1),
    ]
    raw_lower = raw_date.lower()
    for rm_key, rm_val in ROMAN_MONTHS:
        if rm_key in raw_lower:
            nums = re.findall(r'\d+', raw_date)
            if len(nums) >= 2:
                day = int(nums[-1])
                year = int(nums[0])
                try:
                    return datetime(year, rm_val, day)
                except Exception:
                    pass
            break

    # Mongolian month names (e.g. "6 сарын 25, 2026")
    MN_MONTHS = {
        '1 сарын': 1, '2 сарын': 2, '3 сарын': 3, '4 сарын': 4,
        '5 сарын': 5, '6 сарын': 6, '7 сарын': 7, '8 сарын': 8,
        '9 сарын': 9, '10 сарын': 10, '11 сарын': 11, '12 сарын': 12,
        # Alternative with different separators
        '1дугаар сар': 1, '2дугаар сар': 2, '3дугаар сар': 3, '4дүгээр сар': 4,
        '5дугаар сар': 5, '6дугаар сар': 6, '7дугаар сар': 7, '8дугаар сар': 8,
        '9дүгээр сар': 9, '10дугаар сар': 10, '11дүгээр сар': 11, '12дугаар сар': 12,
        # Full Mongolian written month names (e.g. "зургаадугаар сарын 27")
        'нэгдүгээр сарын': 1, 'хоёрдугаар сарын': 2, 'гуравдугаар сарын': 3,
        'дөрөвдүгээр сарын': 4, 'тавдугаар сарын': 5, 'зургаадугаар сарын': 6,
        'долоодугаар сарын': 7, 'наймдугаар сарын': 8, 'есдүгээр сарын': 9,
        'аравдугаар сарын': 10, 'арван нэгдүгээр сарын': 11, 'арван хоёрдугаар сарын': 12,
        # Spelling variant: "аравдугаар" vs "аравдугаар"
        'арваннэгдүгээр сарын': 11, 'арванхоёрдугаар сарын': 12,
    }
    # Pattern: "6 сарын 25, 2026" or "2026 оны 6 сарын 25" or "2026 оны зургаадугаар сарын 27"
    for mn_key, mn_val in MN_MONTHS.items():
        if mn_key in raw_date:
            # Extract numbers - year comes first in "2026 оны ... сарын 27"
            nums = re.findall(r'\d+', raw_date)
            if len(nums) >= 2:
                year = int(nums[0])
                day = int(nums[-1])
                try:
                    return datetime(year, mn_val, day)
                except Exception:
                    pass
            break

    # Fallback: extract first date-like pattern (e.g. "2026-06-26" from "2026-06-26Category")
    date_pattern = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', raw_date)
    if date_pattern:
        date_str = date_pattern.group(1)
        # Normalize separators to "-"
        date_str = date_str.replace('.', '-').replace('/', '-')
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            pass

    # Fallback: YYYY/MM/UUID from URL paths (e.g. "thumbnail/2026/06/uuid.jpg")
    # Only match when YYYY/MM is followed by a non-digit (UUID start), not another digit (day)
    ym_pattern = re.search(r'/(\d{4})/(\d{2})/[a-f]', raw_date)
    if ym_pattern:
        year = int(ym_pattern.group(1))
        month = int(ym_pattern.group(2))
        today = datetime.now()
        if year == today.year and month == today.month:
            return today.replace(hour=0, minute=0, second=0, microsecond=0)

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


def is_within_days(raw_date, days=7):
    """Check if the raw date string is within the last N days (inclusive of today)."""
    dt = parse_date(raw_date)
    if dt is None:
        return False
    from datetime import timedelta
    cutoff = datetime.now().date() - timedelta(days=days - 1)
    return dt.date() >= cutoff
