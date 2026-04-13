import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("graph_rag.scraper")

def scrape_content(url):
    try:
        # Use a real user agent to avoid 403s
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        logger.info(f"Fetching content from: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        
        # Basic cleaning: collapse multiple newlines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        title = soup.title.string if soup.title else "Portfolio"
        extracted_text = f"SOURCE: {url}\nTITLE: {title}\n\n{text}"
        
        logger.debug(f"Successfully scraped content ({len(extracted_text)} chars).")
        return extracted_text
    except Exception as e:
        logger.error(f"Failed to fetch content from {url}: {e}")
        return None
