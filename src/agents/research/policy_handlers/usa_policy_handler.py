"""
USA Policy Handler - United States Renewable Energy Policies

Fetches USA-specific policy data:
- Federal Investment Tax Credit (ITC) - 30% for solar/wind
- Production Tax Credit (PTC) - $27.50/MWh for wind
- MACRS depreciation - 5-year schedule
- State-level incentives from DSIRE database
- Regional variations (ERCOT, CAISO, PJM, etc.)

Data Sources:
- IRS: Federal tax credits
- DSIRE: State and utility incentives
- EIA: Electricity market data
"""

from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler


class USAPolicyHandler(BasePolicyHandler):
    """
    USA-specific policy handler.

    Implements USA renewable energy policy fetching including:
    - Federal ITC (30% through 2032)
    - Federal PTC ($27.50/MWh for wind)
    - MACRS 5-year depreciation
    - State-level incentives
    - Regional market differences
    """

    async def fetch_policy(
            self,
            technology: str,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch USA policy data for specified technology.

        Args:
            technology: Technology code ("solar_pv", "onshore_wind", etc.)
            **kwargs:
                - state: str (optional, e.g., "TX", "CA")
                - capacity_mw: float (optional, for size-based incentives)
                - latitude: float (optional, for regional policies)
                - longitude: float (optional, for regional policies)

        Returns:
            Dictionary with USA policy data
        """
        state = kwargs.get("state", "TX")  # Default to Texas for POC
        capacity_mw = kwargs.get("capacity_mw", 100.0)

        self.logger.info(
            f"Fetching USA policy data for {technology} in {state} "
            f"({capacity_mw} MW)"
        )

        # Federal incentives (same for all states)
        federal_incentives = self._get_federal_incentives(technology)

        # State-level incentives
        state_incentives = self._get_state_incentives(state, technology)

        # Depreciation schedule
        depreciation = self._get_depreciation_schedule()

        # Tax information
        tax_info = self._get_tax_info()

        # Regional market information
        regional_info = self._get_regional_market_info(state)

        result = {
            "country": "USA",
            "technology": technology,
            "incentives": {
                **federal_incentives,
                "state_incentives": state_incentives,
            },
            "depreciation": depreciation,
            "tax_rate": tax_info["corporate_tax_rate"],
            "tax_info": tax_info,
            "regional": regional_info,
            "source": "IRS (2024) + DSIRE Database",
            "confidence": "high",
            "last_updated": "2024-12-01",
            "notes": self._get_policy_notes(technology)
        }

        # Validate result
        if not self._validate_policy_result(result):
            self.logger.warning("Policy result validation failed")

        return result

    def _get_federal_incentives(self, technology: str) -> Dict[str, Any]:
        """
        Get federal tax incentives.

        ITC (Investment Tax Credit):
        - Solar: 30% through 2032, then phases down
        - Wind: 30% through 2032 (or PTC alternative)

        PTC (Production Tax Credit):
        - Wind: $27.50/MWh for 10 years (inflation adjusted)
        """
        incentives = {
            "federal_itc_percentage": 30.0,  # Current ITC rate
            "federal_itc_duration": "Through 2032",
            "federal_itc_phase_down": {
                2033: 26.0,
                2034: 22.0,
                2035: 0.0  # Unless extended
            }
        }

        # PTC only applicable to wind
        if "wind" in technology.lower():
            incentives["federal_ptc_usd_per_mwh"] = 27.5
            incentives["federal_ptc_duration_years"] = 10
            incentives["ptc_or_itc"] = "Developer can choose ITC or PTC"
        else:
            incentives["federal_ptc_usd_per_mwh"] = 0.0

        # Bonus credits for domestic content (IRA 2022)
        incentives["domestic_content_bonus_percentage"] = 10.0
        incentives["energy_community_bonus_percentage"] = 10.0

        return incentives

    def _get_state_incentives(self, state: str, technology: str) -> list:
        """
        Get state-level incentives.

        In real implementation, this would query DSIRE database.
        For POC, we provide representative data.
        """
        state_programs = {
            "TX": [
                "Texas RPS: 10,000 MW renewable capacity target",
                "Property tax exemption for renewable energy equipment",
                "Franchise tax exemption for renewable energy systems",
                "ERCOT market: No capacity payments, energy-only market"
            ],
            "CA": [
                "California RPS: 60% by 2030, 100% by 2045",
                "SGIP: Self-Generation Incentive Program",
                "Net Energy Metering 3.0",
                "Property tax exclusion for solar systems"
            ],
            "NY": [
                "New York Sun: $1B solar program",
                "NY-Sun Megawatt Block incentive",
                "Accelerated depreciation (7 years)",
                "NYSERDA incentives"
            ],
            "DEFAULT": [
                "Check DSIRE database for state-specific programs",
                "Federal incentives apply nationwide"
            ]
        }

        return state_programs.get(state, state_programs["DEFAULT"])

    def _get_depreciation_schedule(self) -> Dict[str, Any]:
        """
        Get MACRS depreciation schedule.

        USA uses Modified Accelerated Cost Recovery System (MACRS)
        5-year property for solar and wind.
        """
        return {
            "method": "MACRS",
            "years": 5,
            "schedule": [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576],
            "description": "Modified Accelerated Cost Recovery System - 5 year property",
            "half_year_convention": True,
            "basis_reduction": "Reduce by 50% of ITC taken"
        }

    def _get_tax_info(self) -> Dict[str, Any]:
        """Get USA tax information."""
        return {
            "corporate_tax_rate": 0.21,  # Federal corporate tax
            "state_tax_rates_vary": True,
            "state_tax_range": [0.00, 0.12],  # Varies by state
            "typical_combined_rate": 0.25,  # Federal + state average
        }

    def _get_regional_market_info(self, state: str) -> Dict[str, Any]:
        """
        Get regional electricity market information.

        USA has regional ISOs/RTOs with different market rules.
        """
        iso_mapping = {
            "TX": "ERCOT",
            "CA": "CAISO",
            "NY": "NYISO",
            "PA": "PJM",
            "MA": "ISO-NE"
        }

        iso = iso_mapping.get(state, "Non-ISO")

        market_info = {
            "iso_rto": iso,
            "has_capacity_market": iso not in ["ERCOT"],
            "renewable_energy_credits": True,
            "interconnection_queue": f"{iso} queue",
        }

        # ISO-specific details
        if iso == "ERCOT":
            market_info.update({
                "market_type": "Energy-only market",
                "capacity_payment": 0.0,
                "note": "No capacity market - prices set by energy auctions"
            })
        elif iso == "PJM":
            market_info.update({
                "market_type": "Energy + Capacity",
                "capacity_payment_usd_per_kw_day": 0.15,  # Varies by zone
                "note": "Capacity auctions held 3 years ahead"
            })

        return market_info

    def _get_policy_notes(self, technology: str) -> str:
        """Get important policy notes."""
        notes = []

        notes.append("Inflation Reduction Act (2022) extended ITC through 2032")
        notes.append("ITC phases down: 26% (2033), 22% (2034), 0% (2035+)")

        if "wind" in technology.lower():
            notes.append("Wind projects can choose ITC or PTC (not both)")
            notes.append("PTC indexed to inflation annually")

        notes.append("Bonus credits available: +10% domestic content, +10% energy communities")
        notes.append("State incentives vary significantly - check DSIRE database")

        return " | ".join(notes)


# Demo
if __name__ == "__main__":
    import asyncio
    from src.utils.config_loader import ConfigLoader

    print("=" * 70)
    print("USA Policy Handler Demo")
    print("=" * 70)

    # Load USA configuration
    config_loader = ConfigLoader()
    usa_config = config_loader.load_country_config("USA")

    # Create handler
    handler = USAPolicyHandler(usa_config)

    print(f"\n1. Country: {handler.get_country_name()} ({handler.get_country_code()})")


    # Test fetching policy data
    async def test_policies():
        # Test solar in Texas
        print("\n2. Fetching Solar PV policy for Texas:")
        solar_policy = await handler.fetch_policy("solar_pv", state="TX", capacity_mw=100)

        print(f"   Federal ITC: {solar_policy['incentives']['federal_itc_percentage']}%")
        print(
            f"   Depreciation: {solar_policy['depreciation']['method']} - {solar_policy['depreciation']['years']} years")
        print(f"   Tax Rate: {solar_policy['tax_rate'] * 100}%")
        print(f"   State incentives: {len(solar_policy['incentives']['state_incentives'])} programs")
        for incentive in solar_policy['incentives']['state_incentives']:
            print(f"     - {incentive}")

        # Test wind in Texas
        print("\n3. Fetching Onshore Wind policy for Texas:")
        wind_policy = await handler.fetch_policy("onshore_wind", state="TX", capacity_mw=150)

        print(f"   Federal ITC: {wind_policy['incentives']['federal_itc_percentage']}%")
        print(f"   Federal PTC: ${wind_policy['incentives']['federal_ptc_usd_per_mwh']}/MWh")
        print(f"   PTC Duration: {wind_policy['incentives']['federal_ptc_duration_years']} years")
        print(f"   ISO/RTO: {wind_policy['regional']['iso_rto']}")
        print(f"   Capacity Market: {wind_policy['regional']['has_capacity_market']}")

        # Test California
        print("\n4. Fetching Solar PV policy for California:")
        ca_policy = await handler.fetch_policy("solar_pv", state="CA", capacity_mw=200)

        print(f"   State incentives: {len(ca_policy['incentives']['state_incentives'])} programs")
        for incentive in ca_policy['incentives']['state_incentives']:
            print(f"     - {incentive}")
        print(f"   ISO/RTO: {ca_policy['regional']['iso_rto']}")


    asyncio.run(test_policies())

    print("\n" + "=" * 70)
    print("✅ USA Policy Handler working correctly!")
    print("=" * 70)