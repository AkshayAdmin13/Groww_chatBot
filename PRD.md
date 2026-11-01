# Product Requirements Document (PRD) - Groww MF FAQ Assistant

## Problem statement recap
We are using 
Groww app to build 
a small FAQ assistant that answers facts about mutual fund schemes—e.g., expense ratio, exit load, minimum SIP, lock-in (ELSS), riskometer, benchmark, and how to download statements—using only official public pages. Every answer must include one source link. No advice.
Who this helps
Retail users comparing schemes; support/content teams answering repetitive MF questions.
What you must build
Data :- Scrape these pages and store ( do not scrape link internal to these pages, just these 5 pages) 
AMC overview — HDFC Mutual Fund- https://groww.in/mutual-funds/amc/hdfc-mutual-funds 
| 2 | Large Cap — HDFC Large Cap Fund Direct Growth | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 3 | Flexi Cap — HDFC Flexi Cap Direct Plan Growth | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 4 | ELSS (tax saver) — HDFC ELSS Tax Saver Fund Direct Plan Growth | https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth |
| 5 | Mid Cap — HDFC Mid Cap Fund Direct Growth | https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth |

FAQ assistant (working prototype):
Answers factual queries only (e.g., “Expense ratio of ?”, “ELSS lock-in?”, “Minimum SIP?”, “Exit load?”, “Riskometer/benchmark?”, “How to download capital-gains statement?”).
Shows one clear citation link in every answer.
Refuses opinionated/portfolio questions (e.g., “Should I buy/sell?”) with a polite, facts-only message and a relevant educational link.
Tiny UI: welcome line + 3 example questions and a note: “Facts-only. No investment advice.”
Key constraints
**Public sources only.** No screenshots of the app back-end; no third-party blogs as sources.
**No PII.** Do not accept/store PAN, Aadhaar, account numbers, OTPs, emails, or phone numbers.
**No performance claims.** Don’t compute/compare returns; link to the official factsheet if asked.
**Clarity & transparency.** Keep answers ≤3 sentences; add “Last updated from sources: ”.
What to submit (deliverables)
Working prototype link (app/notebook) or a ≤3-min demo video if hosting isn’t possible.
Source list (CSV/MD) of the 15–25 URLs you used.
README with setup steps, scope (AMC + schemes), and known limits.
Sample Q&A file (5–10 queries with the assistant’s answers + links).
Disclaimer snippet used in your UI (facts-only, no advice).
Skills being tested
W1 — Thinking Like a Model: identify the exact fact asked; decide answer vs. refuse.
W2 — LLMs & Prompting: instruction style, concise phrasing, polite safe-refusals, citation wording.
W3 — RAGs (only): small-corpus retrieval with accurate citations from AMC/SEBI/AMFI pages.
This is a demo of RAG thus want to have each stage data stored explicitly to be shown. 
Want to implement it in phase wise manner 
Data Loading 
Data Chunking ( use chunking strategy based on the data, AI cosing agent can decide the chunking strategy) 
Data embedding 
sentence-transformers/all-MiniLM-L6-v2 model 
Vecotr DB - We are using chromaDB for this exercise 
Make this thing in the config file, to be changed.


Data retrieval 
Embedding model - same as the one used for data ingestion 
Vector DB - same as data ingestion. 
LLM Model 
Groq - API Keys 
Model - qwen/qwen3.8-27b, take the model deo  .env file. 
Gemini , OPen PI, Anthropic , mistal 


## Objective
Build a small FAQ assistant that answers factual questions about mutual fund schemes using only official public pages from Groww/AMC sources, with every answer including exactly one source link, no advice, and strict PII/safety constraints. The project is a demo of RAG and must show each stage explicitly (Data Loading, Data Chunking, Data Embedding, Data Retrieval) in a phase-wise manner with configurable components.

## Goals
- Answers factual queries only (expense ratio, exit load, minimum SIP, lock-in (ELSS), riskometer, benchmark, how to download statements)
- Every answer must include one clear citation link
- Refuse opinionated/portfolio questions politely with facts-only message and relevant educational link
- Tiny UI: welcome line + 3 example questions + note "Facts-only. No investment advice."
- Phase-wise RAG implementation with explicit stored artifacts for each stage
- Configurable components via config file
- Support multiple LLM providers (Groq, Gemini, OpenAI, Anthropic, Mistral) with Groq/qwen/qwen3.8-27b as primary (from .env)

