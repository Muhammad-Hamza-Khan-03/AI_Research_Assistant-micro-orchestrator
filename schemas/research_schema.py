from pydantic import BaseModel
from typing import List, Optional


class ResearchInput(BaseModel):
    topic: str


class ResearchOutput(BaseModel):
    id: int
    topic: str
    summary: str
    tags: Optional[List[str]] = None
    s3_url: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True
