import streamlit as st
import requests
import os

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8090")

st.set_page_config(page_title="RAG Chatbot", layout="wide")

st.title("📄 AI RAG Assistant")
st.markdown("Chat with your documents using Llama-3 and pgvector.")

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Documents")
    uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    response = requests.post(f"{BACKEND_URL}/upload", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Success! Processed {data['chunks_processed']} chunks.")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/query", 
                    params={"question": prompt}
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer received.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = response.json().get("detail", "Error generating answer.")
                    st.error(error_msg)
            except Exception as e:
                st.error(f"Failed to connect to backend: {str(e)}")
