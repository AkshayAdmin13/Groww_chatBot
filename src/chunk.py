import os
import json
import uuid
import re

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')
LOADED_DIR = os.path.join(BASE_DIR, 'data', 'loaded')
CHUNKS_DIR = os.path.join(BASE_DIR, 'data', 'chunks')
DOCS_IN = os.path.join(LOADED_DIR, 'documents.jsonl')
CHUNKS_OUT = os.path.join(CHUNKS_DIR, 'chunks.jsonl')


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def chunk_text(text, chunk_size=200, chunk_overlap=40):
    if not text:
        return []
    # Split by sentences/sections first for better chunks
    # Try to split on common section markers
    sections = re.split(r'(?=(?:Expense Ratio|Exit Load|Minimum SIP|SIP|Lock.in|Lock in|ELSS|Riskometer|Benchmark|NAV|AUM|Statement|Download|Factsheet))', text, flags=re.IGNORECASE)
    if len(sections) <= 1:
        words = text.split()
        chunks = []
        i = 0
        n = len(words)
        while i < n:
            end = min(i + chunk_size, n)
            chunk_words = words[i:end]
            chunks.append(' '.join(chunk_words))
            if end == n:
                break
            i = end - chunk_overlap
            if i < 0:
                i = end
        return chunks
    chunks = []
    for s in sections:
        s = s.strip()
        if not s or len(s.split()) < 5:
            continue
        if len(s.split()) <= chunk_size + 50:
            chunks.append(s)
        else:
            words = s.split()
            i = 0
            n = len(words)
            while i < n:
                end = min(i + chunk_size, n)
                chunk_words = words[i:end]
                chunks.append(' '.join(chunk_words))
                if end == n:
                    break
                i = end - chunk_overlap
                if i < 0:
                    i = end
    return chunks


def main():
    os.makedirs(CHUNKS_DIR, exist_ok=True)
    config = load_config()
    cconf = config.get('chunking', {})
    chunk_size = cconf.get('chunk_size', 200)
    chunk_overlap = cconf.get('chunk_overlap', 40)
    
    all_chunks = []
    with open(DOCS_IN, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            doc = json.loads(line)
            text = doc['text']
            parts = chunk_text(text, chunk_size, chunk_overlap)
            for p in parts:
                if len(p.split()) < 10:
                    continue
                all_chunks.append({
                    'chunk_id': str(uuid.uuid4()),
                    'doc_id': doc['doc_id'],
                    'source_url': doc['source_url'],
                    'scheme_name': doc['scheme_name'],
                    'text': p,
                    'chunk_meta': {
                        'strategy': 'section_aware_factual',
                        'chunk_size': chunk_size,
                        'chunk_overlap': chunk_overlap
                    }
                })
    
    with open(CHUNKS_OUT, 'w', encoding='utf-8') as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')
    
    print(f'Created {len(all_chunks)} chunks -> {CHUNKS_OUT}')


if __name__ == '__main__':
    main()
