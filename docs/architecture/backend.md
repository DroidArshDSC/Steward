# Steward Backend Architecture

## Overview
The Steward backend powers the AI Onboarding Copilot.  
It provides APIs to query internal knowledge, retrieve relevant context from documentation, and return concise AI-generated responses.

## Tech Stack
- **FastAPI** — lightweight async Python web framework  
- **Chroma** — vector database for semantic search  
- **OpenAI / Claude** — large language models for response generation  
- **Pydantic + dotenv** — configuration and environment management  

## Module Map
steward-backend/
├── main.py # App entry point
├── app/
│ ├── api/
│ │ ├── health.py # Health check endpoint
│ │ └── query.py # RAG query API
│ └── core/
│ ├── ingest.py # Embedding + ingestion pipeline
│ └── rag_engine.py # Context retrieval + LLM call
└── data/chroma/ # Local vector store

## Data Flow
1. **Ingestion** — Markdown and code docs → Embeddings → Chroma vector DB  
2. **Query** — User prompt → Retrieve top-K docs → LLM → Final response  

## Future Additions
- Persistent DB (Qdrant, Weaviate)
- Auth via GitHub SSO
- Frontend dashboard for context visibility