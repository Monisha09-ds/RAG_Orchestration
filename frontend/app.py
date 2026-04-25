import streamlit as st
import requests
import os
import time

# --- Configuration ---
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway:8000/api")

st.set_page_config(
    page_title="RAG Orchestrator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    .header-style {
        font-size:25px;
        font-family:'Courier New', Courier, monospace;
        color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("🤖 RAG Orchestrator")
    st.markdown("---")
    mode = st.radio(
        "Select Service Mode",
        ["🧠 Graph-RAG", "🔍 Vector-RAG", "🎙️ Voice-RAG"],
        index=0
    )
    st.markdown("---")
    st.info("The Gateway routes your request to the specialized microservice.")

# --- Helper Functions ---
def proxy_request(service, path, method="POST", data=None, files=None, json=None):
    url = f"{GATEWAY_URL}/{service}/{path}"
    try:
        if method == "POST":
            if files:
                return requests.post(url, files=files, data=data)
            return requests.post(url, json=json)
        return requests.get(url)
    except Exception as e:
        st.error(f"Gateway Connection Error: {e}")
        return None

# --- Main Logic ---

if mode == "🧠 Graph-RAG":
    st.header("🧠 Graph-Augmented Generation")
    st.subheader("Strictly Grounded Knowledge (Neo4j)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query = st.text_input("Enter your question:", placeholder="e.g., What are the key projects mentioned in the portfolio?")
        if st.button("Query Graph"):
            if query:
                with st.spinner("Traversing knowledge graph..."):
                    resp = proxy_request("graph", "query", json={"query": query})
                    if resp and resp.status_code == 200:
                        st.success("Response Received:")
                        st.markdown(resp.json().get("response", "No response content."))
                    else:
                        st.error(f"Error: {resp.status_code if resp else 'Unknown'}")
    
    with col2:
        st.write("### Data Ingestion")
        url_ingest = st.text_input("Ingest URL:", placeholder="https://example.com")
        if st.button("Ingest URL"):
            with st.spinner("Scraping and mapping..."):
                resp = proxy_request("graph", "ingest/url", json={"url": url_ingest})
                if resp and resp.status_code == 200:
                    st.toast("URL Ingested Successfully!")
                else:
                    st.error("Ingestion failed.")

elif mode == "🔍 Vector-RAG":
    st.header("🔍 Vector-Semantic Search")
    st.subheader("Deep Document Understanding (pgvector)")
    
    uploaded_file = st.file_uploader("Upload Document (PDF/DOCX)", type=["pdf", "docx"])
    if uploaded_file:
        if st.button("Upload & Index"):
            with st.spinner("Generating embeddings..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                resp = proxy_request("vector", "upload", files=files)
                if resp and resp.status_code == 200:
                    st.success("Document indexed successfully!")
                else:
                    st.error("Upload failed.")

    st.markdown("---")
    query = st.text_input("Ask about your documents:")
    if st.button("Search Documents"):
        if query:
            with st.spinner("Searching vector space..."):
                resp = proxy_request("vector", "query", json={"query": query})
                if resp and resp.status_code == 200:
                    st.write("### Results")
                    st.markdown(resp.json().get("response", "No response."))
                else:
                    st.error("Query failed.")

elif mode == "🎙️ Voice-RAG":
    st.header("🎙️ Multimodal Voice-RAG")
    st.subheader("Conversational AI (ElevenLabs + Whisper)")
    
    # Initialize Chat History
    if "voice_messages" not in st.session_state:
        st.session_state.voice_messages = []

    # Display History
    for msg in st.session_state.voice_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Inputs
    col_v1, col_v2 = st.columns([1, 4])
    with col_v1:
        voice_file = st.audio_input("Record", label_visibility="collapsed")
    with col_v2:
        text_input = st.chat_input("Type or record your message...")

    user_input = None
    if voice_file:
        with st.spinner("Transcribing..."):
            files = {"audio": ("input.wav", voice_file.read(), "audio/wav")}
            resp = proxy_request("voice", "transcribe", files=files)
            if resp and resp.status_code == 200:
                user_input = resp.json().get("text")
    elif text_input:
        user_input = text_input

    if user_input:
        st.session_state.voice_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                resp = proxy_request("voice", "chat", json={"messages": st.session_state.voice_messages})
                if resp and resp.status_code == 200:
                    ai_text = resp.json().get("message")
                    st.markdown(ai_text)
                    st.session_state.voice_messages.append({"role": "assistant", "content": ai_text})
                    
                    # Audio Generation
                    audio_resp = proxy_request("voice", "speak", json={"text": ai_text})
                    if audio_resp and audio_resp.status_code == 200:
                        st.audio(audio_resp.content, format="audio/mp3", autoplay=True)
                else:
                    st.error("Failed to get response.")

st.markdown("---")
st.caption("RAG Orchestration Platform v0.1 | Built with FastAPI & Streamlit")
