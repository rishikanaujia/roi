"""
Germany Policy Handler - With Research Context Integration

Handles policy data for Germany renewable energy projects.
NOW INCLUDES: Market research, EEG auctions, offshore wind, grid constraints!

Key Features:
- EEG (Renewable Energy Act) feed-in tariffs
- Auction-based pricing for large projects
- Contract-for-Difference (CfD) for offshore wind
- Rooftop solar incentives
- COMPLETE market research context for AI insights
"""

from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler


class GermanyPolicyHandler(BasePolicyHandler):
    """
    Germany policy handler with comprehensive research context.

    Provides:
    - EEG 2023 auction results
    - Feed-in tariffs for rooftop solar
    - Contract-for-Difference (CfD) for offshore wind
    - Innovation auction structures
    - Market research (offshore wind expansion, grid constraints, hydrogen)
    - Recent policy updates (EEG reform, CfD model)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Germany policy handler.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)

        # Germany-specific configuration (EUR cents per kWh)
        # Feed-in tariffs (rooftop solar)
        self.fit_small_rooftop = 8.20  # €8.20¢/kWh for <10kW
        self.fit_medium_rooftop = 7.10  # €7.10¢/kWh for 10-40kW
        self.fit_large_rooftop = 5.80  # €5.80¢/kWh for >40kW

        # Auction-based pricing (large ground-mount projects)
        self.solar_auction_avg = 6.0  # €6.0¢/kWh average
        self.onshore_wind_auction_avg = 6.5  # €6.5¢/kWh average
        self.offshore_wind_auction_avg = 5.8  # €5.8¢/kWh average (or zero-subsidy)

        # Tax rates
        self.corporate_tax_rate = 0.30  # ~30% effective (includes trade tax)

        self.logger.info("Germany policy handler initialized with EEG 2023 provisions")

    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch Germany policy data with research context.

        Args:
            technology: Technology type (solar_pv, onshore_wind, offshore_wind)
            **kwargs: Additional parameters (capacity, location, etc.)

        Returns:
            Complete policy data including research context
        """
        self.logger.info(f"Fetching Germany policy data for {technology}")

        # Get base policy data (includes research context)
        result = self.get_policy_data()

        # Get capacity (determines auction vs feed-in tariff)
        capacity_mw = kwargs.get('capacity_mw', 1.0)

        # Add Germany-specific policy details based on technology
        if technology == "solar_pv":
            if capacity_mw < 0.75:  # <750 kW - rooftop, feed-in tariff
                if capacity_mw < 0.01:  # <10 kW
                    tariff = self.fit_small_rooftop
                    tariff_type = "Small rooftop (<10kW)"
                elif capacity_mw < 0.04:  # 10-40 kW
                    tariff = self.fit_medium_rooftop
                    tariff_type = "Medium rooftop (10-40kW)"
                else:
                    tariff = self.fit_large_rooftop
                    tariff_type = "Large rooftop (>40kW)"

                result.update({
                    "eeg_tariff": tariff,
                    "eeg_currency": "EUR_cents",
                    "tariff_period_years": 20,
                    "tariff_type": tariff_type,
                    "mechanism": "Feed-in Tariff (FIT)",
                    "confidence": "high"
                })
            else:  # >750 kW - auction-based
                result.update({
                    "eeg_tariff": self.solar_auction_avg,
                    "eeg_currency": "EUR_cents",
                    "tariff_period_years": 20,
                    "tariff_type": "Ground-mount solar (auction)",
                    "mechanism": "Competitive Auction",
                    "auction_range": "€5.15-6.40¢/kWh",
                    "confidence": "high"
                })

        elif technology == "onshore_wind":
            result.update({
                "eeg_tariff": self.onshore_wind_auction_avg,
                "eeg_currency": "EUR_cents",
                "tariff_period_years": 20,
                "tariff_type": "Onshore wind (auction)",
                "mechanism": "Competitive Auction",
                "auction_range": "€5.95-7.35¢/kWh",
                "confidence": "high",
                "land_requirement": "2% of land area designated for wind development"
            })

        elif technology == "offshore_wind":
            result.update({
                "eeg_tariff": self.offshore_wind_auction_avg,
                "eeg_currency": "EUR_cents",
                "tariff_period_years": 20,
                "tariff_type": "Offshore wind (CfD model)",
                "mechanism": "Contract-for-Difference (CfD)",
                "auction_range": "€5.45-6.20¢/kWh (North Sea/Baltic)",
                "zero_subsidy_trend": "Many projects bidding zero-subsidy",
                "confidence": "very_high",
                "note": "Priority grid connection, 20-year revenue stabilization"
            })

        else:
            # Default for other technologies
            result.update({
                "eeg_tariff": self.solar_auction_avg,
                "eeg_currency": "EUR_cents",
                "tariff_period_years": 20,
                "confidence": "medium"
            })

        # Add tax information
        result['tax_rate'] = self.corporate_tax_rate * 100

        # Add state/region-specific context if provided
        state = kwargs.get('state')
        if state:
            region_context = self._get_regional_context(state, technology)
            if region_context:
                result['regional_context'] = region_context
                self.logger.info(f"Added regional context for {state}")

        # Add recent auction results
        result['recent_auctions'] = self._get_recent_auction_results(technology)

        # Log what we're returning
        self.logger.info(
            f"Germany policy data compiled: EEG Tariff=€{result.get('eeg_tariff', 0)}¢/kWh, "
            f"Mechanism={result.get('mechanism', 'Unknown')}"
        )

        if result.get('research_context'):
            self.logger.info(
                f"Including market research: "
                f"{len(result['research_context'].get('sources', []))} sources"
            )

        return result

    def _get_regional_context(
            self,
            state: str,
            technology: str
    ) -> Dict[str, Any]:
        """
        Get regional context for German states.

        Args:
            state: German state (Schleswig-Holstein, Bavaria, etc.)
            technology: Technology type

        Returns:
            Regional context dict or empty dict
        """
        # Regional context database
        regional_context = {
            "Schleswig-Holstein": {
                "onshore_wind": {
                    "wind_resource": "Excellent",
                    "capacity_installed": "High density",
                    "description": "Northern Germany, best wind resources in country, 45-50% capacity factors"
                },
                "offshore_wind": {
                    "wind_resource": "Excellent",
                    "proximity": "North Sea access",
                    "description": "Direct access to North Sea offshore zones, mature supply chain"
                }
            },
            "Lower Saxony": {
                "onshore_wind": {
                    "wind_resource": "Excellent",
                    "capacity_installed": "Very high",
                    "description": "Major wind energy state, excellent resource and infrastructure"
                }
            },
            "Bavaria": {
                "solar_pv": {
                    "solar_resource": "Good",
                    "capacity_installed": "High",
                    "description": "Southern Germany, strong solar resource, high rooftop penetration"
                }
            },
            "Baden-Württemberg": {
                "solar_pv": {
                    "solar_resource": "Good",
                    "capacity_installed": "High",
                    "rooftop_focus": True,
                    "description": "Southern Germany, strong residential solar market"
                }
            },
            "North Rhine-Westphalia": {
                "solar_pv": {
                    "solar_resource": "Moderate",
                    "capacity_installed": "High",
                    "industrial_demand": "Very high",
                    "description": "Industrial heartland, high electricity demand"
                }
            }
        }

        # Get state and technology specific context
        state_data = regional_context.get(state, {})
        tech_context = state_data.get(technology, {})

        if tech_context:
            self.logger.debug(f"Found regional context for {state} - {technology}")

        return tech_context

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
                "ground_mount_solar": "€5.15-6.40¢/kWh (20-year)",
                "rooftop_small": "€8.20¢/kWh (<10kW)",
                "rooftop_medium": "€7.10¢/kWh (10-40kW)",
                "rooftop_large": "€5.80¢/kWh (>40kW)",
                "innovation_solar_storage": "€7.90-9.20¢/kWh",
                "description": "Bundesnetzagentur 2024 auctions showing stable pricing"
            },
            "onshore_wind": {
                "onshore_wind": "€5.95-7.35¢/kWh (20-year)",
                "description": "Onshore wind auctions moderately oversubscribed"
            },
            "offshore_wind": {
                "north_sea": "€5.45¢/kWh average (many zero-subsidy bids)",
                "baltic_sea": "€6.20¢/kWh average",
                "description": "Offshore wind extremely competitive, many projects bid zero-subsidy competing for grid connection rights",
                "zero_subsidy_model": "Projects banking on merchant revenues from volatile wholesale market"
            }
        }

        return auction_results.get(technology, {})

    def calculate_eeg_value(
            self,
            annual_generation_kwh: float,
            eeg_rate_cents: float = None,
            technology: str = "solar_pv",
            years: int = 20
    ) -> Dict[str, float]:
        """
        Calculate EEG (feed-in tariff) value.

        Args:
            annual_generation_kwh: Annual generation in kWh
            eeg_rate_cents: EEG rate in EUR cents (if None, uses default)
            technology: Technology type
            years: Number of years (typically 20)

        Returns:
            Dictionary with EEG calculations
        """
        if eeg_rate_cents is None:
            if technology == "solar_pv":
                eeg_rate_cents = self.solar_auction_avg
            elif technology == "onshore_wind":
                eeg_rate_cents = self.onshore_wind_auction_avg
            elif technology == "offshore_wind":
                eeg_rate_cents = self.offshore_wind_auction_avg
            else:
                eeg_rate_cents = self.solar_auction_avg

        # Convert cents to EUR
        eeg_rate_eur = eeg_rate_cents / 100

        annual_eeg = annual_generation_kwh * eeg_rate_eur
        total_eeg = annual_eeg * years

        # Convert to USD for comparison (approximate: 1 EUR = 1.08 USD)
        usd_exchange_rate = 1.08
        annual_eeg_usd = annual_eeg * usd_exchange_rate
        total_eeg_usd = total_eeg * usd_exchange_rate

        return {
            "eeg_rate_eur_cents_per_kwh": eeg_rate_cents,
            "eeg_rate_eur_per_kwh": eeg_rate_eur,
            "annual_eeg_eur": annual_eeg,
            "total_eeg_20years_eur": total_eeg,
            "annual_eeg_usd": annual_eeg_usd,
            "total_eeg_20years_usd": total_eeg_usd,
            "currency": "EUR",
            "years": years
        }

    def calculate_cfd_benefit(
            self,
            annual_generation_mwh: float,
            strike_price_eur_mwh: float = 58.0,
            market_price_eur_mwh: float = 80.0,
            years: int = 20
    ) -> Dict[str, float]:
        """
        Calculate Contract-for-Difference (CfD) benefit for offshore wind.

        CfD provides revenue stabilization:
        - If market price < strike price: top-up payment
        - If market price > strike price: payment to government

        Args:
            annual_generation_mwh: Annual generation in MWh
            strike_price_eur_mwh: CfD strike price (€/MWh)
            market_price_eur_mwh: Expected market price (€/MWh)
            years: Number of years (typically 20)

        Returns:
            Dictionary with CfD calculations
        """
        # Annual revenue (assuming average market price)
        annual_market_revenue = annual_generation_mwh * market_price_eur_mwh

        # CfD adjustment
        price_difference = market_price_eur_mwh - strike_price_eur_mwh
        annual_cfd_adjustment = annual_generation_mwh * price_difference

        # Net revenue
        annual_net_revenue = annual_generation_mwh * strike_price_eur_mwh

        total_net_revenue = annual_net_revenue * years

        return {
            "strike_price_eur_mwh": strike_price_eur_mwh,
            "assumed_market_price_eur_mwh": market_price_eur_mwh,
            "annual_market_revenue_eur": annual_market_revenue,
            "annual_cfd_adjustment_eur": annual_cfd_adjustment,
            "annual_net_revenue_eur": annual_net_revenue,
            "total_net_revenue_20years_eur": total_net_revenue,
            "revenue_certainty": "High - CfD provides stable revenue regardless of market volatility",
            "note": "If market price < strike price, government pays difference. If market price > strike price, project pays government."
        }


