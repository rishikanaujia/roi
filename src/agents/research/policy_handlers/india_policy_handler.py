"""
India Policy Handler - India-Specific Renewable Energy Policies

India has aggressive renewable energy targets:
- 500 GW renewable capacity by 2030
- Production Linked Incentive (PLI) scheme
- Accelerated depreciation
- Generation-Based Incentives (GBI)
- State-level subsidies and incentives

Key Programs:
- PLI for Solar PV Manufacturing
- MNRE schemes (Ministry of New and Renewable Energy)
- State Solar Policies (Gujarat, Rajasthan, Tamil Nadu)
- Wind Energy Policies (Tamil Nadu, Gujarat, Maharashtra)

Sources: MNRE, SECI, State Nodal Agencies
"""

from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler


class IndiaPolicyHandler(BasePolicyHandler):
    """
    India-specific policy handler.

    Implements Indian renewable energy policies including:
    - PLI scheme
    - Accelerated depreciation
    - Generation-Based Incentives
    - State-level policies
    """

    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch India policy data for specified technology.

        Args:
            technology: Technology type
            **kwargs: Additional parameters
                - state: State code (e.g., "GJ", "RJ", "TN")
                - capacity_mw: Project capacity

        Returns:
            Policy data dictionary
        """
        state = kwargs.get('state', 'GJ')  # Default Gujarat
        capacity_mw = kwargs.get('capacity_mw', 100)

        self.logger.info(
            f"Fetching India policy data for {technology} in {state} ({capacity_mw} MW)"
        )

        # Get central government incentives
        central_incentives = self._get_central_incentives(technology)

        # Get state-level incentives
        state_incentives = self._get_state_incentives(state, technology)

        # Get depreciation
        depreciation = self._get_depreciation_schedule()

        # Get tax information
        tax_info = self._get_tax_info()

        # Get grid/market information
        market_info = self._get_market_info(state)

        # Policy notes
        notes = self._get_policy_notes(technology)

        return {
            "country": "IND",
            "technology": technology,
            "incentives": {
                **central_incentives,
                "state_incentives": state_incentives
            },
            "depreciation": depreciation,
            "tax_rate": tax_info["corporate_tax_rate"],
            "tax_details": tax_info,
            "market_information": market_info,
            "regulatory_notes": notes,
            "source": "MNRE, SECI, State Nodal Agencies (2024)",
            "confidence": "high",
            "last_updated": "2024-12-01"
        }

    def _get_central_incentives(self, technology: str) -> Dict[str, Any]:
        """Get central government incentives."""

        incentives = {
            "pli_scheme_available": False,
            "gbi_available": False,
            "viability_gap_funding": False
        }

        if technology == "solar_pv":
            # PLI Scheme for Solar PV Manufacturing
            incentives.update({
                "pli_scheme_available": True,
                "pli_scheme_details": {
                    "description": "Production Linked Incentive for Solar PV Manufacturing",
                    "incentive_rate_percent": 20.0,
                    "duration_years": 5,
                    "eligibility": "Domestic manufacturing only"
                },
                # Generation-Based Incentives (older projects)
                "gbi_available": True,
                "gbi_rate_inr_per_kwh": 0.50,  # ₹0.50/kWh
                "gbi_duration_years": 10,
                # Accelerated depreciation
                "accelerated_depreciation_available": True,
                "accelerated_depreciation_rate": 0.40  # 40% in first year
            })

        elif "wind" in technology:
            # Wind policies
            incentives.update({
                "gbi_available": True,
                "gbi_rate_inr_per_kwh": 0.50,
                "gbi_duration_years": 10,
                "accelerated_depreciation_available": True,
                "accelerated_depreciation_rate": 0.40
            })

        # Viability Gap Funding for larger projects
        incentives["viability_gap_funding"] = True
        incentives["vgf_max_percent"] = 20.0  # Up to 20% of project cost

        return incentives

    def _get_state_incentives(self, state: str, technology: str) -> list:
        """Get state-level incentives."""

        state_policies = {
            "GJ": {  # Gujarat
                "solar_pv": [
                    "Gujarat Solar Power Policy 2021: Feed-in tariff ₹2.50/kWh",
                    "SGST exemption for 5 years",
                    "Electricity duty exemption",
                    "Land allocation at concessional rates in solar parks"
                ],
                "onshore_wind": [
                    "Gujarat Wind Power Policy: Feed-in tariff ₹2.80/kWh",
                    "SGST exemption for 5 years",
                    "Banking facility for excess generation",
                    "Dedicated wind zones in Kutch and Saurashtra"
                ]
            },
            "RJ": {  # Rajasthan
                "solar_pv": [
                    "Rajasthan Solar Energy Policy: Feed-in tariff ₹2.45/kWh",
                    "Capital subsidy 30% for projects <1 MW",
                    "Stamp duty exemption",
                    "Dedicated solar parks with infrastructure"
                ],
                "onshore_wind": [
                    "Rajasthan Wind Energy Policy: Feed-in tariff ₹2.75/kWh",
                    "SGST exemption for 5 years",
                    "Wheeling charges waiver",
                    "High wind resource areas in Jaisalmer"
                ]
            },
            "TN": {  # Tamil Nadu
                "solar_pv": [
                    "Tamil Nadu Solar Energy Policy: Feed-in tariff ₹2.60/kWh",
                    "Capital subsidy 25% for rooftop projects",
                    "Wheeling and banking facility",
                    "Front-runner state with strong grid infrastructure"
                ],
                "onshore_wind": [
                    "Tamil Nadu Wind Energy Policy: Feed-in tariff ₹2.85/kWh",
                    "25-year PPA available",
                    "Best wind resources in India (Coimbatore, Tirunelveli)",
                    "TANGEDCO power purchase guarantee"
                ]
            },
            "MH": {  # Maharashtra
                "solar_pv": [
                    "Maharashtra Solar Policy: Feed-in tariff ₹2.55/kWh",
                    "Net metering for rooftop projects",
                    "SGST exemption",
                    "Open access facilitation"
                ],
                "onshore_wind": [
                    "Maharashtra Wind Policy: Feed-in tariff ₹2.80/kWh",
                    "Good wind resources in Western Ghats",
                    "Banking facility available",
                    "SGST exemption for 5 years"
                ]
            }
        }

        return state_policies.get(state, {}).get(technology, [
            f"Generic state policies apply for {technology}"
        ])

    def _get_depreciation_schedule(self) -> Dict[str, Any]:
        """
        Get depreciation schedule.

        India allows accelerated depreciation for renewable energy:
        - 40% in first year
        - Then Written Down Value (WDV) method at 40%
        """
        return {
            "method": "Accelerated Depreciation (WDV)",
            "first_year_rate": 0.40,
            "subsequent_years_rate": 0.40,
            "description": "40% WDV method - significantly reduces tax burden",
            "benefit_calculation": "40% of asset value in Year 1, then 40% of remaining value each year"
        }

    def _get_tax_info(self) -> Dict[str, Any]:
        """
        Get tax information.

        India corporate tax structure:
        - Standard rate: 30%
        - Surcharge: 10-12% (for income > ₹1 crore)
        - Health & Education Cess: 4%
        - Effective rate: ~25-26% (with deductions)
        """
        return {
            "corporate_tax_rate": 0.25,  # Effective rate with deductions
            "standard_rate": 0.30,
            "surcharge": 0.10,
            "health_education_cess": 0.04,
            "gst_rate": 0.05,  # 5% GST on renewable energy equipment
            "minimum_alternate_tax": 0.155,  # 15.5% MAT
            "tax_holiday_available": True,
            "tax_holiday_duration_years": 10,
            "tax_holiday_description": "80-IA deduction: 100% profit exemption for 10 years"
        }

    def _get_market_info(self, state: str) -> Dict[str, Any]:
        """Get electricity market information."""

        # State-wise average tariffs (₹/kWh)
        state_tariffs = {
            "GJ": 2.50,  # Gujarat
            "RJ": 2.45,  # Rajasthan
            "TN": 2.60,  # Tamil Nadu
            "MH": 2.55,  # Maharashtra
            "KA": 2.65,  # Karnataka
        }

        return {
            "state": state,
            "average_feed_in_tariff_inr_per_kwh": state_tariffs.get(state, 2.50),
            "power_purchase_agreement_duration_years": 25,
            "payment_security_mechanism": "Letter of Credit / Payment Security Fund",
            "grid_availability": "high",
            "must_run_status": True,  # Renewable energy gets priority dispatch
            "renewable_purchase_obligation_percent": 10.5,  # RPO targets
            "market_type": "Regulated (Feed-in Tariff) + Open Access available",
            "exchanges": ["IEX", "PXIL"],  # Indian Energy Exchange, Power Exchange India
            "spot_market_available": True
        }

    def _get_policy_notes(self, technology: str) -> list:
        """Get important policy notes."""

        notes = [
            "India targeting 500 GW renewable capacity by 2030",
            "Strong policy support at central and state levels",
            "Land acquisition can be challenging - solar parks recommended",
            "Grid connectivity improving but varies by region",
            "Payment security mechanisms in place for most states"
        ]

        if technology == "solar_pv":
            notes.extend([
                "ALMM (Approved List of Models and Manufacturers) compliance required",
                "DCR (Domestic Content Requirement) may apply for government tenders",
                "Rooftop solar has separate schemes (PM-KUSUM, etc.)"
            ])

        elif "wind" in technology:
            notes.extend([
                "Wind resource assessment mandatory before project",
                "Tamil Nadu and Gujarat are preferred states for wind",
                "Repowering policy available for old wind farms"
            ])

        return notes


# Demo
if __name__ == "__main__":
    import asyncio
    from src.utils.config_loader import ConfigLoader

    print("=" * 70)
    print("🇮🇳 India Policy Handler Demo 🇮🇳")
    print("=" * 70)

    config_loader = ConfigLoader()

    # Note: india.yaml doesn't exist yet, so we'll use a minimal config
    india_config = {
        "country": {
            "code": "IND",
            "name": "India"
        }
    }

    handler = IndiaPolicyHandler(india_config)

    print(f"\n1. Country: {handler.get_country_name()} ({handler.get_country_code()})")


    async def test_policies():
        # Test Solar PV in Gujarat
        print("\n2. Fetching Solar PV policy for Gujarat:")
        solar_policy = await handler.fetch_policy("solar_pv", state="GJ", capacity_mw=100)
        print(f"   PLI Available: {solar_policy['incentives']['pli_scheme_available']}")
        print(f"   GBI Rate: ₹{solar_policy['incentives']['gbi_rate_inr_per_kwh']}/kWh")
        print(f"   Accelerated Depreciation: {solar_policy['incentives']['accelerated_depreciation_rate'] * 100}%")
        print(f"   Tax Rate: {solar_policy['tax_rate'] * 100}%")
        print(f"   Feed-in Tariff: ₹{solar_policy['market_information']['average_feed_in_tariff_inr_per_kwh']}/kWh")
        print(f"   State Incentives: {len(solar_policy['incentives']['state_incentives'])} programs")
        for incentive in solar_policy['incentives']['state_incentives'][:2]:
            print(f"     - {incentive}")

        # Test Wind in Tamil Nadu
        print("\n3. Fetching Onshore Wind policy for Tamil Nadu:")
        wind_policy = await handler.fetch_policy("onshore_wind", state="TN", capacity_mw=150)
        print(f"   GBI Available: {wind_policy['incentives']['gbi_available']}")
        print(
            f"   GBI Rate: ₹{wind_policy['incentives']['gbi_rate_inr_per_kwh']}/kWh for {wind_policy['incentives']['gbi_duration_years']} years")
        print(f"   Feed-in Tariff: ₹{wind_policy['market_information']['average_feed_in_tariff_inr_per_kwh']}/kWh")
        print(f"   PPA Duration: {wind_policy['market_information']['power_purchase_agreement_duration_years']} years")
        print(f"   State Incentives: {len(wind_policy['incentives']['state_incentives'])} programs")
        for incentive in wind_policy['incentives']['state_incentives'][:2]:
            print(f"     - {incentive}")

        # Test Solar in Rajasthan
        print("\n4. Fetching Solar PV policy for Rajasthan:")
        rajasthan_policy = await handler.fe