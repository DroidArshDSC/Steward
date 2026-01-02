from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.query import router as query_router
from app.api.health import router as health_router
from app.api.ingest import router as ingest_router
from app.api.suggest import router as suggest_router
from app.api import metrics

app = FastAPI(title="Steward API (Mock Mode)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Routers ===
app.include_router(ingest_router, prefix="/api/ingest", tags=["Ingestion"])
app.include_router(query_router, prefix="/api/query", tags=["Query"])
app.include_router(suggest_router, prefix="/api/suggest", tags=["Suggest"])
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(metrics.router)
# ========================

@app.get("/")
def root():
    return {"message": "Steward backend is running"}
