"""Onshore Wind Calculation Engine"""
from typing import Dict, Any
from src.agents.analysis/calculators.base_calculator import BaseCalculator

class OnshoreWindCalculator(BaseCalculator):
    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        capex = params['capex_usd_per_kw']
        opex = params['opex_usd_per_kw_year']
        cf = params['capacity_factor']
        lifetime = params['project_lifetime_years']
        dr = params['discount_rate']
        
        annual_energy = 8760 * cf
        pv_capex = capex
        pv_opex = opex * ((1 - (1 + dr)**-lifetime) / dr)
        pv_energy = annual_energy * ((1 - (1 + dr)**-lifetime) / dr)
        
        lcoe = ((pv_capex + pv_opex) / pv_energy) * 1000
        return round(lcoe, 2)
    
    def calculate_irr(self, params: Dict[str, Any]) -> float:
        lcoe = self.calculate_lcoe(params)
        electricity_price = params.get('electricity_price', 40.0)
        
        if lcoe < electricity_price:
            irr = 8 + (electricity_price - lcoe) * 0.4
        else:
            irr = 8 - (lcoe - electricity_price) * 0.25
        
        return round(max(5, min(25, irr)), 2)
    
    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        wind_speed = resource_data['avg_wind_speed_m_s']
        
        if wind_speed < 6:
            cf = 0.20
        elif wind_speed < 7:
            cf = 0.30
        elif wind_speed < 8:
            cf = 0.38
        else:
            cf = 0.45
        
        return round(min(max(cf, 0.25), 0.50), 4)
