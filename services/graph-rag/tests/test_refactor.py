try:
    from graph_rag import config
    from graph_rag import neo4j_connector
    from graph_rag import llm_client
    from graph_rag import scraper
    from graph_rag import controller
    
    print(f"✅ Imports successful.")
    print(f"Neo4j URI: {config.Config.NEO4J_URI}")
    
    # Check if we can instantiate driver (don't need to connect for import check)
    driver = neo4j_connector.get_driver()
    print("✅ Driver instantiated.")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
