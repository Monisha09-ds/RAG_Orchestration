import logging
from neo4j import GraphDatabase
from .config import Config

logger = logging.getLogger("graph_rag.neo4j")

try:
    driver = GraphDatabase.driver(
        Config.NEO4J_URI,
        auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
    )
    logger.info(f"Neo4j driver initialized for {Config.NEO4J_URI}")
except Exception as e:
    logger.critical(f"Failed to initialize Neo4j driver: {e}")
    raise

def get_driver():
    return driver

def close_driver():
    driver.close()

def verify_connection():
    """Checks if the Neo4j driver is connected."""
    try:
        driver.verify_connectivity()
        return True
    except Exception as e:
        logger.error(f"Connection verification failed: {e}")
        return False

def seed_graph_data():
    """Seeds specific dummy data."""
    logger.info("Seeding dummy portfolio data...")
    with driver.session() as session:
        session.run("""
        MERGE (p:Person {name: "Monisha", role: "Junior AI Engineer"})
        MERGE (proj:Project {name: "Antigravity Knowledge-Aware Portfolio Bot"})
        MERGE (s1:Skill {name: "Knowledge Graph"})
        MERGE (s2:Skill {name: "RAG Systems"})
        MERGE (t1:Tool {name: "Neo4j"})
        MERGE (t2:Tool {name: "Groq LLM"})
        MERGE (d:Domain {name: "AI Systems"})

        MERGE (p)-[:WORKED_ON]->(proj)
        MERGE (p)-[:HAS_SKILL]->(s1)
        MERGE (p)-[:HAS_SKILL]->(s2)

        MERGE (proj)-[:REQUIRES_SKILL]->(s1)
        MERGE (proj)-[:REQUIRES_SKILL]->(s2)
        MERGE (proj)-[:USES]->(t1)
        MERGE (proj)-[:USES]->(t2)
        MERGE (proj)-[:BELONGS_TO]->(d)
        """)
    logger.info("Dummy data seeding complete.")

def seed_dynamic_data(data):
    """Seeds data extracted from URL."""
    if not data:
        logger.warning("No data provided to seed_dynamic_data.")
        return
        
    person = data.get('person', {})
    p_name = person.get('name', 'Unknown')
    p_role = person.get('role', 'Developer')
    
    logger.info(f"Seeding data for person: {p_name} ({p_role})")
    
    with driver.session() as session:
        session.run("""
        MERGE (p:Person {name: $name})
        SET p.role = $role
        """, name=p_name, role=p_role)
        
        # Skills
        skills = data.get('skills', [])
        logger.info(f"Seeding {len(skills)} skills...")
        for skill in skills:
            session.run("""
            MATCH (p:Person {name: $p_name})
            MERGE (s:Skill {name: $skill})
            MERGE (p)-[:HAS_SKILL]->(s)
            """, p_name=p_name, skill=skill)
            
        # Tools
        tools = data.get('tools', [])
        logger.info(f"Seeding {len(tools)} tools...")
        for tool in tools:
           session.run("MERGE (t:Tool {name: $name})", name=tool)

        # Projects
        projects = data.get('projects', [])
        logger.info(f"Seeding {len(projects)} projects...")
        for proj in projects:
            session.run("""
            MATCH (p:Person {name: $p_name})
            MERGE (pr:Project {name: $proj_name})
            SET pr.description = $desc
            MERGE (p)-[:WORKED_ON]->(pr)
            """, p_name=p_name, proj_name=proj['name'], desc=proj.get('description', ''))
            
    logger.info("Dynamic data seeding complete.")

