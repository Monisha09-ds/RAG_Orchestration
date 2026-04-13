# 🧠 RAG System — Microservices Architecture

A modular RAG (Retrieval-Augmented Generation) platform composed of three independent microservices, unified by an API gateway.

## Architecture

```
┌─────────────────────────────────────────────────┐
│           API Gateway  (:8000)                  │
│    /api/graph/*  /api/vector/*  /api/voice/*    │
└─────┬───────────────┬──────────────┬────────────┘
      │               │              │
┌─────▼─────┐  ┌──────▼──────┐  ┌───▼──────────┐
│ Graph-RAG │  │ Vector-RAG  │  │  Voice-RAG   │
│   :8001   │  │   :8002     │  │ Server :8003 │
│ Neo4j+Groq│  │pgvector+Groq│  │ Client :8004 │
└───────────┘  └──────┬──────┘  └──────────────┘
                      │
               ┌──────▼──────┐
               │ PostgreSQL  │
               │  (pgvector) │
               └─────────────┘
```

## Services

| Service | Port | Stack | Purpose |
|---------|------|-------|---------|
| **Graph-RAG** | 8001 | Neo4j + Groq Llama-3 | Portfolio chatbot with strict grounding via Knowledge Graph |
| **Vector-RAG** | 8002 | pgvector + FastAPI | Document Q&A with vector similarity search |
| **Voice-RAG** | 8003/8004 | FAISS + ElevenLabs TTS | Voice-to-voice document assistant |
| **Gateway** | 8000 | FastAPI + httpx | Unified API entry point |

## Quick Start

### 1. Configure Environment
```bash
cp .env.template .env
# Edit .env with your API keys
```

### 2. Run All Services
```bash
docker-compose up --build
```

### 3. Test
```bash
# Gateway health check
curl http://localhost:8000/health

# Query Graph-RAG via gateway
curl -X POST http://localhost:8000/api/graph/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What projects has Monisha worked on?"}'

# Upload PDF to Vector-RAG
curl -X POST http://localhost:8000/api/vector/upload \
  -F "file=@document.pdf"

# Voice-RAG client UI
open http://localhost:8004
```

## Local Development (Single Service)

```bash
# Example: Run graph-rag locally
cd services/graph-rag
uv sync
uv run uvicorn app.main:app --reload --port 8001
```

## Project Structure

```
RAG-system/
├── services/
│   ├── graph-rag/      # Knowledge Graph RAG (Neo4j)
│   ├── vector-rag/     # Vector Search RAG (pgvector)
│   └── voice-rag/      # Voice RAG (ElevenLabs TTS)
├── gateway/            # API Gateway (reverse proxy)
├── scripts/            # Debug and verification scripts
├── docs/               # Architecture documentation
├── docker-compose.yml  # Unified orchestration
└── .env.template       # Environment variables
```
