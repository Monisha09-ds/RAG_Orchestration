try:
    from langchain_neo4j import Neo4jGraph
    print("✅ Successfully imported Neo4jGraph from langchain_neo4j")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
