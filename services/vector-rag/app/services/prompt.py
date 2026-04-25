"""
Prompt templates and configurations for the RAG system.
"""

from langchain_core.prompts import ChatPromptTemplate

# Main RAG prompt template
RAG_PROMPT_TEMPLATE = """You are a helpful AI assistant that answers questions based on the provided context from documents.

Context from documents:
{context}

User Question: {question}

Instructions:
1. Carefully read the context provided above
2. Answer the question using ONLY the information from the context
3. If the context contains relevant information, provide a clear and detailed answer
4. If you find partial information, answer what you can and mention what's missing
5. Only say you don't have enough information if the context is truly empty or completely unrelated
6. Be conversational and helpful in your tone
7. If the context mentions file names, links, or specific details, include them in your answer

Answer:"""

# Alternative prompt for when we want more creative responses
CREATIVE_RAG_PROMPT_TEMPLATE = """You are a knowledgeable AI assistant helping users understand their documents.

Here's what I found in the documents:
{context}

Question: {question}

Please provide a helpful answer based on the information above. If the documents contain relevant details, use them to give a comprehensive response. If some information is missing, answer what you can and note what additional details would be helpful.

Answer:"""

# Prompt for document summarization
SUMMARY_PROMPT_TEMPLATE = """Based on the following document excerpts, provide a concise summary:

{context}

Summary:"""


def get_rag_prompt(style: str = "default") -> ChatPromptTemplate:
    """
    Get a RAG prompt template based on the specified style.
    
    Args:
        style: The prompt style to use ("default", "creative", "summary")
    
    Returns:
        ChatPromptTemplate configured for RAG
    """
    if style == "creative":
        return ChatPromptTemplate.from_template(CREATIVE_RAG_PROMPT_TEMPLATE)
    elif style == "summary":
        return ChatPromptTemplate.from_template(SUMMARY_PROMPT_TEMPLATE)
    else:
        return ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
