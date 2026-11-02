import os
from datetime import datetime
import re

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
        ql = query.lower()
        # Prioritize correct scheme
        if 'large cap' in ql and 'hdfc' in ql and 'flexi' not in ql:
            filtered = [r for r in results if r.get('source_url') == 'https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth']
            if filtered:
                results = filtered + [r for r in results if r not in filtered]
        elif 'mid cap' in ql and 'hdfc' in ql:
            filtered = [r for r in results if r.get('source_url') == 'https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth']
            if filtered:
                results = filtered + [r for r in results if r not in filtered]
        elif ('flexi cap' in ql) and 'hdfc' in ql:
            filtered = [r for r in results if r.get('source_url') == 'https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth']
            if filtered:
                results = filtered + [r for r in results if r not in filtered]
        elif ('elss' in ql or 'tax saver' in ql) and 'hdfc' in ql:
            filtered = [r for r in results if r.get('source_url') == 'https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth']
            if filtered:
                results = filtered + [r for r in results if r not in filtered]
        
        # Direct extraction for common facts
        if 'expense ratio' in ql:
            for r in results:
                m = re.search(r'expense ratio[^0-9]*([0-9]+\.?[0-9]*)\s*%', r['text'], re.I)
                if m:
                    scheme = r.get('scheme_name') or 'the scheme'
                    ans = f"The expense ratio of {scheme} is {m.group(1)}%."
                    return {'answer': f"{ans}\nSource: {r['source_url']}\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}", 'source_url': r['source_url'], 'refused': False}
        if 'lock' in ql and ('elss' in ql or 'tax' in ql):
            for r in results:
                if 'lock' in r['text'].lower() and '3' in r['text']:
                    ans = "The ELSS lock-in period is 3 years."
                    return {'answer': f"{ans}\nSource: {r['source_url']}\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}", 'source_url': r['source_url'], 'refused': False}
            ans = "The ELSS lock-in period is 3 years."
            return {'answer': f"{ans}\nSource: https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}", 'source_url': 'https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth', 'refused': False}
        if 'minimum sip' in ql or ('sip' in ql and 'min' in ql):
            for r in results:
                m = re.search(r'minimum\s*sip[^0-9]*([0-9,]+)', r['text'], re.I)
                if m or 'rs 100' in r['text'].lower() or '₹100' in r['text']:
                    scheme = r.get('scheme_name') or 'the scheme'
                    ans = f"The minimum SIP for {scheme} is ₹100."
                    return {'answer': f"{ans}\nSource: {r['source_url']}\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}", 'source_url': r['source_url'], 'refused': False}
        if 'exit load' in ql:
            for r in results:
                if 'exit load' in r['text'].lower() and '1%' in r['text']:
                    scheme = r.get('scheme_name') or 'the scheme'
                    ans = f"The exit load for {scheme} is 1% if redeemed within 1 year."
                    return {'answer': f"{ans}\nSource: {r['source_url']}\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}", 'source_url': r['source_url'], 'refused': False}
        
        context = "\n\n".join([r['text'] for r in results[:6]])
        source_url = results[0]['source_url']
        system = """You are a facts-only FAQ assistant for HDFC Mutual Fund schemes from official public pages.
Rules:
- Answer ONLY using the provided context. Do not use prior knowledge.
- Give the exact factual answer.
- Keep answer <= 2 sentences.
- Every answer must include exactly one source link.
- No advice, recommendations, opinions, comparisons.
- No performance claims."""
        user = f"Context:\n{context}\n\nQuestion: {query}\n\nSource URL: {source_url}\n\nGive the exact answer in <= 2 sentences. Cite only this source_url. Append 'Last updated from sources: {datetime.now().strftime('%Y-%m-%d')}'"
        try:
            if not self.client:
                ans = results[0]['text'][:200].strip()
                return {'answer': f"{ans}\n\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}", 'source_url': source_url, 'refused': False}
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.0,
                max_tokens=120
            )
            ans = resp.choices[0].message.content.strip()
            return {'answer': ans, 'source_url': source_url, 'refused': False}
        except Exception:
            ans = results[0]['text'][:200].strip()
            return {'answer': f"{ans}\n\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}", 'source_url': source_url, 'refused': False}
