"""Agent Interface - Following SOLID principles"""
from abc import ABC, abstractmethod
from typing import Any, Dict

class IAgent(ABC):
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