def query_graph_facts(intent="ALL"):
    """
    Fetches facts based on the classified intent.
    Intents: PERSON, PROJECTS, SKILLS, TOOLS, ALL
    """
    logger.info(f"Querying Graph with Intent: {intent}")
    
    query = ""
    
    if intent == "PERSON":
        query = """
        MATCH (p:Person)
        OPTIONAL MATCH (p)-[:BELONGS_TO]->(d:Domain)
        RETURN 
            coalesce(p.name, p.id) as person_name, 
            p.role as role, 
            collect(distinct coalesce(d.name, d.id)) as domains
        """
    elif intent == "PROJECTS":
        query = """
        MATCH (p:Person)-[:WORKED_ON]->(proj:Project)
        OPTIONAL MATCH (proj)-[:USES]->(t:Tool)
        RETURN 
            coalesce(proj.name, proj.id) as name, 
            proj.description as description, 
            collect(distinct coalesce(t.name, t.id)) as details,
            "Project" as type
        UNION ALL
        MATCH (p:Person)-[:WORKED_AT]->(o:Organization)
        RETURN 
            coalesce(o.name, o.id) as name, 
            "Organization" as description, 
            [] as details,
            "Experience" as type
        UNION ALL
        MATCH (p:Person)-[:WORKED_AS]->(e:Experience)
        RETURN 
            coalesce(e.role, e.id) as name, 
            e.company as description, 
            [e.period] as details,
            "Career" as type
        """
    elif intent in ["SKILLS", "TOOLS"]:
        query = """
        MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
        RETURN coalesce(s.name, s.id) as name, "Skill" as type
        UNION ALL
        MATCH (t:Tool)
        RETURN coalesce(t.name, t.id) as name, "Tool" as type
        """
    elif intent == "EDUCATION":
        query = """
        MATCH (p:Person)-[:STUDIED_AT]->(e:Education)
        RETURN 
            coalesce(e.institution, e.id) as name, 
            e.degree as description, 
            [e.year] as details,
            "Education" as type
        UNION ALL
        MATCH (p:Person)-[:EARNED]->(a:Award)
        RETURN 
            coalesce(a.name, a.id) as name, 
            "Certification/Award" as description, 
            [] as details,
            "Achievement" as type
        """
    else: # ALL or unknown - Optimized for Knowledge Base Overview
        query = """
        MATCH (p:Person)
        OPTIONAL MATCH (p)-[:WORKED_ON]->(proj:Project)
        OPTIONAL MATCH (p)-[:HAS_SKILL]->(s:Skill)
        OPTIONAL MATCH (p)-[:STUDIED_AT]->(ed:Education)
        OPTIONAL MATCH (p)-[:EARNED]->(a:Award)
        RETURN
            coalesce(p.name, p.id) AS person,
            p.role AS role,
            collect(DISTINCT coalesce(proj.name, proj.id)) AS projects,
            collect(DISTINCT coalesce(s.name, s.id)) AS skills,
            collect(DISTINCT coalesce(ed.degree, ed.id)) AS education,
            collect(DISTINCT coalesce(a.name, a.id)) AS awards
        LIMIT 1
        """

    with driver.session() as session:
        result = session.run(query)
        data = [r.data() for r in result]
        logger.info(f"Graph query returned {len(data)} records for intent {intent}.")
        return data

def merge_duplicate_nodes():
    """
    Deduplicates nodes with the same name (case-insensitive) to clean up the graph.
    """
    logger.info("Running node deduplication logic...")
    labels = ["Skill", "Tool", "Project", "Organization", "Education", "Award"]
    
    with driver.session() as session:
        for label in labels:
            # Cypher query to merge nodes with same name
            merge_query = f"""
            MATCH (n:{label})
            WITH toLower(n.name) as normalized_name, collect(n) as nodes
            WHERE size(nodes) > 1
            CALL apoc.refactor.mergeNodes(nodes, {{properties: 'combine', mergeRels: true}})
            YIELD node
            RETURN node
            """
            try:
                session.run(merge_query)
            except Exception as e:
                # Fallback if APOC is not installed
                fallback_query = f"""
                MATCH (n:{label})
                WITH toLower(n.name) as normalized_name, collect(n) as nodes
                WHERE size(nodes) > 1
                WITH nodes[0] as first, nodes[1..] as rest
                FOREACH (other in rest |
                    MATCH (other)-[r]->(target)
                    MERGE (first)-[newR:TYPE(r)]->(target)
                    SET newR = r
                    DETACH DELETE other
                )
                """
                session.run(fallback_query)
    logger.info("Deduplication complete.")

def get_graph_stats():
    """
    Returns general statistics about the graph.
    """
    logger.info("Fetching graph statistics...")
    query = """
    CALL () {
        MATCH (n) RETURN count(n) as nodes
    }
    CALL () {
        MATCH ()-[r]->() RETURN count(r) as relationships
    }
    CALL () {
        MATCH (n) RETURN labels(n)[0] as label, count(*) as count ORDER BY count DESC LIMIT 5
    }
    RETURN nodes, relationships, collect({label: label, count: count}) as top_labels
    """
    with driver.session() as session:
        result = session.run(query)
        return result.single().data()

def get_node_importance():
    """
    Returns influential nodes based on degree centrality.
    """
    logger.info("Fetching influential nodes...")
    query = """
    MATCH (n)
    WHERE size(labels(n)) > 0
    RETURN coalesce(n.name, n.id, labels(n)[0]) as name, 
           labels(n)[0] as type, 
           count{(n)--()} as degree
    ORDER BY degree DESC
    LIMIT 10
    """
    with driver.session() as session:
        result = session.run(query)
        return [r.data() for r in result]
