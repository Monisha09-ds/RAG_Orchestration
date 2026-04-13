
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

print(f"URI: {NEO4J_URI}")
print(f"User: {NEO4J_USER}")
# Do not print password

if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
    print("❌ Missing environment variables!")
    exit(1)

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    print("✅ Connection successful!")
    driver.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
