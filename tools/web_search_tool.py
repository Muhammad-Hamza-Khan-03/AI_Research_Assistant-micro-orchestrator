import os
import logging
from typing import List, Dict, Any
import requests

logger = logging.getLogger(__name__)

# tools/web_search_tool.py
import os
import logging
from typing import List, Dict, Any
from tavily import TavilyClient  # make sure you have tavily installed

logger = logging.getLogger(__name__)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

def tavily_search(query: str, num: int = 5) -> List[Dict[str, Any]]:
    """
    Search using Tavily API.
    Returns a list of dicts: [{'title': ..., 'link': ..., 'snippet': ...}, ...]
    """
    if not TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY missing from environment")
    
    client = TavilyClient(api_key=TAVILY_API_KEY)
    results = client.search(query=query, max_results=num)
    
    # Transform to same format as previous
    transformed = []
    for r in results:
        transformed.append({
            "title": r.get("title", ""),
            "link": r.get("url", ""),
            "snippet": r.get("snippet", ""),
        })
    return transformed

def dummy_search(query: str, num: int = 3) -> List[Dict[str, Any]]:
    return [
        {"title": f"Dummy result {i+1} for {query}", "link": "", "snippet": f"This is a dummy snippet {i+1}."}
        for i in range(num)
    ]

def search(query: str, num: int = 5) -> List[Dict[str, Any]]:
    """
    Unified entrypoint. Uses Tavily if API key configured; else dummy results.
    """
    try:
        if TAVILY_API_KEY:
            return tavily_search(query, num=num)
        else:
            logger.warning("TAVILY_API_KEY not configured — using dummy_search")
            return dummy_search(query, num=min(num, 3))
    except Exception as e:
        logger.exception("Search failed, returning dummy_search: %s", e)
        return dummy_search(query, num=min(num, 3))
