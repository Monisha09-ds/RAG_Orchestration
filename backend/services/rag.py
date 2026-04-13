import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from services.prompt import get_rag_prompt

DATABASE_URL = os.getenv("DATABASE_URL")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name="rag_collection",
            connection=DATABASE_URL,
            use_jsonb=True,
        )
        # Increase k to retrieve more chunks for better context
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 8})
        
        self.llm = ChatGroq(
            temperature=0.3,  # Slightly increased for more natural responses
            groq_api_key=GROQ_API_KEY,
            model_name="llama-3.3-70b-versatile"
        )
        
        # Use the improved prompt from prompt.py
        self.prompt = get_rag_prompt(style="default")
        
        # Build the RAG chain
        self.chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    async def query(self, question: str) -> str:
        """
        Retrieves relevant chunks and generates an answer grounded in the documents.
        """
        return self.chain.invoke(question)

rag_service = RAGService()
