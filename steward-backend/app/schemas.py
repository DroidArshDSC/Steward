from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class QueryFilters(BaseModel):
    repo: Optional[str] = None
    doc_type: Optional[str] = None       # code | doc
    symbol_type: Optional[str] = None    # api | class | function | method
    language: Optional[str] = None       # python (future-proof)

class QueryRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    filters: Optional[QueryFilters] = None    

class SuggestRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)

class DocsGenerateRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    doc_type: Literal["overview", "architecture", "api", "onboarding"]
    audience: Literal["engineer", "pm", "stakeholder"] = "engineer"
    business_context: Optional[str] = None


class DocsGenerateResponse(BaseModel):
    doc_type: Literal["overview", "architecture", "api", "onboarding"]
    audience: Literal["engineer", "pm", "stakeholder"]
    content: str
    sources: List[str]
    warning: str

class RepoIngestRequest(BaseModel):
    source_type: Literal["zip", "github", "file"]
    repo_name: str
    branch: Optional[str] = "main"
    source: str
    options: Optional[dict] = {}

class RepoIngestResponse(BaseModel):
    job_id: str
    status: str