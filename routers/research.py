from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency import get_postgres_db, get_mongo_db
from schemas.research_schema import ResearchInput, ResearchOutput
from services.research_service import run_research_pipeline

router = APIRouter()


@router.post("/research", response_model=ResearchOutput)
def research_topic(
    payload: ResearchInput,
    db: Session = Depends(get_postgres_db),
    mongo = Depends(get_mongo_db)
):
    """
    Research pipeline:
    - Web search
    - LLM summary
    - Save to Postgres
    - Save embedding to MongoDB
    - Save raw text to S3
    - Cache in Redis
    """
    result = run_research_pipeline(payload, db, mongo)
    return result
