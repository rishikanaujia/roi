"""Policy Handler Factory - Add countries here"""
from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler
from src.agents.research.policy_handlers.usa_policy_handler import USAPolicyHandler
from src.agents.research.policy_handlers.germany_policy_handler import GermanyPolicyHandler

class PolicyHandlerFactory:
    _handlers = {
        "USA": USAPolicyHandler,
        "DEU": GermanyPolicyHandler,
        # Add more countries here as you scale
    }
    
    @classmethod
    def create(cls, country_code: str, config: Dict[str, Any]) -> BasePolicyHandler:
        handler_class = cls._handlers.get(country_code)
        if not handler_class:
            raise ValueError(f"No policy handler for country: {country_code}")
        return handler_class(config)
    
    @classmethod
    def register(cls, country_code: str, handler_class: type):
        cls._handlers[country_code] = handler_class
