# Architecture - Groww MF FAQ Assistant (RAG Demo)

## Overview
This is a phase-wise RAG demo that answers factual questions about HDFC Mutual Fund schemes using only 5 public Groww pages. Every answer includes exactly one source link, refuses advice, and has explicit artifacts for each stage. All components are config-driven.

## High-level Architecture
```text
[User (Tiny UI)] 
  -> [Query Handler / Guardrails]
    -> [Retriever (ChromaDB + all-MiniLM-L6-v2)]
      -> [Context (top-k chunks with source_url)]
        -> [LLM (Groq qwen/qwen3.8-27b by default, others configurable)]
          -> [Answer Formatter (<=3 sentences, citation, "Last updated from sources: ...")]
            -> [UI (answer + 1 link, refusal path)]
```

## Phase-wise Implementation

### Phase 1: Data Loading
- **Input**: 5 fixed URLs (AMC + 4 schemes)
- **Process**: HTTP fetch only those URLs (no internal link crawling). Validate public sources.
- **Artifacts (explicit)**: `data/raw/` - per-URL raw HTML/text + `data/raw/metadata.json` (url, fetched_at, status, content_hash)
- **Config**: `data_sources` list in config

### Phase 2: Data Chunking
- **Input**: Raw content from Phase 1
- **Process**: Apply chunking strategy selected by agent based on data (e.g., section/heading-aware, markdown/HTML structure aware, or recursive). Strategy and params configurable.
- **Artifacts (explicit)**: `data/chunks/chunks.jsonl` or per-file with fields `{chunk_id, source_url, scheme, text, chunk_meta}`
- **Config**: `chunking.strategy`, `chunking.chunk_size`, `chunking.chunk_overlap`, etc.

### Phase 3: Data Embedding
- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (same for ingestion and retrieval)
- **Process**: Generate embeddings for each chunk
- **Artifacts (explicit)**: `data/embeddings/embeddings.jsonl` (or stored with chunks) containing `{chunk_id, source_url, embedding}`; also record model name
- **Config**: `embedding.model_name`, `embedding.device`, `embedding.batch_size`

### Phase 4: Vector DB (Storage)
- **DB**: ChromaDB (persistent)
- **Process**: Create/load collection, upsert chunks+embeddings+metadata (source_url, scheme, chunk_id)
- **Artifacts (explicit)**: `data/vectorstore/` (Chroma persist directory) with collection metadata
- **Config**: `vectorstore.type=chromadb`, `vectorstore.persist_dir`, `vectorstore.collection_name`

### Phase 5: Data Retrieval
- **Process**: Embed user query with same model, similarity search in ChromaDB (top-k). Return chunks with source_url and text.
- **Config**: `retrieval.top_k`, `retrieval.score_threshold` (optional)
- **Guarantee**: Only corpus from 5 pages is indexed

### Phase 6: LLM & Answer Generation
- **Providers**: Groq (default), Gemini, OpenAI, Anthropic, Mistral - configurable
- **Default model**: `qwen/qwen3.8-27b` via Groq, API key from `.env` (GROQ_API_KEY etc.)
- **Prompting rules**:
  - Answer only if factual and supported by retrieved chunks
  - Cite exactly **one** source link (choose most relevant from retrieved context)
  - Keep answer ≤ 3 sentences
  - Append: `Last updated from sources: <date or source info>`
  - Refuse opinionated/portfolio questions (e.g., "Should I buy/sell?") with polite facts-only message + relevant educational link
  - No performance claims/comparisons; if asked, do not compute - link to official factsheet
  - No PII handling/storage
- **Config**: `llm.provider`, `llm.model`, `llm.temperature`, `llm.max_tokens`, keys via env

## Component Diagram (modules)
```text
groww_chatbot/
├── config/           # config.yaml/json (all params)
├── data/
│   ├── raw/          # Phase 1 artifacts
│   ├── chunks/       # Phase 2 artifacts
│   ├── embeddings/   # Phase 3 artifacts
│   └── vectorstore/  # Phase 4 artifacts (Chroma)
├── src/
│   ├── load.py       # Phase 1
│   ├── chunk.py      # Phase 2
│   ├── embed.py      # Phase 3
│   ├── index.py      # Phase 4 (build Chroma)
│   ├── retrieve.py   # Phase 5
│   ├── generate.py   # Phase 6 (LLM + prompts/guardrails)
│   ├── guardrails.py # refusal logic
│   └── utils.py
├── app/              # Tiny UI (streamlit/gradio/flask) or notebook
├── .env              # API keys (GROQ_API_KEY, etc.)
├── README.md
├── PRD.md
├── architecture.md
└── requirements.txt
```

## Data Flow
1. **Ingestion pipeline** (run once/explicit): load -> chunk -> embed -> index (writes all artifacts to disk)
2. **Query pipeline** (runtime): user query -> guardrails (refuse if opinionated/PII-like) -> embed query -> retrieve from Chroma -> generate with LLM -> format answer with 1 link + timestamp note

## Guardrails
- **Advice/opinion**: detect patterns like buy/sell/hold/recommend/best/worth -> refuse politely with facts-only message and educational link (e.g., Groww/AMFI/SEBI educational page)
- **PII**: do not accept/store PAN/Aadhaar/account/OTP/email/phone
- **Performance claims**: refuse to compute/compare; suggest official factsheet
- **Scope**: only answer from indexed corpus; if no relevant chunk, give safe refusal or direct to relevant source

## Configuration (must be changeable)
All of the following in config file:
- `data_sources` (the 5 URLs)
- `chunking` (strategy, params)
- `embedding.model_name = "sentence-transformers/all-MiniLM-L6-v2"`
- `vectorstore` (type, persist_dir, collection_name)
- `retrieval.top_k`
- `llm.provider`, `llm.model` (Groq `qwen/qwen3.8-27b` default), env key names
- Paths for `data/raw`, `data/chunks`, `data/embeddings`, `data/vectorstore`

## Security & Constraints
- Public sources only
- No PII storage
- No performance claims
- Every answer has one citation
- Answers ≤ 3 sentences
- No third-party blogs/screenshots of backend

## Testing/Deliverables alignment
- Explicit artifacts for each phase visible
- Source list CSV/MD
- Sample Q&A (5-10)
- Disclaimer snippet in UI
- Working prototype/demo video
