from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import shutil
import os
import tempfile

from .services.ingestion import ingestion_service
from .services.rag import rag_service

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="RAG System API")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG System API"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        # Check pgvector extension
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        return {"status": "healthy", "database": "connected", "pgvector": "enabled"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            num_chunks = await ingestion_service.process_file(tmp_path, file.content_type)
            return {
                "filename": file.filename,
                "status": "success",
                "chunks_processed": num_chunks
            }
        finally:
            # Clean up the temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/query")
async def query_rag(question: str):
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        response = await rag_service.query(question)
        return {"question": question, "answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
