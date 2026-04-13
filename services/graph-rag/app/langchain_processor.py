import logging
import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_experimental.graph_transformers import LLMGraphTransformer
# from langchain_community.graphs import Neo4jGraph # Deprecated
from langchain_neo4j import Neo4jGraph # New package
from .config import Config

logger = logging.getLogger("graph_rag.langchain")

def init_graph():
    """Initialize Neo4jGraph connection."""
    try:
        return Neo4jGraph(
            url=Config.NEO4J_URI,
            username=Config.NEO4J_USER,
            password=Config.NEO4J_PASSWORD
        )
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j via LangChain: {e}")
        return None

def process_text_to_graph(text, source="unknown"):
    """
    Transforms unstructured text into a Knowledge Graph using LLMGraphTransformer.
    """
    logger.info(f"Processing text ({len(text)} chars) from source: {source}...")
    
    # 1. Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    docs = [Document(page_content=text, metadata={"source": source})]
    chunks = text_splitter.split_documents(docs)
    logger.info(f"Split into {len(chunks)} chunks.")

    # 2. Setup LLM (Groq)
    # Using a model capable of function calling or structured output is preferred.
    llm = ChatGroq(
        api_key=Config.GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile", 
        temperature=0
    )
    
    # 3. Graph Transformation
    # Broadened schema for comprehensive knowledge
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=["Person", "Project", "Skill", "Tool", "Organization", "Website", "Education", "Experience", "Award"],
        allowed_relationships=[
            "WORKED_ON", "HAS_SKILL", "WORKED_AT", "USES", 
            "STUDIED_AT", "EARNED", "WORKED_AS", "BELONGS_TO"
        ],
        node_properties=["name", "description", "role", "degree", "institution", "year"],
        relationship_properties=False
    )
    
    try:
        graph_documents = llm_transformer.convert_to_graph_documents(chunks)
        logger.info(f"Extracted {len(graph_documents)} graph documents.")
        
        # 4. Ingest to Neo4j
        if graph_documents:
            graph = init_graph()
            if graph:
                graph.add_graph_documents(graph_documents, include_source=True)
                logger.info("Graph documents added to Neo4j.")
                return True
            else:
                logger.error("Failed to connect to Neo4j.")
                return False
        else:
            logger.warning("No graph documents extracted.")
            return False
            
    except Exception as e:
        logger.error(f"Error during graph processing: {e}")
        return False
