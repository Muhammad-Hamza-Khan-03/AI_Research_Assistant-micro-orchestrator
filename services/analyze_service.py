from __future__ import annotations
from typing import List, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import HTTPException

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from tools.embeddings import embed_texts_openai
from tools.db_retrieval_tool import get_related_research
from tools.cache import cache_get, cache_set

import hashlib
import datetime
import json
import logging

logger = logging.getLogger(__name__)


# ----------------------------
# STATE SHAPE for LangGraph
# ----------------------------
class AnalyzeState(BaseModel):
    text: str
    normalized: str | None = None
    embedding: List[float] | None = None
    related: List[Dict[str, Any]] | None = None
    insights: Dict[str, Any] | None = None


# --------------------------------------------------
# NODE 1: ValidatorNode — check input validity
# --------------------------------------------------
def validator_node(state: AnalyzeState) -> AnalyzeState:
    if not state.text or not state.text.strip():
        raise HTTPException(status_code=400, detail="Empty text provided.")
    return state


# --------------------------------------------------
# NODE 2: ContextExpansionNode — normalize text
# --------------------------------------------------
def expand_context_node(state: AnalyzeState) -> AnalyzeState:
    normalized = " ".join(state.text.strip().split())
    state.normalized = normalized
    return state


# --------------------------------------------------
# NODE 3: EmbeddingNode — embed normalized text
# --------------------------------------------------
def embedding_node(state: AnalyzeState) -> AnalyzeState:
    vec = embed_texts_openai([state.normalized], model="text-embedding-3-large")[0]
    state.embedding = vec
    return state


# --------------------------------------------------
# NODE 4: RetrievalNode — get related research
# --------------------------------------------------
def make_retrieval_node(db: Session, mongo_db):
    def retrieval_node(state: AnalyzeState) -> AnalyzeState:
        embeddings_coll = mongo_db["embeddings"]
        related = get_related_research(
            db=db,
            mongo_coll=embeddings_coll,
            embedding_vector=state.embedding,
            top_k=5
        )
        state.related = related
        return state
    return retrieval_node


# --------------------------------------------------
# NODE 5: SynthesisNode — generate insights via LLM
# --------------------------------------------------
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import json
import logging

logger = logging.getLogger(__name__)

def synthesis_node(state):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0
    )

    # Build context from related docs
    if state.related:
        related_block = "\n\n".join(
            f"Topic: {r['topic']}\nSummary: {r['summary']}\nSimilarity: {r['similarity']}"
            for r in state.related
        )
    else:
        related_block = "No related documents found."

    # Prepare the prompt
    prompt_text = f"""
    You are an expert AI analyst. Compare USER_TEXT with RELATED_KNOWLEDGE.
    
    Return ONLY valid JSON with fields:
    - insights
    - contradictions
    - missing_points
    - related_summary
    
    USER_TEXT:
    {state.normalized}
    
    RELATED_KNOWLEDGE:
    {related_block}
    """

    try:
        # Call the LLM correctly
        response = llm([HumanMessage(content=prompt_text)])
        raw = response.content
        parsed = json.loads(raw)
    except Exception as e:
        logger.warning("LLM returned non-JSON or failed: %s", e)
        parsed = {
            "insights": raw if 'raw' in locals() else "",
            "contradictions": [],
            "missing_points": [],
            "related_summary": related_block
        }

    state.insights = parsed
    return state


# --------------------------------------------------
# BUILD THE LANGGRAPH
# --------------------------------------------------
def build_graph(db: Session, mongo_db):
    graph = StateGraph(AnalyzeState)

    # Add nodes
    graph.add_node("validate", validator_node)
    graph.add_node("normalize", expand_context_node)
    graph.add_node("embed", embedding_node)
    graph.add_node("retrieve", make_retrieval_node(db, mongo_db))
    graph.add_node("synthesize", synthesis_node)

    # Set entry
    graph.set_entry_point("validate")

    # Wire transitions
    graph.add_edge("validate", "normalize")
    graph.add_edge("normalize", "embed")
    graph.add_edge("embed", "retrieve")
    graph.add_edge("retrieve", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()


# --------------------------------------------------
# PUBLIC PIPELINE FUNCTION
# --------------------------------------------------
def run_analyze_pipeline(
    text: str,
    db: Session,
    mongo_db,
    use_cache: bool = True
) -> Dict[str, Any]:

    # Normalize early to build stable cache key
    normalized = " ".join(text.strip().split())
    cache_key = "analyze:" + hashlib.sha1(normalized.encode()).hexdigest()

    if use_cache:
        cached = cache_get(cache_key)
        if cached:
            return {**cached, "cached": True}

    # Build graph instance
    app = build_graph(db, mongo_db)

    # Execute graph
    final_state: AnalyzeState = app.invoke(AnalyzeState(text=text))

    # Format API response
    result = {
        "insights": final_state.insights["insights"],
        "related": [
            {
                "topic": r["topic"],
                "summary": r["summary"],
                "similarity": r["similarity"],
            }
            for r in (final_state.related or [])
        ],
        "contradictions": final_state.insights.get("contradictions", []),
        "missing_points": final_state.insights.get("missing_points", []),
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

    cache_set(cache_key, result, ttl_seconds=3600)

    return result
