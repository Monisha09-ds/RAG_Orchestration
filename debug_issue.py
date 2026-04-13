from graph_rag.controller import ingest_url
import logging
import sys

# Configure logging to see output
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

url = "https://monisha09-ds.github.io/SabikunMonisha.github.io/"
print(f"--- Reproducing Issue for {url} ---")

try:
    result = ingest_url(url)
    print("\nResult:", result)
except Exception as e:
    print(f"\nCRITICAL FAILURE: {e}")
    import traceback
    traceback.print_exc()
