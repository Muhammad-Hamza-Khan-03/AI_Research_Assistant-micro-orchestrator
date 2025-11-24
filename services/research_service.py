# app/services/research_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Dict, Any, List

from tools.web_search_tool import search
from tools.s3_tool import upload_text_to_s3
from tools.embeddings import create_and_store_embedding
from tools.cache import cache_set, cache_get
from models.research import Research
from schemas.research_schema import ResearchInput

# -----------------------------------
# LangChain LLM Integration
# -----------------------------------

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import json


def llm_summarize(text: str) -> Dict[str, Any]:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )

    prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert AI research assistant. Summarize content and extract tags."
    ),
    (
        "user",
        """
    Summarize the following research text into a clear, structured summary.
    Extract 5–10 short tags (keywords).
    
    Return ONLY valid JSON:
    {{
      "summary": "...",
      "tags": ["...", "..."]
    }}
    
    TEXT:
    {text}
    """
        ),
    ])


    chain = prompt | llm
    response = chain.invoke({"text": text})
    content = response.content.strip()

    try:
        return json.loads(content)
    except Exception:
        # fallback: return whole text as summary
        return {"summary": content, "tags": []}


# -----------------------------------
# Research Pipeline
# -----------------------------------
def run_research_pipeline(payload: ResearchInput, db: Session, mongo_db):
    topic = payload.topic.strip()

    # 1. Check cache
    cached = cache_get(f"research:{topic}")
    if cached:
        return {**cached, "cached": True}

    # 2. Web search
    results = search(topic, num=5)
    if not results:
        raise HTTPException(500, "Search failed.")

    raw_text = "\n\n".join(
        f"TITLE: {r['title']}\nSNIPPET: {r['snippet']}\nLINK: {r['link']}"
        for r in results
    )

    # 3. LLM summary using LangChain
    summary_data = llm_summarize(raw_text)
    summary = summary_data.get("summary", "")
    tags = summary_data.get("tags", [])
    tags_str = ",".join(tags)

    # 4. Save metadata to Postgres
    research_obj = Research(topic=topic, summary=summary, tags=tags_str)
    db.add(research_obj)
    db.commit()
    db.refresh(research_obj)

    # 5. Upload raw research text to S3
    key = f"research/{research_obj.id}_{topic.replace(' ', '_')}.txt"
    s3_url = upload_text_to_s3(raw_text, key)
    research_obj.s3_url = s3_url
    db.commit()
    db.refresh(research_obj)

    # 6. Generate & store embedding
    mongo_coll = mongo_db["embeddings"]
    create_and_store_embedding(
        mongo_coll,
        research_id=research_obj.id,
        topic=topic,
        text=summary,
    )

    # 7. Cache final output
    result = {
        "id": research_obj.id,
        "topic": topic,
        "summary": summary,
        "tags": tags,
        "s3_url": s3_url,
        "created_at": research_obj.created_at.isoformat(),
    }

    cache_set(f"research:{topic}", result, ttl_seconds=3600)

    return result
