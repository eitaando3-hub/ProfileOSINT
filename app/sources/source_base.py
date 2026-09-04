"""Base class for data sources"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class SourceBase(ABC):
    """Abstract base class for all data sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.results = []
    
    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def validate_result(self, result: Dict[str, Any]) -> bool:
        pass
    
    def get_results(self) -> List[Dict[str, Any]]:
        return self.results.copy()
    
    def clear_results(self):
        self.results.clear()
