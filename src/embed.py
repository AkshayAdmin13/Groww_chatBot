import os
import json

import yaml
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')
CHUNKS_DIR = os.path.join(BASE_DIR, 'data', 'chunks')
EMB_DIR = os.path.join(BASE_DIR, 'data', 'embeddings')
CHUNKS_IN = os.path.join(CHUNKS_DIR, 'chunks.jsonl')
EMB_OUT = os.path.join(EMB_DIR, 'embeddings.jsonl')


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    os.makedirs(EMB_DIR, exist_ok=True)
    config = load_config()
    econf = config.get('embedding', {})
    model_name = econf.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
    batch_size = econf.get('batch_size', 32)
    device = econf.get('device', 'cpu')
    
    model = SentenceTransformer(model_name, device=device)
    
    chunks = []
    with open(CHUNKS_IN, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    
    texts = [c['text'] for c in chunks]
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True)
    
    with open(EMB_OUT, 'w', encoding='utf-8') as f:
        for c, emb in zip(chunks, embeddings):
            rec = {
                'chunk_id': c['chunk_id'],
                'doc_id': c['doc_id'],
                'source_url': c['source_url'],
                'scheme_name': c['scheme_name'],
                'text': c['text'],
                'embedding': emb.tolist()
            }
            f.write(json.dumps(rec) + '\n')
    
    print(f'Embedded {len(chunks)} chunks -> {EMB_OUT} (model={model_name})')


if __name__ == '__main__':
    main()
