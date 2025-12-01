"""Research Agent - Hybrid Architecture with Pluggable Components"""
import json
from typing import Dict, Any
from src.core.base_agent import BaseAgent
from src.utils.config_loader import ConfigLoader
from src.agents.research.policy_handlers.factory import PolicyHandlerFactory
from src.agents.research.resource_fetchers.factory import ResourceFetcherFactory

class ResearchAgent(BaseAgent):
    """Generic research agent that works for any country + technology"""
    
    def __init__(self, llm_provider, config, country_code: str, technology: str, logger=None):
        super().__init__("ResearchAgent", llm_provider, config, logger)
        
        self.country_code = country_code
        self.technology = technology
        
        # Load dynamic configuration
        config_loader = ConfigLoader()
        self.runtime_config = config_loader.load_combination_config(country_code, technology)
        
        # Plug in country-specific policy handler
        self.policy_handler = PolicyHandlerFactory.create(country_code, self.runtime_config)
        
        # Plug in technology-specific resource fetcher
        self.resource_fetcher = ResourceFetcherFactory.create(technology, self.runtime_config)
    
    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Fetch policy (country-specific implementation)
        policy_data = await self.policy_handler.fetch_policy(
            technology=self.technology,
            **input_data
        )
        
        # Fetch resource (technology-specific implementation)
        resource_data = await self.resource_fetcher.fetch_resource(
            latitude=input_data["latitude"],
            longitude=input_data["longitude"],
            **input_data
        )
        
        # Normalize using LLM
        normalized = await self._normalize_with_llm(policy_data, resource_data)
        
        return normalized
    
    async def _normalize_with_llm(self, policy_data, resource_data):
        prompt = f"""
Normalize renewable energy data for:
Country: {self.runtime_config['country']['name']}
Technology: {self.runtime_config['technology']['name']}

Policy Data: {json.dumps(policy_data, indent=2)}
Resource Data: {json.dumps(resource_data, indent=2)}

Output valid JSON with keys: policy_data, resource_data, data_completeness
"""
        response = await self.llm_provider.generate(prompt)
        return json.loads(response)
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        required = ["latitude", "longitude"]
        return all(k in input_data for k in required)
