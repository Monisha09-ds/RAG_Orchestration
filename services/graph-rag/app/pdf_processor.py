import logging
import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger("graph_rag.pdf")

def process_pdf(file_obj, chunk_size=200, chunk_overlap=40):
    """
    Processes an uploaded PDF file:
    1. Saves to temp file
    2. Loads via PyPDFLoader
    3. Splits into chunks
    4. Returns list of LangChain Documents
    """
    logger.info(f"Processing PDF: {file_obj.name}")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_obj.read())
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        pages = loader.load_and_split()
        
        # Clean up temp file
        os.remove(tmp_path)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        docs = text_splitter.split_documents(pages)

        # Clean content and metadata
        cleaned_docs = []
        for doc in docs:
            cleaned_docs.append(Document(
                page_content=doc.page_content.replace("\n", " "),
                metadata={'source': file_obj.name, 'page': doc.metadata.get('page', 0)}
            ))
            
        logger.info(f"PDF processed into {len(cleaned_docs)} chunks.")
        return cleaned_docs

    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        return []
