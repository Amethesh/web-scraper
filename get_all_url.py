import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_urls(base_url):
    try:
        # Send a request to the website
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the website content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all anchor tags with href attributes
        links = soup.find_all('a', href=True)
        
        # Define file extensions to ignore
        excluded_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
                               '.mp4', '.mp3', '.avi', '.mov', '.wmv', '.flv', '.webm', '.webp')
        
        # Extract and normalize URLs
        urls = set()  # Use a set to avoid duplicates
        for link in links:
            full_url = urljoin(base_url, link['href'])  # Join relative URLs with the base URL
            if full_url.startswith(base_url) and not full_url.lower().endswith(excluded_extensions):
                urls.add(full_url)
        
        return urls

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return set()

# Example usage
base_url = "https://www.finolexpipes.com/"
urls = extract_urls(base_url)
for url in urls:
    print(url)
