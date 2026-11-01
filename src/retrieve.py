import os
import yaml
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class Retriever:
    def __init__(self):
        self.config = load_config()
        econf = self.config.get('embedding', {})
        vconf = self.config.get('vectorstore', {})
        rconf = self.config.get('retrieval', {})
        
        self.model_name = econf.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
        self.device = econf.get('device', 'cpu')
        self.model = SentenceTransformer(self.model_name, device=self.device)
        
        persist_dir = os.path.join(BASE_DIR, vconf.get('persist_dir', 'data/vectorstore'))
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(vconf.get('collection_name', 'groww_mf_faq'))
        self.top_k = rconf.get('top_k', 4)
    
    def retrieve(self, query, top_k=None):
        if top_k is None:
            top_k = self.top_k
        qemb = self.model.encode([query])[0].tolist()
        res = self.collection.query(query_embeddings=[qemb], n_results=top_k)
        results = []
        ids = res.get('ids', [[]])[0]
        docs = res.get('documents', [[]])[0]
        metas = res.get('metadatas', [[]])[0]
        dists = res.get('distances', [[]])[0] if res.get('distances') else []
        for i in range(len(ids)):
            results.append({
                'chunk_id': ids[i],
                'text': docs[i],
                'source_url': metas[i].get('source_url') if metas[i] else None,
                'scheme_name': metas[i].get('scheme_name') if metas[i] else None,
                'distance': dists[i] if i < len(dists) else None
            })
        return results


if __name__ == '__main__':
    r = Retriever()
    out = r.retrieve("What is expense ratio of HDFC Large Cap Fund?")
    for o in out:
        print(o['source_url'], o['scheme_name'])
