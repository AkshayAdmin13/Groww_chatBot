import os
import json

import yaml
import chromadb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')
EMB_DIR = os.path.join(BASE_DIR, 'data', 'embeddings')
VEC_DIR = os.path.join(BASE_DIR, 'data', 'vectorstore')
EMB_IN = os.path.join(EMB_DIR, 'embeddings.jsonl')


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    os.makedirs(VEC_DIR, exist_ok=True)
    config = load_config()
    vconf = config.get('vectorstore', {})
    persist_dir = os.path.join(BASE_DIR, vconf.get('persist_dir', 'data/vectorstore'))
    collection_name = vconf.get('collection_name', 'groww_mf_faq')
    
    client = chromadb.PersistentClient(path=persist_dir)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
    collection = client.create_collection(name=collection_name)
    
    ids = []
    documents = []
    embeddings = []
    metadatas = []
    
    with open(EMB_IN, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            ids.append(rec['chunk_id'])
            documents.append(rec['text'])
            embeddings.append(rec['embedding'])
            metadatas.append({
                'source_url': rec['source_url'],
                'scheme_name': rec['scheme_name'],
                'doc_id': rec['doc_id']
            })
    
    if ids:
        collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    
    print(f'Indexed {len(ids)} chunks into Chroma collection "{collection_name}" at {persist_dir} (count={collection.count()})')


if __name__ == '__main__':
    main()
