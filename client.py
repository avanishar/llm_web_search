import streamlit as st
from get_links import get_links
from scrape import scrape_links, initialize_logs
from cleaning import combine_logs
from llm import call_gemini, context_combine_prompt
from urllib.parse import urlparse, parse_qs, unquote
import os

# --- Streamlit UI ---
st.set_page_config(page_title="AI Web Search & Answer", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    body { background: #f9fafb; color: #111827; }
    .main { background-color: #ffffff; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 24px rgba(0,0,0,0.1); }
    .stTextInput>div>div>input { font-size: 18px; border-radius: 8px; background-color: #f3f4f6; color: #111827; border: 1px solid #d1d5db; }
    .stButton>button { font-size: 18px; background-color: #2563eb; color: white; border-radius: 8px; padding: 0.5em 2em; }
    .scraped-card { background: #f3f4f6; border-radius: 10px; padding: 1em; margin-bottom: 1em; box-shadow: 0 2px 6px rgba(0,0,0,0.05); color: #111827; }
    .answer-box-short { background: #6366f1; border-radius: 12px; padding: 1em; font-size: 1.1em; font-weight: 500; color: white; margin-bottom: 1em; }
    .answer-box-full { background: #4f46e5; border-radius: 12px; padding: 1.5em; font-size: 1.1em; font-weight: 500; color: white; margin-bottom: 1em; }
    .how-it-works { background: #e0e7ff; border-radius: 12px; padding: 1em; font-size: 1em; margin-bottom: 1em; color: #1e3a8a; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("🤖 AI Web Search & Answer")

# --- How it works ---
st.markdown(
    """
    <div class="how-it-works">
    <h4>📝 How it works:</h4>
    1. Enter a topic or question.<br>
    2. App finds top links and scrapes content.<br>
    3. Show combined content or content per website.<br>
    4. AI provides short answer & detailed summary.<br>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.header("Settings")
    num_links = st.slider("Number of links to scrape", 1, 10, 3)
    show_scraped = st.checkbox("Show combined scraped content", value=False)
    save_logs = st.checkbox("Save logs to markdown files", value=True)

topic = st.text_input("Enter your topic or question:", placeholder="e.g., latest AI news for today")

# DuckDuckGo cleaner
def clean_duckduckgo_url(url):
    if "duckduckgo.com/l/?" in url:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if 'uddg' in query:
            return unquote(query['uddg'][0])
    if url.startswith("//"):
        url = "https:" + url
    return url

# --- Main ---
if st.button("🔍 Get AI Answer"):
    if topic:
        with st.spinner("Processing your query..."):
            try:
                # Get links
                links = get_links(topic, num_links)
                links = [clean_duckduckgo_url(link) for link in links]

                # Logs
                log_folder = initialize_
