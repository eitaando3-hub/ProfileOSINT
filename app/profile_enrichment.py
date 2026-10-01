"""Profile manager enhancements for search history, image references, and data persistence."""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ProfileManager:
    # existing functionality preserved; this adds convenience methods for external data
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) if hasattr(super(), "__init__") else None
        self.logger = logging.getLogger(__name__)

    def add_web_search_result(self, profile_id: str, query: str, results: List[Dict[str, Any]]) -> bool:
        try:
            profile = self.load_profile(profile_id)
            if not profile:
                return False
            profile.setdefault("search_history", []).append({
                "kind": "web_search",
                "query": query,
                "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                "results": results,
            })
            return self.save_profile(profile_id, profile)
        except Exception:
            logger.exception("Could not save web search result")
            return False

    def add_image_reference(self, profile_id: str, image_url: str, source: str = "profile") -> bool:
        try:
            profile = self.load_profile(profile_id)
            if not profile:
                return False
            profile.setdefault("image_references", []).append({
                "url": image_url,
                "source": source,
                "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            })
            return self.save_profile(profile_id, profile)
        except Exception:
            logger.exception("Could not save image reference")
            return False

    def add_search_history_entry(self, profile_id: str, kind: str, payload: Dict[str, Any]) -> bool:
        try:
            profile = self.load_profile(profile_id)
            if not profile:
                return False
            profile.setdefault("search_history", []).append({"kind": kind, "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z", **payload})
            return self.save_profile(profile_id, profile)
        except Exception:
            logger.exception("Could not append search history entry")
            return False
