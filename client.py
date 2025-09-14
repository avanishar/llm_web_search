import streamlit as st
from get_links import get_links
from scrape import scrape_links, initialize_logs
from cleaning import combine_logs
from llm import call_gemini, context_combine_prompt
import glob
import os

# --- Summarization helper ---
def summarize_answer(answer):
    # You can replace this with a call to your LLM for better summarization
    prompt = f"Summarize the following answer in 3-4 concise sentences:\n\n{answer}"
    summary = call_gemini(prompt)
    return summary

# --- Streamlit UI setup ---
st.set_page_config(page_title="AI Web Search & Answer", page_icon="🤖", layout="centered")

st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
    }
    .main {
        background-color: #f5f7fa;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
    }
    .stTextInput>div>div>input {
        font-size: 18px;
        border-radius: 8px;
    }
    .stButton>button {
        font-size: 18px;
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5em 2em;
    }
    .stMarkdown {
        font-size: 16px;
    }
    .scraped-card {
        background: #f0f4fa;
        border-radius: 10px;
        padding: 1em;
        margin-bottom: 1em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .answer-box {
        background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 12px;
        padding: 1.5em;
        font-size: 1.2em;
        font-weight: 500;
        color: #222;
        margin-bottom: 1em;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
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

# Sidebar for options
with st.sidebar:
    st.header("Settings")
    num_links = st.slider("Number of links to scrape", 1, 10, 3)
    show_scraped = st.checkbox("Show combined scraped content", value=False)
    save_logs = st.checkbox("Save logs to markdown files", value=True)

# Input for topic
topic = st.text_input("Enter your topic or question:", placeholder="e.g., latest AI news for today")

if st.button("🔍 Get AI Answer"):
    if topic:
        with st.spinner("Searching and processing..."):
            try:
                # Get links
                links = get_links(topic, num_links)
                if not links:
                    st.warning("No links found for your topic. Try a different query.")
                else:
                    st.success(f"Found {len(links)} links.")
                    st.markdown("#### Scraped Links")
                    for link in links:
                        st.markdown(f"- [{link}]({link})")

                    # Initialize logs
                    log_folder = initialize_logs(topic)

                    # Scrape content
                    scrape_links(links, save_logs=save_logs, log_folder=log_folder)

                    # Display each scraped markdown file in an expander
                    if save_logs:
                        st.markdown("### 📄 Scraped Content from Each Link")
                        md_files = sorted(glob.glob(os.path.join(log_folder, "*.md")))
                        if md_files:
                            for md_file in md_files:
                                with open(md_file, "r", encoding="utf-8") as f:
                                    content = f.read()
                                filename = os.path.basename(md_file)
                                with st.expander(f"📰 {filename}"):
                                    st.markdown(
                                        f'<div class="scraped-card">{content}</div>',
                                        unsafe_allow_html=True
                                    )
                        else:
                            st.info("No markdown files found in the log folder.")

                    # Combine logs
                    context_from_logs = combine_logs(log_folder)

                    if show_scraped:
                        st.markdown("#### Scraped Content (Combined)")
                        st.code(context_from_logs[:2000] + ("..." if len(context_from_logs) > 2000 else ""), language="markdown")

                    # Create prompt
                    final_prompt = context_combine_prompt(context_from_logs, topic)

                    # Get answer
                    answer = call_gemini(final_prompt)

                    # Summarize answer
                    summary = summarize_answer(answer)

                    # Display summarized answer in a nice box
                    st.markdown("### 🤖 AI Summarized Answer")
                    st.markdown(f'<div class="answer-box">{summary}</div>', unsafe_allow_html=True)

                    # Optionally, show full answer in an expander
                    with st.expander("Show Full AI Answer"):
                        st.markdown(answer)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic or question first!")

st.markdown('</div>', unsafe_allow_html=True)