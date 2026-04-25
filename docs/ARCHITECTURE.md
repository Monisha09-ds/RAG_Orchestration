# System Architecture & Logic Documentation

## Overview
This project is a **Knowledge-Aware Portfolio Chatbot** that uses a **GraphRAG (Retrieval-Augmented Generation)** approach.
It combines **Neo4j** (Graph Database) for structured knowledge and **Groq (Llama 3)** for reasoning and natural language generation.

The core philosophy is **Strict Grounding**: The bot is designed to **never exhale** or hallucinate. It only answers using facts explicitly found in the Knowledge Graph.

---

## 🏗️ Core Architecture

### 1. Module Structure (`graph_rag/`)
The backend logic is modularized into the `graph_rag` package:

| Module | Purpose |
| :--- | :--- |
| **`controller.py`** | **The Brain.** Orchestrates the flow. It handles user questions and URL ingestion. It implements the "Guardrails". |
| **`llm_client.py`** | **The Mouth & Ears.** Handles all calls to Groq. Responsible for **Intent Classification** and **Answer Generation**. |
| **`neo4j_connector.py`** | **The Memory.** Manages connection to Neo4j. Executes Cypher queries to fetch specific facts based on intent. |
| **`langchain_processor.py`** | **The Digestor.** Uses `LangChain` + `LLMGraphTransformer` to convert unstructured website text into structured Graph Nodes (Person, Project, Skill, Organization). |
| **`scraper.py`** | **The Eyes.** Fetches and cleans text from provided URLs. |
| **`config.py`** | Manages Environment Variables (`NEO4J_URI`, `GROQ_API_KEY`, etc.). |

---

## 🧠 Logic Flow: "Strict Grounding"

When a user asks a question, the system follows this strict pipeline:

### Step 1: Intent Classification
**Where:** `llm_client.classify_intent(question)`
The LLM analyzes the question and categorizes it into one of these intents:
*   `PERSON`: (Bio, Contact, Role)
*   `PROJECTS`: (Work, Apps, Experience)
*   `SKILLS`: (Tech stack, Languages, Tools)
*   `ALL`: (Fallback for complex queries)

### Step 2: Scoped Fact Retrieval
**Where:** `neo4j_connector.query_graph_facts(intent)`
Instead of dumping the whole database, we run a **Scoped Cypher Query**:
*   If `PROJECTS` -> Retrieve only `(Person)-[:WORKED_ON]->(Project)` and `(Person)-[:WORKED_AT]->(Organization)`.
*   If `SKILLS` -> Retrieve only `(Person)-[:HAS_SKILL]->(Skill)`.
*   **Result:** Context window is cleaner, and irrelevant info is hidden from the LLM.

### Step 3: The Empty-Fact Guardrail
**Where:** `controller.handle_question`
*   If the Graph Query returns **zero results**, the Controller **STOPs**.
*   It immediately returns: *"I don't have that information available in the current knowledge base."*
*   The LLM is **never called** to generate an answer. This guarantees 0% hallucination for missing topics.

### Step 4: Strict Answer Generation
**Where:** `llm_client.generate_answer`
If facts exist, the LLM generates an answer with these strict rules:
*   **Refusal**: "If answer is not in facts, say distinct phrase..."
*   **Tone**: Professional, no "I'm sorry", no marketing fluff.
*   **Length**: Max 3 sentences.

---

## 📥 Ingestion Logic (LangChain)
**Where:** `langchain_processor.process_text_to_graph`

1.  **Scrape**: `scraper.py` gets the text.
2.  **Transform**: `LLMGraphTransformer` (powered by Groq) reads the text and extracts:
    *   **Nodes**: `Person`, `Project`, `Skill`, `Tool`, `Domain`, `Organization`, `Website`.
    *   **rels**: `WORKED_ON`, `HAS_SKILL`, `WORKED_AT`, etc.
3.  **Sync**: `Neo4jGraph.add_graph_documents` writes this directly to the DB.

---

## 🚀 How to Resume Work

1.  **Run the App**:
    ```bash
    streamlit run portfoilio_bot.py
    ```

2.  **Debug / Verification Scripts**:
    *   `verify_strict_mode.py`: Tests the QA flow and guardrails.
    *   `reingest_fix.py`: Used to re-scan the URL and check for specific nodes (like missing Companies).

3.  **Future TODOs**:
    *   The **Website Name** extraction is currently hit-or-miss. You might need to add a specific rule or Regex in `scraper.py` or `custom extraction` if `LLMGraphTransformer` continues to ignore the `<title>`.
