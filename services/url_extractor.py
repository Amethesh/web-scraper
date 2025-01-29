import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json

def extract_all_urls(base_url, max_depth=2, delay=1):
    """
    Extracts all unique URLs from a given website recursively.

    :param base_url: The starting URL to scrape.
    :param max_depth: Maximum depth to traverse links.
    :param delay: Delay (in seconds) between requests to avoid server overload.
    :return: A set of all unique URLs within the same domain.
    """
    visited = set()
    all_urls = set()
    excluded_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.svg', '.zip', '.rar', '.mp3', '.PDF', '.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt', '.mp4', '.avi', '.wmv', '.flv', '.webm', '.webp'}

    def crawl(url, depth):
        # Base case: stop if max depth is reached
        if depth > max_depth or url in visited:
            return
        try:
            # Mark the URL as visited
            visited.add(url)
            # Fetch and parse the page
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract all links on the page
            links = soup.find_all('a', href=True)
            for link in links:
                full_url = urljoin(url, link['href'])
                # Ensure the URL is within the same domain and not excluded
                if full_url.startswith(base_url) and full_url not in visited:
                    parsed_url = urlparse(full_url)
                    if not any(parsed_url.path.endswith(ext) for ext in excluded_extensions):
                        all_urls.add(full_url)
                        crawl(full_url, depth + 1)  # Recursive crawl

            # Optional: Delay to avoid server overload
            time.sleep(delay)

        except requests.exceptions.RequestException as e:
            print(f"Error accessing {url}: {e}")

    # Start crawling from the base URL
    crawl(base_url, 0)
    return all_urls


def organize_urls(urls, base_url):
    """
    Organizes a set of URLs into a structured dictionary based on their base paths.

    :param urls: A set of full URLs to process.
    :param base_url: The base URL to organize the structure.
    :return: A dictionary organizing URLs into a hierarchical structure.
    """
    organized = {"base_url": base_url, "/": []}
    parsed_base = urlparse(base_url)
    base_netloc = parsed_base.netloc

    for url in urls:
        parsed_url = urlparse(url)
        # Skip external URLs
        if parsed_url.netloc != base_netloc:
            continue

        # Convert to relative path
        relative_path = url.replace(f"{parsed_url.scheme}://{parsed_url.netloc}", "").lstrip("/")
        parts = relative_path.split("/")

        # Organize under base path
        if len(parts) == 1:
            # Root-level paths
            organized["/"].append(parts[0] or "home")  # Add "home" for root
        else:
            # Nested paths
            base_path = "/" + parts[0]
            if base_path not in organized:
                organized[base_path] = []
            organized[base_path].append("/".join(parts[1:]))

    # Deduplicate and sort each group
    for key in organized:
        if isinstance(organized[key], list):
            organized[key] = sorted(set(organized[key]))

    return organized

# Example usage
if __name__ == "__main__":
    website_url = "https://www.iglonline.net/"
    urls = extract_all_urls(website_url, max_depth=3)
    print(f"Found {len(urls)} URLs:")
    organized_urls = organize_urls(urls, website_url)
    print(organized_urls)

    # Save the result to a JSON file
    with open("organized_urls_igl.json", "w") as json_file:
        json.dump(organized_urls, json_file, indent=4)
    
