"""Policy Handler Interface - Country-specific implementations"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class IPolicyHandler(ABC):
    @abstractmethod
    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_country_code(self) -> str:
        pass
