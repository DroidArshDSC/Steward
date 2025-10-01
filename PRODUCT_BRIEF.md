# Steward — Product Brief

## 🌟 Mission
Steward is an **AI Onboarding Copilot for Engineers**.  
Its goal is to help new and existing developers become productive faster by answering questions, guiding setup, and surfacing knowledge in context.

---

## 👤 User Personas
- **New Hire / Junior Dev**: Needs fast onboarding, setup, and task guidance.  
- **Mid-level Engineer**: Needs quick answers about code and architecture.  
- **Senior Engineer**: Needs runbooks, ownership lookups, and provenance.  
- **Engineering Manager**: Wants metrics on onboarding efficiency and doc health.

---

## 🚨 Problems Steward Solves
- Long **time-to-first-PR** for new hires.  
- Repeated basic questions draining senior engineers.  
- Tribal knowledge scattered in Slack, PRs, and old docs.  
- Stale, hard-to-find documentation.  

---

## 💡 Value Proposition
- Instant, context-specific answers with source links.  
- Step-by-step onboarding workflows.  
- Runbooks for incidents and deployments.  
- Reduced reliance on tribal knowledge.  
- Faster ramp-up and better onboarding satisfaction.

---

## 🔑 Core Features
### MVP
- **Chat interface** with Retrieval-Augmented Generation (RAG).  
- **Git-based ingestion**: pull docs (Markdown), chunk, embed, index.  
- **Source citation**: answers always include repo excerpt + commit link.  
- **Basic access control** via GitHub SSO.  
- **Simple Web UI** (chat + links to docs).

### Future
- **VS Code Extension** for in-IDE help.  
- **Knowledge Graph** for ownership and dependencies.  
- **Guided workflows** (e.g., adding an API endpoint).  
- **Feedback loop** to improve retrieval & prompts.  
- **Offline mode** for secure environments.

---

## ⚙️ Technical Overview
- **Backend**: FastAPI (Python) for ingestion & query APIs.  
- **Storage**:  
  - Docs: GitHub (Markdown).  
  - Metadata: Postgres.  
  - Embeddings: Vector DB (Pinecone/Weaviate/Qdrant).  
  - Large files: S3/GCS.  
- **LLM Layer**: GPT-4.1 / Claude 3.5 for reasoning.  
- **Frontend**: React (Next.js) chat UI.  
- **Auth**: GitHub SSO → role-based access.

---

## 📈 Success Metrics
- ⏱️ Reduce **time-to-first-PR** for new hires.  
- 📊 % of onboarding questions answered by Steward.  
- 🔄 Decrease in repeated questions to senior engineers.  
- ✅ Doc coverage and freshness scores.  
- 🙌 New hire satisfaction with onboarding.

---

## ⚠️ Risks & Mitigations
- **Wrong answers** → Always cite sources, allow feedback.  
- **Stale docs** → Track `last_updated`, add doc health alerts.  
- **Sensitive info leaks** → PII/secrets filters before indexing.  
- **Cost overruns** → Cache answers, batch embeddings, monitor LLM spend.  
- **Access issues** → Use team-based namespaces in vector DB.

---

## 🛠️ Roadmap
- **Set up repo + doc structure.**  
- **Build ingestion pipeline** (Markdown → embeddings → vector DB).  
- **Expose query endpoint** (RAG over docs + code).  
- **Basic chat UI** to ask questions.  
- **Integrate SSO + access control.**  
- **Iterate** based on internal usage and feedback.

---

## 🎯 Vision
Steward becomes a **developer knowledge layer**:  
- Always available in docs, chat, and IDE.  
- Contextual, reliable, and self-updating.  
- A “junior mentor” that reduces friction, accelerates learning, and scales engineering culture.

---
