import streamlit as st
from get_links import get_links
from scrape import scrape_links, initialize_logs
from cleaning import combine_logs
from llm import call_gemini, context_combine_prompt
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
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("🤖 AI Web Search & Answer")

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    num_links = st.slider("Number of links to scrape", 1, 10, 3)
    show_scraped = st.checkbox("Show combined scraped content", value=False)
    save_logs = st.checkbox("Save logs to markdown files", value=True)

topic = st.text_input("Enter your topic or question:", placeholder="e.g., latest AI news for today")

if st.button("🔍 Get AI Answer"):
    if topic:
        st.write("🟢 **Starting process...**")
        with st.spinner("Searching and scraping..."):
            try:
                st.write("🟢 **Getting links...**")
                links = get_links(topic, num_links)
                st.success(f"Found {len(links)} links.")

                log_folder = initialize_logs(topic)
                st.write(f"🟢 **Log folder created:** {log_folder}")

                st.write("🟢 **Scraping links...**")
                result = scrape_links(links, save_logs=save_logs, log_folder=log_folder)

                # ✅ Wrap in check to avoid crashing
                success_count = len(result.get('success', []))
                st.success(f"✅ Scraped {success_count} websites successfully.")
                errors = result.get("errors", [])
                if errors:
                    for link, msg in errors:
                        st.error(f"⚠️ Could not scrape {link}: {msg}")

                if success_count == 0:
                    st.error("No content scraped.")
                else:
                    st.write("🟢 **Combining logs...**")
                    context_from_logs = combine_logs(log_folder)

                    if len(context_from_logs) > 10000:
                        st.warning("⚠️ Context too large, truncating to 10,000 characters.")
                        context_from_logs = context_from_logs[:10000]

                    if show_scraped:
                        st.markdown("#### Scraped Content (Combined)")
                        st.code(
                            context_from_logs[:2000] + ("..." if len(context_from_logs) > 2000 else ""), 
                            language="markdown"
                        )

                    st.write("🟢 **Sending prompt to LLM...**")
                    final_prompt = context_combine_prompt(context_from_logs, topic)
                    answer = call_gemini(final_prompt)

                    st.markdown("### 🤖 AI Answer")
                    st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic or question first!")

st.markdown('</div>', unsafe_allow_html=True)
