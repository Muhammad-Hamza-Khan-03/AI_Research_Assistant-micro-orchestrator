import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import redis
import boto3

load_dotenv()  # Load from .env file


class Settings:
    def __init__(self):
        # ---- PostgreSQL ----
        self.POSTGRES_URI = os.getenv("POSTGRES_URI")

        # ---- MongoDB ----
        self.MONGO_URI = os.getenv("MONGO_URI")
        self.MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "research_db")

        # ---- Redis ----
        self.REDIS_URI = os.getenv("REDIS_URI")

        # ---- AWS ----
        self.AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
        self.AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
        self.AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

        # ---- LLM API ----
        self.LLM_API_KEY = os.getenv("LLM_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


settings = Settings()

# -----------------------------
# PostgreSQL Engine + Session
# -----------------------------
engine = create_engine(
    settings.POSTGRES_URI,
    future=True,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -----------------------------
# MongoDB Client
# -----------------------------
mongo_client = MongoClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

# -----------------------------
# Redis Client (SYNC)
# -----------------------------
redis_client = redis.from_url(settings.REDIS_URI)

# -----------------------------
# AWS S3 Client
# -----------------------------
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY
)
