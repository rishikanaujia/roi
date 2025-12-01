"""Solar-specific Resource Fetcher"""
from typing import Dict, Any
from src.agents.research.resource_fetchers.base_resource_fetcher import BaseResourceFetcher

class SolarResourceFetcher(BaseResourceFetcher):
    async def fetch_resource(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        # Solar-specific: GHI, temperature
        # In real implementation, call NASA POWER API or NREL API
        avg_ghi = 5.5  # Mock data
        avg_temp = 25.0
        
        return {
            "technology": "solar_pv",
            "avg_ghi_kwh_m2_day": avg_ghi,
            "avg_temperature_c": avg_temp,
            "confidence": "high",
            "source": "NASA POWER (mock)"
        }
