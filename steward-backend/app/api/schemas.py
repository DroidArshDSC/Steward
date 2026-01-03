from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class QueryRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)


class SuggestRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)

class DocsGenerateRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    doc_type: Literal["overview", "architecture", "api", "onboarding"]
    audience: Literal["engineer", "pm", "stakeholder"] = "engineer"
    business_context: Optional[str] = None


class DocsGenerateResponse(BaseModel):
    doc_type: str
    audience: str
    content: str
    sources: List[str]
    warning: str