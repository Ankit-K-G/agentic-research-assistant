# backend/tools/web_search.py
import time
import logging

logger = logging.getLogger(__name__)

def simple_search_stub(query, max_results=5):
    """
    Placeholder search function.
    Replace or extend this to call SerpAPI/Tavily/generic API.
    """
    logger.info("Running stub search for: %s", query)
    time.sleep(0.3)
    # Return list of dicts with title, url, snippet
    return [
        {"title": f"Result {i+1} for {query}", "url": f"https://example.com/{i+1}", "snippet": f"Snippet {i+1}"}
        for i in range(max_results)
    ]
