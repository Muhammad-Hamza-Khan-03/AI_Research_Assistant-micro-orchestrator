from sqlalchemy import Column, Integer, String, Text,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func


Base = declarative_base()

class Research(Base):
    __tablename__ = 'research'

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    tags = Column(String(100), nullable=False)
    s3_url =  Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now())