import os
import logging
from typing import List, Optional, Dict, Any
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")


def embed_texts_openai(texts: List[str], model="text-embedding-3-large"):
    embedder = OpenAIEmbeddings(model=model)
    return embedder.embed_documents(texts)


def create_and_store_embedding(mongo_coll, research_id: int, topic: str, text: str, model: str = "text-embedding-3-large") -> Dict[str, Any]:
    """
    Creates embedding for `text` and stores a document in mongo_coll with fields:
    { research_id, topic, embedding, text, created_at }
    Returns the inserted document (with _id).
    """
    embeddings = embed_texts_openai([text], model=model)
    vec = embeddings[0]
    doc = {
        "research_id": research_id,
        "topic": topic,
        "embedding": vec,
        "text": text,
    }
    res = mongo_coll.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return doc
