import streamlit as st
from get_links import get_links
from scrape import scrape_links, initialize_logs
from cleaning import combine_logs
from llm import call_gemini, context_combine_prompt
import glob
import os
import time

# --- Summarization helper ---
def summarize_answer(answer):
    prompt = f"Summarize the following answer in 3-4 concise sentences:\n\n{answer}"
    summary = call_gemini(prompt)
    return summary

# --- Caching Wrappers ---
@st.cache_data(ttl=3600)
def cached_get_links(topic, num_links):
    return get_links(topic, num_links)

@st.cache_data(ttl=3600)
def cached_combine_logs(log_folder):
    return combine_logs(log_folder)

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Web Search & Answer", page_icon="🤖", layout="centered")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    theme = st.radio("Theme", ["🌞 Light", "🌙 Dark"], horizontal=True)
    num_links = st.slider("Number of links to scrape", 1, 10, 3)
    show_scraped = st.checkbox("Show combined scraped content", value=False)
    save_logs = st.checkbox("Save logs to markdown files", value=True)

    if st.button("🧹 Clear Cache"):
        st.cache_data.clear()
        st.success("✅ Cache cleared successfully!")

# Apply full-page theme
if theme == "🌙 Dark":
    bg_color = "#121212"
    text_color = "#ffffff"
    answer_box_bg = "#1f2937"  # dark gray box for answers
else:
    bg_color = "#f5f7fa"
    text_color = "#222"
    answer_box_bg = "#ffffff"  # clean white box

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .main {{
        background-color: {bg_color};
        border-radius: 16px;
        padding: 2rem;
    }}
    .answer-box {{
        background: {answer_box_bg};
        border-radius: 12px;
        padding: 1.2em;
        font-size: 1.1em;
        font-weight: 500;
        color: {text_color};
        border: 1px solid rgba(0,0,0,0.1);
        margin-bottom: 1em;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("🤖 AI Web Search & Answer")

topic = st.text_input("Enter your topic or question:", placeholder="e.g., latest AI news for today")

if st.button("🔍 Get AI Answer"):
    if topic:
        with st.spinner("Searching and scraping..."):
            try:
                # Step 1: Get links
                links = cached_get_links(topic, num_links)
                if not links:
                    st.warning("No links found. Try a different topic.")
                else:
                    st.success(f"Found {len(links)} links.")
                    st.markdown("#### 🔗 Scraped Links")
                    for link in links:
                        st.markdown(f"- [{link}]({link})")

                    # Step 2: Initialize logs
                    log_folder = initialize_logs(topic)

                    # Step 3: Scrape links one by one with progress
                    progress = st.progress(0)
                    errors = []
                    for i, link in enumerate(links):
                        try:
                            scrape_links([link], save_logs=save_logs, log_folder=log_folder)
                        except Exception as e:
                            errors.append(f"❌ Failed to scrape: {link} ({e})")
                        progress.progress((i + 1) / len(links))
                        time.sleep(0.2)  # small delay to smooth progress bar
                    progress.empty()

                    if errors:
                        st.warning("\n".join(errors))

                    # Step 4: Show logs
                    if save_logs:
                        st.markdown("### 📄 Scraped Content")
                        md_files = sorted(glob.glob(os.path.join(log_folder, "*.md")))
                        if md_files:
                            for md_file in md_files:
                                with open(md_file, "r", encoding="utf-8") as f:
                                    content = f.read()
                                filename = os.path.basename(md_file)
                                with st.expander(f"📰 {filename}"):
                                    st.markdown(content)
                        else:
                            st.info("No markdown files found.")

                    # Step 5: Combine logs
                    context_from_logs = cached_combine_logs(log_folder)

                    if show_scraped:
                        st.markdown("#### 📜 Combined Scraped Content")
                        st.code(context_from_logs[:2000] + ("..." if len(context_from_logs) > 2000 else ""), language="markdown")
                        st.download_button("⬇️ Download Logs", data=context_from_logs, file_name="scraped_logs.md")

                    # Step 6: Get AI Answer
                    final_prompt = context_combine_prompt(context_from_logs, topic)
                    answer = call_gemini(final_prompt)

                    # Step 7: Summarize & Display
                    summary = summarize_answer(answer)
                    st.markdown("### 🤖 AI Summarized Answer")
                    st.markdown(f'<div class="answer-box">{summary}</div>', unsafe_allow_html=True)

                    with st.expander("Show Full AI Answer"):
                        st.markdown(answer)

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic first!")

st.markdown('</div>', unsafe_allow_html=True)
