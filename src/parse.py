import os
import json
import re

from bs4 import BeautifulSoup
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
LOADED_DIR = os.path.join(BASE_DIR, 'data', 'loaded')
METADATA_RAW = os.path.join(RAW_DIR, 'metadata.json')
DOCS_OUT = os.path.join(LOADED_DIR, 'documents.jsonl')


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'noscript', 'svg', 'aside', 'form', 'button']):
        tag.decompose()

    collected = []
    factual_keywords = re.compile(r'(expense ratio|exit load|minimum sip|sip|min.*invest|lock.*in|lock in|elss|tax saver|riskometer|benchmark|nav|aum|fund size|statement|capital gains|factsheet)', re.I)

    # Grab everything with factual keywords
    for tag in soup.find_all(True):
        try:
            txt = tag.get_text(' ')
        except:
            continue
        if not txt:
            continue
        if factual_keywords.search(txt):
            # keep reasonably sized chunks
            if 10 < len(txt.split()) < 200:
                collected.append(txt)

    # Also explicitly look for lock-in patterns in full text
    text_all = soup.get_text(' ')
    for m in re.finditer(r'.{0,60}(?:elss|tax saver).{0,80}(?:lock.?in|3\s*year|3 years).{0,60}', text_all, re.I):
        collected.append(m.group())
    for m in re.finditer(r'.{0,40}lock.?in.{0,80}', text_all, re.I):
        collected.append(m.group())
    for m in re.finditer(r'ELSS.*?3Y.*?Lock|3Y.*?Lock.*?ELSS', text_all, re.I):
        collected.append(m.group())

    if collected:
        # deduplicate while preserving order
        seen = set()
        uniq = []
        for c in collected:
            c2 = re.sub(r'\s+', ' ', c).strip()
            if len(c2.split()) < 5:
                continue
            if c2 not in seen:
                seen.add(c2)
                uniq.append(c2)
        text = ' '.join(uniq)
    else:
        main = soup.find('main') or soup
        text = re.sub(r'\s+', ' ', main.get_text(separator=' ')).strip()

    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def main():
    os.makedirs(LOADED_DIR, exist_ok=True)
    config = load_config()
    sources = {s['url']: s.get('scheme', '') for s in config.get('data_sources', [])}

    with open(METADATA_RAW, 'r', encoding='utf-8') as f:
        raw_meta = json.load(f)

    docs = []
    for i, meta in enumerate(raw_meta):
        if not meta.get('filename'):
            continue
        fpath = os.path.join(RAW_DIR, meta['filename'])
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            html = f.read()
        cleaned = clean_html(html)
        doc = {
            'doc_id': f'doc_{i+1}',
            'source_url': meta['url'],
            'scheme_name': meta.get('scheme') or sources.get(meta['url'], ''),
            'text': cleaned,
            'metadata': {
                'filename': meta['filename'],
                'fetched_at': meta.get('fetched_at')
            }
        }
        docs.append(doc)

    with open(DOCS_OUT, 'w', encoding='utf-8') as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + '\n')

    print(f'Loaded & cleaned {len(docs)} documents -> {DOCS_OUT}')


if __name__ == '__main__':
    main()
