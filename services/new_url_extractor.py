import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import cloudscraper
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from webdriver_manager.chrome import ChromeDriverManager
import traceback

class URLExtractor:
    def __init__(self, user_agent=None):
        """
        Initialize URL extractor with optional custom user agent
        
        Args:
            user_agent (str, optional): Custom user agent to use in requests
        """
        self.headers = {
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def extract_urls(self, base_url, max_depth=2):
        """
        Comprehensive URL extraction method with multiple fallback strategies
        
        Args:
            base_url (str): Base URL to extract links from
            max_depth (int, optional): Maximum depth of link extraction. Defaults to 2.
        
        Returns:
            set: Unique URLs extracted from the webpage
        """
        # Ensure base_url has a scheme
        if not urlparse(base_url).scheme:
            base_url = f'https://{base_url}'
        
        # List of extraction methods to try
        extraction_methods = [
            self._extract_with_requests,
            self._extract_with_cloudscraper,
            self._extract_with_selenium,
            self._extract_with_regex
        ]
        
        # Try each method until we find URLs
        urls = set()
        for method in extraction_methods:
            try:
                print(f"Trying method: {method.__name__}")
                urls = method(base_url)
                if urls:
                    print(f"Method {method.__name__} succeeded")
                    break
            except Exception as e:
                print(f"Method {method.__name__} failed: {e}")
                continue
        
        # Filter and clean URLs
        filtered_urls = self._filter_urls(base_url, urls, max_depth)
        return filtered_urls

    def _extract_with_requests(self, base_url):
        """
        Extract URLs using requests library with various headers and SSL verification
        
        Args:
            base_url (str): Base URL to extract links from
        
        Returns:
            set: Extracted URLs
        """
        # Multiple header variations
        header_variations = [
            self.headers,
            {**self.headers, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'},
            {**self.headers, 'Referer': base_url}
        ]
        
        for headers in header_variations:
            try:
                response = requests.get(
                    base_url, 
                    headers=headers, 
                    verify=False,  # Disable SSL verification
                    timeout=10
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                urls = {urljoin(base_url, link['href']) for link in links}
                if urls:
                    return urls
            except Exception as e:
                print(f"Requests method failed: {e}")
        
        return set()

    def _extract_with_cloudscraper(self, base_url):
        """
        Extract URLs using cloudscraper to bypass Cloudflare protection
        
        Args:
            base_url (str): Base URL to extract links from
        
        Returns:
            set: Extracted URLs
        """
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(base_url, timeout=10)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            return {urljoin(base_url, link['href']) for link in links}
        except Exception as e:
            print(f"Cloudscraper method failed: {e}")
            return set()

    def _extract_with_selenium(self, base_url):
        """
        Extract URLs using Selenium WebDriver
        
        Args:
            base_url (str): Base URL to extract links from
        
        Returns:
            set: Extracted URLs
        """
        try:
            # Set up Selenium WebDriver
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Use a context manager for the WebDriver
            with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as driver:
                driver.get(base_url)
                
                # Extract URLs
                links = driver.find_elements(By.TAG_NAME, 'a')
                urls = {urljoin(base_url, link.get_attribute('href')) 
                        for link in links 
                        if link.get_attribute('href') and link.get_attribute('href').startswith(('http', 'https'))}
                return urls
        except Exception as e:
            print(f"Selenium method failed: {e}")
            traceback.print_exc()
            return set()

    def _extract_with_regex(self, base_url):
        """
        Extract URLs using regex pattern matching
        
        Args:
            base_url (str): Base URL to extract links from
        
        Returns:
            set: Extracted URLs
        """
        try:
            response = requests.get(base_url, headers=self.headers, verify=False)
            url_pattern = r'https?://[^\s<>"]+|/[^\s<>"]+\.[^\s<>"]+'
            urls = set(re.findall(url_pattern, response.text))
            return {urljoin(base_url, url) for url in urls if url.startswith(('http', '/'))}
        except Exception as e:
            print(f"Regex method failed: {e}")
            return set()

    def _filter_urls(self, base_url, urls, max_depth):
        """
        Filter and clean extracted URLs
        
        Args:
            base_url (str): Base URL to filter against
            urls (set): Set of extracted URLs
            max_depth (int): Maximum depth of links to include
        
        Returns:
            set: Filtered and cleaned URLs
        """
        excluded_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
                                '.mp4', '.mp3', '.avi', '.mov', '.wmv', '.flv', 
                                '.webm', '.webp', '.pdf', '.doc', '.docx', '.zip')
        
        filtered_urls = set()
        for url in urls:
            try:
                parsed_url = urlparse(url)
                # Check base domain
                if parsed_url.netloc.replace('www.', '') == urlparse(base_url).netloc.replace('www.', ''):
                    # Check depth
                    path_segments = [seg for seg in parsed_url.path.split('/') if seg]
                    if len(path_segments) <= max_depth:
                        # Check file extensions
                        if not url.lower().endswith(excluded_extensions):
                            filtered_urls.add(url)
            except Exception as e:
                print(f"URL filtering error: {e}")
        
        return filtered_urls

# Example usage
url_extractor = URLExtractor()
if __name__ == "__main__":
    # base_url = 'https://bhilosa.com/'
    # base_url = 'https://www.iglonline.net/'
    base_url = 'https://www.gujaratgas.com/'
    extracted_urls = url_extractor.extract_urls(base_url)
    print(f"Extracted {len(extracted_urls)} URLs:")
    for url in extracted_urls:
        print(url)