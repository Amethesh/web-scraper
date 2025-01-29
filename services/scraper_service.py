import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin
import PyPDF2
import io
import concurrent.futures
from typing import List, Tuple, Dict
import re

class ScraperService:
    """
    An enhanced service class for handling web scraping and PDF extraction.
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def is_pdf_link(self, url: str) -> bool:
        """Check if the URL points to a PDF file."""
        return url.lower().endswith('.pdf') or 'application/pdf' in requests.head(url, headers=self.headers).headers.get('Content-Type', '')

    def extract_pdf_content(self, url: str) -> Tuple[str, set]:
        """
        Extract text content from a PDF file.
        Returns tuple of (text_content, set of links found in PDF)
        """
        try:
            # Download PDF content
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Read PDF content
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = []
            links = set()
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text.strip())
                
                # Try to extract links from PDF
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annotation in annotations:
                        if isinstance(annotation, dict) and '/A' in annotation and '/URI' in annotation['/A']:
                            links.add(annotation['/A']['/URI'])
            
            return '\n'.join(text_content), links
            
        except Exception as e:
            print(f"Error extracting PDF content from {url}: {str(e)}")
            return f"Error processing PDF: {str(e)}", set()

    def scrape_page_info(self, url: str) -> Tuple[str, set]:
        """
        Scrape content from a webpage or PDF.
        Returns tuple of (content, links)
        """
        try:
            if self.is_pdf_link(url):
                return self.extract_pdf_content(url)
            
            # Original web scraping logic
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Selectors for elements to remove (unchanged from original)
            remove_selectors = [
                'nav', '.navigation', '#navigation', '.main-nav', '.header-nav',
                '[class*="nav"]', '[id*="nav"]', 'header', '.header',
                'footer', '.footer', '#footer', '.site-footer', 
                '[class*="footer"]', '[id*="footer"]',
                'form', 'input', 'textarea', 'select', 'button',
                '.form', '#form', '[class*="form"]', '[id*="form"]',
                '[type="text"]', '[type="email"]', '[type="password"]',
                '[type="submit"]', '[type="button"]',
                '.modal', '#modal', '[class*="modal"]',
                '.popup', '#popup', '[class*="popup"]',
                '.sidebar', '#sidebar', '[class*="sidebar"]',
                'meta', 'comment', '.comment', '#comment',
                '[class*="comment"]', '[id*="comment"]'
            ]
            
            for selector in remove_selectors:
                for element in soup.select(selector):
                    element.decompose()
            
            for element in soup(['script', 'style', 'iframe', 'svg', 'canvas']):
                element.decompose()
            
            link_map = {}
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if full_url.startswith(('http://', 'https://')):
                    anchor_text = link.get_text(strip=True)
                    if anchor_text:
                        link_map[link] = (full_url, anchor_text)
            
            for link, (full_url, anchor_text) in link_map.items():
                md_link_str = NavigableString(f'[{anchor_text}]({full_url})')
                link.replace_with(md_link_str)
            
            for element in soup.find_all():
                if not element.get_text(strip=True):
                    element.decompose()
            
            text_content = soup.get_text(separator='\n', strip=True)
            text_lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            cleaned_text_content = '\n'.join(text_lines)
            
            links = set(url for url, _ in link_map.values())
            
            return cleaned_text_content, links

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return f"Error processing URL: {str(e)}", set()

    def process_multiple_links(self, urls: List[str]) -> List[Dict]:
        """
        Process multiple URLs concurrently and return their content and links.
        """
        results = []
        
        # Use ThreadPoolExecutor for concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.scrape_page_info, url): url for url in urls}
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    content, links = future.result()
                    results.append({
                        'url': url,
                        'content': content,
                        'links': list(links),
                        'type': 'pdf' if self.is_pdf_link(url) else 'webpage'
                    })
                except Exception as e:
                    results.append({
                        'url': url,
                        'content': f"Error processing {url}: {str(e)}",
                        'links': [],
                        'type': 'error'
                    })
        
        return results

    def write_to_markdown(self, results: List[Dict]) -> str:
        """
        Generate markdown content for multiple scraped pages.
        """
        markdown_content = "# Scraped Content Summary\n\n"
        
        for result in results:
            markdown_content += f"## Source: {result['url']}\n"
            markdown_content += f"Type: {result['type']}\n\n"
            markdown_content += "### Content\n"
            markdown_content += result['content']
            markdown_content += "\n\n"
            
            if result['links']:
                markdown_content += "### Found Links\n"
                for link in sorted(result['links']):
                    markdown_content += f"- {link}\n"
            markdown_content += "\n---\n\n"
        
        return markdown_content


# Example usage:
scraper_service = ScraperService()


