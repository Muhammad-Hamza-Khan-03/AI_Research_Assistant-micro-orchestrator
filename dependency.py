from config import SessionLocal, mongo_db, redis_client, s3_client
from sqlalchemy.orm import Session
from fastapi import Depends


# -----------------------------
# PostgreSQL Dependency
# -----------------------------
def get_postgres_db() -> Session: # type: ignore
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# MongoDB Dependency
# -----------------------------
def get_mongo_db():
    return mongo_db


# -----------------------------
# Redis Dependency
# -----------------------------
def get_redis_client():
    return redis_client


# -----------------------------
# AWS S3 Client Dependency
# -----------------------------
def get_s3_client():
    return s3_client
