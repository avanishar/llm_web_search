import streamlit as st
from get_links import get_links
from scrape import scrape_links, initialize_logs
from cleaning import combine_logs
from llm import call_gemini, context_combine_prompt
from urllib.parse import urlparse, parse_qs, unquote
import glob
import os

# --- Streamlit UI setup ---
st.set_page_config(page_title="AI Web Search & Answer", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        color: black;
    }
    .main {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.15);
    }
    .stTextInput>div>div>input {
        font-size: 18px;
        border-radius: 8px;
        background-color: #f8fafc;
        color: black;
        border: 1px solid #cbd5e1;
    }
    .stButton>button {
        font-size: 18px;
        background-color: #16a34a;
        color: white;
        border-radius: 8px;
        padding: 0.5em 2em;
    }
    .scraped-card {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 1em;
        margin-bottom: 1em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        color: #111827;
    }
    .answer-box {
        background: #0ea5e9;
        border-radius: 12px;
        padding: 1.5em;
        font-size: 1.2em;
        font-weight: 500;
        color: white;
        margin-bottom: 1em;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }
    .how-it-works {
        background: #fef3c7;
        border-radius: 12px;
        padding: 1em;
        font-size: 1em;
        margin-bottom: 1em;
        color: #92400e;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main">', unsafe_allow_html=
