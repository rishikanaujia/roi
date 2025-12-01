"""Resource Fetcher Interface - Technology-specific implementations"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class IResourceFetcher(ABC):
    @abstractmethod
    async def fetch_resource(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_technology(self) -> str:
        pass
