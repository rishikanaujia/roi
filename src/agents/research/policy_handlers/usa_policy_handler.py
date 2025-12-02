"""
USA Policy Handler - With Research Context Integration

Handles policy data for United States renewable energy projects.
NOW INCLUDES: Market research, recent policies, trends, opportunities!

Key Features:
- Federal ITC (Investment Tax Credit): 30%
- Federal PTC (Production Tax Credit): $27.50/MWh
- Bonus credits for domestic content and energy communities
- State-specific incentives (if applicable)
- COMPLETE market research context for AI insights
"""

from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler


class USAPolicyHandler(BasePolicyHandler):
    """
    USA policy handler with comprehensive research context.

    Provides:
    - Federal tax credits (ITC/PTC)
    - Bonus credits (domestic content, energy communities)
    - State incentives (extensible)
    - Market research (corporate PPAs, grid issues, auction results)
    - Recent policy updates (IRA details)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize USA policy handler.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)

        # USA-specific configuration
        self.federal_itc_rate = 0.30  # 30% ITC through 2032
        self.federal_ptc_rate = 27.5  # $27.50/MWh through 2032
        self.domestic_content_bonus = 0.10  # +10%
        self.energy_community_bonus = 0.10  # +10%

        self.logger.info("USA policy handler initialized with IRA provisions")

    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch USA policy data with research context.

        Args:
            technology: Technology type (solar_pv, onshore_wind, etc.)
            **kwargs: Additional parameters (state code, capacity, etc.)

        Returns:
            Complete policy data including research context
        """
        self.logger.info(f"Fetching USA policy data for {technology}")

        # Get base policy data (includes research context)
        result = self.get_policy_data()

        # Add USA-specific policy details based on technology
        if technology == "solar_pv":
            result.update({
                "federal_itc": self.federal_itc_rate * 100,  # Convert to percentage
                "federal_ptc": 0.0,  # Solar uses ITC, not PTC
                "bonus_credits": {
                    "domestic_content": self.domestic_content_bonus * 100,
                    "energy_community": self.energy_community_bonus * 100,
                    "description": "Additional 10% for domestic content + 10% for energy communities"
                },
                "tax_rate": 0.21,  # Federal corporate tax rate
                "depreciation": {
                    "macrs": True,
                    "period_years": 5,
                    "description": "5-year MACRS depreciation"
                },
                "confidence": "high",
                "policy_type": "Investment Tax Credit (ITC)",
                "credit_period": "Through 2032, then phase down"
            })

        elif "wind" in technology:
            result.update({
                "federal_itc": 0.0,  # Wind typically uses PTC, not ITC
                "federal_ptc": self.federal_ptc_rate,  # $27.50/MWh
                "bonus_credits": {
                    "domestic_content": self.domestic_content_bonus * 100,
                    "energy_community": self.energy_community_bonus * 100,
                    "description": "Additional 10% for domestic content + 10% for energy communities (applied to PTC base rate)"
                },
                "tax_rate": 0.21,
                "depreciation": {
                    "macrs": True,
                    "period_years": 5,
                    "description": "5-year MACRS depreciation"
                },
                "confidence": "high",
                "policy_type": "Production Tax Credit (PTC)",
                "credit_period": "10 years of production, through 2032 start date"
            })

        else:
            # Default for other technologies
            result.update({
                "federal_itc": self.federal_itc_rate * 100,
                "federal_ptc": 0.0,
                "tax_rate": 0.21,
                "confidence": "medium"
            })

        # Add state-specific incentives if provided
        state = kwargs.get('state')
        if state:
            state_incentives = self._get_state_incentives(state, technology)
            if state_incentives:
                result['state_incentives'] = state_incentives
                self.logger.info(f"Added state incentives for {state}")

        # Log what we're returning
        self.logger.info(
            f"USA policy data compiled: ITC={result.get('federal_itc', 0)}%, "
            f"PTC=${result.get('federal_ptc', 0)}/MWh"
        )

        if result.get('research_context'):
            self.logger.info(
                f"Including market research: "
                f"{len(result['research_context'].get('sources', []))} sources"
            )

        return result

    def _get_state_incentives(
            self,
            state: str,
            technology: str
    ) -> Dict[str, Any]:
        """
        Get state-specific incentives.

        This is extensible - add more states as needed.

        Args:
            state: State code (TX, CA, NY, etc.)
            technology: Technology type

        Returns:
            State incentives dict or empty dict
        """
        # State incentive database (extensible)
        state_incentives = {
            "TX": {
                "solar_pv": {
                    "property_tax_exemption": True,
                    "sales_tax_exemption": True,
                    "description": "Texas offers property tax and sales tax exemptions for renewable energy systems"
                },
                "onshore_wind": {
                    "property_tax_exemption": True,
                    "sales_tax_exemption": True,
                    "description": "Texas offers property tax and sales tax exemptions for wind energy systems"
                }
            },
            "CA": {
                "solar_pv": {
                    "sgip_storage_incentive": True,
                    "net_metering": True,
                    "description": "California offers SGIP storage incentives and net metering programs"
                }
            },
            "NY": {
                "solar_pv": {
                    "ny_sun_incentive": True,
                    "description": "New York Sun program provides upfront incentives for solar installations"
                },
                "onshore_wind": {
                    "offshore_wind_target": True,
                    "description": "New York has aggressive offshore wind targets with procurement support"
                }
            }
        }

        # Get state and technology specific incentives
        state_data = state_incentives.get(state, {})
        tech_incentives = state_data.get(technology, {})

        if tech_incentives:
            self.logger.debug(f"Found state incentives for {state} - {technology}")

        return tech_incentives

    def calculate_itc_value(
            self,
            project_capex: float,
            include_bonuses: bool = True
    ) -> Dict[str, float]:
        """
        Calculate ITC value including bonuses.

        Args:
            project_capex: Project capital expenditure
            include_bonuses: Whether to include bonus credits

        Returns:
            Dictionary with ITC calculations
        """
        base_itc = project_capex * self.federal_itc_rate

        if include_bonuses:
            # Domestic content bonus
            dc_bonus = project_capex * self.domestic_content_bonus
            # Energy community bonus
            ec_bonus = project_capex * self.energy_community_bonus

            total_itc = base_itc + dc_bonus + ec_bonus
            effective_rate = (total_itc / project_capex) * 100
        else:
            total_itc = base_itc
            effective_rate = self.federal_itc_rate * 100

        return {
            "base_itc": base_itc,
            "domestic_content_bonus": dc_bonus if include_bonuses else 0,
            "energy_community_bonus": ec_bonus if include_bonuses else 0,
            "total_itc": total_itc,
            "effective_rate_percent": effective_rate
        }

    def calculate_ptc_value(
            self,
            annual_generation_mwh: float,
            include_bonuses: bool = True,
            years: int = 10
    ) -> Dict[str, float]:
        """
        Calculate PTC value over production period.

        Args:
            annual_generation_mwh: Annual generation in MWh
            include_bonuses: Whether to include bonus credits
            years: Number of years (typically 10)

        Returns:
            Dictionary with PTC calculations
        """
        base_ptc_rate = self.federal_ptc_rate

        if include_bonuses:
            # Bonuses are additive to base rate
            bonus_rate = base_ptc_rate * (
                    self.domestic_content_bonus + self.energy_community_bonus
            )
            total_rate = base_ptc_rate + bonus_rate
        else:
            total_rate = base_ptc_rate

        annual_ptc = annual_generation_mwh * total_rate
        total_ptc = annual_ptc * years

        return {
            "base_rate_per_mwh": base_ptc_rate,
            "bonus_rate_per_mwh": bonus_rate if include_bonuses else 0,
            "total_rate_per_mwh": total_rate,
            "annual_ptc_value": annual_ptc,
            "total_ptc_value_10years": total_ptc
        }


