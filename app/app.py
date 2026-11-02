import sys
import os
from datetime import datetime

import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from generate import Generator

st.set_page_config(page_title="Groww MF FAQ Assistant", page_icon="💸", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    }
    .header-container {
        background: linear-gradient(90deg, #00d09c 0%, #5367ff 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin: 0;
    }
    .header-subtitle {
        color: white;
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.5rem;
        opacity: 0.95;
    }
    .example-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00d09c;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    .example-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .answer-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #00d09c;
        margin-top: 1rem;
        box-shadow: 0 2px 8px rgba(0, 208, 156, 0.1);
    }
    .disclaimer {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-top: 2rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #00d09c 0%, #00b386 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0, 208, 156, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🌱 Groww MF FAQ Assistant</h1>
    <p class="header-subtitle">Your trusted source for factual mutual fund information</p>
</div>
""", unsafe_allow_html=True)

# Welcome section
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### 👋 Welcome!")
    st.write("Ask factual questions about HDFC Mutual Fund schemes using only official public sources.")
    st.markdown("**🎯 Facts-only. No investment advice.**")
    
    st.markdown("### 💡 Example Questions")
    st.markdown("""
    <div class="example-card">💰 <strong>Expense Ratio:</strong> "What is the expense ratio of HDFC Large Cap Fund Direct Growth?"</div>
    <div class="example-card">🔒 <strong>ELSS Lock-in:</strong> "What is the ELSS lock-in period?"</div>
    <div class="example-card">💸 <strong>Minimum SIP:</strong> "What is the minimum SIP for HDFC Mid Cap Fund Direct Growth?"</div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📋 Quick Facts")
    st.info("**Covers:**\n- Expense Ratio\n- Exit Load\n- Minimum SIP\n- ELSS Lock-in\n- Riskometer & Benchmark\n- Statement Download")
    st.success("**Features:**\n- ✅ Official Sources Only\n- ✅ Exact Citations\n- ✅ No Investment Advice\n- ✅ Safe & Transparent")

st.divider()

# Query section
st.markdown("### 🔍 Ask Your Question")
query = st.text_input("", placeholder="Type your question here... e.g., What is the expense ratio of HDFC Large Cap Fund Direct Growth?", label_visibility="collapsed")

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
with col_btn2:
    submit = st.button("🚀 Get Answer", use_container_width=True)

if submit:
    if not query.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        if 'gen' not in st.session_state:
            with st.spinner("Initializing assistant..."):
                st.session_state.gen = Generator()
        with st.spinner("🔍 Searching official sources..."):
            res = st.session_state.gen.answer(query)
        if res.get('refused'):
            st.error(res['answer'])
            if res.get('source_url'):
                st.markdown(f"**🔗 Relevant Link:** [{res['source_url']}]({res['source_url']})")
        else:
            st.markdown(f"""
            <div class="answer-box">
                <h4 style="color: #00d09c; margin-top: 0;">✅ Answer</h4>
                <p style="font-size: 1.1rem; line-height: 1.6;">{res['answer'].replace(chr(10), '<br>')}</p>
                <hr style="border: 1px solid #e0e0e0;">
                <p><strong>🔗 Source:</strong> <a href="{res['source_url']}" target="_blank">{res['source_url']}</a></p>
            </div>
            """, unsafe_allow_html=True)
        st.caption(f"🕒 Last updated from sources: {datetime.now().strftime('%Y-%m-%d')}")

# Disclaimer
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Disclaimer:</strong> This is a facts-only assistant. No investment advice provided. 
    All answers are based solely on official public pages of the listed HDFC Mutual Fund schemes. 
    No personal information is collected or stored.
</div>
""", unsafe_allow_html=True)
