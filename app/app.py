import sys
import os
from datetime import datetime

import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from generate import Generator

st.set_page_config(page_title="Groww MF FAQ Assistant", page_icon="💸", layout="centered")

st.title("Groww MF FAQ Assistant")
st.write("**Welcome!** Ask factual questions about HDFC Mutual Fund schemes.")
st.write("**Example questions:**")
st.write("1. What is the expense ratio of HDFC Large Cap Fund Direct Growth?")
st.write("2. What is the ELSS lock-in period?")
st.write("3. What is the minimum SIP for HDFC Mid Cap Fund Direct Growth?")
st.caption("Facts-only. No investment advice.")
st.divider()

if 'gen' not in st.session_state:
    st.session_state.gen = Generator()

query = st.text_input("Ask your question", placeholder="e.g., Expense ratio of HDFC Large Cap Fund Direct Growth?")
if st.button("Submit"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching..."):
            res = st.session_state.gen.answer(query)
        if res.get('refused'):
            st.error(res['answer'])
            if res.get('source_url'):
                st.markdown(f"**Relevant link:** [{res['source_url']}]({res['source_url']})")
        else:
            st.success(res['answer'])
            st.markdown(f"**Source:** [{res['source_url']}]({res['source_url']})")
        st.caption(f"Last updated from sources: {datetime.now().strftime('%Y-%m-%d')}")

st.divider()
st.caption("Disclaimer: Facts-only. No investment advice. Answers are based only on official public pages of the listed HDFC schemes. No PII is collected or stored.")
