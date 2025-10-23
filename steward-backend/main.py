from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.query import router as query_router
from app.api.health import router as health_router
from app.api import metrics

app = FastAPI(title="Steward API (Mock Mode)")

# === CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict later: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ========================

# === Routers ===
app.include_router(query_router, prefix="/api/query", tags=["Query"])
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(metrics.router)
# ========================

# Optional: root redirect for quick sanity check
@app.get("/")
def root():
    return {"message": "Steward backend is running"}
