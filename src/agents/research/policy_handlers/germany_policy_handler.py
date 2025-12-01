"""Germany-specific Policy Handler"""
from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler

class GermanyPolicyHandler(BasePolicyHandler):
    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        # Germany-specific: EEG feed-in tariff
        offshore_bonus = 0
        if technology == "offshore_wind":
            offshore_bonus = 5.0
        
        return {
            "country": "DEU",
            "feed_in_tariff_eur_per_mwh": 45.0,
            "offshore_wind_bonus": offshore_bonus,
            "depreciation_method": "Straight-line",
            "depreciation_years": 20,
            "tax_rate": 0.30,
            "source": "EEG"
        }
