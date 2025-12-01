"""Calculation Engine Interface - Technology-specific calculations"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class ICalculationEngine(ABC):
    @abstractmethod
    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        pass
    
    @abstractmethod
    def calculate_irr(self, params: Dict[str, Any]) -> float:
        pass
    
    @abstractmethod
    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        pass
