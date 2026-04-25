# 🧠 RAG System — Microservices Architecture

A modular RAG (Retrieval-Augmented Generation) platform composed of three independent microservices, unified by an API gateway.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Unified Frontend (:8005)                    │
│      (Single Dashboard for all RAG services)             │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│                API Gateway  (:8000)                      │
│     /api/graph/*  /api/vector/*  /api/voice/*            │
└───────┬──────────────────┬──────────────────┬────────────┘
        │                  │                  │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│   Graph-RAG   │  │   Vector-RAG  │  │   Voice-RAG   │
│     :8001     │  │     :8002     │  │ Server :8003  │
│  Neo4j + Groq │  │ pgvector+Groq │  └───────────────┘
└───────────────┘  └───────┬───────┘
                           │
                    ┌──────▼──────┐
                    │  PostgreSQL │
                    │  (pgvector) │
                    └─────────────┘
```

## Services

| Service | Port | Stack | Purpose |
|---------|------|-------|---------|
| **Unified Frontend**| 8005 | Streamlit | Single dashboard for interacting with all services |
| **API Gateway** | 8000 | FastAPI + httpx | Unified entry point & routing hub |
| **Graph-RAG** | 8001 | Neo4j + Groq | Strict grounded knowledge via Knowledge Graph |
| **Vector-RAG** | 8002 | pgvector + FastAPI | Semantic document search and Q&A |
| **Voice-RAG** | 8003 | Flask + ElevenLabs | Multimodal voice-to-voice document assistant |

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

### 3. Access the Dashboard
Open your browser and navigate to:
**[http://localhost:8005](http://localhost:8005)**

From here, you can switch between Graph-RAG, Vector-RAG, and Voice-RAG modes in a single interface.

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
