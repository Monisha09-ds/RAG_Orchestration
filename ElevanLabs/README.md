# Voice RAG Knowledge Assistant (Groq + ElevenLabs + LangChain)

This project is an interactive AI Knowledge Assistant that uses Retrieval-Augmented Generation (RAG) to answer questions based on uploaded PDFs.

## Architecture

- **Backend (Flask)**: Handles Groq (LLM), ElevenLabs (TTS), and FAISS (Vector Store).
- **Frontend (Streamlit)**: Interactive chat UI with PDF uploader and voice support.
- **RAG Engine**: LangChain + FAISS + HuggingFace Embeddings.
- **LLM**: Llama 3 via Groq.
- **Voice**: ElevenLabs & Whisper (via Groq).

## Features

- **PDF Ingestion**: Upload and index your documents in real-time.
- **Knowledge-Augmented Chat**: The bot searches your documents before answering.
- **Voice-to-Voice**: Speak your questions and hear the answers.

1.  **Configure API Keys**:
    - Open the `.env` file.
    - Add `ELEVENLABS_API_KEY`.
    - Add `GROQ_API_KEY` (from console.groq.com).

## Running the App (Docker)

To run the entire application in one go:

```bash
docker-compose up
```

-   **Frontend**: http://localhost:8502
-   **Backend**: http://localhost:5000

## Running the App (Manual)

**Terminal 1: Start the Backend**
```bash
uv run python server/app.py
```
*Runs on http://localhost:5000*

**Terminal 2: Start the Frontend**
```bash
uv run streamlit run client/app.py
```
*Opens in your browser at http://localhost:8501*

## Usage

1.  Go to the Streamlit tab in your browser.
2.  Enter some text.
3.  Click "Generate Audio".
4.  Listen to the result!
