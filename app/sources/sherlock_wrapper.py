"""Sherlock username search wrapper"""
import subprocess
import json
import logging
from typing import Dict, List, Any, Tuple
import hashlib
import secrets
from app.sources.source_base import SourceBase

logger = logging.getLogger(__name__)

class SherlockWrapper(SourceBase):
    """Wrapper for Sherlock username search tool"""
    
    def __init__(self):
        super().__init__()
        self.sherlock_installed = self._check_sherlock_installed()
        self.username_hash_mapping = {}
    
    def _check_sherlock_installed(self) -> bool:
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
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.sha256((username + salt).encode())
        username_hash = hash_obj.hexdigest()
        
        return f"{salt}${username_hash}", salt
    
    def search(self, username: str) -> List[Dict[str, Any]]:
        if not self.sherlock_installed:
            self.logger.error("Sherlock is not installed")
            return []
        
        if not username or len(username.strip()) == 0:
            return []
        
        try:
            username_hash, salt = self.hash_username(username)
            self.username_hash_mapping[username_hash] = (username, salt)
            
            self.logger.info(f"Starting Sherlock search")
            
            result = subprocess.run(
                ['python', '-m', 'sherlock', '--json', username],
                capture_output=True,
                text=True,
                timeout=60
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
        required_fields = ['username', 'name', 'url_main']
        
        for field in required_fields:
            if field not in result:
                return False
        
        return True
    
    def clear_sensitive_data(self):
        self.username_hash_mapping.clear()
        self.logger.info("Cleared sensitive data")
