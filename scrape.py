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
    combined_content = ""
    for i, link in enumerate(links, 1):
        try:
            response = requests.get(link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                print(f"✅ Successfully scraped {link}")
                soup = BeautifulSoup(response.content, 'html.parser')

                title = soup.find('title')
                title_text = title.get_text().strip() if title else f"Article_{i}"

                safe_title = re.sub(r'[^\w\s-]', '', title_text)
                safe_title = re.sub(r'[-\s]+', '_', safe_title)

                content_selectors = ['article', 'main', '.content', '.post-content', '.entry-content', '.article-content', 'body']
                content_text = ""
                for selector in content_selectors:
                    selected = soup.select_one(selector)
                    if selected:
                        content_text = selected.get_text(separator="\n", strip=True)
                        if content_text:
                            break

                if not content_text:
                    content_text = soup.get_text(separator="\n", strip=True)

                content_text = clean_content(content_text)

                markdown_content = f"# {title_text}\n\n**Source:** {link}\n\n**Scraped on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n{content_text}"

                if save_logs and log_folder:
                    filename = f"{str(i).zfill(3)}_{safe_title}.md"
                    filepath = os.path.join(log_folder, filename)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    print(f"💾 Saved content to {filepath}")
                else:
                    combined_content += markdown_content + "\n\n"
            else:
                print(f"⚠️ Could not scrape {link}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to scrape {link}: {str(e)}")

    if save_logs and log_folder:
        print(f"📂 All scraped content saved in: {log_folder}")
        return None
    else:
        return combined_content
