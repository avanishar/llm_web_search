import streamlit as st
from get_links import get_links
from scrape import scrape_links, initialize_logs
from cleaning import combine_logs
from llm import call_gemini, context_combine_prompt
import glob
import os

# --- Summarization helper ---
def summarize_answer(answer):
    prompt = f"Summarize the following answer in 3-4 concise sentences:\n\n{answer}"
    return call_gemini(prompt)

# --- Streamlit UI setup ---
st.set_page_config(page_title="AI Web Search & Answer", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
    }
    .main {
        background-color: #1e293b;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.6);
    }
    .stTextInput>div>div>input {
        font-size: 18px;
        border-radius: 8px;
        background-color: #334155;
        color: white;
    }
    .stButton>button {
        font-size: 18px;
        background-color: #22c55e;
        color: white;
        border-radius: 8px;
        padding: 0.5em 2em;
    }
    .scraped-card {
        background: #334155;
        border-radius: 10px;
        padding: 1em;
        margin-bottom: 1em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
        color: #e2e8f0;
    }
    .answer-box {
        background: #0ea5e9;
        border-radius: 12px;
        padding: 1.5em;
        font-size: 1.2em;
        font-weight: 500;
        color: white;
        margin-bottom: 1em;
        box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("🤖 AI Web Search & Answer")

with st.expander("ℹ️ How it works", expanded=False):
    st.markdown(
        """
        1. Enter a topic or question.
        2. The app searches the web, scrapes content, and summarizes an answer using AI.
        3. You can view the scraped links, the full scraped content, and the AI's summarized answer below.
        """
    )

# Sidebar
with st.sidebar:
    st.header("Settings")
    num_links = st.slider("Number of links to scrape", 1, 10, 3)
    show_scraped = st.checkbox("Show combined scraped content", value=False)
    save_logs = st.checkbox("Save logs to markdown files", value=True)

topic = st.text_input("Enter your topic or question:", placeholder="e.g., latest AI news for today")

if st.button("🔍 Get AI Answer"):
    if topic:
        with st.spinner("Searching and processing..."):
            try:
                links = get_links(topic, num_links)
                if not links:
                    st.warning("No links found. Try a different query.")
                else:
                    st.success(f"Found {len(links)} links.")
                    st.markdown("#### Scraped Links")
                    for link in links:
                        st.markdown(f"- [{link}]({link})")

                    log_folder = initialize_logs(topic)
                    result = scrape_links(links, save_logs=save_logs, log_folder=log_folder)

                    if result["errors"]:
                        for link, msg in result["errors"]:
                            st.warning(f"⚠️ Could not scrape {link}: {msg}")

                    if not result["success"]:
                        st.error("No content was successfully scraped.")
                    else:
                        st.success(f"✅ Scraped {len(result['success'])} website(s) successfully.")

                        if save_logs:
                            st.markdown("### 📄 Scraped Content from Each Link")
                            md_files = sorted(glob.glob(os.path.join(log_folder, "*.md")))
                            for md_file in md_files:
                                with open(md_file, "r", encoding="utf-8") as f:
                                    content = f.read()
                                filename = os.path.basename(md_file)
                                with st.expander(f"📰 {filename}"):
                                    st.markdown(f'<div class="scraped-card">{content}</div>', unsafe_allow_html=True)

                        context_from_logs = combine_logs(log_folder)
                        if show_scraped:
                            st.markdown("#### Scraped Content (Combined)")
                            st.code(context_from_logs[:2000] + ("..." if len(context_from_logs) > 2000 else ""), language="markdown")

                        final_prompt = context_combine_prompt(context_from_logs, topic)
                        answer = call_gemini(final_prompt)
                        summary = summarize_answer(answer)

                        st.markdown("### 🤖 AI Summarized Answer")
                        st.markdown(f'<div class="answer-box">{summary}</div>', unsafe_allow_html=True)

                        with st.expander("Show Full AI Answer"):
                            st.markdown(answer)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic or question first!")

st.markdown('</div>', unsafe_allow_html=True)
