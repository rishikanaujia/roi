"""
Calculation Engine Interface - Technology-Specific Financial Calculations

Each technology (Solar, Wind, Hydro) has different calculation methods:
- Solar: GHI → capacity factor → LCOE (includes temperature derating)
- Wind: Wind speed → capacity factor → LCOE (includes Weibull distribution)
- Hydro: Flow rate → capacity factor → LCOE (includes head calculations)

This interface ensures all calculators provide the same core metrics.

Example:
    solar_calc = SolarPVCalculator()
    lcoe = solar_calc.calculate_lcoe({
        'capex_usd_per_kw': 1200,
        'opex_usd_per_kw_year': 15,
        'capacity_factor': 0.25,
        'discount_rate': 0.08,
        'project_lifetime_years': 25
    })
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ICalculationEngine(ABC):
    """
    Interface for technology-specific financial calculation engines.

    All calculators must implement these core financial metrics:
    - LCOE (Levelized Cost of Energy)
    - IRR (Internal Rate of Return)
    - NPV (Net Present Value)
    - Capacity Factor (from resource data)
    """

    @abstractmethod
    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        """
        Calculate Levelized Cost of Energy (LCOE).

        LCOE is the average cost per MWh over the project lifetime,
        accounting for all capital and operating costs.

        Formula (simplified):
            LCOE = (PV of CAPEX + PV of OPEX) / (PV of Energy Production)

        Args:
            params: Dictionary containing:
                - capex_usd_per_kw: Capital expenditure per kW
                - opex_usd_per_kw_year: Annual operating expenditure per kW
                - capacity_factor: Average capacity factor (0-1)
                - discount_rate: Discount rate (WACC)
                - project_lifetime_years: Project lifetime
                - (technology-specific params)

        Returns:
            LCOE in USD/MWh

        Example:
            >>> calc = SolarPVCalculator()
            >>> lcoe = calc.calculate_lcoe({
            ...     'capex_usd_per_kw': 1200,
            ...     'opex_usd_per_kw_year': 15,
            ...     'capacity_factor': 0.25,
            ...     'discount_rate': 0.08,
            ...     'project_lifetime_years': 25
            ... })
            >>> print(f"LCOE: ${lcoe:.2f}/MWh")
            LCOE: $45.32/MWh
        """
        pass

    @abstractmethod
    def calculate_irr(self, params: Dict[str, Any]) -> float:
        """
        Calculate Internal Rate of Return (IRR).

        IRR is the discount rate that makes NPV = 0.
        It represents the project's effective return rate.

        Args:
            params: Dictionary containing:
                - capex_usd_per_kw: Capital expenditure
                - opex_usd_per_kw_year: Operating expenditure
                - capacity_factor: Capacity factor
                - electricity_price_usd_per_mwh: Revenue per MWh
                - project_lifetime_years: Project lifetime
                - capacity_kw: Project capacity
                - (technology-specific params)

        Returns:
            IRR as percentage (e.g., 12.5 for 12.5%)

        Example:
            >>> irr = calc.calculate_irr({...})
            >>> print(f"IRR: {irr:.1f}%")
            IRR: 12.5%
        """
        pass

    @abstractmethod
    def calculate_npv(self, params: Dict[str, Any]) -> float:
        """
        Calculate Net Present Value (NPV).

        NPV is the present value of all future cash flows minus initial investment.
        Positive NPV = profitable project.

        Args:
            params: Dictionary containing financial parameters

        Returns:
            NPV in USD

        Example:
            >>> npv = calc.calculate_npv({...})
            >>> print(f"NPV: ${npv:,.0f}")
            NPV: $5,234,567
        """
        pass

    @abstractmethod
    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        """
        Calculate capacity factor from resource data.

        Capacity factor = Actual energy / Theoretical maximum energy

        This is technology-specific:
        - Solar: Based on GHI, temperature, system losses
        - Wind: Based on wind speed, Weibull distribution, turbine curve
        - Hydro: Based on river flow, head, seasonal variation

        Args:
            resource_data: Technology-specific resource data
                Solar: GHI, temperature
                Wind: Wind speed, Weibull parameters
                Hydro: Flow rate, head

        Returns:
            Capacity factor (0-1, typically 0.15-0.50)

        Example:
            >>> cf = calc.calculate_capacity_factor({
            ...     'avg_ghi_kwh_m2_day': 5.5,
            ...     'avg_temperature_c': 25
            ... })
            >>> print(f"Capacity Factor: {cf*100:.1f}%")
            Capacity Factor: 24.5%
        """
        pass


if __name__ == "__main__":
    print("=" * 70)
    print("Calculation Engine Interface Demo")
    print("=" * 70)

    print("\nThis interface defines the contract for technology-specific calculators.")
    print("\nAll calculators must implement:")
    print("  1. calculate_lcoe() - Levelized Cost of Energy")
    print("  2. calculate_irr() - Internal Rate of Return")
    print("  3. calculate_npv() - Net Present Value")
    print("  4. calculate_capacity_factor() - From resource data")

    print("\n" + "=" * 70)
    print("Key Points:")
    print("- Solar calculator: Uses GHI and temperature")
    print("- Wind calculator: Uses wind speed and Weibull distribution")
    print("- All return consistent financial metrics")
    print("- AnalysisAgent doesn't care which calculator is used")
    print("=" * 70)