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
        "%Y/%m/%d, %H:%M",
        "%Y/%m/%d",
        "%Y / %m / %d",
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
        # English date with comma: "16 Jun, 2026" (mongol.news)
        "%d %b, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw_date, fmt)
        except Exception:
            continue

    # Time-only format HH:MM (e.g. "14:58") — article published today
    time_match = re.match(r'^\s*(\d{1,2}):(\d{2})\s*$', raw_date)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        now = datetime.now()
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Roman numeral months (e.g. "2026 VI сар 26" from mongolbank.mn)
    # Order: longest first to avoid partial matches (e.g. "viii" before "iii")
    ROMAN_MONTHS = [
        ('xiii сар', 13), ('viii сар', 8), ('vii сар', 7), ('iii сар', 3),
        ('xii сар', 12), ('xi сар', 11), ('ix сар', 9),
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
        # "X-р сарын" ordinal suffix (e.g. "6-р сарын 21" from mono.mn)
        '1-р сарын': 1, '2-р сарын': 2, '3-р сарын': 3, '4-р сарын': 4,
        '5-р сарын': 5, '6-р сарын': 6, '7-р сарын': 7, '8-р сарын': 8,
        '9-р сарын': 9, '10-р сарын': 10, '11-р сарын': 11, '12-р сарын': 12,
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
        # Common Mongolian typo variants (missing 'д' in month names)
        'зургааугаар сарын': 6, 'долооугаар сарын': 7, 'наймугаар сарын': 8,
    }
    # Pattern: "6 сарын 25, 2026" or "2026 оны 6 сарын 25" or "2026 оны зургаадугаар сарын 27"
    for mn_key, mn_val in MN_MONTHS.items():
        if mn_key in raw_date:
            nums = re.findall(r'\d+', raw_date)
            if len(nums) >= 2:
                parsed = [int(n) for n in nums]
                if len(parsed) >= 3:
                    # Try to identify year (4-digit number) and day (remaining non-month)
                    if parsed[0] >= 1000:
                        # "2026 оны 6 сарын 25": year first, day last
                        year, day = parsed[0], parsed[-1]
                    elif parsed[0] == mn_val:
                        # "6 сарын 25, 2026": month first, year last
                        year, day = parsed[-1], parsed[1]
                    else:
                        # Unknown order: assume year first, day last
                        year, day = parsed[0], parsed[-1]
                else:
                    # Only 2 numbers: assume day and use current year
                    day = parsed[-1]
                    year = datetime.now().year
                try:
                    return datetime(year, mn_val, day)
                except Exception:
                    pass
            break

    # "Уржигдар X цаг Y мин" = the day before yesterday at X:YY (e.g. "Уржигдар 17 цаг 36 мин")
    # "Өчигдөр X цаг Y мин" = yesterday at X:YY
    urjigdar_match = re.match(r'^\s*(Уржигдар|Өчигдөр)\s+(\d{1,2})\s*цаг\s*(\d{1,2})?\s*мин\s*$', raw_date)
    if urjigdar_match:
        keyword = urjigdar_match.group(1)
        hour = int(urjigdar_match.group(2))
        minute = int(urjigdar_match.group(3)) if urjigdar_match.group(3) else 0
        from datetime import timedelta
        now = datetime.now()
        days_ago = 2 if keyword == 'Уржигдар' else 1
        target = (now - timedelta(days=days_ago)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return target

    # "Өчигдөр" alone (yesterday) — used by tovch.mn, news.mn etc.
    if re.match(r'^\s*Өчигдөр\s*$', raw_date):
        from datetime import timedelta
        now = datetime.now()
        return (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Relative time in Mongolian (e.g. "8 цаг" = 8 hours ago, "5 өдөр" = 5 days ago)
    # Also handle genitive/"өмнө" forms: "2 өдрийн өмнө" = 2 days ago, "3 сарын өмнө" = 3 months ago
    # Includes abbreviated forms: "мин" (short for минут), "өд" (short for өдөр)
    rel_match = re.match(r'^\s*(\d+)\s*(?:цагийн\s*(?:өмнө|урьд)|цаг|өдрийн\s*(?:өмнө|урьд)|өдөр|хоногийн\s*(?:өмнө|урьд)|хоног|долоо\s*хоногийн\s*(?:өмнө|урьд)|долоо\s*хоног\S*\s*(?:өмнө|урьд)|долоо\s*хоног|сарын\s*(?:өмнө|урьд)|сар|жилийн\s*(?:өмнө|урьд)|жил|минутын\s*(?:өмнө|урьд)|минут|мин)\s*$', raw_date)
    if rel_match:
        num = int(rel_match.group(1))
        full = rel_match.group(0)
        from datetime import timedelta
        now = datetime.now()
        if 'минут' in full or 'мин' in full:
            return now - timedelta(minutes=num)
        elif 'цаг' in full:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'сар' in full:
            return (now - timedelta(days=num * 30)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'жил' in full:
            return (now - timedelta(days=num * 365)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'долоо хоног' in full:
            return (now - timedelta(days=num * 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # өдөр / өдрийн / хоног / хоногийн
            return (now - timedelta(days=num)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Combined relative time: "X өдөр, Y цаг" or "X цаг, Y минут"
    # e.g. "2 өдөр, 22 цаг", "3 цаг, 12 минут", "3 өдөр, 15 цаг"
    from datetime import timedelta
    now = datetime.now()
    # Match "X өдөр, Y цаг" pattern
    combined_dh = re.match(r'^\s*(\d+)\s*[,\s]*өдөр[,，\s]*\s*(\d+)\s*[,\s]*цаг\s*$', raw_date)
    if combined_dh:
        days = int(combined_dh.group(1))
        hours = int(combined_dh.group(2))
        return (now - timedelta(days=days, hours=hours)).replace(minute=0, second=0, microsecond=0)

    # Match "X цаг, Y минут" pattern (comma-separated)
    combined_hm = re.match(r'^\s*(\d+)\s*[,\s]*цаг[,，\s]*\s*(\d+)\s*[,\s]*минут\s*$', raw_date)
    if combined_hm:
        hours = int(combined_hm.group(1))
        minutes = int(combined_hm.group(2))
        return now - timedelta(hours=hours, minutes=minutes)

    # Match "X цаг Y минутын өмнө" pattern (MNB style: space-separated, genitive suffix)
    # e.g. "3 цаг 48 минутын өмнө", "1 цаг 15 минутын өмнө", "23 цаг 40 минутын өмнө"
    combined_hm2 = re.match(r'^\s*(\d+)\s*цаг\s*(\d+)\s*минутын\s*(?:өмнө|урьд)\s*$', raw_date)
    if combined_hm2:
        hours = int(combined_hm2.group(1))
        minutes = int(combined_hm2.group(2))
        return now - timedelta(hours=hours, minutes=minutes)

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
