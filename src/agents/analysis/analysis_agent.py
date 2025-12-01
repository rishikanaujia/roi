"""Analysis Agent - Hybrid Architecture"""
from typing import Dict, Any
from src.core.base_agent import BaseAgent
from src.utils.config_loader import ConfigLoader
from src.agents.analysis.calculators.factory import CalculationEngineFactory

class AnalysisAgent(BaseAgent):
    """Generic analysis agent with technology-specific calculations"""
    
    def __init__(self, llm_provider, config, country_code: str, technology: str, logger=None):
        super().__init__("AnalysisAgent", llm_provider, config, logger)
        
        self.country_code = country_code
        self.technology = technology
        
        config_loader = ConfigLoader()
        self.runtime_config = config_loader.load_combination_config(country_code, technology)
        
        # Get technology-specific calculation engine
        self.calc_engine = CalculationEngineFactory.get_engine(technology)
    
    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        research_data = input_data['research_data']
        resource_data = research_data['resource_data']
        
        # Calculate capacity factor (technology-specific)
        cf = self.calc_engine.calculate_capacity_factor(resource_data)
        
        # Build financial parameters (country-specific)
        params = {
            'capex_usd_per_kw': self.runtime_config['technology']['financial']['capex_usd_per_kw'],
            'opex_usd_per_kw_year': self.runtime_config['technology']['financial']['opex_usd_per_kw_year'],
            'project_lifetime_years': self.runtime_config['technology']['financial']['project_lifetime_years'],
            'discount_rate': self.runtime_config['country']['financial']['discount_rate'],
            'capacity_factor': cf,
            'electricity_price': self.runtime_config['country']['grid'].get('wholesale_price_usd_per_mwh', 40.0),
        }
        
        # Calculate LCOE and IRR (technology-specific)
        lcoe = self.calc_engine.calculate_lcoe(params)
        irr = self.calc_engine.calculate_irr(params)
        
        return {
            "lcoe_usd_per_mwh": lcoe,
            "irr_percent": irr,
            "capacity_factor": cf,
            "assumptions": params,
            "confidence": "high"
        }
