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

                # Initialize logs
                log_folder = initialize_logs(topic)

                # Scrape links
                result = scrape_links(links, save_logs=save_logs, log_folder=log_folder)
                success_links = result.get('success', [])
                errors = result.get('errors', [])

                if not success_links:
                    st.warning("No content could be scraped from the links.")
                    for link, msg in errors:
                        st.error(f"Could not scrape {link}: {msg}")
                else:
                    # Show content based on user selection
                    context_from_logs = combine_logs(log_folder)
                    if show_scraped:
                        if len(context_from_logs) > 10000:
                            context_from_logs = context_from_logs[:10000]
                        st.markdown("#### Combined Scraped Content")
                        st.code(context_from_logs[:3000] + ("..." if len(context_from_logs) > 3000 else ""), language="markdown")
                    else:
                        st.markdown("#### Scraped Content per Website")
                        for log_file in sorted(os.listdir(log_folder)):
                            if log_file.endswith(".md"):
                                with open(os.path.join(log_folder, log_file), "r", encoding="utf-8") as f:
                                    content = f.read()
                                    st.markdown(f"**{log_file.replace('.md','')}**")
                                    st.code(content[:3000] + ("..." if len(content) > 3000 else ""), language="markdown")
                        if len(context_from_logs) > 10000:
                            context_from_logs = context_from_logs[:10000]

                    # Short answer
                    final_prompt_short = context_combine_prompt(
                        context_from_logs, topic + "\nPlease provide a concise answer in 2-3 sentences."
                    )
                    answer_short = call_gemini(final_prompt_short)
                    st.markdown("### 🤖 AI Short Answer")
                    st.markdown(f'<div class="answer-box-short">{answer_short}</div>', unsafe_allow_html=True)

                    # Detailed summary
                    final_prompt_full = context_combine_prompt(
                        context_from_logs, topic + "\nPlease provide a detailed summary of all the information."
                    )
                    answer_full = call_gemini(final_prompt_full)
                    st.markdown("### 📜 AI Detailed Summary")
                    st.markdown(f'<div class="answer-box-full">{answer_full}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic or question first!")

st.markdown('</div>', unsafe_allow_html=True)