# Demo / Testing
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("🇺🇸 USA Policy Handler Demo - With Research Context")
    print("=" * 70)


    async def demo():
        # Create handler
        config = {
            "country": {
                "code": "USA",
                "name": "United States"
            }
        }

        handler = USAPolicyHandler(config)

        print("\n" + "=" * 70)
        print("TEST 1: Solar PV Policy")
        print("=" * 70)

        solar_policy = await handler.fetch_policy("solar_pv", state="TX")

        print(f"\n💰 Federal Incentives:")
        print(f"  ITC: {solar_policy['federal_itc']}%")
        print(f"  PTC: ${solar_policy['federal_ptc']}/MWh")
        print(f"  Bonus Credits: {solar_policy['bonus_credits']['description']}")

        if solar_policy.get('state_incentives'):
            print(f"\n🏛️  State Incentives (Texas):")
            print(f"  {solar_policy['state_incentives']['description']}")

        if solar_policy.get('research_context'):
            research = solar_policy['research_context']
            print(f"\n📊 Market Research Available:")
            print(f"  Market Overview: {len(research.get('market_overview', ''))} chars")
            print(f"  Recent Policies: {len(research.get('recent_policies', ''))} chars")
            print(f"  Key Trends: {len(research.get('key_trends', ''))} chars")
            print(f"  Sources: {len(research.get('sources', []))} URLs")

            print(f"\n📈 Market Overview (excerpt):")
            print(f"  {research.get('market_overview', '')[:200]}...")

            print(f"\n🔗 Sources:")
            for source in research.get('sources', [])[:3]:
                print(f"  - {source}")

        print("\n" + "=" * 70)
        print("TEST 2: Wind Policy")
        print("=" * 70)

        wind_policy = await handler.fetch_policy("onshore_wind", state="TX")

        print(f"\n💰 Federal Incentives:")
        print(f"  ITC: {wind_policy['federal_itc']}%")
        print(f"  PTC: ${wind_policy['federal_ptc']}/MWh")
        print(f"  Credit Period: {wind_policy['credit_period']}")

        print("\n" + "=" * 70)
        print("TEST 3: ITC Calculation")
        print("=" * 70)

        project_capex = 150_000_000  # $150M project
        itc_calc = handler.calculate_itc_value(project_capex, include_bonuses=True)

        print(f"\n💵 ITC Calculation for ${project_capex:,} project:")
        print(f"  Base ITC (30%): ${itc_calc['base_itc']:,.0f}")
        print(f"  Domestic Content Bonus: ${itc_calc['domestic_content_bonus']:,.0f}")
        print(f"  Energy Community Bonus: ${itc_calc['energy_community_bonus']:,.0f}")
        print(f"  Total ITC: ${itc_calc['total_itc']:,.0f}")
        print(f"  Effective Rate: {itc_calc['effective_rate_percent']:.1f}%")

        print("\n" + "=" * 70)
        print("✅ USA Policy Handler Working with Research Context!")
        print("=" * 70)


    asyncio.run(demo())