## Target users
Retail users comparing schemes; support/content teams answering repetitive MF questions.

## Data sources (only these 5 pages, no internal links scraped)
| # | Scheme/AMC | URL |
|---|---|---|
| 1 | AMC overview — HDFC Mutual Fund | https://groww.in/mutual-funds/amc/hdfc-mutual-funds |
| 2 | Large Cap — HDFC Large Cap Fund Direct Growth | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 3 | Flexi Cap — HDFC Flexi Cap Direct Plan Growth | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 4 | ELSS (tax saver) — HDFC ELSS Tax Saver Fund Direct Plan Growth | https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth |
| 5 | Mid Cap — HDFC Mid Cap Fund Direct Growth | https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth |

## Scope
- AMC + the 4 schemes listed above
- Factual MF scheme facts only
- Public sources only (no app backend screenshots, no third-party blogs)

## Key constraints
- Public sources only. No screenshots of app back-end; no third-party blogs as sources.
- No PII. Do not accept/store PAN, Aadhaar, account numbers, OTPs, emails, or phone numbers.
- No performance claims. Don't compute/compare returns; link to the official factsheet if asked.
- Clarity & transparency. Keep answers ≤ 3 sentences; add "Last updated from sources: "
- Every answer must include one source link.
- No investment advice.

## RAG architecture (phase-wise, explicit artifacts)
### Phase 1: Data Loading
- Scrape only the 5 pages listed above (no following internal links)
- Store raw scraped content explicitly (e.g., `data/raw/` with per-URL files/metadata)
- Record source URLs, timestamps, fetch status

### Phase 2: Data Chunking
- Chunk scraped data using a chunking strategy chosen by the coding agent based on the data structure
- Store chunks explicitly (e.g., `data/chunks/` with chunk metadata: source_url, chunk_id, text)
- Make strategy configurable/documented

### Phase 3: Data Embedding
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Generate embeddings for all chunks
- Store embeddings explicitly
- Configuration: model name in config file

### Phase 4: Vector DB
- Vector DB: ChromaDB
- Persist collection/index explicitly (e.g., `data/vectorstore/`)
- Store collection name, embedding model, chunking strategy in metadata/config
- All of the above must be configurable via a config file

### Phase 5: Data Retrieval
- Embedding model: same as data ingestion
- Vector DB: same as data ingestion (ChromaDB)
- Retrieve relevant chunks for user query with citations

### Phase 6: LLM & Answering
- LLM providers supported: Groq, Gemini, OpenAI, Anthropic, Mistral (configurable)
- Primary/default via Groq: model `qwen/qwen3.8-27b` (read from `.env`)
- API keys from `.env`
- Prompting: factual-only, cite exactly one source link, refuse advice/opinionated queries politely with educational link, answer ≤3 sentences, append "Last updated from sources: "
- If asked for returns/comparisons/performance claims → do not compute; link to official factsheet
- If PII attempted → refuse/ignore per constraints

## Configuration
- Central config file (e.g., `config.yaml` or `config.json`) controlling scraping targets, chunking strategy/params, embedding model, vector store, retrieval params, LLM provider/model, API keys env var names, paths for artifacts

## UI requirements (tiny)
- Welcome line
- 3 example questions
- Note: "Facts-only. No investment advice."
- Input for query, answer area showing answer + exactly one source link
- Polite refusal for opinionated questions with facts-only message and relevant educational link

## Deliverables
1. Working prototype link (app/notebook) OR ≤3-min demo video if hosting not possible
2. Source list (CSV/MD) of the 15–25 URLs used
3. README with setup steps, scope (AMC + schemes), and known limits
4. Sample Q&A file (5–10 queries with assistant’s answers + links)
5. Disclaimer snippet used in UI (facts-only, no advice)

## Success criteria
- All answers grounded only in the 5 indexed pages; every answer has exactly one citation link
- Correctly refuses "Should I buy/sell?" style questions with facts-only message + educational link
- Adheres to all constraints
- Each RAG stage has explicit stored artifacts visible
- Config-driven design

## Skills tested
- W1 — Thinking Like a Model
- W2 — LLMs & Prompting
- W3 — RAGs (only)
