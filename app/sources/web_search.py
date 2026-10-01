"""Web search integration for profile enrichment using generic search endpoints."""
import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


class WebSearchClient:
    """A minimal web search client used for enrichment and external lookups."""

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key or None
        self.endpoint = endpoint or "https://api.github.com/search/users"

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []
        params = quote_plus(query)
        url = f"{self.endpoint}?q={params}&per_page={max(1, min(limit, 20))}"
        try:
            headers = {"Accept": "application/json", "User-Agent": "ProfileOSINT/1.0"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            req = Request(url, headers=headers)
            with urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
            items = payload.get("items", []) if isinstance(payload, dict) else []
            return [
                {
                    "name": item.get("login") or item.get("name") or "Unknown",
                    "url": item.get("html_url") or item.get("url") or "",
                    "score": item.get("score"),
                    "source": self.endpoint,
                }
                for item in items[:limit]
            ]
        except Exception:
            logger.exception("Web search failed")
            return []
