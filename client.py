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
        background: #f9fafb;
        color: #111827;
    }
    .main {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.1);
    }
    .stTextInput>div>div>input {
        font-size: 18px;
        border-radius: 8px;
        background-color: #f3f4f6;
        color: #111827;
        border: 1px solid #d1d5db;
    }
    .stButton>button {
        font-size: 18px;
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 0.5em 2em;
    }
    .scraped-card {
        background: #f3f4f6;
        border-radius: 10px;
        padding: 1em;
        margin-bottom: 1em;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        color: #111827;
    }
    .answer-box-short {
        background: #6366f1;
        border-radius: 12px;
        padding: 1em;
        font-size: 1.1em;
        font-weight: 500;
        color: white;
        margin-bottom: 1em;
    }
    .answer-box-full {
        background: #4f46e5;
        border-radius: 12px;
        padding: 1.5em;
        font-size: 1.1em;
        font-weight: 500;
        color: white;
        margin-bottom: 1em;
    }
    .how-it-works {
        background: #e0e7ff;
        border-radius: 12px;
        padding: 1em;
        font-size: 1em;
        margin-bottom: 1em;
        color: #1e3a8a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("🤖 AI Web Search & Answer")

# --- How it works for users ---
st.markdown(
    """
    <div class="how-it-works">
    <h4>📝 How it works:</h4>
    1. Enter a topic or question.<br>
    2. The app finds top web links and scrapes content.<br>
    3. Content is combined and sent to the AI.<br>
    4. You get a **short answer** and a **detailed summary**.<br>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    num_links = st.slider("Number of links to scrape", 1, 10, 3)
    show_scraped = st.checkbox("Show combined scraped content", value=False)
    save_logs = st.checkbox("Save logs to markdown files", value=True)

topic = st.text_input("Enter your topic or question:", placeholder="e.g., latest AI news for today")

# --- DuckDuckGo URL cleaner ---
def clean_duckduckgo_url(url):
    if "duckduckgo.com/l/?" in url:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if 'uddg' in query:
            return unquote(query['uddg'][0])
    if url.startswith("//"):
        url = "https:" + url
    return url

# --- Main action ---
if st.button("🔍 Get AI Answer"):
    if topic:
        with st.spinner("Processing your query..."):
            try:
                # Get links
                links = get_links(topic, num_links)
                links = [clean_duckduckgo_url(link) for link in links]

                # Initialize logs
                log_folder = initialize_logs(topic)

                # Scrape links
                result = scrape_links(links, save_logs=save_logs, log_folder=log_folder)
                success_count = len(result.get('success', []))
                errors = result.get("errors", [])

                if success_count == 0:
                    st.warning("No content could be scraped from the links.")
                    for link, msg in errors:
                        st.error(f"Could not scrape {link}: {msg}")
                else:
                    context_from_logs = combine_logs(log_folder)
                    if len(context_from_logs) > 10000:
                        context_from_logs = context_from_logs[:10000]

                    if show_scraped:
                        st.markdown("#### Scraped Content (Combined)")
                        st.code(
                            context_from_logs[:2000] + ("..." if len(context_from_logs) > 2000 else ""),
                            language="markdown"
                        )

                    # Short answer
                    final_prompt_short = context_combine_prompt(context_from_logs, topic, mode="short")
                    answer_short = call_gemini(final_prompt_short)
                    st.markdown("### 🤖 AI Short Answer")
                    st.markdown(f'<div class="answer-box-short">{answer_short}</div>', unsafe_allow_html=True)

                    # Detailed summary
                    final_prompt_full = context_combine_prompt(context_from_logs, topic, mode="detailed")
                    answer_full = call_gemini(final_prompt_full)
                    st.markdown("### 📜 AI Detailed Summary")
                    st.markdown(f'<div class="answer-box-full">{answer_full}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic or question first!")

st.markdown('</div>', unsafe_allow_html=True)
