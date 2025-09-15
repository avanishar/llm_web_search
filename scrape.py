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
    lines = [line for line in text.splitlines() if len(line.strip()) > 20]
    return "\n".join(lines)

def scrape_links(links, save_logs=True, log_folder=None):
    """
    Scrape data from the provided links with better error handling.
    
    Returns:
        dict with keys:
            - "success": list of file paths (if save_logs=True)
            - "errors": list of (link, error_message)
            - "combined": combined content if save_logs=False
    """
    combined_content = ""
    scraped_files = []
    errors = []

    for i, link in enumerate(links, 1):
        try:
            response = requests.get(link, timeout=10)
            if response.status_code != 200:
                errors.append((link, f"HTTP {response.status_code}"))
                continue

            print(f"✅ Successfully scraped {link}")
            soup = BeautifulSoup(response.content, 'html.parser')

            title = soup.find('title')
            title_text = title.get_text().strip() if title else f"Article_{i}"

            safe_title = re.sub(r'[^\w\s-]', '', title_text)
            safe_title = re.sub(r'[-\s]+', '_', safe_title)

            content_selectors = [
                'article', 'main', '.content', '.post-content',
                '.entry-content', '.article-content', 'body'
            ]
            content_text = ""
            for selector in content_selectors:
                selected = soup.select_one(selector)
                if selected:
                    content_text = selected.get_text(separator="\n", strip=True)
                    if content_text and len(content_text) > 200:
                        break

            if not content_text:
                errors.append((link, "No meaningful content found"))
                continue

            content_text = clean_content(content_text)

            markdown_content = (
                f"# {title_text}\n\n"
                f"**Source:** {link}\n\n"
                f"**Scraped on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"---\n\n"
                f"{content_text}"
            )

            if save_logs and log_folder:
                filename = f"{str(i).zfill(3)}_{safe_title}.md"
                filepath = os.path.join(log_folder, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                scraped_files.append(filepath)
            else:
                combined_content += markdown_content + "\n\n"

        except Exception as e:
            errors.append((link, str(e)))

    return {
        "success": scraped_files if save_logs else None,
        "errors": errors,
        "combined": None if save_logs else combined_content
    }
