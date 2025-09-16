import requests
from bs4 import BeautifulSoup

def get_links(query, num_results=5):
    """
    Get top links for a query using DuckDuckGo (no API key required).
    """
    print("\033[96m🔍 Searching for:\033[0m", query)
    url = f"https://duckduckgo.com/html/?q={query}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    for a in soup.select(".result__a")[:num_results]:
        links.append(a["href"])
    return links
