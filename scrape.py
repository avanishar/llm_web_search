from datetime import datetime
from bs4 import BeautifulSoup
import os
import re
import requests
import random
import time

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
    Scrapes multiple links and returns structured results.
    """
    results = {"success": [], "errors": []}
    combined_content = ""

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
    ]

    for i, link in enumerate(links, 1):
        try:
            headers = {"User-Agent": random.choice(user_agents)}
            response = requests.get(link, timeout=10, headers=headers)

            # Retry once if blocked
            if response.status_code == 403:
                print("\033[93m⚠ 403 Forbidden, retrying...\033[0m")
                time.sleep(1)
                headers = {"User-Agent": random.choice(user_agents)}
                response = requests.get(link, timeout=10, headers=headers)

            if response.status_code == 200:
                print("\033[92m✅ Successfully scraped:\033[0m", link)
                results["success"].append(link)

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
                        if content_text:
                            break

                if not content_text:
                    content_text = soup.get_text(separator="\n", strip=True)

                content_text = clean_content(content_text)

                markdown_content = (
                    f"# {title_text}\n\n"
                    f"**Source:** {link}\n\n"
                    f"**Scraped on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    "---\n\n"
                    f"{content_text}"
                )

                if save_logs and log_folder:
                    filename = f"{str(i).zfill(3)}_{safe_title}.md"
                    filepath = os.path.join(log_folder, filename)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    print("\033[92m💾 Saved to:\033[0m", filepath)
                else:
                    combined_content += markdown_content + "\n\n"

            else:
                msg = f"HTTP {response.status_code}"
                print("\033[91m❌ Failed:\033[0m", link, "-", msg)
                results["errors"].append((link, msg))

        except Exception as e:
            msg = str(e)
            print("\033[91m❌ Exception:\033[0m", link, "-", msg)
            results["errors"].append((link, msg))

    if not save_logs:
        results["combined_content"] = combined_content

    return results
