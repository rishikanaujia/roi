"""LLM Provider Interface - Strategy Pattern"""
from abc import ABC, abstractmethod

class ILLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass
    
    @abstractmethod
    def estimate_cost(self, tokens: int) -> float:
        pass
