# 🧠 Steward — AI Onboarding Copilot for Engineers

🚀 **Steward** is an **AI-powered onboarding assistant** for developers.  
It helps new and existing engineers ramp up faster by answering questions, guiding setup, and surfacing knowledge directly from your **codebase and documentation**.

---

## ✨ What Steward Does

- 🔍 **Answers developer questions** with real context from your code and docs.  
- 📖 **Guides onboarding** with setup walkthroughs and first-PR workflows.  
- 🛠️ **Provides runbooks** for deployments and incident response.  
- 📎 **Cites sources** (files, paths, commits) so answers are verifiable.  
- 🔑 **Respects access control** using GitHub SSO (planned).  

---

## 📦 Tech Overview

| Layer | Technology | Purpose |
|-------|-------------|----------|
| **Backend** | FastAPI (Python) | REST API for ingestion & querying |
| **Frontend** | React (Next.js) | Chat-like interface for interacting with Steward |
| **Vector DB** | Chroma | Stores embeddings of your code & docs |
| **AI Model** | OpenAI GPT-4o / GPT-4-Turbo | Reasoning, summarization & answering |
| **Auth (Planned)** | GitHub SSO | Role-based access to company repos |

---

## 🚧 Roadmap (MVP)

- ✅ Ingestion pipeline: Markdown → embeddings → vector DB  
- ✅ `/api/query` endpoint: RAG-powered answers  
- ⚙️ Minimal chat UI with source links  
- 🔐 GitHub SSO integration  
- 🧾 Spec Drift Detection *(planned)* — detect mismatches between docs and code  

---

## 📂 Repo Structure

steward-backend/
│
├── app/
│ ├── api/ # API routes (query, health)
│ ├── core/ # RAG engine + ingestion logic
│ └── models/ # Schemas / dataclasses
│
├── data/
│ └── chroma/ # Auto-generated embeddings (ignored in Git)
│
├── requirements.txt
├── main.py # FastAPI entrypoint
├── .env.example # Example environment config
└── README.md

yaml
Copy code

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Steward.git
cd Steward/steward-backend
2️⃣ Create and Activate a Virtual Environment
bash
Copy code
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Configure Environment
bash
Copy code
cp .env.example .env
Edit .env and fill in:

bash
Copy code
OPENAI_API_KEY=sk-your-openai-key
CHROMA_PERSIST_DIR=data/chroma
APP_ENV=dev
PORT=8000
5️⃣ Build the Knowledge Base
bash
Copy code
python app/core/ingest.py
This parses your Python files (and Markdown docs, if any) → generates embeddings → stores them in data/chroma.

Expected output:

csharp
Copy code
✅ Steward knowledge base built successfully!
6️⃣ Run the API
bash
Copy code
uvicorn main:app --reload
7️⃣ Test Query Endpoint
bash
Copy code
curl -X POST "http://127.0.0.1:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does this project do?"}'
8️⃣ Health Check
bash
Copy code
curl http://127.0.0.1:8000/api/health
Expected:

json
Copy code
{
  "status": "ok",
  "message": "✅ OpenAI API key is valid.",
  "model_detected": "gpt-4o"
}
🧠 How Steward Works
Steward uses Retrieval-Augmented Generation (RAG) to connect your docs and code to an intelligent assistant.

mermaid
Copy code
flowchart TD
    A[Ingestion] -->|Embeds Markdown & Code| B[Vector DB (Chroma)]
    B -->|Retrieves Context| C[LLM (GPT-4o)]
    C -->|Generates Answer + Citations| D[Steward API]
    D -->|Served to User| E[Chat UI / CLI / IDE Plugin]
🔍 Process Overview
Ingest: Parses .py and .md files → creates embeddings → stores in Chroma.

Query: User asks a question → system retrieves relevant chunks → sends to GPT-4o.

Respond: GPT-4o generates a contextual, sourced answer.

Example:

“How do I deploy staging?”
→ Steward: “Run deploy_staging.sh (source: /docs/runbooks/deployments.md).”

🤝 Contributing
Fork the repo

Add or update Markdown docs under /docs

Open a PR → ensure metadata (last_updated, owners) is filled

🎯 Vision
Steward aims to become the developer knowledge layer — available in chat, docs, and IDEs — helping engineers learn faster, code smarter, and build with confidence.

⚠️ Note
Do not commit:

data/chroma/ (auto-generated)

.env (contains secrets)

