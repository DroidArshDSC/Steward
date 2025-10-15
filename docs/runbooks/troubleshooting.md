# Steward Runbook: Troubleshooting

## 1. App Fails to Start
**Error:** `ModuleNotFoundError`  
**Fix:** Run `pip install -r requirements.txt`

## 2. No AI Responses
**Error:** 400 / “API key not provided”  
**Fix:** Check `.env` contains `OPENAI_API_KEY`.

## 3. Chroma Issues
**Error:** Vector store corrupted or missing  
**Fix:** Delete `data/chroma/` and rerun ingestion.

## 4. API Timeout
**Fix:** Reduce retrieval size in `rag_engine.py` or increase FastAPI timeout.

## 5. Debugging Logs
Run with:
```bash
uvicorn main:app --reload --log-level debug
```