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
def cached_scrape_links(links, save_logs, log_folder):
    scrape_links(links, save_logs=save_logs, log_folder=log_folder)
    return log_folder

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
else:
    bg_color = "#f5f7fa"
    text_color = "#222"

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
        background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 12px;
        padding: 1.5em;
        font-size: 1.2em;
        font-weight: 500;
        color: #222;
        margin-bottom: 1em;
    }}
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
        2. The app searches the web, scrapes multiple links, and summarizes an answer using AI.
        3. Toggle light/dark mode, clear cache, and leave feedback after reading.
        """
    )

topic = st.text_input("Enter your topic or question:", placeholder="e.g., latest AI news for today")

if st.button("🔍 Get AI Answer"):
    if topic:
        with st.spinner("Searching and processing..."):
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

                    # Step 3: Scrape all links at once
                    scrape_links(links, save_logs=save_logs, log_folder=log_folder)

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

                    # Step 8: Ask for Rating
                    st.markdown("### ⭐ How helpful was this answer?")
                    rating = st.radio("Select a rating:", [1, 2, 3, 4, 5], horizontal=True)
                    if rating:
                        if rating <= 2:
                            st.warning("😔 Sorry we missed the mark. You can leave feedback below!")
                        elif rating == 3:
                            st.info("🙂 Thanks! We’ll try to improve.")
                        else:
                            st.success("🎉 Great! Glad you found this helpful.")

                        feedback = st.text_area("Optional feedback (what to improve?):")
                        if st.button("Submit Feedback"):
                            with open("feedback.txt", "a", encoding="utf-8") as f:
                                f.write(f"Topic: {topic}\nRating: {rating}\nFeedback: {feedback}\n{'='*40}\n")
                            st.success("✅ Feedback submitted! Thank you.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic first!")

st.markdown('</div>', unsafe_allow_html=True)
