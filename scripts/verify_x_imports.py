import os
import sys

print("--- Checking Imports ---")
try:
    from dotenv import load_dotenv
    print("✅ dotenv")
    from langchain_community.document_loaders import PyPDFLoader
    print("✅ PyPDFLoader")
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("✅ RecursiveCharacterTextSplitter")
    from langchain_community.vectorstores import Neo4jVector
    print("✅ Neo4jVector")
    from langchain_groq import ChatGroq
    print("✅ ChatGroq")
    from langchain_huggingface import HuggingFaceEmbeddings
    print("✅ HuggingFaceEmbeddings")
    from langchain_community.graphs import Neo4jGraph
    print("✅ Neo4jGraph")
    from langchain_experimental.graph_transformers import LLMGraphTransformer
    print("✅ LLMGraphTransformer")
    from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
    print("✅ GraphCypherQAChain")
    import streamlit as st
    print("✅ streamlit")
    print("\n🎉 ALL IMPORTS PASSED")
except Exception as e:
    print(f"\n❌ IMPORT FAILED: {e}")
