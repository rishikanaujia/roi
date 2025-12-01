"""Base Calculation Engine"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.interfaces.calculation_engine_interface import ICalculationEngine

class BaseCalculator(ICalculationEngine):
    @abstractmethod
    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        pass
    
    @abstractmethod
    def calculate_irr(self, params: Dict[str, Any]) -> float:
        pass
    
    @abstractmethod
    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        pass
