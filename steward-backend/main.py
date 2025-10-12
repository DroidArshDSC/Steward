from fastapi import FastAPI
from app.api.query import router as query_router
from app.api.health import router as health_router

app = FastAPI(title="Steward API (Mock Mode)")

app.include_router(query_router, prefix="/api/query", tags=["Query"])
app.include_router(health_router, prefix="/api/health", tags=["Health"])