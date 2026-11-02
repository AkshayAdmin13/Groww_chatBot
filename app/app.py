import sys
import os
from datetime import datetime

import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from generate import Generator

st.set_page_config(page_title="Groww MF FAQ Assistant", page_icon="💸", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for better UI with dark mode support
st.markdown("""
<style>
    /* Light mode */
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(90deg, #00d09c 0%, #5367ff 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        color: white !important;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin: 0;
    }
    .header-subtitle {
        color: white !important;
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.5rem;
        opacity: 0.95;
    }
    
    /* Cards */
    .example-card {
        background: white;
        color: #1f1f1f !important;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00d09c;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .example-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Answer box */
    .answer-box {
        background: white;
        color: #1f1f1f !important;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #00d09c;
        margin-top: 1rem;
        box-shadow: 0 2px 8px rgba(0, 208, 156, 0.1);
    }
    
    /* Disclaimer */
    .disclaimer {
        background: #fff3cd;
        color: #856404 !important;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-top: 2rem;
    }
    
    /* Button */
    .stButton > button {
        background: linear-gradient(90deg, #00d09c 0%, #00b386 100%);
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0, 208, 156, 0.3);
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .main, .stApp {
            background: linear-gradient(135deg, #0e1117 0%, #1e1e1e 100%) !important;
        }
        .example-card, .answer-box {
            background: #262730 !important;
            color: #fafafa !important;
            border-color: #00d09c !important;
        }
        .disclaimer {
            background: #3d341f !important;
            color: #ffd93d !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #fafafa !important;
        }
        .stTextInput > div > div > input {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">Groww MF FAQ Assistant</h1>
    <p class="header-subtitle">Factual answers about HDFC Mutual Fund schemes • Official sources only</p>
</div>
""", unsafe_allow_html=True)

# Main content
tab1, tab2 = st.tabs(["💬 Ask Question", "ℹ️ About"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Example Questions")
        st.markdown("""
        <div class="example-card"><strong>Expense Ratio</strong> • What is the expense ratio of HDFC Large Cap Fund Direct Growth?</div>
        <div class="example-card"><strong>ELSS Lock-in</strong> • What is the ELSS lock-in period?</div>
        <div class="example-card"><strong>Minimum SIP</strong> • What is the minimum SIP for HDFC Mid Cap Fund Direct Growth?</div>
        <div class="example-card"><strong>Exit Load</strong> • What is the exit load of HDFC Flexi Cap Direct Plan Growth?</div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Key Features")
        st.info("**Scope:** HDFC AMC + 4 schemes\n\n**Constraints:** Public sources only • No PII • No advice")
        st.success("**Every answer includes:**\n- Exact fact\n- Single source link\n- Timestamp")
    
    st.markdown("### Your Question")
    query = st.text_input("", placeholder="Ask a factual question...", label_visibility="collapsed")
    
    if st.button("Get Answer", use_container_width=False):
        if not query.strip():
            st.warning("Please enter a question.")
        else:
            if 'gen' not in st.session_state:
                with st.spinner("Loading..."):
                    st.session_state.gen = Generator()
            with st.spinner("Searching official sources..."):
                res = st.session_state.gen.answer(query)
            if res.get('refused'):
                st.error(res['answer'])
                if res.get('source_url'):
                    st.markdown(f"**Source:** [{res['source_url']}]({res['source_url']})")
            else:
                st.markdown(f"""
                <div class="answer-box">
                    <p style="font-size: 1.05rem; margin: 0; line-height: 1.6;">{res['answer'].replace(chr(10), '<br>')}</p>
                </div>
                """, unsafe_allow_html=True)
            st.caption(f"Last updated from sources: {datetime.now().strftime('%Y-%m-%d')}")

with tab2:
    st.markdown("### About This Assistant")
    st.write("This is a RAG-based FAQ assistant built for HDFC Mutual Fund schemes. It answers only factual questions using official public pages from Groww.")
    st.markdown("### Data Sources")
    st.write("- HDFC Mutual Fund AMC Overview\n- HDFC Large Cap Fund Direct Growth\n- HDFC Flexi Cap Direct Plan Growth\n- HDFC ELSS Tax Saver Fund Direct Plan Growth\n- HDFC Mid Cap Fund Direct Growth")
    st.markdown("### Disclaimer")
    st.markdown("""
    <div class="disclaimer">
        <strong>Facts-only. No investment advice.</strong><br>
        No PII collected or stored. No performance claims or comparisons. Every answer cites official sources.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center><small>Powered by RAG • ChromaDB • Sentence Transformers • Groq</small></center>", unsafe_allow_html=True)
