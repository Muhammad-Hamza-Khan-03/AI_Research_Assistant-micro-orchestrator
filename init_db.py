from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.research import Base  # PostgreSQL model
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# PostgreSQL Setup
# ----------------------------
POSTGRES_URI = os.getenv("POSTGRES_URI")
engine = create_engine(POSTGRES_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print("Creating Postgres tables...")
Base.metadata.create_all(bind=engine)
print("Postgres tables created successfully.")

# ----------------------------
# MongoDB Setup
# ----------------------------
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "research_db")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Create embeddings collection if not exists
if "embeddings" not in db.list_collection_names():
    db.create_collection("embeddings")
    print("MongoDB collection 'embeddings' created.")
else:
    print("MongoDB collection 'embeddings' already exists.")

print("Database initialization complete.")