Use .env.example as a safe template for contributors.# 🧠 Steward — AI Onboarding Copilot for Engineers

🚀 **Steward** is an **AI-powered onboarding assistant** for developers.  
It helps new and existing engineers ramp up faster by answering questions, guiding setup, and surfacing knowledge directly from your **codebase and documentation**.

---

## ✨ What Steward Does

- 🔍 **Answers developer questions** with real context from your code and docs.  
- 📖 **Guides onboarding** with setup walkthroughs and first-PR workflows.  
- 🛠️ **Provides runbooks** for deployments and incident response.  
- 📎 **Cites sources** (files, paths, commits) so answers are verifiable.  
- 🔑 **Respects access control** using GitHub SSO (planned).  

---

## 📦 Tech Overview

| Layer | Technology | Purpose |
|-------|-------------|----------|
| **Backend** | FastAPI (Python) | REST API for ingestion & querying |
| **Frontend** | React (Next.js) | Chat-like interface for interacting with Steward |
| **Vector DB** | Chroma | Stores embeddings of your code & docs |
| **AI Model** | OpenAI GPT-4o / GPT-4-Turbo | Reasoning, summarization & answering |
| **Auth (Planned)** | GitHub SSO | Role-based access to company repos |

---

## 🚧 Roadmap (MVP)

- ✅ Ingestion pipeline: Markdown → embeddings → vector DB  
- ✅ `/api/query` endpoint: RAG-powered answers  
- ⚙️ Minimal chat UI with source links  
- 🔐 GitHub SSO integration  
- 🧾 Spec Drift Detection *(planned)* — detect mismatches between docs and code  

---

## 📂 Repo Structure

steward-backend/
│
├── app/
│ ├── api/ # API routes (query, health)
│ ├── core/ # RAG engine + ingestion logic
│ └── models/ # Schemas / dataclasses
│
├── data/
│ └── chroma/ # Auto-generated embeddings (ignored in Git)
│
├── requirements.txt
├── main.py # FastAPI entrypoint
├── .env.example # Example environment config
└── README.md

yaml
Copy code

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Steward.git
cd Steward/steward-backend
2️⃣ Create and Activate a Virtual Environment
bash
Copy code
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Configure Environment
bash
Copy code
cp .env.example .env
Edit .env and fill in:

bash
Copy code
OPENAI_API_KEY=sk-your-openai-key
CHROMA_PERSIST_DIR=data/chroma
APP_ENV=dev
PORT=8000
5️⃣ Build the Knowledge Base
bash
Copy code
python app/core/ingest.py
This parses your Python files (and Markdown docs, if any) → generates embeddings → stores them in data/chroma.

Expected output:

csharp
Copy code
✅ Steward knowledge base built successfully!
6️⃣ Run the API
bash
Copy code
uvicorn main:app --reload
7️⃣ Test Query Endpoint
bash
Copy code
curl -X POST "http://127.0.0.1:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does this project do?"}'
8️⃣ Health Check
bash
Copy code
curl http://127.0.0.1:8000/api/health
Expected:

json
Copy code
{
  "status": "ok",
  "message": "✅ OpenAI API key is valid.",
  "model_detected": "gpt-4o"
}
🧠 How Steward Works
Steward uses Retrieval-Augmented Generation (RAG) to connect your docs and code to an intelligent assistant.

mermaid
Copy code
flowchart TD
    A[Ingestion] -->|Embeds Markdown & Code| B[Vector DB (Chroma)]
    B -->|Retrieves Context| C[LLM (GPT-4o)]
    C -->|Generates Answer + Citations| D[Steward API]
    D -->|Served to User| E[Chat UI / CLI / IDE Plugin]
🔍 Process Overview
Ingest: Parses .py and .md files → creates embeddings → stores in Chroma.

Query: User asks a question → system retrieves relevant chunks → sends to GPT-4o.

Respond: GPT-4o generates a contextual, sourced answer.

Example:

“How do I deploy staging?”
→ Steward: “Run deploy_staging.sh (source: /docs/runbooks/deployments.md).”

🤝 Contributing
Fork the repo

Add or update Markdown docs under /docs

Open a PR → ensure metadata (last_updated, owners) is filled

🎯 Vision
Steward aims to become the developer knowledge layer — available in chat, docs, and IDEs — helping engineers learn faster, code smarter, and build with confidence.

⚠️ Note
Do not commit:

data/chroma/ (auto-generated)

.env (contains secrets)

