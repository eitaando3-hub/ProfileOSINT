"""Sherlock username search wrapper"""
import subprocess
import json
import logging
from typing import Dict, List, Any, Tuple
import hashlib
import secrets
import re
from app.sources.source_base import SourceBase

logger = logging.getLogger(__name__)

class SherlockWrapper(SourceBase):
    """Wrapper for Sherlock username search tool"""
    
    def __init__(self):
        super().__init__()
        self.sherlock_installed = self._check_sherlock_installed()
        self.username_hash_mapping = {}
    
    def _check_sherlock_installed(self) -> bool:
        """Check if Sherlock is installed"""
        try:
            result = subprocess.run(
                ['python', '-m', 'pip', 'show', 'sherlock-project'],
                capture_output=True,
                text=True,
                timeout=5
            )
            is_installed = result.returncode == 0
            if is_installed:
                self.logger.info("Sherlock is installed")
            else:
                self.logger.warning("Sherlock is not installed")
            return is_installed
        except Exception as e:
            self.logger.error(f"Error checking Sherlock: {e}")
            return False
    
    @staticmethod
    def hash_username(username: str, salt: str = None) -> Tuple[str, str]:
        """Hash username
        
        Args:
            username: Username to hash
            salt: Optional salt
        
        Returns:
            (hashed_username, salt) tuple
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.sha256((username + salt).encode())
        username_hash = hash_obj.hexdigest()
        
        return f"{salt}${username_hash}", salt
    
    def extract_profile_info(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract profile information from Sherlock result
        
        Args:
            result: Sherlock search result
        
        Returns:
            Extracted information
        """
        info = {
            "platform": result.get("name", ""),
            "username": result.get("username", ""),
            "url": result.get("url_main", ""),
            "profile_image_url": None,
            "name": None,
            "bio": None,
            "email": None,
            "phone": None,
        }
        
        # Try to extract additional information from user_data if available
        if "user_data" in result:
            user_data = result["user_data"]
            if isinstance(user_data, dict):
                info["name"] = user_data.get("name") or user_data.get("full_name")
                info["bio"] = user_data.get("bio") or user_data.get("description")
                info["profile_image_url"] = user_data.get("profile_image") or user_data.get("avatar_url")
                info["email"] = user_data.get("email")
                info["phone"] = user_data.get("phone")
        
        return info
    
    def search(self, username: str) -> List[Dict[str, Any]]:
        """Search for username across platforms
        
        Args:
            username: Username to search
        
        Returns:
            List of search results
        """
        if not self.sherlock_installed:
            self.logger.error("Sherlock is not installed")
            return []
        
        if not username or len(username.strip()) == 0:
            return []
        
        try:
            username_hash, salt = self.hash_username(username)
            self.username_hash_mapping[username_hash] = (username, salt)
            
            self.logger.info(f"Starting Sherlock search for username")
            
            result = subprocess.run(
                ['python', '-m', 'sherlock', '--json', username],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                try:
                    output_lines = result.stdout.strip().split('\n')
                    results = []
                    
                    for line in output_lines:
                        if line.startswith('{'):
                            try:
                                data = json.loads(line)
                                data['username_hash'] = username_hash
                                extracted = self.extract_profile_info(data)
                                data['extracted_info'] = extracted
                                results.append(data)
                            except json.JSONDecodeError:
                                continue
                    
                    self.results = results
                    self.logger.info(f"Search completed: {len(results)} profiles found")
                    return results
                
                except Exception as e:
                    self.logger.error(f"Error parsing output: {e}")
                    return []
            
            else:
                self.logger.error(f"Search failed: {result.stderr}")
                return []
        
        except subprocess.TimeoutExpired:
            self.logger.error("Search timed out")
            return []
        
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return []
    
    def validate_result(self, result: Dict[str, Any]) -> bool:
        """Validate search result
        
        Args:
            result: Result to validate
        
        Returns:
            True if valid
        """
        required_fields = ['username', 'name', 'url_main']
        
        for field in required_fields:
            if field not in result:
                return False
        
        return True
    
    def clear_sensitive_data(self):
        """Clear sensitive data from memory"""
        self.username_hash_mapping.clear()
        self.logger.info("Cleared sensitive data")
