from datetime import datetime
from bs4 import BeautifulSoup
import os
import re
import requests

def initialize_logs(topic):
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_folder = os.path.join(logs_dir, f"{topic}_{timestamp}")
    os.makedirs(topic_folder, exist_ok=True)
    return topic_folder

def clean_content(text):
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
    lines = [line for line in text.splitlines() if len(line.strip()) > 20]
    return "\n".join(lines)

def scrape_links(links, save_logs=True, log_folder=None):
    """
    Scrape given links, save to logs if enabled, and return a dictionary of results.
    Returns always a dictionary: {"success": [...], "errors": [...]}
    """
    results = {"success": [], "errors": []}

    if not links:
        results["errors"].append(("NO_LINKS", "No links to scrape."))
        return results

    for i, link in enumerate(links[:10], 1):
        try:
            response = requests.get(link, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                results["errors"].append((link, f"HTTP {response.status_code}"))
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            title_text = title.get_text().strip() if title else f"Article_{i}"

            safe_title = re.sub(r'[^\w\s-]', '', title_text)
            safe_title = re.sub(r'[-\s]+', '_', safe_title)

            # Try multiple selectors to get main content
            content_selectors = ['article', 'main', '.content', '.post-content', '.entry-content', '.article-content', 'body']
            content_text = ""
            for selector in content_selectors:
                selected = soup.select_one(selector)
                if selected:
                    content_text = selected.get_text(separator="\n", strip=True)
                    if len(content_text) > 500:  # ensure enough content
                        break

            if not content_text:
                content_text = soup.get_text(separator="\n", strip=True)

            content_text = clean_content(content_text)
            markdown_content = f"# {title_text}\n\n**Source:** {link}\n\n---\n\n{content_text}"

            if save_logs and log_folder:
                try:
                    filename = f"{str(i).zfill(3)}_{safe_title}.md"
                    filepath = os.path.join(log_folder, filename)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                except Exception as e:
                    results["errors"].append((link, f"Failed to save log: {str(e)}"))

            results["success"].append(link)

        except Exception as e:
            results["errors"].append((link, str(e)))

    return results