Use .env.example as a safe template for contributors.# 🧠 Steward — AI Onboarding Copilot for Engineers

🚀 **Steward** is an **AI-powered onboarding assistant** for developers.  
It helps new and existing engineers ramp up faster by answering questions, guiding setup, and surfacing knowledge directly from your **codebase and documentation**.

---

## ✨ What Steward Does

- 🔍 **Answers developer questions** with real context from your code and docs.  
- 📖 **Guides onboarding** with setup walkthroughs and first-PR workflows.  
- 🛠️ **Provides runbooks** for deployments and incident response.  
- 📎 **Cites sources** (files, paths, commits) so answers are verifiable.  
- 🔑 **Respects access control** using GitHub SSO (planned).  

---

## 📦 Tech Overview

| Layer | Technology | Purpose |
|-------|-------------|----------|
| **Backend** | FastAPI (Python) | REST API for ingestion & querying |
| **Frontend** | React (Next.js) | Chat-like interface for interacting with Steward |
| **Vector DB** | Chroma | Stores embeddings of your code & docs |
| **AI Model** | OpenAI GPT-4o / GPT-4-Turbo | Reasoning, summarization & answering |
| **Auth (Planned)** | GitHub SSO | Role-based access to company repos |

---

## 🚧 Roadmap (MVP)

- ✅ Ingestion pipeline: Markdown → embeddings → vector DB  
- ✅ `/api/query` endpoint: RAG-powered answers  
- ⚙️ Minimal chat UI with source links  
- 🔐 GitHub SSO integration  
- 🧾 Spec Drift Detection *(planned)* — detect mismatches between docs and code  

---

## 📂 Repo Structure

steward-backend/
│
├── app/
│ ├── api/ # API routes (query, health)
│ ├── core/ # RAG engine + ingestion logic
│ └── models/ # Schemas / dataclasses
│
├── data/
│ └── chroma/ # Auto-generated embeddings (ignored in Git)
│
├── requirements.txt
├── main.py # FastAPI entrypoint
├── .env.example # Example environment config
└── README.md

yaml
Copy code

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Steward.git
cd Steward/steward-backend
2️⃣ Create and Activate a Virtual Environment
bash
Copy code
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Configure Environment
bash
Copy code
cp .env.example .env
Edit .env and fill in:

bash
Copy code
OPENAI_API_KEY=sk-your-openai-key
CHROMA_PERSIST_DIR=data/chroma
APP_ENV=dev
PORT=8000
5️⃣ Build the Knowledge Base
bash
Copy code
python app/core/ingest.py
This parses your Python files (and Markdown docs, if any) → generates embeddings → stores them in data/chroma.

Expected output:

csharp
Copy code
✅ Steward knowledge base built successfully!
6️⃣ Run the API
bash
Copy code
uvicorn main:app --reload
7️⃣ Test Query Endpoint
bash
Copy code
curl -X POST "http://127.0.0.1:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does this project do?"}'
8️⃣ Health Check
bash
Copy code
curl http://127.0.0.1:8000/api/health
Expected:

json
Copy code
{
  "status": "ok",
  "message": "✅ OpenAI API key is valid.",
  "model_detected": "gpt-4o"
}
🧠 How Steward Works
Steward uses Retrieval-Augmented Generation (RAG) to connect your docs and code to an intelligent assistant.

mermaid
Copy code
flowchart TD
    A[Ingestion] -->|Embeds Markdown & Code| B[Vector DB (Chroma)]
    B -->|Retrieves Context| C[LLM (GPT-4o)]
    C -->|Generates Answer + Citations| D[Steward API]
    D -->|Served to User| E[Chat UI / CLI / IDE Plugin]
🔍 Process Overview
Ingest: Parses .py and .md files → creates embeddings → stores in Chroma.

Query: User asks a question → system retrieves relevant chunks → sends to GPT-4o.

Respond: GPT-4o generates a contextual, sourced answer.

Example:

“How do I deploy staging?”
→ Steward: “Run deploy_staging.sh (source: /docs/runbooks/deployments.md).”

🤝 Contributing
Fork the repo

Add or update Markdown docs under /docs

Open a PR → ensure metadata (last_updated, owners) is filled

🎯 Vision
Steward aims to become the developer knowledge layer — available in chat, docs, and IDEs — helping engineers learn faster, code smarter, and build with confidence.

⚠️ Note
Do not commit:

data/chroma/ (auto-generated)

.env (contains secrets)

