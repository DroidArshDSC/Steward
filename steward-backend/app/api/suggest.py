from fastapi import APIRouter, HTTPException
from app.core.rag_engine import run_suggest
from app.api.schemas import SuggestRequest

router = APIRouter()

@router.post("/")
async def suggest(payload: SuggestRequest):
    question = payload.get("question", "").strip()
    session_id = payload.get("session_id")

    if not question:
        raise HTTPException(status_code=400, detail="Missing question")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id")

    return run_suggest(
        question=question,
        session_id=session_id,
    )