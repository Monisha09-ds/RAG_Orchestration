import logging
import sys

# Ensure logging is set up before imports if they log on module level (which they do)
# But our package init does it, so importing the package should work.

print("--- Starting Verification Script ---")
try:
    import graph_rag
    from graph_rag.controller import ingest_url
    from graph_rag.neo4j_connector import get_driver
    
    print("✅ Imports successful.")
    
    # We expect some logs from the imports if they do any work on init (neo4j does)
    # The neo4j driver init in neo4j_connector.py logs an INFO message.
    
    print("--- Calling ingest_url with a dummy URL (expecting logs) ---")
    ingest_url("http://example.com/nonexistent") 
    
except Exception as e:
    print(f"❌ Verification failed: {e}")