Use .env.example as a safe template for contributors.# 🧠 Steward — AI Onboarding Copilot for Engineers

🚀 **Steward** is an **AI-powered onboarding assistant** for developers.  
It helps new and existing engineers ramp up faster by answering questions, guiding setup, and surfacing knowledge directly from your **codebase and documentation**.

---

## ✨ What Steward Does

- 🔍 **Answers developer questions** with real context from your code and docs.  
- 📖 **Guides onboarding** with setup walkthroughs and first-PR workflows.  
- 🛠️ **Provides runbooks** for deployments and incident response.  
- 📎 **Cites sources** (files, paths, commits) so answers are verifiable.  
- 🔑 **Respects access control** using GitHub SSO (planned).  

---

## 📦 Tech Overview

| Layer | Technology | Purpose |
|-------|-------------|----------|
| **Backend** | FastAPI (Python) | REST API for ingestion & querying |
| **Frontend** | React (Next.js) | Chat-like interface for interacting with Steward |
| **Vector DB** | Chroma | Stores embeddings of your code & docs |
| **AI Model** | OpenAI GPT-4o / GPT-4-Turbo | Reasoning, summarization & answering |
| **Auth (Planned)** | GitHub SSO | Role-based access to company repos |

---

## 🚧 Roadmap (MVP)

- ✅ Ingestion pipeline: Markdown → embeddings → vector DB  
- ✅ `/api/query` endpoint: RAG-powered answers  
- ⚙️ Minimal chat UI with source links  
- 🔐 GitHub SSO integration  
- 🧾 Spec Drift Detection *(planned)* — detect mismatches between docs and code  

---

## 📂 Repo Structure

steward-backend/
│
├── app/
│ ├── api/ # API routes (query, health)
│ ├── core/ # RAG engine + ingestion logic
│ └── models/ # Schemas / dataclasses
│
├── data/
│ └── chroma/ # Auto-generated embeddings (ignored in Git)
│
├── requirements.txt
├── main.py # FastAPI entrypoint
├── .env.example # Example environment config
└── README.md

yaml
Copy code

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Steward.git
cd Steward/steward-backend
2️⃣ Create and Activate a Virtual Environment
bash
Copy code
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Configure Environment
bash
Copy code
cp .env.example .env
Edit .env and fill in:

bash
Copy code
OPENAI_API_KEY=sk-your-openai-key
CHROMA_PERSIST_DIR=data/chroma
APP_ENV=dev
PORT=8000
5️⃣ Build the Knowledge Base
bash
Copy code
python app/core/ingest.py
This parses your Python files (and Markdown docs, if any) → generates embeddings → stores them in data/chroma.

Expected output:

csharp
Copy code
✅ Steward knowledge base built successfully!
6️⃣ Run the API
bash
Copy code
uvicorn main:app --reload
7️⃣ Test Query Endpoint
bash
Copy code
curl -X POST "http://127.0.0.1:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does this project do?"}'
8️⃣ Health Check
bash
Copy code
curl http://127.0.0.1:8000/api/health
Expected:

json
Copy code
{
  "status": "ok",
  "message": "✅ OpenAI API key is valid.",
  "model_detected": "gpt-4o"
}
🧠 How Steward Works
Steward uses Retrieval-Augmented Generation (RAG) to connect your docs and code to an intelligent assistant.

mermaid
Copy code
flowchart TD
    A[Ingestion] -->|Embeds Markdown & Code| B[Vector DB (Chroma)]
    B -->|Retrieves Context| C[LLM (GPT-4o)]
    C -->|Generates Answer + Citations| D[Steward API]
    D -->|Served to User| E[Chat UI / CLI / IDE Plugin]
🔍 Process Overview
Ingest: Parses .py and .md files → creates embeddings → stores in Chroma.

Query: User asks a question → system retrieves relevant chunks → sends to GPT-4o.

Respond: GPT-4o generates a contextual, sourced answer.

Example:

“How do I deploy staging?”
→ Steward: “Run deploy_staging.sh (source: /docs/runbooks/deployments.md).”

🤝 Contributing
Fork the repo

Add or update Markdown docs under /docs

Open a PR → ensure metadata (last_updated, owners) is filled

🎯 Vision
Steward aims to become the developer knowledge layer — available in chat, docs, and IDEs — helping engineers learn faster, code smarter, and build with confidence.

⚠️ Note
Do not commit:

data/chroma/ (auto-generated)

.env (contains secrets)

