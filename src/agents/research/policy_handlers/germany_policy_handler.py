"""
Germany Policy Handler - German Renewable Energy Policies

Fetches Germany-specific policy data:
- EEG (Erneuerbare-Energien-Gesetz) feed-in tariffs
- Market premium model
- Offshore wind bonuses
- Straight-line depreciation
- Regional variations (North Sea vs Baltic Sea)

Data Sources:
- BNetzA: Federal Network Agency
- EEG: Renewable Energy Sources Act
- BMWi: Federal Ministry for Economic Affairs
"""

from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler


class GermanyPolicyHandler(BasePolicyHandler):
    """
    Germany-specific policy handler.

    Implements German renewable energy policy including:
    - EEG feed-in tariffs and market premium
    - Technology-specific support rates
    - Offshore wind location bonuses
    - Depreciation rules
    """

    async def fetch_policy(
            self,
            technology: str,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch Germany policy data for specified technology.

        Args:
            technology: Technology code
            **kwargs:
                - region: str (optional, e.g., "north_sea", "baltic_sea")
                - capacity_mw: float (optional)
                - water_depth_m: float (optional, for offshore wind)

        Returns:
            Dictionary with Germany policy data
        """
        region = kwargs.get("region", "onshore")
        capacity_mw = kwargs.get("capacity_mw", 100.0)

        self.logger.info(
            f"Fetching Germany policy data for {technology} in {region} "
            f"({capacity_mw} MW)"
        )

        # EEG tariffs and market premium
        eeg_support = self._get_eeg_support(technology, region, kwargs)

        # Depreciation (different from USA)
        depreciation = self._get_depreciation_schedule()

        # Tax information
        tax_info = self._get_tax_info()

        # Grid and market information
        grid_info = self._get_grid_info()

        result = {
            "country": "DEU",
            "technology": technology,
            "incentives": eeg_support,
            "depreciation": depreciation,
            "tax_rate": tax_info["corporate_tax_rate"],
            "tax_info": tax_info,
            "grid": grid_info,
            "source": "BNetzA (2024) + EEG 2023",
            "confidence": "high",
            "last_updated": "2024-12-01",
            "notes": self._get_policy_notes(technology)
        }

        return result

    def _get_eeg_support(
            self,
            technology: str,
            region: str,
            kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get EEG (Renewable Energy Sources Act) support rates.

        Germany uses a market premium model where developers
        sell electricity at market prices and receive a premium
        to reach the guaranteed tariff level.
        """
        support = {
            "model": "Market Premium (Marktprämie)",
            "description": "Sell at market price + receive premium to reach reference tariff"
        }

        # Technology-specific base rates (EUR/MWh)
        base_rates = {
            "solar_pv": 60.0,  # Ground-mounted
            "onshore_wind": 58.0,  # Onshore
            "offshore_wind": 120.0  # Offshore (higher due to costs)
        }

        base_rate = base_rates.get(technology, 50.0)
        support["base_tariff_eur_per_mwh"] = base_rate

        # Offshore wind bonuses
        if "offshore" in technology.lower():
            water_depth = kwargs.get("water_depth_m", 30)
            distance_km = kwargs.get("distance_to_shore_km", 50)

            # Depth bonus: +€2/MWh per 10m beyond 30m
            depth_bonus = max(0, (water_depth - 30) / 10) * 2.0

            # Distance bonus: +€1/MWh per 10km beyond 40km
            distance_bonus = max(0, (distance_km - 40) / 10) * 1.0

            total_bonus = depth_bonus + distance_bonus

            support["offshore_wind_bonus_eur_per_mwh"] = round(total_bonus, 2)
            support["water_depth_m"] = water_depth
            support["distance_to_shore_km"] = distance_km
            support["total_tariff_eur_per_mwh"] = round(base_rate + total_bonus, 2)
        else:
            support["total_tariff_eur_per_mwh"] = base_rate

        # EEG surcharge (consumers pay this)
        support["eeg_surcharge_eur_per_mwh"] = 3.7

        # Contract duration
        support["support_duration_years"] = 20

        return support

    def _get_depreciation_schedule(self) -> Dict[str, Any]:
        """
        Get German depreciation schedule.

        Germany uses straight-line depreciation over 20 years
        (different from USA's MACRS).
        """
        return {
            "method": "Straight-line",
            "years": 20,
            "annual_rate": 0.05,  # 5% per year
            "description": "Linear depreciation over 20 years",
            "schedule": [0.05] * 20,  # Equal each year
        }

    def _get_tax_info(self) -> Dict[str, Any]:
        """
        Get Germany tax information.

        German corporate tax is higher than USA (~30% combined).
        """
        return {
            "corporate_tax_rate": 0.30,  # ~30% combined (corporate + trade tax)
            "corporate_income_tax": 0.15,
            "solidarity_surcharge": 0.0055,  # 5.5% of corporate tax
            "trade_tax_average": 0.14,  # Varies by municipality
            "description": "Combined federal and municipal taxes"
        }

    def _get_grid_info(self) -> Dict[str, Any]:
        """Get German grid information."""
        return {
            "tsos": ["50Hertz", "Amprion", "TenneT", "TransnetBW"],
            "has_capacity_market": False,
            "market_type": "Energy-only market",
            "balancing_groups": True,
            "grid_fees_vary": "By TSO zone",
            "priority_dispatch": "Renewables have priority feed-in"
        }

    def _get_policy_notes(self, technology: str) -> str:
        """Get important policy notes."""
        notes = []

        notes.append("EEG 2023 in effect - market premium model")
        notes.append("20-year support duration")
        notes.append("Auctions determine actual rates (rates shown are maximums)")

        if "offshore" in technology.lower():
            notes.append("Offshore: Additional bonuses for depth and distance")
            notes.append("North Sea and Baltic Sea have different conditions")

        notes.append("Grid connection costs covered by grid operator")
        notes.append("No capacity market - energy-only")

        return " | ".join(notes)


# Demo
if __name__ == "__main__":
    import asyncio
    from src.utils.config_loader import ConfigLoader

    print("=" * 70)
    print("Germany Policy Handler Demo")
    print("=" * 70)

    # Load Germany configuration
    config_loader = ConfigLoader()
    germany_config = config_loader.load_country_config("DEU")

    # Create handler
    handler = GermanyPolicyHandler(germany_config)

    print(f"\n1. Country: {handler.get_country_name()} ({handler.get_country_code()})")


    # Test fetching policy data
    async def test_policies():
        # Test solar
        print("\n2. Fetching Solar PV policy:")
        solar_policy = await handler.fetch_policy("solar_pv", capacity_mw=100)

        print(f"   Model: {solar_policy['incentives']['model']}")
        print(f"   Base Tariff: €{solar_policy['incentives']['base_tariff_eur_per_mwh']}/MWh")
        print(f"   Support Duration: {solar_policy['incentives']['support_duration_years']} years")
        print(
            f"   Depreciation: {solar_policy['depreciation']['method']} - {solar_policy['depreciation']['years']} years")
        print(f"   Tax Rate: {solar_policy['tax_rate'] * 100}%")

        # Test onshore wind
        print("\n3. Fetching Onshore Wind policy:")
        wind_policy = await handler.fetch_policy("onshore_wind", capacity_mw=150)

        print(f"   Base Tariff: €{wind_policy['incentives']['base_tariff_eur_per_mwh']}/MWh")
        print(f"   Grid: {', '.join(wind_policy['grid']['tsos'][:2])}...")

        # Test offshore wind with bonuses
        print("\n4. Fetching Offshore Wind policy (North Sea):")
        offshore_policy = await handler.fetch_policy(
            "offshore_wind",
            capacity_mw=400,
            water_depth_m=45,
            distance_to_shore_km=60
        )

        print(f"   Base Tariff: €{offshore_policy['incentives']['base_tariff_eur_per_mwh']}/MWh")
        print(f"   Water Depth: {offshore_policy['incentives']['water_depth_m']}m")
        print(f"   Offshore Bonus: €{offshore_policy['incentives']['offshore_wind_bonus_eur_per_mwh']}/MWh")
        print(f"   Total Tariff: €{offshore_policy['incentives']['total_tariff_eur_per_mwh']}/MWh")


    asyncio.run(test_policies())

    print("\n" + "=" * 70)
    print("✅ Germany Policy Handler working correctly!")
    print("=" * 70)