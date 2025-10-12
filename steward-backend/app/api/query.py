from fastapi import APIRouter
from app.core.rag_engine import answer_query

router = APIRouter()

@router.post("/")
async def query_steward(payload: dict):
    question = payload.get("question", "").strip()
    if not question:
        return {"error": "Missing 'question' in request."}

    try:
        result = answer_query(question)
        return {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
            "mode": "live"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Query failed: {str(e)}"
        }