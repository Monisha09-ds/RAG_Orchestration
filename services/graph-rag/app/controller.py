import logging
from .scraper import scrape_content
from .langchain_processor import process_text_to_graph
from .llm_client import classify_intent, generate_answer
from .neo4j_connector import query_graph_facts, seed_dynamic_data, merge_duplicate_nodes
from .pdf_processor import process_pdf 

logger = logging.getLogger("graph_rag.controller")

def handle_question(question, history=None):
    """
    Orchestrates the RAG flow with strict guardrails and history awareness.
    """
    # 1. Classify Intent
    intent = classify_intent(question)
    
    # 2. Fetch Scoped Facts
    facts = query_graph_facts(intent)
    
    # 3. Guardrail: Empty Facts -> Fast Refusal
    is_empty = True
    if facts:
        if len(facts) > 0:
            is_empty = False
            
    if is_empty:
        logger.warning(f"Guardrail triggered: No facts found for intent {intent}.")
        return "I don't have that information available in the current knowledge base."
        
    # 4. Generate Answer with History
    answer = generate_answer(question, facts, history)
    return answer

def ingest_url(url):
    """
    Orchestrates ingestion from a URL.
    """
    logger.info(f"Starting ingestion for URL: {url}")
    
    raw_text = scrape_content(url)
    if not raw_text:
        return {"success": False, "message": "Failed to scrape content."}

    logger.info("Delegating to LangChain Graph Processor...")
    success = process_text_to_graph(raw_text, source=url)
    
    if not success:
         return {"success": False, "message": "Graph processing failed."}

    # Clean up graph after ingestion
    merge_duplicate_nodes()
    
    return {"success": True, "message": f"Successfully ingested content from {url}."}

def ingest_file(file_obj):
    """
    Orchestrates ingestion from a PDF file.
    """
    logger.info(f"Starting ingestion for file: {file_obj.name}")
    
    # 1. Process PDF to text chunks
    docs = process_pdf(file_obj)
    if not docs:
        return {"success": False, "message": "Failed to process PDF."}
        
    # 2. Combine text for graph processing (or process cleanly per chunk)
    # For now, we concatenate to simulate full text context for the graph transformer
    full_text = " ".join([d.page_content for d in docs])
    
    # 3. Extract to Graph
    success = process_text_to_graph(full_text, source=file_obj.name)
    
    if success:
        # Clean up graph after ingestion
        merge_duplicate_nodes()
        return {"success": True, "message": f"Successfully ingested {len(docs)} chunks from PDF."}
    else:
        return {"success": False, "message": "Graph extraction failed."}

def ingest_bulk(urls=None, files=None):
    """
    Processes multiple URLs and files sequentially.
    """
    results = {"success_count": 0, "fail_count": 0, "details": []}
    
    if urls:
        for url in urls:
            res = ingest_url(url)
            if res["success"]:
                results["success_count"] += 1
            else:
                results["fail_count"] += 1
            results["details"].append(res)
            
    if files:
        for file in files:
            res = ingest_file(file)
            if res["success"]:
                results["success_count"] += 1
            else:
                results["fail_count"] += 1
            results["details"].append(res)
            
    return results
