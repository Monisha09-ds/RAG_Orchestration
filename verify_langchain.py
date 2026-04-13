import logging
import sys

# Configure basic logging to see output
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

print("--- Starting LangChain Verification ---")
try:
    from graph_rag.controller import ingest_url
    
    # Use a dummy URL that we know works or has simple content
    # Since we don't have internet access for reliable scraping of random sites,
    # we might expect it to fail scraping or succeed if the URL is valid.
    # But wait, scrape_content uses 'requests', so it needs internet.
    # I will assume the user has internet since they asked for it. 
    # I'll use a very simple documentation page or Google.
    
    test_url = "https://www.example.com" 
    print(f"Testing ingestion with: {test_url}")
    
    result = ingest_url(test_url)
    print(f"Result: {result}")
    
except Exception as e:
    print(f"❌ Verification failed: {e}")
