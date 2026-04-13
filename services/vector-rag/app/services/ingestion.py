import os
import tempfile
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
# Use a common open-source embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

class IngestionService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name="rag_collection",
            connection=DATABASE_URL,
            use_jsonb=True,
        )

    async def process_file(self, file_path: str, file_type: str) -> int:
        """
        Processes a file, splits it into chunks, generates embeddings, and stores them.
        Returns the number of chunks added.
        """
        if file_type == "application/pdf":
            loader = PyPDFLoader(file_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        
        # Add to vector store
        self.vector_store.add_documents(chunks)
        
        return len(chunks)

ingestion_service = IngestionService()
