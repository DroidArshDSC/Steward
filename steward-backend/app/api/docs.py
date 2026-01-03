from fastapi import APIRouter
from app.api.schemas import DocsGenerateRequest, DocsGenerateResponse
from app.core.rag_engine import run_generate_docs

router = APIRouter()


@router.post("/generate", response_model=DocsGenerateResponse)
async def generate_docs(payload: DocsGenerateRequest):
    return run_generate_docs(
        session_id=payload.session_id,
        doc_type=payload.doc_type,
        audience=payload.audience,
        business_context=payload.business_context,
    )
