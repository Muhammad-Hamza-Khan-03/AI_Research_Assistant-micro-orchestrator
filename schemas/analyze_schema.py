from pydantic import BaseModel
from typing import List, Optional, Any


class AnalyzeInput(BaseModel):
    text: str


class RetrievedKnowledge(BaseModel):
    topic: str
    summary: str
    similarity: float


class AnalyzeOutput(BaseModel):
    insights: str
    related: List[RetrievedKnowledge]
    contradictions: Optional[List[str]] = None
    missing_points: Optional[List[str]] = None

    class Config:
        orm_mode = True
