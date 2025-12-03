"""
Calculation Engine Factory - Creates Technology-Specific Calculators

Just like ResourceFetcherFactory and PolicyHandlerFactory,
this factory creates the right calculator for each technology.

Example:
    solar_calc = CalculationEngineFactory.get_engine("solar_pv")
    wind_calc = CalculationEngineFactory.get_engine("onshore_wind")

    # Both have same interface, different formulas
    solar_lcoe = solar_calc.calculate_lcoe(params)
    wind_lcoe = wind_calc.calculate_lcoe(params)
"""

from typing import Dict
from src.core.interfaces.calculation_engine_interface import ICalculationEngine
from src.agents.analysis.calculators.base_calculator import BaseCalculator
from src.agents.analysis.calculators.solar_calculator import SolarPVCalculator
from src.agents.analysis.calculators.wind_calculator import WindCalculator


class CalculationEngineFactory:
    """
    Factory for creating technology-specific calculation engines.

    Maintains a registry of available calculators.
    """

    # Registry of available calculators
    _engines: Dict[str, type] = {
        "solar_pv": SolarPVCalculator,
        "onshore_wind": WindCalculator,
        # Add more technologies:
        # "offshore_wind": OffshoreWindCalculator,
        # "hydro": HydroCalculator,
        # "geothermal": GeothermalCalculator,
    }

    @classmethod
    def get_engine(cls, technology: str) -> BaseCalculator:
        """
        Get calculation engine for specified technology.

        Args:
            technology: Technology code (e.g., "solar_pv", "onshore_wind")

        Returns:
            Calculator instance

        Raises:
            ValueError: If technology not supported

        Example:
            >>> calc = CalculationEngineFactory.get_engine("solar_pv")
            >>> cf = calc.calculate_capacity_factor({...})
        """
        technology = technology.lower()

        engine_class = cls._engines.get(technology)
        if engine_class is None:
            available = ", ".join(cls._engines.keys())
            raise ValueError(
                f"No calculation engine for technology: {technology}. "
                f"Available: {available}"
            )

        return engine_class()

    @classmethod
    def register(cls, technology: str, engine_class: type):
        """Register a new calculation engine dynamically."""
        cls._engines[technology.lower()] = engine_class

    @classmethod
    def get_supported_technologies(cls) -> list:
        """Get list of supported technologies."""
        return sorted(cls._engines.keys())


if __name__ == "__main__":
    print("=" * 70)
    print("Calculation Engine Factory Demo")
    print("=" * 70)

    print(f"\n1. Supported technologies: {CalculationEngineFactory.get_supported_technologies()}")

    # Test solar
    print("\n2. Solar PV Calculator:")
    solar_calc = CalculationEngineFactory.get_engine("solar_pv")
    print(f"   Created: {type(solar_calc).__name__}")

    solar_cf = solar_calc.calculate_capacity_factor({
        'avg_ghi_kwh_m2_day': 5.5,
        'avg_temperature_c': 25
    })
    print(f"   Capacity Factor: {solar_cf * 100:.1f}%")

    # Test wind
    print("\n3. Wind Calculator:")
    wind_calc = CalculationEngineFactory.get_engine("onshore_wind")
    print(f"   Created: {type(wind_calc).__name__}")

    wind_cf = wind_calc.calculate_capacity_factor({
        'avg_wind_speed_m_s': 7.5
    })
    print(f"   Capacity Factor: {wind_cf * 100:.1f}%")

    # Test error handling
    print("\n4. Error handling:")
    try:
        CalculationEngineFactory.get_engine("nuclear")
    except ValueError as e:
        print(f"   Expected error: {e}")

    print("\n" + "=" * 70)
    print("✅ Calculation Engine Factory working correctly!")
    print("=" * 70)