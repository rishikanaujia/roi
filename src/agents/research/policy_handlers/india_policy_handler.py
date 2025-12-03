"""
India Policy Handler - With Research Context Integration

Handles policy data for India renewable energy projects.
NOW INCLUDES: Market research, PLI scheme, auction results, state opportunities!

Key Features:
- Generation Based Incentive (GBI)
- Accelerated depreciation (40%)
- PLI scheme (20% capital subsidy)
- State-specific policies
- COMPLETE market research context for AI insights
"""

from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler


class IndiaPolicyHandler(BasePolicyHandler):
    """
    India policy handler with comprehensive research context.

    Provides:
    - Generation Based Incentive (GBI)
    - Accelerated depreciation
    - PLI scheme details
    - State incentives (Gujarat, Rajasthan, Karnataka, Tamil Nadu)
    - Market research (SECI auctions, DISCOMs, green hydrogen)
    - Recent policy updates (PM-KUSUM, hydrogen mission)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize India policy handler.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)

        # India-specific configuration (INR per kWh)
        self.gbi_solar = 2.5  # ₹2.50/kWh for solar
        self.gbi_wind = 3.0  # ₹3.00/kWh for wind
        self.accelerated_depreciation = 0.40  # 40%
        self.corporate_tax_rate = 0.25  # 25% for new manufacturing companies

        # PLI scheme (Production Linked Incentive)
        self.pli_module_subsidy = 0.20  # 20% capital subsidy for modules
        self.pli_cell_subsidy = 0.15  # 15% capital subsidy for cells

        self.logger.info("India policy handler initialized with PLI scheme provisions")

    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch India policy data with research context.

        Args:
            technology: Technology type (solar_pv, onshore_wind, etc.)
            **kwargs: Additional parameters (state, capacity, etc.)

        Returns:
            Complete policy data including research context
        """
        self.logger.info(f"Fetching India policy data for {technology}")

        # Get base policy data (includes research context)
        result = self.get_policy_data()

        # Add India-specific policy details based on technology
        if technology == "solar_pv":
            result.update({
                "gbi_rate": self.gbi_solar,  # ₹2.50/kWh
                "gbi_currency": "INR",
                "gbi_period_years": 10,
                "accelerated_depreciation": self.accelerated_depreciation * 100,
                "corporate_tax_rate": self.corporate_tax_rate * 100,
                "pli_scheme": {
                    "module_subsidy": self.pli_module_subsidy * 100,
                    "cell_subsidy": self.pli_cell_subsidy * 100,
                    "description": "PLI scheme offers 20% subsidy for modules, 15% for cells",
                    "deadline": "Apply before March 2025"
                },
                "confidence": "high",
                "policy_type": "Generation Based Incentive (GBI) + Accelerated Depreciation",
                "incentive_period": "10 years generation incentive"
            })

        elif "wind" in technology:
            result.update({
                "gbi_rate": self.gbi_wind,  # ₹3.00/kWh
                "gbi_currency": "INR",
                "gbi_period_years": 10,
                "accelerated_depreciation": self.accelerated_depreciation * 100,
                "corporate_tax_rate": self.corporate_tax_rate * 100,
                "confidence": "high",
                "policy_type": "Generation Based Incentive (GBI) + Accelerated Depreciation",
                "incentive_period": "10 years generation incentive"
            })

        else:
            # Default for other technologies
            result.update({
                "gbi_rate": self.gbi_solar,
                "gbi_currency": "INR",
                "accelerated_depreciation": self.accelerated_depreciation * 100,
                "corporate_tax_rate": self.corporate_tax_rate * 100,
                "confidence": "medium"
            })

        # Add state-specific incentives if provided
        state = kwargs.get('state')
        if state:
            state_incentives = self._get_state_incentives(state, technology)
            if state_incentives:
                result['state_incentives'] = state_incentives
                self.logger.info(f"Added state incentives for {state}")

        # Add recent auction results context
        result['recent_auctions'] = self._get_recent_auction_results(technology)

        # Log what we're returning
        self.logger.info(
            f"India policy data compiled: GBI=₹{result.get('gbi_rate', 0)}/kWh, "
            f"AD={result.get('accelerated_depreciation', 0)}%"
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

        India has significant state-level policy variation.

        Args:
            state: State name (Gujarat, Rajasthan, Karnataka, Tamil Nadu, etc.)
            technology: Technology type

        Returns:
            State incentives dict or empty dict
        """
        # State incentive database
        state_incentives = {
            "Gujarat": {
                "solar_pv": {
                    "land_allocation": True,
                    "single_window_clearance": True,
                    "transmission_waiver": True,
                    "renewable_energy_zone": "30 GW zone with dedicated transmission",
                    "description": "Gujarat offers dedicated renewable zones with plug-and-play infrastructure, best grid connectivity in India"
                },
                "onshore_wind": {
                    "land_allocation": True,
                    "single_window_clearance": True,
                    "transmission_waiver": True,
                    "offshore_wind_zone": "30 GW offshore zone identified",
                    "description": "Gujarat leading offshore wind development with first auction Q1 2025"
                }
            },
            "Rajasthan": {
                "solar_pv": {
                    "mega_solar_parks": True,
                    "land_lease_facilitation": True,
                    "wheeling_charges_waiver": True,
                    "description": "Rajasthan's Ultra Mega Renewable Energy Power Parks offer plug-and-play infrastructure, excellent solar resource"
                }
            },
            "Karnataka": {
                "solar_pv": {
                    "rooftop_solar_incentive": True,
                    "open_access_facilitation": True,
                    "net_metering": True,
                    "commercial_tariff": "₹5/kWh C&I rooftop tariffs",
                    "description": "Karnataka offers attractive C&I rooftop economics with ₹5/kWh tariffs, strong distributed solar market"
                }
            },
            "Tamil Nadu": {
                "onshore_wind": {
                    "wind_resource_zones": True,
                    "land_allocation": True,
                    "description": "Tamil Nadu has excellent wind corridors, mature supply chain ecosystem"
                }
            }
        }

        # Get state and technology specific incentives
        state_data = state_incentives.get(state, {})
        tech_incentives = state_data.get(technology, {})

        if tech_incentives:
            self.logger.debug(f"Found state incentives for {state} - {technology}")

        return tech_incentives

    def _get_recent_auction_results(self, technology: str) -> Dict[str, Any]:
        """
        Get recent auction results for context.

        Args:
            technology: Technology type

        Returns:
            Recent auction results
        """
        auction_results = {
            "solar_pv": {
                "seci_solar": "₹2.44-2.53/kWh",
                "gujarat_solar": "₹2.39/kWh",
                "karnataka_solar": "₹2.50/kWh",
                "manufacturing_linked": "₹2.40/kWh (with domestic modules)",
                "description": "Recent SECI tenders clearing at ₹2.44-2.53/kWh"
            },
            "onshore_wind": {
                "seci_wind": "₹2.77-2.93/kWh",
                "hybrid": "₹2.67-2.85/kWh",
                "description": "Wind auctions clearing at ₹2.77-2.93/kWh"
            },
            "hybrid": {
                "solar_wind_hybrid": "₹2.67-2.85/kWh",
                "rtc_firm_power": "₹3.62-4.04/kWh",
                "description": "Round-the-clock (RTC) renewable tenders at ₹3.62-4.04/kWh"
            }
        }

        return auction_results.get(technology, {})

    def calculate_gbi_value(
            self,
            annual_generation_kwh: float,
            technology: str = "solar_pv",
            years: int = 10
    ) -> Dict[str, float]:
        """
        Calculate GBI (Generation Based Incentive) value.

        Args:
            annual_generation_kwh: Annual generation in kWh
            technology: Technology type (affects GBI rate)
            years: Number of years (typically 10)

        Returns:
            Dictionary with GBI calculations
        """
        if technology == "solar_pv":
            gbi_rate = self.gbi_solar
        elif "wind" in technology:
            gbi_rate = self.gbi_wind
        else:
            gbi_rate = self.gbi_solar

        annual_gbi = annual_generation_kwh * gbi_rate
        total_gbi = annual_gbi * years

        # Convert to USD for comparison (approximate: 1 USD = 83 INR)
        usd_exchange_rate = 83
        annual_gbi_usd = annual_gbi / usd_exchange_rate
        total_gbi_usd = total_gbi / usd_exchange_rate

        return {
            "gbi_rate_inr_per_kwh": gbi_rate,
            "annual_gbi_inr": annual_gbi,
            "total_gbi_10years_inr": total_gbi,
            "annual_gbi_usd": annual_gbi_usd,
            "total_gbi_10years_usd": total_gbi_usd,
            "currency": "INR",
            "years": years
        }

    def calculate_pli_value(
            self,
            project_capex: float,
            uses_domestic_modules: bool = True
    ) -> Dict[str, float]:
        """
        Calculate PLI (Production Linked Incentive) value.

        Args:
            project_capex: Project capital expenditure
            uses_domestic_modules: Whether project uses domestic modules

        Returns:
            Dictionary with PLI calculations
        """
        if not uses_domestic_modules:
            return {
                "module_subsidy": 0,
                "total_pli": 0,
                "effective_capex": project_capex,
                "note": "PLI only available for domestic module usage"
            }

        module_subsidy = project_capex * self.pli_module_subsidy
        effective_capex = project_capex - module_subsidy

        return {
            "module_subsidy": module_subsidy,
            "subsidy_rate": self.pli_module_subsidy * 100,
            "total_pli": module_subsidy,
            "original_capex": project_capex,
            "effective_capex": effective_capex,
            "savings_percent": (module_subsidy / project_capex) * 100,
            "deadline": "Apply before March 2025"
        }

    def calculate_accelerated_depreciation_benefit(
            self,
            project_capex: float
    ) -> Dict[str, float]:
        """
        Calculate accelerated depreciation tax benefit.

        Args:
            project_capex: Project capital expenditure

        Returns:
            Dictionary with depreciation benefit calculations
        """
        # First year depreciation
        year1_depreciation = project_capex * self.accelerated_depreciation

        # Tax benefit (at corporate tax rate)
        tax_benefit = year1_depreciation * self.corporate_tax_rate

        # Present value benefit (assuming discount rate of 10%)
        discount_rate = 0.10
        pv_benefit = tax_benefit / (1 + discount_rate)

        return {
            "year1_depreciation": year1_depreciation,
            "depreciation_rate": self.accelerated_depreciation * 100,
            "tax_benefit": tax_benefit,
            "tax_rate": self.corporate_tax_rate * 100,
            "pv_benefit": pv_benefit,
            "benefit_as_percent_capex": (tax_benefit / project_capex) * 100
        }


# Demo / Testing
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("🇮🇳 India Policy Handler Demo - With Research Context")
    print("=" * 70)


    async def demo():
        # Create handler
        config = {
            "country": {
                "code": "IND",
                "name": "India"
            }
        }

        handler = IndiaPolicyHandler(config)

        print("\n" + "=" * 70)
        print("TEST 1: Solar PV Policy (Gujarat)")
        print("=" * 70)

        solar_policy = await handler.fetch_policy("solar_pv", state="Gujarat")

        print(f"\n💰 National Incentives:")
        print(f"  GBI Rate: ₹{solar_policy['gbi_rate']}/kWh")
        print(f"  GBI Period: {solar_policy['gbi_period_years']} years")
        print(f"  Accelerated Depreciation: {solar_policy['accelerated_depreciation']}%")

        if solar_policy.get('pli_scheme'):
            pli = solar_policy['pli_scheme']
            print(f"\n🏭 PLI Scheme:")
            print(f"  {pli['description']}")
            print(f"  Deadline: {pli['deadline']}")

        if solar_policy.get('state_incentives'):
            print(f"\n🏛️  State Incentives (Gujarat):")
            print(f"  {solar_policy['state_incentives']['description']}")

        if solar_policy.get('recent_auctions'):
            print(f"\n📊 Recent Auction Results:")
            auctions = solar_policy['recent_auctions']
            print(f"  SECI Solar: {auctions.get('seci_solar', 'N/A')}")
            print(f"  Gujarat Solar: {auctions.get('gujarat_solar', 'N/A')}")

        if solar_policy.get('research_context'):
            research = solar_policy['research_context']
            print(f"\n📊 Market Research Available:")
            print(f"  Market Overview: {len(research.get('market_overview', ''))} chars")
            print(f"  Recent Policies: {len(research.get('recent_policies', ''))} chars")
            print(f"  Opportunities: {len(research.get('opportunities', ''))} chars")
            print(f"  Sources: {len(research.get('sources', []))} URLs")

            print(f"\n📈 Market Overview (excerpt):")
            print(f"  {research.get('market_overview', '')[:200]}...")

            print(f"\n🎯 Opportunities (excerpt):")
            print(f"  {research.get('opportunities', '')[:200]}...")

        print("\n" + "=" * 70)
        print("TEST 2: GBI Calculation")
        print("=" * 70)

        annual_generation = 175_000_000  # 175 GWh = 175,000 MWh
        gbi_calc = handler.calculate_gbi_value(annual_generation, "solar_pv", 10)

        print(f"\n💵 GBI Calculation for {annual_generation:,} kWh/year:")
        print(f"  GBI Rate: ₹{gbi_calc['gbi_rate_inr_per_kwh']}/kWh")
        print(f"  Annual GBI: ₹{gbi_calc['annual_gbi_inr']:,.0f} (${gbi_calc['annual_gbi_usd']:,.0f})")
        print(
            f"  Total 10-year GBI: ₹{gbi_calc['total_gbi_10years_inr']:,.0f} (${gbi_calc['total_gbi_10years_usd']:,.0f})")

        print("\n" + "=" * 70)
        print("TEST 3: PLI Scheme Calculation")
        print("=" * 70)

        project_capex = 5_000_000_000  # ₹500 crore = ₹5 billion
        pli_calc = handler.calculate_pli_value(project_capex, uses_domestic_modules=True)

        print(f"\n💰 PLI Calculation for ₹{project_capex:,} project:")
        print(f"  Module Subsidy ({pli_calc['subsidy_rate']}%): ₹{pli_calc['module_subsidy']:,.0f}")
        print(f"  Effective CapEx: ₹{pli_calc['effective_capex']:,.0f}")
        print(f"  Savings: {pli_calc['savings_percent']:.1f}%")
        print(f"  Deadline: {pli_calc['deadline']}")

        print("\n" + "=" * 70)
        print("✅ India Policy Handler Working with Research Context!")
        print("=" * 70)


    asyncio.run(demo())