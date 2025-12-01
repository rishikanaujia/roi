"""Base Agent - Template Method Pattern"""
import logging
from typing import Any, Dict, Optional
from abc import abstractmethod
from src.core.interfaces.agent_interface import IAgent
from src.core.interfaces.llm_interface import ILLMProvider

class BaseAgent(IAgent):
    def __init__(self, name: str, llm_provider: ILLMProvider, 
                 config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.name = name
        self.llm_provider = llm_provider
        self.config = config
        self.logger = logger or logging.getLogger(self.name)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data):
                raise ValueError(f"Invalid input for {self.name}")
            
            self.logger.info(f"{self.name} execution started")
            processed = await self._preprocess(input_data)
            result = await self._execute_core(processed)
            final = await self._postprocess(result)
            self.logger.info(f"{self.name} execution completed")
            return final
        except Exception as e:
            self.logger.error(f"{self.name} failed: {str(e)}")
            raise
    
    @abstractmethod
    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    async def _preprocess(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return input_data
    
    async def _postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return result
    
    def get_name(self) -> str:
        return self.name
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return input_data is not None and isinstance(input_data, dict)
