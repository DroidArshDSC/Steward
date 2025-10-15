# Run Steward Locally

## Prerequisites
- Python 3.10+
- Virtual environment (venv or conda)
- OpenAI API key

## Setup
```bash
git clone https://github.com/DroidArshDSC/Steward.git
cd steward-backend
cp .env.example .env
# Add your keys to .env
pip install -r requirements.txt
```

---

## Run
uvicorn main:app --reload

### 🧠 **`docs/how-to/ingest-data.md`**

# Ingest New Data into Steward

## Purpose
Add new documentation or knowledge files to the vector store.

## Steps
1. Place your Markdown files under `/data/docs` (create if missing).
2. Run the ingestion script:
   ```bash
        python app/core/ingest.py
   ```
3. The script will:
- Embed text via OpenAI
- Store vectors in /data/chroma
- Restart the app for updated retrieval.

Notes
- You can tweak embedding model in rag_engine.py.
- Future: automate ingestion via GitHub webhook.

