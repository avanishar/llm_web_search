import streamlit as st
import time
from scraper import scrape_links, initialize_logs
from cleaning import combine_logs

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="LLM Web Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for UI ---
st.markdown("""
<style>
/* Global background */
body {
    background-color: #f5f5f5;
}

/* AI Response box */
.ai-box {
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 1rem;
    margin-top: 1rem;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    font-size: 1rem;
    color: #111;
    line-height: 1.6;
}

/* Scraped content area */
.scraped-card {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.04);
}

/* Buttons */
button[kind="primary"] {
    background-color: #333 !important;
    color: white !important;
    border-radius: 8px !important;
}
button[kind="primary"]:hover {
    background-color: #444 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.header("🔧 Controls")
st.sidebar.write("Use this panel to configure your search.")

clear_cache = st.sidebar.button("🧹 Clear Cache")

# --- Main App UI ---
st.title("🔍 LLM Web Search")
st.write("Enter a topic, scrape links, and get an AI-powered summary.")

topic = st.text_input("Enter Topic", placeholder="e.g., NISAR Satellite")
num_links = st.slider("Number of links to scrape", 1, 5, 2)

# --- Session State ---
if "cache" not in st.session_state:
    st.session_state.cache = {}

if clear_cache:
    st.session_state.cache.clear()
    st.success("✅ Cache cleared successfully!")

if st.button("Scrape & Generate Answer"):
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        cache_key = f"{topic}_{num_links}"
        if cache_key in st.session_state.cache:
            st.info("⚡ Using cached results")
            combined_content = st.session_state.cache[cache_key]
        else:
            log_folder = initialize_logs(topic)
            with st.spinner("🔎 Scraping links... This may take a few seconds"):
                scrape_links([f"https://en.wikipedia.org/wiki/{topic}"], save_logs=True, log_folder=log_folder)
                combined_content = combine_logs(log_folder)
                st.session_state.cache[cache_key] = combined_content

        if combined_content:
            st.markdown("### 📄 Scraped Content")
            st.markdown(f"<div class='scraped-card'>{combined_content[:2000]}...</div>", unsafe_allow_html=True)

            st.markdown("### 🤖 AI Response")
            with st.spinner("Thinking..."):
                time.sleep(2)  # Simulate processing
                st.markdown("<div class='ai-box'>This is where your AI-generated answer will appear, summarized from the scraped content.</div>", unsafe_allow_html=True)
        else:
            st.error("❌ No content found or failed to scrape links.")
