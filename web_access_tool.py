import requests

class WebAccessTool:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def search(self, query: str):
        """Search for a query using the web access service."""
        response = requests.get(f"{self.base_url}/search", params={"query": query})
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def open_url(self, url: str):
        """Fetch and sanitize content from a given URL."""
        response = requests.get(f"{self.base_url}/open_url", params={"url": url})
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()