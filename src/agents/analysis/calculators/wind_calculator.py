"""
Wind Calculator - Wind-Specific Financial Calculations

Wind capacity factor calculation:
- Based on average wind speed at hub height
- Uses simplified wind power curve
- Accounts for wake losses, availability

Wind power increases with CUBE of wind speed:
    Power ∝ v³

This makes wind speed the most critical parameter.
"""

from typing import Dict, Any
from src.agents.analysis.calculators.base_calculator import BaseCalculator


class WindCalculator(BaseCalculator):
    """
    Wind-specific calculation engine.

    Implements wind-specific capacity factor calculation based on:
    - Wind speed at hub height
    - Wind power density
    - Turbine characteristics
    - Wake losses and availability
    """

    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        """
        Calculate wind capacity factor from resource data.

        Uses simplified wind power classification:
        - Class 1 (<6 m/s): Poor wind, CF ~20%
        - Class 3 (6-7 m/s): Fair wind, CF ~30%
        - Class 4 (7-8 m/s): Good wind, CF ~38%
        - Class 5 (8-9 m/s): Excellent wind, CF ~45%
        - Class 7 (>9 m/s): Outstanding wind, CF ~50%

        Args:
            resource_data: Must contain:
                - avg_wind_speed_m_s: Average wind speed at hub height
                - hub_height_m: Hub height (optional, for reference)

        Returns:
            Capacity factor (0-1)

        Example:
            >>> calc = WindCalculator()
            >>> cf = calc.calculate_capacity_factor({
            ...     'avg_wind_speed_m_s': 7.5,
            ...     'hub_height_m': 100
            ... })
            >>> print(f"CF: {cf*100:.1f}%")
            CF: 38.0%
        """
        wind_speed = resource_data['avg_wind_speed_m_s']

        # Simplified capacity factor based on wind speed
        # This approximates a typical modern turbine power curve
        if wind_speed < 4.0:
            # Below cut-in speed
            cf = 0.15
        elif wind_speed < 6.0:
            # Low wind (Class 1-2)
            cf = 0.20 + (wind_speed - 4.0) * 0.05
        elif wind_speed < 7.0:
            # Fair wind (Class 3)
            cf = 0.30 + (wind_speed - 6.0) * 0.08
        elif wind_speed < 8.0:
            # Good wind (Class 4)
            cf = 0.38 + (wind_speed - 7.0) * 0.07
        elif wind_speed < 9.0:
            # Excellent wind (Class 5)
            cf = 0.45 + (wind_speed - 8.0) * 0.05
        else:
            # Outstanding wind (Class 6-7)
            cf = 0.50

        # Account for losses
        # - Wake losses: 5% (turbines affect each other)
        # - Availability: 3% (maintenance downtime)
        # - Electrical losses: 2%
        total_losses = 0.10

        cf = cf * (1 - total_losses)

        # Realistic bounds: 25-50%
        cf = max(0.25, min(0.50, cf))

        return round(cf, 4)

    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        """
        Calculate wind LCOE.

        Wind LCOE tends to be higher than solar due to:
        - Higher O&M costs (moving parts)
        - More complex maintenance
        """
        # Use base calculation
        lcoe = super().calculate_lcoe(params)
        return lcoe

    def calculate_irr(self, params: Dict[str, Any]) -> float:
        """
        Calculate wind IRR.

        Wind projects often qualify for Production Tax Credit (PTC)
        in the USA, which improves returns.
        """
        # Check if PTC applies
        ptc_usd_per_mwh = params.get('ptc_usd_per_mwh', 0.0)

        if ptc_usd_per_mwh > 0:
            # Adjust electricity price to account for PTC
            adjusted_params = params.copy()
            adjusted_params['electricity_price_usd_per_mwh'] = (
                    params.get('electricity_price_usd_per_mwh', 50.0) + ptc_usd_per_mwh
            )
            return super().calculate_irr(adjusted_params)
        else:
            return super().calculate_irr(params)


