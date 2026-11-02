# Groww MF FAQ Assistant (RAG-based)

A facts-only Retrieval Augmented Generation (RAG) assistant that answers questions about HDFC Mutual Fund schemes using only official public Groww pages. 

## Features
- **Facts-only**: Answers only factual questions (no investment advice, recommendations, opinions, or performance claims)
- **Exact citations**: Every answer includes exactly one source link
- **Guardrails**: Refuses advice, PII, comparisons, performance claims
- **RAG Pipeline**: Data loading → Parsing/Cleaning → Section-aware Chunking → Embeddings (`sentence-transformers/all-MiniLM-L6-v2`) → ChromaDB → Retrieval → Generation
- **Multi-provider support**: Groq (default: `qwen/qwen3.8-27b`) via `.env`/Streamlit secrets
- **Clean UI**: Streamlit app with tabs, cards, and dark/system mode support

## Data Sources (Official Public Pages)
The assistant uses only these 5 official public Groww pages:

1. [HDFC Mutual Fund - AMC Overview](https://groww.in/mutual-funds/amc/hdfc-mutual-funds)
2. [HDFC Large Cap Fund Direct Growth](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth)
3. [HDFC Flexi Cap Direct Plan Growth](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth)
4. [HDFC ELSS Tax Saver Fund Direct Plan Growth](https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth)
5. [HDFC Mid Cap Fund Direct Growth](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)

## Sample Q&A
| Question | Answer | Source |
|---|---|---|
| What is the expense ratio of HDFC Large Cap Fund Direct Growth? | The expense ratio of HDFC Large Cap Fund Direct Growth is 1.02%. | [Source](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth) |
| What is the expense ratio of HDFC Mid Cap Fund Direct Growth? | The expense ratio of HDFC Mid Cap Fund Direct Growth is 1.05%. | [Source](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth) |
| What is the expense ratio of HDFC Flexi Cap Direct Plan Growth? | The expense ratio of HDFC Flexi Cap Fund Direct Plan Growth is 1.07%. | [Source](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth) |
| What is the ELSS lock-in period? | The ELSS lock-in period is 3 years. | [Source](https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth) |
| What is the minimum SIP for HDFC Large Cap Fund Direct Growth? | The minimum SIP for HDFC Large Cap Fund Direct Growth is ₹100. | [Source](# PR Title
diff --git a/README.md b/README.md
new file mode 100644
index 0000000..bf7f0df
--- /dev/null
+++ b/README.md
@@ -0,0 +1,113 @@
+# Groww MF FAQ Assistant (RAG-based)
+
+A facts-only Retrieval Augmented Generation (RAG) assistant that answers questions about HDFC Mutual Fund schemes using only official public Groww pages. 
+
+## Features
+- **Facts-only**: Answers only factual questions (no investment advice, recommendations, opinions, or performance claims)
+- **Exact citations**: Every answer includes exactly one source link
+- **Guardrails**: Refuses advice, PII, comparisons, performance claims
+- **RAG Pipeline**: Data loading → Parsing/Cleaning → Section-aware Chunking → Embeddings (`sentence-transformers/all-MiniLM-L6-v2`) → ChromaDB → Retrieval → Generation
+- **Multi-provider support**: Groq (default: `qwen/qwen3.8-27b`) via `.env`/Streamlit secrets
+- **Clean UI**: Streamlit app with tabs, cards, and dark/system mode support
+
+## Data Sources (Official Public Pages)
+The assistant uses only these 5 official public Groww pages:
+
+1. [HDFC Mutual Fund - AMC Overview](https://groww.in/mutual-funds/amc/hdfc-mutual-funds)
+2. [HDFC Large Cap Fund Direct Growth](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth)
+3. [HDFC Flexi Cap Direct Plan Growth](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth)
+4. [HDFC ELSS Tax Saver Fund Direct Plan Growth](https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth)
+5. [HDFC Mid Cap Fund Direct Growth](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)
+
+## Sample Q&A
+| Question | Answer | Source |
+|---|---|---|
+| What is the expense ratio of HDFC Large Cap Fund Direct Growth? | The expense ratio of HDFC Large Cap Fund Direct Growth is 1.02%. | [Source](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth) |
+| What is the expense ratio of HDFC Mid Cap Fund Direct Growth? | The expense ratio of HDFC Mid Cap Fund Direct Growth is 1.05%. | [Source](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth) |
+| What is the expense ratio of HDFC Flexi Cap Direct Plan Growth? | The expense ratio of HDFC Flexi Cap Fund Direct Plan Growth is 1.07%. | [Source](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth) |
+| What is the ELSS lock-in period? | The ELSS lock-in period is 3 years. | [Source](https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth) |
+| What is the minimum SIP for HDFC Large Cap Fund Direct Growth? | The minimum SIP for HDFC Large Cap Fund Direct Growth is ₹100. | [Source](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth) |
+| What is the exit load of HDFC Large Cap Fund Direct Growth? | The exit load for HDFC Large Cap Fund Direct Growth is 1% if redeemed within 1 year. | [Source](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth) |
+
+## Setup & Installation
+
+### Prerequisites
+- Python 3.10+
+- [Groq API key](https://console.groq.com/keys) (or configure your preferred provider)
+
+### Local Setup
+1. Clone the repository
+```bash
+git clone https://github.com/AkshayAdmin13/Groww_chatBot.git
+cd Groww_chatBot
+```
+
+2. Create virtual environment and install dependencies
+```bash
+pip install -r requirements.txt
+```
+
+3. Create `.env` file
+```env
+GROQ_API_KEY=your_groq_api_key_here
+```
+
+4. Run the Streamlit app
+```bash
+streamlit run app/app.py
+```
+
+## Project Structure
+```
+groww_chatbot/
+├── app/                # Streamlit UI
+├── config/             # Configuration files
+├── data/               # Raw data, chunks, embeddings, vectorstore
+├── src/                # Core modules (load, parse, chunk, embed, index, retrieve, generate, guardrails)
+├── scripts/            # Utility scripts
+├── requirements.txt    # Dependencies
+└── README.md
+```
+
+## Usage
+Ask factual questions like:
+- "What is the expense ratio of HDFC Large Cap Fund Direct Growth?"
+- "What is the ELSS lock-in period?"
+- "What is the minimum SIP for HDFC Mid Cap Fund Direct Growth?"
+- "What is the exit load of HDFC Flexi Cap Direct Plan Growth?"
+
+## Disclaimer
+**This is a facts-only assistant. No investment advice provided.**
+
+- Answers are based solely on the official public pages listed above
+- No personal information is collected or stored
+- No performance claims, comparisons, or recommendations are made
+- The assistant may refuse questions that ask for advice, opinions, PII, or non-factual information
+- Always refer to the official scheme documents for the most up-to-date information
+
+## Tech Stack
+- **Frontend**: [Streamlit](https://streamlit.io/)
+- **LLM**: [Groq](https://console.groq.com/) with `qwen/qwen3.8-27b`
+- **Embeddings**: [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
+- **Vector Store**: [ChromaDB](https://www.trychroma.com/)
+- **Parsing**: BeautifulSoup
+
+## Deployment
+This app is deployed on [Streamlit Community Cloud](https://share.streamlit.io/). For deployment:
+1. Push code to GitHub
+2. Create app from repo with `app/app.py` as main file
+3. Add `GROQ_API_KEY` to Streamlit Secrets
+
+## Contributing
+Feel free to open issues or submit pull requests for improvements.
+
+## License
+This project is for educational purposes.
