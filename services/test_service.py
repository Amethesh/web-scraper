from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin

def serach_service(url):
    try:
        # Send a request to the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the webpage content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Selectors for elements to remove
        remove_selectors = [
            # Navigation and structural elements
            'nav', '.navigation', '#navigation', '.main-nav', '.header-nav',
            '[class*="nav"]', '[id*="nav"]', 'header', '.header',
            
            # Footer elements
            'footer', '.footer', '#footer', '.site-footer', 
            '[class*="footer"]', '[id*="footer"]',
            
            # Form-related elements
            'form', 'input', 'textarea', 'select', 'button',
            '.form', '#form', '[class*="form"]', '[id*="form"]',
            '[type="text"]', '[type="email"]', '[type="password"]',
            '[type="submit"]', '[type="button"]',
            
            # Potentially irrelevant interactive elements
            '.modal', '#modal', '[class*="modal"]',
            '.popup', '#popup', '[class*="popup"]',
            '.sidebar', '#sidebar', '[class*="sidebar"]',
            
            # Comments and metadata
            'meta', 'comment', '.comment', '#comment',
            '[class*="comment"]', '[id*="comment"]'
        ]
        
        # Remove selected elements
        for selector in remove_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Remove scripts, styles, and other non-content elements
        for element in soup(['script', 'style', 'iframe', 'svg', 'canvas']):
            element.decompose()
        
        # Prepare links and their anchor texts
        link_map = {}
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            
            # Filter and store links
            if full_url.startswith(('http://', 'https://')):
                anchor_text = link.get_text(strip=True)
                if anchor_text:
                    link_map[link] = (full_url, anchor_text)
        
        # Replace links with Markdown-style links
        for link, (full_url, anchor_text) in link_map.items():
            # Create a NavigableString with the Markdown link
            md_link_str = NavigableString(f'[{anchor_text}]({full_url})')
            link.replace_with(md_link_str)
        
        # Remove empty elements
        for element in soup.find_all():
            if not element.get_text(strip=True):
                element.decompose()
        
        # Extract text content
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Clean up text content
        text_lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        cleaned_text_content = '\n'.join(text_lines)
        
        # Extract unique links
        links = set(url for url, _ in link_map.values())
        
        return cleaned_text_content, links

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None, None

def save_to_markdown(text_content, links, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        # Write page text content
        file.write("# Scraped Page Information\n\n")
        file.write("## Page Text Content\n")
        file.write(text_content)
        file.write("\n\n")
        
        # Write extracted links
        file.write("## Extracted Links\n")
        for link in sorted(links):
            file.write(f"- {link}\n")

# Example usage
page_url = "https://bhilosa.com/about-us/"
text, links = scrape_page_info(page_url)

if text:
    output_file = "scraped_page_bhi.md"
    save_to_markdown(text, links, output_file)
    print(f"Scraped data saved to {output_file}")
else:
    print("Failed to scrape the page.")