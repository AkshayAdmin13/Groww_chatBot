import os
from datetime import datetime

import yaml
from dotenv import load_dotenv
from groq import Groq

from retrieve import Retriever
from guardrails import check_guardrails

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')
load_dotenv(os.path.join(BASE_DIR, '.env'))


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class Generator:
    def __init__(self):
        self.config = load_config()
        self.retriever = Retriever()
        lconf = self.config.get('llm', {})
        self.provider = lconf.get('provider', 'groq')
        self.model = lconf.get('model', 'qwen/qwen3.8-27b')
        self.api_key_env = lconf.get('api_key_env', 'GROQ_API_KEY')
        api_key = os.getenv(self.api_key_env)
        self.client = Groq(api_key=api_key) if api_key else None
        self.temperature = lconf.get('temperature', 0.0)
        self.max_tokens = lconf.get('max_tokens', 256)
    
    def answer(self, query):
        ok, refusal = check_guardrails(query)
        if not ok:
            return {
                'answer': refusal,
                'source_url': 'https://www.amfiindia.com/investor-corner/knowledge-center',
                'refused': True
            }
        results = self.retriever.retrieve(query)
        if not results:
            return {
                'answer': "I could not find relevant factual information in the indexed sources for this query. Please ask about expense ratio, exit load, minimum SIP, lock-in (ELSS), riskometer, benchmark, or how to download statements for the listed HDFC schemes. Facts-only. No investment advice.",
                'source_url': 'https://groww.in/mutual-funds/amc/hdfc-mutual-funds',
                'refused': True
            }
        context = "\n\n".join([r['text'] for r in results])
        source_url = results[0]['source_url']
        system = """You are a facts-only FAQ assistant for HDFC Mutual Fund schemes from official public pages.
Rules:
- Answer ONLY using the provided context. Do not use prior knowledge.
- If the answer is not clearly supported by context, say you don't have that exact fact in the indexed sources.
- Keep answer <= 3 sentences.
- Every answer must include exactly one source link (use the provided source_url).
- Do not give advice, recommendations, opinions, or comparisons.
- Do not compute or claim returns/performance.
- Do not ask for or store PII.
- Be concise and factual."""
        user = f"Context:\n{context}\n\nQuestion: {query}\n\nSource URL: {source_url}\n\nAnswer in <= 3 sentences, cite only this source_url, and append 'Last updated from sources: {datetime.now().strftime('%Y-%m-%d')}'"
        try:
            if not self.client:
                # Fallback without LLM - simple extractive style
                ans = results[0]['text'][:400].strip() + '...'
                return {
                    'answer': f"{ans}\n\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}",
                    'source_url': source_url,
                    'refused': False
                }
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            ans = resp.choices[0].message.content.strip()
            return {
                'answer': ans,
                'source_url': source_url,
                'refused': False
            }
        except Exception as e:
            ans = results[0]['text'][:300].strip() + '...'
            return {
                'answer': f"{ans}\n\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}",
                'source_url': source_url,
                'refused': False
            }
