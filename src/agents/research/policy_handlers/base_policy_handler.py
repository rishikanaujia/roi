"""Base Policy Handler"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.interfaces.policy_handler_interface import IPolicyHandler

class BasePolicyHandler(IPolicyHandler):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        pass
    
    def get_country_code(self) -> str:
        return self.config.get("country", {}).get("code", "UNKNOWN")
