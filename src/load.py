import os
import json
import hashlib
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
METADATA_PATH = os.path.join(RAW_DIR, 'metadata.json')


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def sanitize_filename(url):
    parsed = urlparse(url)
    name = parsed.path.strip('/').replace('/', '_')
    if not name:
        name = 'page'
    return name + '.html'


def fetch_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; GrowwMF-FAQ-Bot/1.0)'
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    config = load_config()
    sources = config.get('data_sources', [])
    metadata = []

    for src in sources:
        url = src['url']
        scheme = src.get('scheme', '')
        try:
            html = fetch_page(url)
            fname = sanitize_filename(url)
            fpath = os.path.join(RAW_DIR, fname)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(html)
            content_hash = hashlib.sha256(html.encode('utf-8')).hexdigest()
            metadata.append({
                'url': url,
                'scheme': scheme,
                'filename': fname,
                'fetched_at': datetime.utcnow().isoformat() + 'Z',
                'status_code': 200,
                'content_hash': content_hash
            })
            print(f'Scraped: {url} -> {fpath}')
        except Exception as e:
            metadata.append({
                'url': url,
                'scheme': scheme,
                'filename': None,
                'fetched_at': datetime.utcnow().isoformat() + 'Z',
                'status_code': getattr(e, 'response', None).status_code if hasattr(e, 'response') and e.response is not None else None,
                'error': str(e)
            })
            print(f'Failed: {url} -> {e}')

    with open(METADATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f'Metadata saved to {METADATA_PATH}')


if __name__ == '__main__':
    main()
