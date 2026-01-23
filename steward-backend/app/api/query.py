from fastapi import APIRouter, HTTPException
from app.core.rag_engine import run_query
from app.schemas import QueryRequest

router = APIRouter()


@router.post("/")
async def query(payload: QueryRequest):
    question = payload.question.strip()
    session_id = payload.session_id.strip()
    filters = payload.filters

    if not question:
        raise HTTPException(status_code=400, detail="Missing question")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id")

    return run_query(
        question=question,
        session_id=session_id,
        filters=filters,
    )
