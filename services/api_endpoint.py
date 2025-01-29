import requests
from bs4 import BeautifulSoup
import re

def find_api_endpoints(url):
    """
    Scrape a website to find potential API endpoints.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all script tags
        scripts = soup.find_all("script", src=True)
        api_endpoints = set()

        for script in scripts:
            script_url = script["src"]
            if "api" in script_url or script_url.endswith(".js"):
                script_content = requests.get(script_url).text
                # Look for common API patterns in the JavaScript file
                api_endpoints.update(re.findall(r"https?://[^\s'\"<>]+", script_content))

        return list(api_endpoints)

    except Exception as e:
        print(f"Error: {e}")
        return []

# Example usage
if __name__ == "__main__":
    endpoints = find_api_endpoints("https://www.rites.com/")
    print("Potential API Endpoints:")
    print(endpoints)
