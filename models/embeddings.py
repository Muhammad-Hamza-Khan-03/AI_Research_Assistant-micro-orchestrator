from typing import List, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class MongoObjectId(ObjectId):
    """For Pydantic compatibility."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return ObjectId(v)


class EmbeddingModel(BaseModel):
    id: MongoObjectId | None = Field(alias="_id", default=None)
    research_id: int 
    embedding: List[float]
    topic: str
    created_at: Any = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
