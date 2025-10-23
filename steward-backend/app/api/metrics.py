from fastapi import APIRouter
from app.core.rag_engine import _engine

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/")
def get_metrics():
    """
    Returns basic performance stats from the RAG engine.
    Example:
    {
        "queries": 27,
        "cache_hits": 12,
        "avg_latency_s": 2.41
    }
    """
    return _engine.get_metrics()
