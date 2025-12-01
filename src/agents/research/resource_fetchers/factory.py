"""Resource Fetcher Factory - Add technologies here"""
from typing import Dict, Any
from src.agents.research.resource_fetchers.base_resource_fetcher import BaseResourceFetcher
from src.agents.research.resource_fetchers.solar_fetcher import SolarResourceFetcher
from src.agents.research.resource_fetchers.wind_fetcher import WindResourceFetcher

class ResourceFetcherFactory:
    _fetchers = {
        "solar_pv": SolarResourceFetcher,
        "onshore_wind": WindResourceFetcher,
        # Add more technologies here as you scale
    }
    
    @classmethod
    def create(cls, technology: str, config: Dict[str, Any]) -> BaseResourceFetcher:
        fetcher_class = cls._fetchers.get(technology)
        if not fetcher_class:
            raise ValueError(f"No resource fetcher for technology: {technology}")
        return fetcher_class(config)
    
    @classmethod
    def register(cls, technology: str, fetcher_class: type):
        cls._fetchers[technology] = fetcher_class