# Demo / Testing
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("🇩🇪 Germany Policy Handler Demo - With Research Context")
    print("=" * 70)


    async def demo():
        # Create handler
        config = {
            "country": {
                "code": "DEU",
                "name": "Germany"
            }
        }

        handler = GermanyPolicyHandler(config)

        print("\n" + "=" * 70)
        print("TEST 1: Rooftop Solar Policy (<10kW)")
        print("=" * 70)

        rooftop_policy = await handler.fetch_policy("solar_pv", capacity_mw=0.008)

        print(f"\n💰 Feed-in Tariff:")
        print(f"  Rate: €{rooftop_policy['eeg_tariff']}¢/kWh")
        print(f"  Type: {rooftop_policy['tariff_type']}")
        print(f"  Period: {rooftop_policy['tariff_period_years']} years")
        print(f"  Mechanism: {rooftop_policy['mechanism']}")

        print("\n" + "=" * 70)
        print("TEST 2: Ground-Mount Solar (100 MW)")
        print("=" * 70)

        solar_policy = await handler.fetch_policy("solar_pv", capacity_mw=100, state="Bavaria")

        print(f"\n💰 Auction-Based Pricing:")
        print(f"  Average Rate: €{solar_policy['eeg_tariff']}¢/kWh")
        print(f"  Auction Range: {solar_policy['auction_range']}")
        print(f"  Mechanism: {solar_policy['mechanism']}")

        if solar_policy.get('regional_context'):
            print(f"\n🏛️  Regional Context (Bavaria):")
            print(f"  {solar_policy['regional_context']['description']}")

        print("\n" + "=" * 70)
        print("TEST 3: Offshore Wind Policy")
        print("=" * 70)

        offshore_policy = await handler.fetch_policy("offshore_wind", capacity_mw=500)

        print(f"\n💰 Offshore Wind (CfD Model):")
        print(f"  Average Rate: €{offshore_policy['eeg_tariff']}¢/kWh")
        print(f"  Auction Range: {offshore_policy['auction_range']}")
        print(f"  Mechanism: {offshore_policy['mechanism']}")
        print(f"  Note: {offshore_policy['zero_subsidy_trend']}")

        if offshore_policy.get('research_context'):
            research = offshore_policy['research_context']
            print(f"\n📊 Market Research Available:")
            print(f"  Market Overview: {len(research.get('market_overview', ''))} chars")
            print(f"  Key Trends: {len(research.get('key_trends', ''))} chars")
            print(f"  Opportunities: {len(research.get('opportunities', ''))} chars")
            print(f"  Sources: {len(research.get('sources', []))} URLs")

            print(f"\n🎯 Key Trends (excerpt):")
            print(f"  {research.get('key_trends', '')[:250]}...")

        print("\n" + "=" * 70)
        print("TEST 4: EEG Value Calculation")
        print("=" * 70)

        annual_generation = 175_000_000  # 175 GWh
        eeg_calc = handler.calculate_eeg_value(annual_generation, 6.0, "solar_pv", 20)

        print(f"\n💵 EEG Calculation for {annual_generation:,} kWh/year:")
        print(f"  EEG Rate: €{eeg_calc['eeg_rate_eur_cents_per_kwh']}¢/kWh")
        print(f"  Annual Revenue: €{eeg_calc['annual_eeg_eur']:,.0f} (${eeg_calc['annual_eeg_usd']:,.0f})")
        print(
            f"  Total 20-year Revenue: €{eeg_calc['total_eeg_20years_eur']:,.0f} (${eeg_calc['total_eeg_20years_usd']:,.0f})")

        print("\n" + "=" * 70)
        print("TEST 5: CfD Model Calculation")
        print("=" * 70)

        annual_generation_mwh = 1_750_000  # 1.75 TWh
        cfd_calc = handler.calculate_cfd_benefit(annual_generation_mwh, 58.0, 80.0, 20)

        print(f"\n💵 CfD Calculation for {annual_generation_mwh:,} MWh/year:")
        print(f"  Strike Price: €{cfd_calc['strike_price_eur_mwh']}/MWh")
        print(f"  Market Price (assumed): €{cfd_calc['assumed_market_price_eur_mwh']}/MWh")
        print(f"  Annual Net Revenue: €{cfd_calc['annual_net_revenue_eur']:,.0f}")
        print(f"  Total 20-year Revenue: €{cfd_calc['total_net_revenue_20years_eur']:,.0f}")
        print(f"  Certainty: {cfd_calc['revenue_certainty']}")

        print("\n" + "=" * 70)
        print("✅ Germany Policy Handler Working with Research Context!")
        print("=" * 70)


    asyncio.run(demo())