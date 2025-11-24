from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency import get_postgres_db, get_mongo_db
from schemas.analyze_schema import AnalyzeInput, AnalyzeOutput, RetrievedKnowledge
from services.analyze_service import run_analyze_pipeline

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeOutput)
def analyze_text(
    payload: AnalyzeInput,
    db: Session = Depends(get_postgres_db),
    mongo = Depends(get_mongo_db)
):
    """
    /graph/analyze endpoint:
    - Validates input
    - Retrieves similar stored knowledge
    - Uses LLM to synthesize insights, contradictions, and missing points
    """
    result = run_analyze_pipeline(payload.text, db, mongo)
    
    return {
        "insights": result.insights["insights"],
        "related": [
            {
                "topic": r.get("topic"),
                "summary": r.get("summary"),
                "similarity": r.get("similarity"),
            } for r in result.get("related", [])
        ],
        "contradictions": result.insights.get("contradictions", []),
        "missing_points": result.insights.get("missing_points", []),
    }