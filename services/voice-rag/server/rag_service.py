import os
import base64
from io import BytesIO
from PIL import Image
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

class RAGService:
    def __init__(self, documents_dir="documents", index_path="faiss_index"):
        self.documents_dir = documents_dir
        self.index_path = index_path
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        
        # Initialize Groq client for Vision
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None
        
        if not os.path.exists(self.documents_dir):
            os.makedirs(self.documents_dir)
            
        # Try to load existing index
        if os.path.exists(self.index_path):
            try:
                self.vector_store = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
                print("Loaded existing FAISS index.")
            except Exception as e:
                print(f"Failed to load index: {e}")

    def _encode_image(self, image_bytes):
        return base64.b64encode(image_bytes).decode('utf-8')

    def _describe_image(self, image_bytes):
        """Uses Groq Vision model to describe an image."""
        if not self.groq_client:
            return "Vision analysis unavailable (API key missing)."
        
        base64_image = self._encode_image(image_bytes)
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image in detail. What objects, text, or data are visible? Focus on facts useful for a knowledge base."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=512,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Vision error: {e}")
            return f"Error describing image: {e}"

    def index_pdf(self, file_path):
        """Indexes a PDF file including text and image descriptions."""
        import fitz  # PyMuPDF
        
        # 1. Load Text
        loader = PyPDFLoader(file_path)
        text_docs = loader.load()
        
        # 2. Extract Images and Describe them
        image_docs = []
        pdf_document = fitz.open(file_path)
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                
                print(f"Describing image {img_index} on page {page_num}...")
                description = self._describe_image(image_bytes)
                
                # Create a virtual document for the image description
                image_docs.append(Document(
                    page_content=f"[IMAGE DESCRIPTION FROM PAGE {page_num+1}]: {description}",
                    metadata={"source": file_path, "page": page_num, "type": "image"}
                ))
        
        pdf_document.close()
        
        # 3. Combine and Chunk
        all_docs = text_docs + image_docs
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(all_docs)
        
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vector_store.add_documents(chunks)
        
        # Save the index
        self.vector_store.save_local(self.index_path)
        return len(chunks)

    def query(self, question, k=3):
        """Retrieves relevant snippets for a question."""
        if self.vector_store is None:
            return ""
        
        docs = self.vector_store.similarity_search(question, k=k)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context

# Singleton instance
rag_service = RAGService()
