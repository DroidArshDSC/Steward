# Steward

🚀 **Steward** is an **AI Onboarding Copilot for Engineers**.  
It helps new and existing developers ramp up faster by answering questions, guiding setup, and surfacing knowledge directly from your docs and code.

---

## ✨ What Steward Does
- 🔍 **Answers developer questions** with context from code + docs.  
- 📖 **Guides onboarding** with step-by-step setup and first-PR workflows.  
- 🛠️ **Provides runbooks** for incidents, deployments, and ops tasks.  
- 📎 **Cites sources** with repo links and commit references.  
- 🔑 **Respects access control** via GitHub SSO.

---

## 📦 Tech Overview
- **Backend**: FastAPI (Python)  
- **Frontend**: React (Next.js)  
- **Storage**: Markdown in GitHub, Postgres for metadata, Vector DB for embeddings  
- **AI Layer**: RAG (OpenAI / Claude)  
- **Auth**: GitHub SSO (role-based access)  

---

## 🚧 Roadmap (MVP)
- Ingestion pipeline: Markdown → embeddings → vector DB  
- `/api/query` endpoint → RAG-powered answers  
- Minimal chat UI with source links  
- GitHub SSO integration  

---


---

## 🤝 Contributing
1. Fork the repo  
2. Add or update Markdown docs under `/docs`  
3. Open a PR → ensure metadata (`last_updated`, `owners`) is filled  

---

## 🎯 Vision
Steward becomes the **developer knowledge layer** — always available in docs, chat, and IDE, helping engineers learn faster and build with confidence.
