import json
import time
import requests
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
from date_utils import parse_date, format_date, is_within_days


def _fetch_api_with_retry(api_url, max_retries=3, timeout=45, verify=True):
    """Fetch API endpoint with retry logic for connection timeouts."""
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, headers={
                'User-Agent': 'Mozilla/5.0'
            }, timeout=timeout, verify=verify)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = (attempt + 1) * 10
                time.sleep(wait)
            else:
                raise last_error


def _extract_raw_list(data, source):
    """Extract the raw list of items from API response using configurable data path(s).
    Supports both single 'api_data_path' (string) and multiple 'api_data_paths' (array).
    """
    # Support multiple data paths (merge all)
    data_paths = source.get('api_data_paths', [])
    if data_paths:
        all_items = []
        for dp in data_paths:
            items = _navigate_data_path(data, dp)
            all_items.extend(items)
        return all_items

    # Single data path
    data_path = source.get('api_data_path', '')
    if not data_path:
        # Legacy: default path data.list
        if isinstance(data, dict):
            return data.get('data', {}).get('list', [])
        elif isinstance(data, list):
            return data
        return []

    return _navigate_data_path(data, data_path)


def _navigate_data_path(data, data_path):
    """Navigate a dot-separated path into a nested dict to extract a list."""
    parts = data_path.split('.')
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part, [])
        else:
            return []
    if isinstance(current, list):
        return current
    return []


def _set_page_param(url, page):
    """Set or replace the 'page' query parameter in a URL."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    # Flatten multi-value lists and set page
    flat = {k: v[0] for k, v in params.items()}
    if page == 0:
        if 'page' in flat:
            del flat['page']
    else:
        flat['page'] = str(page)
    new_query = urlencode(flat, doseq=False)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

def _get_paginated_items(source):
    """Fetch items from API with optional pagination."""
    api_url = source.get('api_url')
    if not api_url:
        raise ValueError('api_url is required for api source_type')

    all_items = []
    max_pages = source.get('api_max_pages', 5)
    verify = source.get('api_verify_ssl', True)

    for page in range(max_pages):
        # Build page URL using proper query parameter manipulation
        page_url = _set_page_param(api_url, page)

        # Try primary URL pattern, then fallback URLs
        urls_to_try = [page_url]
        fallback_urls = source.get('api_fallback_urls', [])
        for fb in fallback_urls:
            urls_to_try.append(_set_page_param(fb, page))

        data = None
        last_error = None
        for url in urls_to_try:
            try:
                data = _fetch_api_with_retry(url, max_retries=2, timeout=30, verify=verify)
                break
            except Exception as e:
                last_error = e

        if data is None:
            if page == 0:
                raise last_error
            else:
                break  # No more pages

        raw_list = _extract_raw_list(data, source)
        if not raw_list:
            break

        # Check if any items are still within the last 7 days
        has_recent = False
        date_field = source.get('api_date_field', 'createdDateText')
        for item in raw_list:
            pub_date = _get_date_from_item(item, date_field, source)
            if pub_date and is_within_days(pub_date, days=7):
                has_recent = True
                break

        all_items.extend(raw_list)

        if not has_recent:
            break  # No more recent items in older pages

        # Check total if available
        if isinstance(data, dict):
            total = data.get('total', 0)
            if total and len(all_items) >= total:
                break

    return all_items


def _get_date_from_item(item, date_field, source):
    """Extract date from an item using configurable field name."""
    raw = item.get(date_field, '')
    if raw:
        return raw

    # Try alternate date fields
    alt_fields = source.get('api_date_alt_fields', [])
    if not alt_fields:
        alt_fields = ['createdDate', 'createdAt', 'publishDate', 'updatedAt', 'date']
    for alt in alt_fields:
        val = item.get(alt, '')
        if val:
            return val
    return ''


def _get_id_from_item(item, source):
    """Extract ID from an item using configurable field name."""
    id_field = source.get('api_id_field', '')
    if not id_field:
        return item.get('urlId') or item.get('id')
    return item.get(id_field)


def _get_link(item, source):
    """Build the detail page link using configurable template."""
    url_id = _get_id_from_item(item, source)
    if url_id is None:
        return ''

    link_template = source.get('api_link_template', '')
    if link_template:
        return urljoin(source.get('homepage', ''), link_template.replace('{id}', str(url_id)))
    else:
        return urljoin(source.get('homepage', ''), f'/news/{url_id}')


def _get_summary(item, source):
    """Extract summary from an item using configurable field name."""
    summary_field = source.get('api_summary_field', '')
    if summary_field:
        summary = item.get(summary_field, '')
        if summary:
            # If it's HTML content, strip tags
            if '<' in summary:
                try:
                    soup = BeautifulSoup(summary, 'lxml')
                except Exception:
                    soup = BeautifulSoup(summary, 'html.parser')
                return soup.get_text(strip=True)[:300]
            return summary[:300]

    # Fallback: try shortContent, then content HTML
    summary = item.get('shortContent') or ''
    if not summary:
        content_html = item.get('content') or ''
        try:
            soup = BeautifulSoup(content_html, 'lxml')
        except Exception:
            soup = BeautifulSoup(content_html, 'html.parser')
        summary = soup.get_text(strip=True)[:300]
    return summary


def fetch_api(source_file):
    with open(source_file, 'r', encoding='utf-8') as f:
        source = json.load(f)

    # Use pagination if api_data_path or api_data_paths is configured
    use_pagination = bool(source.get('api_data_path', '') or source.get('api_data_paths', []))

    verify = source.get('api_verify_ssl', True)

    if use_pagination:
        raw_list = _get_paginated_items(source)
    else:
        api_url = source.get('api_url')
        if not api_url:
            raise ValueError('api_url is required for api source_type')

        urls_to_try = [api_url] + source.get('api_fallback_urls', [])
        data = None
        last_error = None
        for url in urls_to_try:
            try:
                data = _fetch_api_with_retry(url, max_retries=2, timeout=30, verify=verify)
                break
            except Exception as e:
                last_error = e

        if data is None:
            raise last_error

        raw_list = _extract_raw_list(data, source)

    date_field = source.get('api_date_field', 'createdDateText')
    title_field = source.get('api_title_field', 'title')
    items = []

    for item in raw_list:
        title = (item.get(title_field) or '').strip()
        if not title:
            continue

        url_id = _get_id_from_item(item, source)
        if url_id is None:
            continue

        link = _get_link(item, source)
        if not link:
            continue

        publish_date_raw = _get_date_from_item(item, date_field, source)
        dt = parse_date(publish_date_raw)
        if not dt or not is_within_days(publish_date_raw, days=7):
            continue  # only keep articles from the last 7 days

        summary = _get_summary(item, source)

        items.append({
            'title': title,
            'publish_date': format_date(dt),
            'source': source.get('name'),
            'url': link,
            'summary': summary,
            'category': source.get('category', 'government'),
        })

    return items
