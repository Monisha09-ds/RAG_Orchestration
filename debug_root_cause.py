import logging
import sys
import json
from graph_rag.neo4j_connector import get_driver, query_graph_facts
from graph_rag.llm_client import classify_intent
from graph_rag.scraper import scrape_content

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

print("--- ROOT CAUSE ANALYSIS ---")

# 1. Inspect the Graph Content (What do we ACTUALLY have?)
print("\n[Step 1] Dumping Graph Nodes...")
driver = get_driver()
with driver.session() as session:
    # Get all nodes with labels and name property
    result = session.run("MATCH (n) RETURN labels(n) as labels, coalesce(n.name, n.id, 'No Name') as name")
    nodes = [{"labels": r["labels"], "name": r["name"]} for r in result]
    print(f"Total Nodes: {len(nodes)}")
    
    # Check for specific keywords
    keywords = ["MCP", "Sabikun", "Portfolio", "Website"]
    for kw in keywords:
        matches = [n for n in nodes if kw.lower() in str(n["name"]).lower()]
        if matches:
            print(f"✅ Found key '{kw}': {matches}")
        else:
            print(f"❌ Key '{kw}' NOT found in Graph.")

# 2. Test Intent Classification for the failing questions
print("\n[Step 2] Testing Intent Classification...")
questions = [
    "did she work with MCP ?",
    "the name of the portfolio website ?"
]

for q in questions:
    intent = classify_intent(q)
    print(f"Question: '{q}' -> Intent: {intent}")
    
    # Simulate what facts would be retrieved
    facts = query_graph_facts(intent)
    print(f"Facts Retrieved: {len(facts)} records")
    # print(json.dumps(facts[:2], indent=2)) # Peak next 2

# 3. Check Scraper Content again for the website name
url = "https://monisha09-ds.github.io/SabikunMonisha.github.io/"
print(f"\n[Step 3] Checking Scraped Text for '{url}'...")
text = scrape_content(url)
if text:
    print(f"Scraped {len(text)} chars.")
    # Check if 'MCP' or 'Portfolio' title appears in text
    if "MCP" in text:
        print("✅ 'MCP' is in the text.")
    else:
        print("❌ 'MCP' is NOT in the text.")
        
    lines = text.split('\n')
    print("First 5 lines of text (Header/Title info):")
    for l in lines[:5]:
        print(f" - {l.strip()}")
