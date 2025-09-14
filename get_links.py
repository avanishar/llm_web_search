import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_links(topic, num_links=5):
    topic = topic.replace(" ", "+")
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        raise ValueError("SERPER_API_KEY not found in environment variables.")

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    payload = {"q": topic}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Serper API error: {response.status_code} {response.text}")

    json_data = response.json()
    links = []

    for item in json_data.get("organic", []):
        if "link" in item:
            links.append(item["link"])
        if "sitelinks" in item:
            for sub in item["sitelinks"]:
                if "link" in sub:
                    links.append(sub["link"])
        if len(links) >= num_links:
            break

    return links[:num_links]