Use .env.example as a safe template for contributors.# 🧠 Steward — AI Onboarding Copilot for Engineers

🚀 **Steward** is an **AI-powered onboarding assistant** for developers.  
It helps new and existing engineers ramp up faster by answering questions, guiding setup, and surfacing knowledge directly from your **codebase and documentation**.

---

## ✨ What Steward Does

- 🔍 **Answers developer questions** with real context from your code and docs.  
- 📖 **Guides onboarding** with setup walkthroughs and first-PR workflows.  
- 🛠️ **Provides runbooks** for deployments and incident response.  
- 📎 **Cites sources** (files, paths, commits) so answers are verifiable.  
- 🔑 **Respects access control** using GitHub SSO (planned).  

---

## 📦 Tech Overview

| Layer | Technology | Purpose |
|-------|-------------|----------|
| **Backend** | FastAPI (Python) | REST API for ingestion & querying |
| **Frontend** | React (Next.js) | Chat-like interface for interacting with Steward |
| **Vector DB** | Chroma | Stores embeddings of your code & docs |
| **AI Model** | OpenAI GPT-4o / GPT-4-Turbo | Reasoning, summarization & answering |
| **Auth (Planned)** | GitHub SSO | Role-based access to company repos |

---

## 🚧 Roadmap (MVP)

- ✅ Ingestion pipeline: Markdown → embeddings → vector DB  
- ✅ `/api/query` endpoint: RAG-powered answers  
- ⚙️ Minimal chat UI with source links  
- 🔐 GitHub SSO integration  
- 🧾 Spec Drift Detection *(planned)* — detect mismatches between docs and code  

---

## 📂 Repo Structure

steward-backend/
│
├── app/
│ ├── api/ # API routes (query, health)
│ ├── core/ # RAG engine + ingestion logic
│ └── models/ # Schemas / dataclasses
│
├── data/
│ └── chroma/ # Auto-generated embeddings (ignored in Git)
│
├── requirements.txt
├── main.py # FastAPI entrypoint
├── .env.example # Example environment config
└── README.md

yaml
Copy code

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Steward.git
cd Steward/steward-backend
2️⃣ Create and Activate a Virtual Environment
bash
Copy code
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Configure Environment
bash
Copy code
cp .env.example .env
Edit .env and fill in:

bash
Copy code
OPENAI_API_KEY=sk-your-openai-key
CHROMA_PERSIST_DIR=data/chroma
APP_ENV=dev
PORT=8000
5️⃣ Build the Knowledge Base
bash
Copy code
python app/core/ingest.py
This parses your Python files (and Markdown docs, if any) → generates embeddings → stores them in data/chroma.

Expected output:

csharp
Copy code
✅ Steward knowledge base built successfully!
6️⃣ Run the API
bash
Copy code
uvicorn main:app --reload
7️⃣ Test Query Endpoint
bash
Copy code
curl -X POST "http://127.0.0.1:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does this project do?"}'
8️⃣ Health Check
bash
Copy code
curl http://127.0.0.1:8000/api/health
Expected:

json
Copy code
{
  "status": "ok",
  "message": "✅ OpenAI API key is valid.",
  "model_detected": "gpt-4o"
}
🧠 How Steward Works
Steward uses Retrieval-Augmented Generation (RAG) to connect your docs and code to an intelligent assistant.

mermaid
Copy code
flowchart TD
    A[Ingestion] -->|Embeds Markdown & Code| B[Vector DB (Chroma)]
    B -->|Retrieves Context| C[LLM (GPT-4o)]
    C -->|Generates Answer + Citations| D[Steward API]
    D -->|Served to User| E[Chat UI / CLI / IDE Plugin]
🔍 Process Overview
Ingest: Parses .py and .md files → creates embeddings → stores in Chroma.

Query: User asks a question → system retrieves relevant chunks → sends to GPT-4o.

Respond: GPT-4o generates a contextual, sourced answer.

Example:

“How do I deploy staging?”
→ Steward: “Run deploy_staging.sh (source: /docs/runbooks/deployments.md).”

🤝 Contributing
Fork the repo

Add or update Markdown docs under /docs

Open a PR → ensure metadata (last_updated, owners) is filled

🎯 Vision
Steward aims to become the developer knowledge layer — available in chat, docs, and IDEs — helping engineers learn faster, code smarter, and build with confidence.

⚠️ Note
Do not commit:

data/chroma/ (auto-generated)

.env (contains secrets)

Use .env.example as a safe template for contributors.