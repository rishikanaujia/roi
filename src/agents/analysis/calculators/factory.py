"""Calculation Engine Factory"""
from typing import Dict, Any
from src.agents.analysis.calculators.base_calculator import BaseCalculator
from src.agents.analysis.calculators.solar_calculator import SolarPVCalculator
from src.agents.analysis.calculators.wind_calculator import OnshoreWindCalculator

class CalculationEngineFactory:
    _engines = {
        "solar_pv": SolarPVCalculator,
        "onshore_wind": OnshoreWindCalculator,
        # Add more technologies here
    }
    
    @classmethod
    def get_engine(cls, technology: str) -> BaseCalculator:
        engine_class = cls._engines.get(technology)
        if not engine_class:
            raise ValueError(f"No calculation engine for: {technology}")
        return engine_class()
