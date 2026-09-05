"""Profile manager module"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import secrets
from app.config.settings import global_settings

logger = logging.getLogger(__name__)

class ProfileManager:
    """Manages profile creation, loading, and saving"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.profiles_dir = Path(global_settings.get("data_dir"))
        self.current_profile = None
    
    @staticmethod
    def hash_string(value: str, salt: str = None) -> tuple:
        """Hash string with SHA-256
        
        Args:
            value: String to hash
            salt: Optional salt
        
        Returns:
            (hashed_string, salt) tuple
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.sha256((value + salt).encode())
        return f"{salt}${hash_obj.hexdigest()}", salt
    
    def generate_profile_id(self) -> str:
        """Generate unique profile ID"""
        existing_ids = []
        
        if self.profiles_dir.exists():
            for profile_dir in self.profiles_dir.iterdir():
                if profile_dir.is_dir() and profile_dir.name.startswith("profile_"):
                    try:
                        profile_num = int(profile_dir.name.split("_")[1])
                        existing_ids.append(profile_num)
                    except (ValueError, IndexError):
                        continue
        
        next_id = max(existing_ids) + 1 if existing_ids else 1
        return f"profile_{next_id:06d}"
    
    def create_profile(self, username: str = "", name: str = "", 
                      job: str = "", profile_url: str = "", 
                      memo: str = "") -> str:
        """Create new profile
        
        Args:
            username: Public username (will be hashed)
            name: Public name (will be hashed)
            job: Job/occupation
            profile_url: Profile URL
            memo: Memo/notes
        
        Returns:
            Profile ID
        """
        try:
            profile_id = self.generate_profile_id()
            profile_dir = self.profiles_dir / profile_id
            
            profile_dir.mkdir(parents=True, exist_ok=True)
            (profile_dir / "photos").mkdir(exist_ok=True)
            (profile_dir / "face").mkdir(exist_ok=True)
            
            # Hash name and username
            name_hash = None
            if name and len(name.strip()) > 0:
                name_hash, _ = self.hash_string(name)
            
            username_hash = None
            if username and len(username.strip()) > 0:
                username_hash, _ = self.hash_string(username)
            
            profile_data = {
                "profile_id": profile_id,
                "name_hash": name_hash,
                "username_hash": username_hash,
                "job": job,
                "profile_url": profile_url,
                "memo": memo,
                "consent": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "face_photos": [],
                "contacts": [],
                "sns_profiles": [],
                "search_results": [],
            }
            
            profile_file = profile_dir / "profile.json"
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            self.current_profile = profile_data
            self.logger.info(f"Profile created: {profile_id}")
            return profile_id
        
        except Exception as e:
            self.logger.error(f"Error creating profile: {e}")
            raise
    
    def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Load profile from file
        
        Args:
            profile_id: Profile ID to load
        
        Returns:
            Profile data or None
        """
        try:
            profile_file = self.profiles_dir / profile_id / "profile.json"
            
            if not profile_file.exists():
                return None
            
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            self.current_profile = profile_data
            return profile_data
        
        except Exception as e:
            self.logger.error(f"Error loading profile: {e}")
            return None
    
    def save_profile(self, profile_id: str, data: Dict[str, Any]) -> bool:
        """Save profile to file
        
        Args:
            profile_id: Profile ID
            data: Profile data to save
        
        Returns:
            True if successful
        """
        try:
            profile_file = self.profiles_dir / profile_id / "profile.json"
            data['updated_at'] = datetime.now().isoformat()
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.current_profile = data
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving profile: {e}")
            return False
    
    def add_search_result(self, profile_id: str, source: str, result: Dict[str, Any]) -> bool:
        """Add search result to profile
        
        Args:
            profile_id: Profile ID
            source: Source name (e.g., "Sherlock")
            result: Search result data
        
        Returns:
            True if successful
        """
        try:
            profile_data = self.load_profile(profile_id)
            if not profile_data:
                return False
            
            if 'search_results' not in profile_data:
                profile_data['search_results'] = []
            
            search_entry = {
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "result": result,
            }
            
            profile_data['search_results'].append(search_entry)
            return self.save_profile(profile_id, profile_data)
        
        except Exception as e:
            self.logger.error(f"Error adding search result: {e}")
            return False
    
    def add_contact(self, profile_id: str, contact_type: str, value: str) -> bool:
        """Add contact information
        
        Args:
            profile_id: Profile ID
            contact_type: Type (email, phone, etc.)
            value: Contact value
        
        Returns:
            True if successful
        """
        try:
            profile_data = self.load_profile(profile_id)
            if not profile_data:
                return False
            
            if 'contacts' not in profile_data:
                profile_data['contacts'] = []
            
            contact_entry = {
                "type": contact_type,
                "value": value,
                "source": "Sherlock",
                "timestamp": datetime.now().isoformat(),
            }
            
            profile_data['contacts'].append(contact_entry)
            return self.save_profile(profile_id, profile_data)
        
        except Exception as e:
            self.logger.error(f"Error adding contact: {e}")
            return False
    
    def add_face_photo(self, profile_id: str, photo_url: str, source: str) -> bool:
        """Add face photo reference
        
        Args:
            profile_id: Profile ID
            photo_url: Photo URL
            source: Source platform
        
        Returns:
            True if successful
        """
        try:
            profile_data = self.load_profile(profile_id)
            if not profile_data:
                return False
            
            if 'face_photos' not in profile_data:
                profile_data['face_photos'] = []
            
            photo_entry = {
                "url": photo_url,
                "source": source,
                "timestamp": datetime.now().isoformat(),
            }
            
            profile_data['face_photos'].append(photo_entry)
            return self.save_profile(profile_id, profile_data)
        
        except Exception as e:
            self.logger.error(f"Error adding face photo: {e}")
            return False
    
    def get_all_profiles(self) -> list:
        """Get list of all profiles"""
        profiles = []
        
        if self.profiles_dir.exists():
            for profile_dir in sorted(self.profiles_dir.iterdir()):
                if profile_dir.is_dir() and profile_dir.name.startswith("profile_"):
                    profiles.append(profile_dir.name)
        
        return profiles
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete profile
        
        Args:
            profile_id: Profile ID to delete
        
        Returns:
            True if successful
        """
        try:
            import shutil
            profile_dir = self.profiles_dir / profile_id
            
            if profile_dir.exists():
                shutil.rmtree(profile_dir)
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error deleting profile: {e}")
            return False
