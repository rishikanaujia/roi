"""Base Resource Fetcher"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.interfaces.resource_fetcher_interface import IResourceFetcher

class BaseResourceFetcher(IResourceFetcher):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def fetch_resource(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        pass
    
    def get_technology(self) -> str:
        return self.config.get("technology", {}).get("code", "UNKNOWN")
