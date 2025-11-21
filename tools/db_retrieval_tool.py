from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from pymongo.collection import Collection
from models.research import Research  # SQLAlchemy model
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


def get_recent_research(db: Session, limit: int = 10) -> List[Research]:
    """
    Return recent Research SQLAlchemy objects ordered by created_at desc.
    """
    return db.query(Research).order_by(Research.created_at.desc()).limit(limit).all()


def get_research_by_id(db: Session, research_id: int) -> Optional[Research]:
    return db.query(Research).filter(Research.id == research_id).first()


def find_similar_embeddings(mongo_coll: Collection, embedding_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Basic similarity retrieval using cosine similarity calculated in Python.
    For production use, use a vector DB (Milvus, Pinecone, or MongoDB Atlas Vector Search).
    mongo_coll is a pymongo Collection instance (e.g., mongo_db['embeddings'])
    Each document in collection expected to have fields: 'research_id', 'embedding', 'topic', 'created_at'
    """
    import math

    def dot(a, b):
        return sum(x*y for x, y in zip(a, b))

    def norm(a):
        return math.sqrt(sum(x*x for x in a))

    results = []
    cursor = mongo_coll.find({})
    for doc in cursor:
        vec = doc.get("embedding")
        if not vec:
            continue
        # Ensure same length
        if len(vec) != len(embedding_vector):
            continue
        denom = (norm(vec) * norm(embedding_vector))
        similarity = dot(vec, embedding_vector) / denom if denom != 0 else 0.0
        results.append({
            "research_id": doc.get("research_id"),
            "topic": doc.get("topic"),
            "similarity": float(similarity),
            "_id": str(doc.get("_id"))
        })

    # sort by similarity descending
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


def get_related_research(db: Session, mongo_coll: Collection, embedding_vector: List[float], top_k: int = 5):
    """
    Combines vector similarity results with Postgres metadata. Returns list of dicts.
    """
    sims = find_similar_embeddings(mongo_coll, embedding_vector, top_k=top_k)
    related = []
    for s in sims:
        research = get_research_by_id(db, s["research_id"])
        if research:
            related.append({
                "research_id": research.id,
                "topic": research.topic,
                "summary": research.summary,
                "similarity": s["similarity"],
                "s3_url": research.s3_url,
                "created_at": research.created_at.isoformat() if research.created_at else None
            })
    return related
