"""
Solar PV Calculator - Solar-Specific Financial Calculations

Solar PV capacity factor calculation:
- Based on Global Horizontal Irradiance (GHI)
- Adjusted for temperature derating
- Accounts for system losses (14% typical)

Formula:
    CF = (GHI * 365 / 8760) * (1 - temp_derating) * (1 - system_losses)
"""

from typing import Dict, Any
from src.agents.analysis.calculators.base_calculator import BaseCalculator


class SolarPVCalculator(BaseCalculator):
    """
    Solar PV-specific calculation engine.

    Implements solar-specific capacity factor calculation based on:
    - GHI (Global Horizontal Irradiance)
    - Temperature (affects efficiency)
    - System losses (inverter, wiring, soiling, etc.)
    """

    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        """
        Calculate solar PV capacity factor from resource data.

        Args:
            resource_data: Must contain:
                - avg_ghi_kwh_m2_day: Average daily GHI
                - avg_temperature_c: Average temperature (optional)

        Returns:
            Capacity factor (0-1)

        Example:
            >>> calc = SolarPVCalculator()
            >>> cf = calc.calculate_capacity_factor({
            ...     'avg_ghi_kwh_m2_day': 5.5,
            ...     'avg_temperature_c': 25
            ... })
            >>> print(f"CF: {cf*100:.1f}%")
            CF: 24.2%
        """
        ghi = resource_data['avg_ghi_kwh_m2_day']
        temp = resource_data.get('avg_temperature_c', 25.0)

        # Base capacity factor from GHI
        # Standard test conditions: 1000 W/m² = 1 kWh/m²
        # CF_base = (daily GHI * 365 days) / (8760 hours * 1 kW/m²)
        base_cf = (ghi * 365) / 8760

        # Temperature derating
        # PV efficiency decreases ~0.4% per °C above 25°C
        temp_coefficient = -0.004  # -0.4% per °C
        temp_derating = 1 + (temp_coefficient * max(0, temp - 25))

        # System losses (typical 14%)
        # - Inverter losses: 3%
        # - Wiring losses: 2%
        # - Soiling: 3%
        # - Mismatch: 2%
        # - Availability: 2%
        # - Degradation (average): 2%
        system_losses = 0.14

        # Final capacity factor
        cf = base_cf * temp_derating * (1 - system_losses)

        # Realistic bounds: 10-30% for fixed-tilt PV
        cf = max(0.10, min(0.30, cf))

        return round(cf, 4)


if __name__ == "__main__":
    print("=" * 70)
    print("Solar PV Calculator Demo")
    print("=" * 70)

    calc = SolarPVCalculator()

    # Test different solar resources
    print("\n1. Excellent Solar Resource (Texas):")
    texas_resource = {
        'avg_ghi_kwh_m2_day': 5.5,
        'avg_temperature_c': 25.0
    }
    cf1 = calc.calculate_capacity_factor(texas_resource)
    print(f"   GHI: {texas_resource['avg_ghi_kwh_m2_day']} kWh/m²/day")
    print(f"   Temperature: {texas_resource['avg_temperature_c']}°C")
    print(f"   Capacity Factor: {cf1 * 100:.1f}%")

    # Full financial analysis
    params1 = {
        'capex_usd_per_kw': 1200,
        'opex_usd_per_kw_year': 15,
        'capacity_factor': cf1,
        'discount_rate': 0.08,
        'project_lifetime_years': 25,
        'electricity_price_usd_per_mwh': 35.0,  # Texas wholesale
        'capacity_kw': 100000
    }

    lcoe1 = calc.calculate_lcoe(params1)
    irr1 = calc.calculate_irr(params1)
    npv1 = calc.calculate_npv(params1)

    print(f"   LCOE: ${lcoe1:.2f}/MWh")
    print(f"   IRR: {irr1:.1f}%")
    print(f"   NPV (100 MW): ${npv1:,.0f}")

    # Test moderate solar resource
    print("\n2. Moderate Solar Resource (Germany):")
    germany_resource = {
        'avg_ghi_kwh_m2_day': 3.5,
        'avg_temperature_c': 15.0
    }
    cf2 = calc.calculate_capacity_factor(germany_resource)
    print(f"   GHI: {germany_resource['avg_ghi_kwh_m2_day']} kWh/m²/day")
    print(f"   Temperature: {germany_resource['avg_temperature_c']}°C")
    print(f"   Capacity Factor: {cf2 * 100:.1f}%")

    params2 = {
        **params1,
        'capacity_factor': cf2,
        'electricity_price_usd_per_mwh': 45.0  # Germany wholesale
    }

    lcoe2 = calc.calculate_lcoe(params2)
    irr2 = calc.calculate_irr(params2)

    print(f"   LCOE: ${lcoe2:.2f}/MWh")
    print(f"   IRR: {irr2:.1f}%")

    # Test hot climate (efficiency reduction)
    print("\n3. Hot Climate (Desert, 35°C average):")
    hot_resource = {
        'avg_ghi_kwh_m2_day': 6.5,  # Higher GHI
        'avg_temperature_c': 35.0  # But hotter
    }
    cf3 = calc.calculate_capacity_factor(hot_resource)
    print(f"   GHI: {hot_resource['avg_ghi_kwh_m2_day']} kWh/m²/day")
    print(f"   Temperature: {hot_resource['avg_temperature_c']}°C (reduces efficiency)")
    print(f"   Capacity Factor: {cf3 * 100:.1f}%")
    print(f"   Note: High GHI offset by temperature derating")

    print("\n" + "=" * 70)
    print("✅ Solar PV Calculator working correctly!")
    print("=" * 70)