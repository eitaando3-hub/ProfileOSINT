"""Core profile manager with search result and contact management."""
import hashlib
import json
import logging
import secrets
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.db.audit_db import log_event
from app.utils.progress import get_progress_tracker

logger = logging.getLogger(__name__)


class ProfileManager:
    def __init__(self, data_dir: str = "app/data"):
        self.profiles_dir = Path(data_dir) / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def hash_string(value: str, salt: Optional[str] = None) -> tuple:
        if salt is None:
            salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((value + salt).encode())
        return f"{salt}${hash_obj.hexdigest()}", salt

    def generate_profile_id(self) -> str:
        existing = []
        if self.profiles_dir.exists():
            for d in self.profiles_dir.iterdir():
                if d.is_dir() and d.name.startswith("profile_"):
                    try:
                        num = int(d.name.split("_")[1])
                        existing.append(num)
                    except (ValueError, IndexError):
                        pass
        next_id = max(existing) + 1 if existing else 1
        return f"profile_{next_id:06d}"

    def create_profile(self, username: str = "", name: str = "", job: str = "",
                       profile_url: str = "", memo: str = "") -> str:
        try:
            profile_id = self.generate_profile_id()
            profile_dir = self.profiles_dir / profile_id
            profile_dir.mkdir(parents=True, exist_ok=True)
            (profile_dir / "photos").mkdir(exist_ok=True)
            (profile_dir / "face").mkdir(exist_ok=True)

            name_hash = self.hash_string(name)[0] if name and name.strip() else None
            username_hash = self.hash_string(username)[0] if username and username.strip() else None

            profile_data = {
                "profile_id": profile_id,
                "name_hash": name_hash,
                "username_hash": username_hash,
                "job": job,
                "profile_url": profile_url,
                "memo": memo,
                "consent": True,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "face_photos": [],
                "contacts": [],
                "sns_profiles": [],
                "search_results": [],
                "search_history": [],
                "image_references": [],
            }

            with open(profile_dir / "profile.json", "w", encoding="utf-8") as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)

            log_event("profile_create", "profile", profile_id, "system", status="success",
                      details={"username": username, "job": job})
            return profile_id
        except Exception as e:
            log_event("profile_create", "profile", status="failure", error_message=str(e))
            raise

    def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        try:
            path = self.profiles_dir / profile_id / "profile.json"
            if not path.exists():
                return None
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not load {profile_id}: {e}")
            return None

    def save_profile(self, profile_id: str, data: Dict[str, Any]) -> bool:
        try:
            before = self.load_profile(profile_id)
            path = self.profiles_dir / profile_id / "profile.json"
            data["updated_at"] = datetime.utcnow().isoformat() + "Z"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log_event("profile_update", "profile", profile_id, "system", status="success",
                      before_data=before, after_data=data)
            return True
        except Exception as e:
            logger.error(f"Could not save {profile_id}: {e}")
            log_event("profile_update", "profile", profile_id, status="failure", error_message=str(e))
            return False

    def add_search_result(self, profile_id: str, source: str, result: Dict[str, Any]) -> bool:
        profile = self.load_profile(profile_id)
        if not profile:
            return False
        profile.setdefault("search_results", []).append({
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "result": result,
        })
        log_event("search_result_add", "profile", profile_id, "system", status="success",
                  details={"source": source, "platform": result.get("name")})
        return self.save_profile(profile_id, profile)

    def add_contact(self, profile_id: str, contact_type: str, value: str) -> bool:
        profile = self.load_profile(profile_id)
        if not profile:
            return False
        profile.setdefault("contacts", []).append({
            "type": contact_type,
            "value": value,
            "source": "Sherlock",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
        log_event("contact_add", "profile", profile_id, "system", status="success",
                  details={"type": contact_type})
        return self.save_profile(profile_id, profile)

    def add_face_photo(self, profile_id: str, photo_url: str, source: str) -> bool:
        profile = self.load_profile(profile_id)
        if not profile:
            return False
        profile.setdefault("face_photos", []).append({
            "url": photo_url,
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
        log_event("face_photo_add", "profile", profile_id, "system", status="success",
                  details={"source": source})
        return self.save_profile(profile_id, profile)

    def add_web_search_result(self, profile_id: str, query: str,
                              results: List[Dict[str, Any]]) -> bool:
        profile = self.load_profile(profile_id)
        if not profile:
            return False
        profile.setdefault("search_history", []).append({
            "kind": "web_search",
            "query": query,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results": results,
        })
        log_event("web_search_add", "profile", profile_id, "system", status="success",
                  details={"query": query, "result_count": len(results)})
        return self.save_profile(profile_id, profile)

    def add_image_reference(self, profile_id: str, image_url: str,
                            source: str = "profile") -> bool:
        profile = self.load_profile(profile_id)
        if not profile:
            return False
        profile.setdefault("image_references", []).append({
            "url": image_url,
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
        log_event("image_reference_add", "profile", profile_id, "system", status="success",
                  details={"source": source})
        return self.save_profile(profile_id, profile)

    def get_all_profiles(self) -> List[str]:
        if not self.profiles_dir.exists():
            return []
        return sorted([d.name for d in self.profiles_dir.iterdir()
                      if d.is_dir() and d.name.startswith("profile_")])

    def delete_profile(self, profile_id: str) -> bool:
        try:
            before = self.load_profile(profile_id)
            profile_dir = self.profiles_dir / profile_id
            if profile_dir.exists():
                shutil.rmtree(profile_dir)
                log_event("profile_delete", "profile", profile_id, "system", status="success",
                          before_data=before)
                return True
            log_event("profile_delete", "profile", profile_id, status="failure",
                      error_message="Profile dir not found")
            return False
        except Exception as e:
            logger.error(f"Could not delete {profile_id}: {e}")
            log_event("profile_delete", "profile", profile_id, status="failure",
                      error_message=str(e))
            return False
