from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency import (
    get_postgres_db,
    get_mongo_db,
    get_redis_client,
    get_s3_client
)

router = APIRouter()

@router.get("/test")
def test_route(
    db: Session = Depends(get_postgres_db),
    mongo = Depends(get_mongo_db),
    cache = Depends(get_redis_client),
    s3 = Depends(get_s3_client)
):
    return {"status": "ok"}
