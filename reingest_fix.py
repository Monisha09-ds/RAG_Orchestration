from graph_rag.controller import ingest_url
from graph_rag.neo4j_connector import get_driver, query_graph_facts
import logging
import sys
import json

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

url = "https://monisha09-ds.github.io/SabikunMonisha.github.io/"
print(f"--- Re-Ingesting {url} for Website Info ---")
ingest_url(url)

print("\n--- Checking for Website Nodes ---")
driver = get_driver()
with driver.session() as session:
    result = session.run("MATCH (w:Website) RETURN w.name, w.url, w.id")
    websites = [dict(r) for r in result]
    print(f"Websites found: {json.dumps(websites, indent=2)}")

print("\n--- Testing Retrieval for 'ALL' Intent ---")
facts = query_graph_facts("ALL")
print(json.dumps(facts[:2], indent=2))
