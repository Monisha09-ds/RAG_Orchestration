import streamlit as st
import requests
import os

# Configuration
BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:5000").replace("/api/speak", "")
SPEAK_URL = f"{BACKEND_BASE_URL}/api/speak"
MODELS_URL = f"{BACKEND_BASE_URL}/api/models"
CHAT_URL = f"{BACKEND_BASE_URL}/api/chat"
TRANSCRIBE_URL = f"{BACKEND_BASE_URL}/api/transcribe"

st.set_page_config(page_title="Voice RAG Assistant", page_icon="🧬")

st.title("🧬 Voice RAG Knowledge Assistant")
st.markdown("Upload a PDF and ask questions! I'll answer using the document's content and speak the response.")

# Sidebar Settings
with st.sidebar:
    st.header("Knowledge Base")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    
    if uploaded_file:
        if st.button("Index Document"):
            with st.spinner("Indexing PDF..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    UPLOAD_URL = f"{BACKEND_BASE_URL}/api/upload"
                    resp = requests.post(UPLOAD_URL, files=files)
                    if resp.status_code == 200:
                        st.success(resp.json().get("message"))
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    st.divider()
    st.header("Voice Settings")
    @st.cache_data
    def get_available_models():
        try:
            response = requests.get(MODELS_URL)
            return response.json() if response.status_code == 200 else None
        except: return None

    models_data = get_available_models()
    if models_data:
        model_options = {m['name']: m['model_id'] for m in models_data}
        selected_model_name = st.selectbox("Speech Model:", options=list(model_options.keys()), index=0)
        selected_model_id = model_options[selected_model_name]
    else:
        selected_model_id = "eleven_multilingual_v2"
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Inputs: Voice or Text
col1, col2 = st.columns([1, 4])
with col1:
    voice_file = st.audio_input("Voice Input", label_visibility="collapsed")
with col2:
    text_input = st.chat_input("Type your message here...")

user_input = None

# Handle Voice Input
if voice_file:
    with st.spinner("Transcribing..."):
        try:
            files = {"audio": ("input.wav", voice_file.read(), "audio/wav")}
            resp = requests.post(TRANSCRIBE_URL, files=files)
            if resp.status_code == 200:
                user_input = resp.json().get("text")
            else:
                st.error("Transcription failed.")
        except Exception as e:
            st.error(f"Error: {e}")

# Handle Text Input
if text_input:
    user_input = text_input

# Process Message
if user_input:
    # Add User Message to History
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                chat_resp = requests.post(CHAT_URL, json={"messages": st.session_state.messages})
                if chat_resp.status_code == 200:
                    ai_text = chat_resp.json().get("message")
                    st.markdown(ai_text)
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
                    
                    # Generate Audio
                    with st.spinner("Generating voice..."):
                        audio_resp = requests.post(SPEAK_URL, json={
                            "text": ai_text,
                            "model_id": selected_model_id
                        })
                        if audio_resp.status_code == 200:
                            st.audio(audio_resp.content, format="audio/mp3", autoplay=True)
                else:
                    st.error("Failed to get AI response.")
            except Exception as e:
                st.error(f"Error: {e}")
