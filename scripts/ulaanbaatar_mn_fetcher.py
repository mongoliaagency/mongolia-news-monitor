import json
from datetime import datetime
from pathlib import Path

from api_fetcher import fetch_api


def save_ulaanbaatar_json(
    config_path='config/sources/ulaanbaatar_mn.json',
    output_path='data/news/ulaanbaatar_mn.json'
):
    items = fetch_api(config_path)

    with open(config_path, 'r', encoding='utf-8') as f:
        source = json.load(f)

    output = {
        'name': source.get('name'),
        'homepage': source.get('homepage'),
        'fetched_at': datetime.utcnow().isoformat() + 'Z',
        'items': items
    }

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return output_path, len(items)


if __name__ == '__main__':
    path, count = save_ulaanbaatar_json()
    print('wrote', path, 'items', count)
