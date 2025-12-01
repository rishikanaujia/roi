"""Solar PV Calculation Engine"""
from typing import Dict, Any
from src.agents.analysis.calculators.base_calculator import BaseCalculator

class SolarPVCalculator(BaseCalculator):
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
        # Simplified IRR calculation
        lcoe = self.calculate_lcoe(params)
        electricity_price = params.get('electricity_price', 40.0)
        
        if lcoe < electricity_price:
            irr = 8 + (electricity_price - lcoe) * 0.5
        else:
            irr = 8 - (lcoe - electricity_price) * 0.3
        
        return round(max(5, min(25, irr)), 2)
    
    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        ghi = resource_data['avg_ghi_kwh_m2_day']
        temp = resource_data.get('avg_temperature_c', 25)
        
        base_cf = (ghi * 365) / 8760
        temp_factor = 1 - 0.004 * max(0, temp - 25)
        system_losses = 0.14
        
        cf = base_cf * temp_factor * (1 - system_losses)
        return round(min(max(cf, 0.10), 0.30), 4)
