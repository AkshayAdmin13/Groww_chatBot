import os

src = r'C:\Akshay\Next Leap\groww_chatbot\architecture.md'
dst = r'C:\Akshay\Next Leap\groww_chatbot\implementation.md'

with open(src, 'r', encoding='utf-8', errors='ignore') as f:
    arch = f.read()

impl = '''# Implementation Plan (Simplified)

## Goal
Simple, phase-wise implementation for Groww MF FAQ Assistant with explicit artifacts, config-driven setup, ChromaDB + sentence-transformers/all-MiniLM-L6-v2, Groq qwen/qwen3.8-27b by default, guardrails, and a tiny UI.

## 1) Creating Directories
Create the following folders/files at project root:

```text
groww_chatbot/
├── config/
│   └── config.yaml        # all configurable values
├── data/
│   ├── raw/               # scraped HTML/text + metadata.json
│   ├── chunks/            # chunks.jsonl
│   ├── embeddings/        # embeddings.jsonl (optional if stored in Chroma)
│   └── vectorstore/       # Chroma persistent store
├── src/
│   ├── load.py
│   ├── chunk.py
│   ├── embed.py
│   ├── index.py
│   ├── retrieve.py
│   ├── generate.py
│   ├── guardrails.py
│   └── utils.py
├── app/
│   └── app.py             # tiny UI
├── .env
├── requirements.txt
├── README.md
├── PRD.md
├── architecture.md
└── implementation.md
```

**Tasks:**
- [ ] Create directories with `os.makedirs(exist_ok=True)`
- [ ] Add `config/config.yaml` with defaults (5 URLs, chunking, embedding, chroma, retrieval, llm)
- [ ] Add `.env` template for API keys (e.g., `GROQ_API_KEY`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MISTRAL_API_KEY`)

## 2) Scraping Documents (Data Loading)
**Source URLs (only these 5):**
1. https://groww.in/mutual-funds/amc/hdfc-mutual-funds
2. https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth
3. https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth
4. https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth
5. https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth

**Implementation (`src/load.py`):**
- [ ] Read `data_sources` from config
- [ ] Use `requests` with headers (user-agent). Fetch only listed URLs (no following internal links)
- [ ] Extract main text from HTML (BeautifulSoup) - keep relevant facts (expense ratio, exit load, SIP min, lock-in, riskometer, benchmark, statement download)
- [ ] Save raw: `data/raw/<sanitized_name>.html` or `.txt` + update `data/raw/metadata.json` with `{url, filename, fetched_at, status_code, content_hash}`
- [ ] Validate public sources only

## 3) Chunking
**Goal:** Split raw text into smaller chunks for retrieval. Choose strategy based on data (section/heading-aware preferred).

**Implementation (`src/chunk.py`):**
- [ ] Load raw files from `data/raw/`
- [ ] Apply chunking strategy from config (e.g., `recursive`/`section-aware`). Configurable: `chunk_size` (e.g., 300-500), `chunk_overlap` (e.g., 50)
- [ ] Attach metadata: `chunk_id` (uuid), `source_url`, `scheme_name`, `text`
- [ ] Save to `data/chunks/chunks.jsonl` (one JSON per line) - explicit artifact
- [ ] Log chunk counts

## 4) Embedding
**Model:** `sentence-transformers/all-MiniLM-L6-v2` (same for ingestion and retrieval)

**Implementation (`src/embed.py`):**
- [ ] Load chunks from `data/chunks/chunks.jsonl`
- [ ] Load model from `sentence-transformers` (configurable via `embedding.model_name`)
- [ ] Generate embeddings in batches (`embedding.batch_size`)
- [ ] Save to `data/embeddings/embeddings.jsonl` with `{chunk_id, source_url, text, embedding}` (or keep minimal) - explicit artifact
- [ ] Device configurable (`cpu`/`cuda`)

## 5) Storing Data in Vector DB (ChromaDB)
**DB:** ChromaDB persistent

**Implementation (`src/index.py`):**
- [ ] Load chunks+embeddings (or generate on-the-fly)
- [ ] Init Chroma client with `persist_directory = data/vectorstore/`
- [ ] Create/get collection `vectorstore.collection_name` (e.g., `groww_mf_faq`)
- [ ] Upsert documents with `ids=[chunk_id]`, `documents=[text]`, `embeddings=[embedding]`, `metadatas=[{"source_url": ..., "scheme": ...}]`
- [ ] Persist to disk - explicit artifact in `data/vectorstore/`
- [ ] Verify count

## 6) Retrieval Logic
**Implementation (`src/retrieve.py`):**
- [ ] Load same embedding model as ingestion
- [ ] Embed user query
- [ ] Query Chroma collection with `n_results = retrieval.top_k` (e.g., 3-5)
- [ ] Return list of results with `document`, `metadata.source_url`, `distance/similarity`
- [ ] Only search indexed corpus (5 pages)

## 7) UI (Tiny)
**Implementation (`app/app.py`):**
- [ ] Welcome line
- [ ] 3 example questions (e.g., "What is the expense ratio of HDFC Large Cap Fund Direct Growth?", "What is the ELSS lock-in?", "What is the minimum SIP for HDFC Mid Cap Fund Direct Growth?")
- [ ] Note: `Facts-only. No investment advice.`
- [ ] Input box for query + Submit
- [ ] Answer area: show answer (<=3 sentences), exactly **one** source link, and `Last updated from sources: <date>`
- [ ] On refusal (guardrails), show polite facts-only message + relevant educational link
- [ ] Disclaimer snippet visible

## 8) Edge Cases & Test Cases for Guardrails

### Edge Cases
| Case | Expected |
|---|---|
| Empty query | Prompt user / ignore safely |
| Query with PII (PAN/Aadhaar/email/phone/account/OTP) | Refuse politely; do not store/process PII |
| Opinion/advice ("Should I buy/sell/hold/recommend?") | Facts-only refusal + relevant educational link |
| Performance/returns/comparison ("Which is better?", "1 year return?") | Do not compute/compare; refuse and link to official factsheet |
| Out of scope (non-MF/general) | Refuse or say facts not found in indexed sources; suggest checking official pages |
| Ambiguous scheme name | Ask for clarification or pick most relevant from retrieved; still cite one link |
| No relevant chunks found | Safe refusal with suggestion to use official factsheet/link |
| Very long query | Truncate/handle; focus on factual intent |

### Guardrail Test Cases
| Test Query | Type | Expected Behavior |
|---|---|---|
| "What is the expense ratio of HDFC Large Cap Fund Direct Growth?" | Factual | Answer from corpus, <=3 sentences, exactly 1 source link, append "Last updated from sources: ..." |
| "ELSS lock-in period?" | Factual | Correct factual answer + 1 link |
| "Minimum SIP for HDFC Flexi Cap Direct Plan Growth?" | Factual | Correct factual answer + 1 link |
| "Exit load of HDFC Mid Cap Fund Direct Growth?" | Factual | Correct factual answer + 1 link |
| "Riskometer and benchmark of HDFC ELSS Tax Saver Fund Direct Plan Growth?" | Factual | Correct factual answer + 1 link |
| "Should I buy HDFC Large Cap Fund now?" | Advice/Opinion | Polite facts-only refusal + relevant educational link (no recommendation) |
| "Which fund is better, Large Cap or Mid Cap?" | Comparison/Opinion | Do not compare returns; facts-only refusal + factsheet/educational link |
| "Give me your recommendation for SIP amount" | Advice | Polite refusal with facts-only message |
| "My PAN is ABCDE1234F, tell me..." | PII | Refuse; do not accept/store PII |
| "What were the returns last year?" | Performance claim | Do not compute; link to official factsheet |
| "How to download capital-gains statement?" | Factual (process) | Factual answer from sources if present + 1 link, else safe refusal with official source suggestion |

## Implementation Order
1. Create directories + `config/config.yaml` + `.env` template
2. `src/load.py` - scrape 5 URLs, save `data/raw/` + metadata
3. `src/chunk.py` - chunk, save `data/chunks/chunks.jsonl`
4. `src/embed.py` - embed with all-MiniLM-L6-v2, save `data/embeddings/embeddings.jsonl`
5. `src/index.py` - build Chroma in `data/vectorstore/`
6. `src/guardrails.py` - detect advice/PII/performance/comparison
7. `src/retrieve.py` - query Chroma
8. `src/generate.py` - prompt + call LLM (Groq default) + format answer
9. `app/app.py` - tiny UI
10. Test with guardrail cases

## Config (example structure)
```yaml
data_sources:
  - url: https://groww.in/mutual-funds/amc/hdfc-mutual-funds
    scheme: "HDFC Mutual Fund - AMC Overview"
  - url: https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth
    scheme: "HDFC Large Cap Fund Direct Growth"
  - url: https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth
    scheme: "HDFC Flexi Cap Direct Plan Growth"
  - url: https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth
    scheme: "HDFC ELSS Tax Saver Fund Direct Plan Growth"
  - url: https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth
    scheme: "HDFC Mid Cap Fund Direct Growth"

chunking:
  strategy: "section_aware"  # or recursive
  chunk_size: 400
  chunk_overlap: 50

embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"
  batch_size: 32

vectorstore:
  type: "chromadb"
  persist_dir: "data/vectorstore"
  collection_name: "groww_mf_faq"

retrieval:
  top_k: 4

llm:
  provider: "groq"  # groq|gemini|openai|anthropic|mistral
  model: "qwen/qwen3.8-27b"
  temperature: 0.0
  max_tokens: 256
  api_key_env: "GROQ_API_KEY"
```

## Notes
- All stages write explicit artifacts to `data/` (visible for demo)
- Config file makes everything changeable
- Exactly one source link per answer
- Answers ≤ 3 sentences
- No advice, no PII, no performance claims/comparisons
'''

with open(dst, 'w', encoding='utf-8') as out:
    out.write(impl)

print('done')
