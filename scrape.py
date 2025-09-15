from datetime import datetime
from bs4 import BeautifulSoup
import os
import re
import requests

def initialize_logs(topic):
    """
    Create a folder named as the topic with timestamp
    Returns the path to the created folder
    """
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_folder = os.path.join(logs_dir, f"{topic}_{timestamp}")
    os.makedirs(topic_folder, exist_ok=True)
    
    return topic_folder

def clean_content(text):
    """
    Remove common boilerplate/footer/navigation patterns from scraped text.
    """
    boilerplate_patterns = [
        r"About\s*Press\s*Copyright.*?Google LLC",
        r"Terms\s*Privacy\s*Policy.*?features",
        r"All rights reserved\.",
        r"Contact us.*?Developers",
        r"How YouTube works.*?Google LLC",
        r"^(\s*|\n*)$",
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    # Optionally remove very short lines
    lines = [line for line in text.splitlines() if len(line.strip()) > 20]
    return "\n".join(lines)

def scrape_links(links, save_logs=True, log_folder=None):
    """
    Scrape data from the provided links with better error handling and headers.
    
    Returns:
        dict with keys:
            - "success": list of file paths (if save_logs=True)
            - "errors": list of (link, error_message)
            - "combined": combined content if save_logs=False
    """
    combined_content = ""
    scraped_files = []
    errors = []

    # ✅ Use browser-like headers to avoid 403 Forbidden
    headers = {
        "User-
