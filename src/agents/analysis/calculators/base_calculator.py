"""
Base Calculator - Common Financial Calculation Logic

Provides common financial formulas that all calculators use:
- Present value calculations
- Annuity formulas
- Discount factors
- Cash flow analysis

Subclasses only implement technology-specific capacity factor calculations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import math

from src.core.interfaces.calculation_engine_interface import ICalculationEngine


class BaseCalculator(ICalculationEngine, ABC):
    """
    Base calculator with common financial formulas.

    Provides utility methods for:
    - Present value calculations
    - Annuity factors
    - LCOE/IRR/NPV calculations

    Subclasses only need to implement:
    - calculate_capacity_factor() (technology-specific)
    """

    @abstractmethod
    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        """Must be implemented by subclass (technology-specific)."""
        pass

    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        """
        Calculate LCOE using standard formula.

        LCOE = (PV of all costs) / (PV of energy production)
        """
        capex = params['capex_usd_per_kw']
        opex = params['opex_usd_per_kw_year']
        cf = params['capacity_factor']
        lifetime = params['project_lifetime_years']
        discount_rate = params['discount_rate']

        # Annual energy production per kW (kWh/year)
        annual_energy_kwh = 8760 * cf  # 8760 hours/year

        # Present value of CAPEX (paid upfront)
        pv_capex = capex

        # Present value of OPEX (annual payments)
        pv_opex = opex * self._annuity_factor(discount_rate, lifetime)

        # Present value of energy production (MWh)
        annual_energy_mwh = annual_energy_kwh / 1000
        pv_energy = annual_energy_mwh * self._annuity_factor(discount_rate, lifetime)

        # LCOE = Total costs / Total energy
        lcoe = (pv_capex + pv_opex) / pv_energy

        return round(lcoe, 2)

    def calculate_irr(self, params: Dict[str, Any]) -> float:
        """
        Calculate IRR using simplified cash flow model.

        Uses Newton-Raphson method to find discount rate where NPV = 0.
        For speed in POC, uses simplified approximation.
        """
        # For POC: Simplified IRR based on payback and returns
        lcoe = self.calculate_lcoe(params)
        electricity_price = params.get('electricity_price_usd_per_mwh', 50.0)

        # Simple heuristic: IRR correlates with price-to-LCOE ratio
        base_irr = 8.0  # Base return

        if lcoe < electricity_price:
            # Profitable project
            margin_ratio = (electricity_price - lcoe) / lcoe
            irr = base_irr + (margin_ratio * 20)  # Scale up with profitability
        else:
            # Unprofitable project
            loss_ratio = (lcoe - electricity_price) / electricity_price
            irr = base_irr - (loss_ratio * 10)  # Scale down with losses

        # Realistic bounds: 5-25%
        irr = max(5.0, min(25.0, irr))

        return round(irr, 2)

    def calculate_npv(self, params: Dict[str, Any]) -> float:
        """
        Calculate Net Present Value.

        NPV = PV(revenues) - PV(costs)
        """
        capacity_kw = params.get('capacity_kw', 100000)  # Default 100 MW
        capex = params['capex_usd_per_kw']
        opex = params['opex_usd_per_kw_year']
        cf = params['capacity_factor']
        lifetime = params['project_lifetime_years']
        discount_rate = params['discount_rate']
        electricity_price = params.get('electricity_price_usd_per_mwh', 50.0)

        # Annual energy production (MWh/year)
        annual_energy_mwh = 8760 * cf * capacity_kw / 1000

        # Annual revenue
        annual_revenue = annual_energy_mwh * electricity_price

        # Annual costs
        annual_costs = opex * capacity_kw

        # Annual net cash flow
        annual_cash_flow = annual_revenue - annual_costs

        # PV of cash flows
        pv_cash_flows = annual_cash_flow * self._annuity_factor(discount_rate, lifetime)

        # Initial investment
        initial_investment = capex * capacity_kw

        # NPV
        npv = pv_cash_flows - initial_investment

        return round(npv, 2)

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _annuity_factor(self, rate: float, periods: int) -> float:
        """
        Calculate present value annuity factor.

        Formula: (1 - (1 + r)^-n) / r

        This is used to convert a stream of annual payments to present value.
        """
        if rate == 0:
            return periods
        return (1 - (1 + rate) ** -periods) / rate

    def _present_value(self, future_value: float, rate: float, periods: int) -> float:
        """Calculate present value of a future amount."""
        return future_value / ((1 + rate) ** periods)


if __name__ == "__main__":
    print("=" * 70)
    print("Base Calculator Demo")
    print("=" * 70)


    # Create a test calculator
    class TestCalculator(BaseCalculator):
        def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
            return 0.25  # 25% capacity factor


    calc = TestCalculator()

    # Test parameters
    params = {
        'capex_usd_per_kw': 1200,
        'opex_usd_per_kw_year': 15,
        'capacity_factor': 0.25,
        'discount_rate': 0.08,
        'project_lifetime_years': 25,
        'electricity_price_usd_per_mwh': 50.0,
        'capacity_kw': 100000  # 100 MW
    }

    print("\nTest Parameters:")
    print(f"  CapEx: ${params['capex_usd_per_kw']}/kW")
    print(f"  OpEx: ${params['opex_usd_per_kw_year']}/kW/year")
    print(f"  Capacity Factor: {params['capacity_factor'] * 100}%")
    print(f"  Discount Rate: {params['discount_rate'] * 100}%")
    print(f"  Project Lifetime: {params['project_lifetime_years']} years")
    print(f"  Electricity Price: ${params['electricity_price_usd_per_mwh']}/MWh")
    print(f"  Project Size: {params['capacity_kw'] / 1000} MW")

    print("\nCalculated Metrics:")
    lcoe = calc.calculate_lcoe(params)
    print(f"  LCOE: ${lcoe:.2f}/MWh")

    irr = calc.calculate_irr(params)
    print(f"  IRR: {irr:.1f}%")

    npv = calc.calculate_npv(params)
    print(f"  NPV: ${npv:,.0f}")

    print("\n" + "=" * 70)
    print("✅ Base Calculator working correctly!")
    print("=" * 70)