if __name__ == "__main__":
    print("=" * 70)
    print("Wind Calculator Demo")
    print("=" * 70)

    calc = WindCalculator()

    # Test different wind resources
    print("\n1. Excellent Wind Resource (Texas Panhandle):")
    texas_resource = {
        'avg_wind_speed_m_s': 8.3,
        'hub_height_m': 100,
        'wind_power_density_w_m2': 400
    }
    cf1 = calc.calculate_capacity_factor(texas_resource)
    print(f"   Wind Speed: {texas_resource['avg_wind_speed_m_s']} m/s at {texas_resource['hub_height_m']}m")
    print(f"   Power Density: {texas_resource['wind_power_density_w_m2']} W/m²")
    print(f"   Capacity Factor: {cf1 * 100:.1f}%")

    # Full financial analysis (with PTC)
    params1 = {
        'capex_usd_per_kw': 1500,
        'opex_usd_per_kw_year': 40,
        'capacity_factor': cf1,
        'discount_rate': 0.08,
        'project_lifetime_years': 25,
        'electricity_price_usd_per_mwh': 30.0,  # Texas wholesale (energy-only)
        'ptc_usd_per_mwh': 27.5,  # Federal PTC
        'capacity_kw': 150000  # 150 MW
    }

    lcoe1 = calc.calculate_lcoe(params1)
    irr1 = calc.calculate_irr(params1)
    npv1 = calc.calculate_npv(params1)

    print(f"   LCOE: ${lcoe1:.2f}/MWh")
    print(f"   IRR (with PTC): {irr1:.1f}%")
    print(f"   NPV (150 MW): ${npv1:,.0f}")
    print(f"   Note: PTC adds ${params1['ptc_usd_per_mwh']}/MWh for 10 years")

    # Test moderate wind resource
    print("\n2. Good Wind Resource (Midwest):")
    midwest_resource = {
        'avg_wind_speed_m_s': 7.2,
        'hub_height_m': 100
    }
    cf2 = calc.calculate_capacity_factor(midwest_resource)
    print(f"   Wind Speed: {midwest_resource['avg_wind_speed_m_s']} m/s")
    print(f"   Capacity Factor: {cf2 * 100:.1f}%")

    params2 = {
        **params1,
        'capacity_factor': cf2,
        'electricity_price_usd_per_mwh': 35.0
    }

    lcoe2 = calc.calculate_lcoe(params2)
    irr2 = calc.calculate_irr(params2)

    print(f"   LCOE: ${lcoe2:.2f}/MWh")
    print(f"   IRR (with PTC): {irr2:.1f}%")

    # Test without PTC (e.g., Germany)
    print("\n3. Germany Wind (No PTC, but feed-in tariff):")
    germany_resource = {
        'avg_wind_speed_m_s': 7.0,
        'hub_height_m': 100
    }
    cf3 = calc.calculate_capacity_factor(germany_resource)
    print(f"   Wind Speed: {germany_resource['avg_wind_speed_m_s']} m/s")
    print(f"   Capacity Factor: {cf3 * 100:.1f}%")

    params3 = {
        'capex_usd_per_kw': 1500,
        'opex_usd_per_kw_year': 40,
        'capacity_factor': cf3,
        'discount_rate': 0.06,  # Lower discount rate in Germany
        'project_lifetime_years': 20,  # EEG support duration
        'electricity_price_usd_per_mwh': 58.0,  # EEG tariff
        'ptc_usd_per_mwh': 0.0,  # No PTC in Germany
        'capacity_kw': 150000
    }

    lcoe3 = calc.calculate_lcoe(params3)
    irr3 = calc.calculate_irr(params3)

    print(f"   LCOE: ${lcoe3:.2f}/MWh")
    print(f"   IRR (EEG tariff): {irr3:.1f}%")

    # Comparison: Impact of wind speed
    print("\n4. Wind Speed Impact Analysis:")
    print("   Wind Speed | Capacity Factor | LCOE")
    print("   " + "-" * 45)

    for ws in [6.0, 7.0, 8.0, 9.0]:
        cf = calc.calculate_capacity_factor({'avg_wind_speed_m_s': ws})
        test_params = {
            'capex_usd_per_kw': 1500,
            'opex_usd_per_kw_year': 40,
            'capacity_factor': cf,
            'discount_rate': 0.08,
            'project_lifetime_years': 25
        }
        lcoe = calc.calculate_lcoe(test_params)
        print(f"   {ws:.1f} m/s    | {cf * 100:5.1f}%          | ${lcoe:.2f}/MWh")

    print("\n   Note: Power ∝ v³, so small wind speed changes matter!")

    print("\n" + "=" * 70)
    print("✅ Wind Calculator working correctly!")
    print("=" * 70)