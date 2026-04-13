"""
FastAPI entrypoint for the Graph-RAG microservice.
Exposes the existing controller functions as REST endpoints.
"""
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

from .neo4j_connector import verify_connection, close_driver, seed_graph_data
from .controller import handle_question, ingest_url, ingest_file

logger = logging.getLogger("graph_rag.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    if verify_connection():
        logger.info("Neo4j connection verified on startup.")
    else:
        logger.warning("Neo4j connection could not be verified on startup.")
    yield
    close_driver()
    logger.info("Neo4j driver closed on shutdown.")


app = FastAPI(
    title="Graph-RAG Service",
    description="Knowledge Graph RAG powered by Neo4j + Groq (Llama-3)",
    version="0.1.0",
    lifespan=lifespan,
)


# --- Request / Response Models ---

class QueryRequest(BaseModel):
    question: str
    history: list[dict] | None = None

class IngestURLRequest(BaseModel):
    url: str


# --- Endpoints ---

@app.get("/health")
async def health():
    connected = verify_connection()
    return {
        "service": "graph-rag",
        "status": "healthy" if connected else "unhealthy",
        "neo4j": "connected" if connected else "disconnected",
    }


@app.post("/query")
async def query(req: QueryRequest):
    """Ask a question against the Knowledge Graph."""
    if not req.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    answer = handle_question(req.question, history=req.history)
    return {"question": req.question, "answer": answer}


@app.post("/ingest/url")
async def ingest_from_url(req: IngestURLRequest):
    """Scrape a URL and ingest its content into the Knowledge Graph."""
    if not req.url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")
    result = ingest_url(req.url)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.post("/ingest/file")
async def ingest_from_file(file: UploadFile = File(...)):
    """Upload a PDF and ingest its content into the Knowledge Graph."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    result = ingest_file(file.file)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.post("/seed")
async def seed():
    """Load dummy portfolio data into the Knowledge Graph."""
    seed_graph_data()
    return {"status": "seeded", "message": "Dummy data loaded successfully."}
