# app/api/ingest.py

from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.ingestion.repo_ingestor import ingest_repository
from app.schemas import RepoIngestRequest, RepoIngestResponse

router = APIRouter()

@router.post("/ingest", response_model=RepoIngestResponse)
async def ingest_repo(
    req: RepoIngestRequest,
    background_tasks: BackgroundTasks
):
    if req.source_type not in {"zip", "github"}:
        raise HTTPException(status_code=400, detail="Invalid source_type")

    job_id = f"ingest-{req.repo_name}"

    background_tasks.add_task(
        ingest_repository,
        job_id=job_id,
        request=req
    )

    return RepoIngestResponse(
        job_id=job_id,
        status="started"
    )
