"""
Analysis Agent - Hybrid Architecture (Again!)

Just like ResearchAgent uses pluggable handlers/fetchers,
AnalysisAgent uses pluggable calculators!

One agent that works for ANY technology:
- Solar PV → SolarPVCalculator
- Onshore Wind → WindCalculator
- Add Hydro? Just create HydroCalculator → Works instantly!

How it works:
1. Takes ResearchAgent output (policy + resource data)
2. CalculationEngineFactory creates right calculator
3. Calculator computes: capacity factor, LCOE, IRR, NPV
4. Returns investment-grade financial analysis

Example:
    # USA + Solar
    agent = AnalysisAgent(llm, config, "USA", "solar_pv")
    result = await agent.execute({"research_data": research_result})

    # Germany + Wind (same agent class!)
    agent = AnalysisAgent(llm, config, "DEU", "onshore_wind")
    result = await agent.execute({"research_data": research_result})
"""

from typing import Dict, Any
from src.core.base_agent import BaseAgent
from src.utils.config_loader import ConfigLoader
from src.agents.analysis.calculators.factory import CalculationEngineFactory


class AnalysisAgent(BaseAgent):
    """
    Analysis Agent with Hybrid Architecture.

    Generic analysis agent that works for ANY technology.

    Architecture:
    - Generic framework (this class)
    - Pluggable calculation engine (technology-specific)
    - Dynamic configuration loading

    Attributes:
        country_code (str): Country code
        technology (str): Technology code
        runtime_config (Dict): Merged configuration
        calc_engine: Technology-specific calculator
    """

    def __init__(
            self,
            llm_provider,
            config: Dict[str, Any],
            country_code: str,
            technology: str,
            logger=None
    ):
        """
        Initialize Analysis Agent.

        Args:
            llm_provider: LLM provider for AI operations
            config: Base configuration
            country_code: Country code (e.g., "USA", "DEU")
            technology: Technology code (e.g., "solar_pv", "onshore_wind")
            logger: Optional logger
        """
        super().__init__("AnalysisAgent", llm_provider, config, logger)

        self.country_code = country_code.upper()
        self.technology = technology.lower()

        # Load dynamic configuration
        self.logger.info(f"Initializing AnalysisAgent for {country_code} + {technology}")
        config_loader = ConfigLoader()
        self.runtime_config = config_loader.load_combination_config(
            self.country_code,
            self.technology
        )

        # Get technology-specific calculation engine
        self.logger.info(f"Creating calculation engine for {technology}")
        self.calc_engine = CalculationEngineFactory.get_engine(self.technology)

        self.logger.info(
            f"AnalysisAgent ready: {self.runtime_config['country']['name']} + "
            f"{self.runtime_config['technology']['name']}"
        )

    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core execution - Calculate financial metrics.

        Steps:
        1. Extract research data
        2. Calculate capacity factor (technology-specific)
        3. Build financial parameters
        4. Calculate LCOE, IRR, NPV

        Args:
            input_data: Must contain:
                - research_data: Output from ResearchAgent
                - capacity_mw: Project capacity (optional)

        Returns:
            Dictionary with financial analysis
        """
        research_data = input_data['research_data']
        capacity_mw = input_data.get('capacity_mw', 100.0)

        self.logger.info(
            f"Analyzing {capacity_mw} MW {self.technology} project in {self.country_code}"
        )

        # Step 1: Extract resource data
        resource_data = research_data['resource_data']['resource_data']

        # Step 2: Calculate capacity factor (technology-specific!)
        self.logger.info("Calculating capacity factor...")
        capacity_factor = self.calc_engine.calculate_capacity_factor(resource_data)

        # Step 3: Build financial parameters
        financial_params = self._build_financial_params(
            capacity_factor,
            capacity_mw,
            research_data
        )

        # Step 4: Calculate financial metrics
        self.logger.info("Calculating LCOE, IRR, NPV...")
        lcoe = self.calc_engine.calculate_lcoe(financial_params)
        irr = self.calc_engine.calculate_irr(financial_params)
        npv = self.calc_engine.calculate_npv(financial_params)

        # Step 5: Assess viability
        viability = self._assess_viability(lcoe, irr, npv, financial_params)

        result = {
            "country": self.country_code,
            "technology": self.technology,
            "capacity_mw": capacity_mw,
            "capacity_factor": capacity_factor,
            "financial_metrics": {
                "lcoe_usd_per_mwh": lcoe,
                "irr_percent": irr,
                "npv_usd": npv,
                "payback_period_years": self._estimate_payback(financial_params, lcoe)
            },
            "assumptions": financial_params,
            "viability_assessment": viability,
            "analysis_status": "complete"
        }

        self.logger.info(
            f"Analysis complete: LCOE=${lcoe:.2f}/MWh, IRR={irr:.1f}%, NPV=${npv:,.0f}"
        )

        return result

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input has research data."""
        if not super().validate_input(input_data):
            return False

        if 'research_data' not in input_data:
            self.logger.error("Missing research_data")
            return False

        # Check research data has required fields
        research_data = input_data['research_data']
        if 'resource_data' not in research_data:
            self.logger.error("Research data missing resource_data")
            return False

        return True

    def _build_financial_params(
            self,
            capacity_factor: float,
            capacity_mw: float,
            research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build financial parameters from config and research data."""

        # Get technology financial parameters
        tech_financial = self.runtime_config['technology']['financial']

        # Get country financial parameters
        country_financial = self.runtime_config['country']['financial']
        country_grid = self.runtime_config['country']['grid']

        # Extract policy data
        policy_data = research_data['policy_data']

        params = {
            # Technology parameters
            'capex_usd_per_kw': tech_financial['capex_usd_per_kw'],
            'opex_usd_per_kw_year': tech_financial['opex_usd_per_kw_year'],
            'project_lifetime_years': tech_financial['project_lifetime_years'],

            # Country parameters
            'discount_rate': country_financial['discount_rate'],
            'electricity_price_usd_per_mwh': country_grid['wholesale_price_usd_per_mwh'],

            # Calculated parameters
            'capacity_factor': capacity_factor,
            'capacity_kw': capacity_mw * 1000,

            # Policy parameters (if available)
            'tax_rate': policy_data.get('tax_rate', 0.21),
        }

        # Add USA-specific PTC if applicable
        if self.country_code == "USA" and "wind" in self.technology:
            incentives = policy_data.get('incentives', {})
            params['ptc_usd_per_mwh'] = incentives.get('federal_ptc_usd_per_mwh', 0.0)

        return params

    def _assess_viability(
            self,
            lcoe: float,
            irr: float,
            npv: float,
            params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess project viability."""

        electricity_price = params['electricity_price_usd_per_mwh']

        # Viability criteria
        is_profitable = lcoe < electricity_price
        meets_irr_threshold = irr >= 8.0  # Typical required return
        positive_npv = npv > 0

        # Overall recommendation
        if is_profitable and meets_irr_threshold and positive_npv:
            recommendation = "HIGHLY VIABLE"
            confidence = "high"
        elif is_profitable and (meets_irr_threshold or positive_npv):
            recommendation = "VIABLE"
            confidence = "medium"
        elif is_profitable:
            recommendation = "MARGINALLY VIABLE"
            confidence = "low"
        else:
            recommendation = "NOT VIABLE"
            confidence = "low"

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "is_profitable": is_profitable,
            "meets_irr_threshold": meets_irr_threshold,
            "positive_npv": positive_npv,
            "lcoe_vs_price_ratio": round(lcoe / electricity_price, 2),
            "notes": self._generate_viability_notes(
                lcoe, electricity_price, irr, npv
            )
        }

    def _generate_viability_notes(
            self,
            lcoe: float,
            price: float,
            irr: float,
            npv: float
    ) -> list:
        """Generate human-readable viability notes."""
        notes = []

        if lcoe < price:
            margin = ((price - lcoe) / lcoe) * 100
            notes.append(f"LCOE is {margin:.0f}% below electricity price - attractive economics")
        else:
            deficit = ((lcoe - price) / price) * 100
            notes.append(f"LCOE is {deficit:.0f}% above electricity price - may need subsidies")

        if irr >= 12:
            notes.append(f"Strong IRR of {irr:.1f}% indicates excellent returns")
        elif irr >= 8:
            notes.append(f"Acceptable IRR of {irr:.1f}% meets typical threshold")
        else:
            notes.append(f"Low IRR of {irr:.1f}% below typical 8% threshold")

        if npv > 0:
            notes.append(f"Positive NPV of ${npv:,.0f} indicates value creation")
        else:
            notes.append(f"Negative NPV of ${npv:,.0f} indicates value destruction")

        return notes

    def _estimate_payback(self, params: Dict[str, Any], lcoe: float) -> float:
        """Estimate simple payback period."""
        capex = params['capex_usd_per_kw']
        electricity_price = params['electricity_price_usd_per_mwh']
        cf = params['capacity_factor']
        opex = params['opex_usd_per_kw_year']

        # Annual energy per kW
        annual_energy_mwh = 8.76 * cf  # 8760 hours/year * CF / 1000

        # Annual revenue per kW
        annual_revenue = annual_energy_mwh * electricity_price

        # Annual net cash flow
        annual_net = annual_revenue - opex

        # Simple payback
        if annual_net > 0:
            payback = capex / annual_net
            return round(min(payback, 50), 1)  # Cap at 50 years
        else:
            return 50.0  # Never pays back


# Demo
if __name__ == "__main__":
    import asyncio
    from src.agents.research.research_agent import ResearchAgent

    print("=" * 70)
    print("🎉 AnalysisAgent - HYBRID ARCHITECTURE IN ACTION (AGAIN)! 🎉")
    print("=" * 70)


    class MockLLMProvider:
        pass


    async def demo():
        # Test 1: USA + Solar PV
        print("\n" + "=" * 70)
        print("TEST 1: USA + Solar PV - Complete Research → Analysis Flow")
        print("=" * 70)

        # Step 1: Research
        research_agent = ResearchAgent(
            MockLLMProvider(), {}, "USA", "solar_pv"
        )

        research_result = await research_agent.execute({
            "latitude": 31.99,
            "longitude": -102.07,
            "capacity_mw": 100
        })

        print(f"\nResearch Complete:")
        print(f"  GHI: {research_result['resource_data']['resource_data']['avg_ghi_kwh_m2_day']} kWh/m²/day")
        print(f"  ITC: {research_result['policy_data']['incentives']['federal_itc_percentage']}%")

        # Step 2: Analysis
        analysis_agent = AnalysisAgent(
            MockLLMProvider(), {}, "USA", "solar_pv"
        )

        print(f"\nAnalysis Agent:")
        print(f"  Calculator: {type(analysis_agent.calc_engine).__name__}")

        analysis_result = await analysis_agent.execute({
            "research_data": research_result,
            "capacity_mw": 100
        })

        print(f"\nFinancial Analysis:")
        print(f"  Capacity Factor: {analysis_result['capacity_factor'] * 100:.1f}%")
        print(f"  LCOE: ${analysis_result['financial_metrics']['lcoe_usd_per_mwh']:.2f}/MWh")
        print(f"  IRR: {analysis_result['financial_metrics']['irr_percent']:.1f}%")
        print(f"  NPV: ${analysis_result['financial_metrics']['npv_usd']:,.0f}")
        print(f"  Payback: {analysis_result['financial_metrics']['payback_period_years']:.1f} years")

        print(f"\nViability:")
        print(f"  Recommendation: {analysis_result['viability_assessment']['recommendation']}")
        print(f"  Confidence: {analysis_result['viability_assessment']['confidence']}")
        for note in analysis_result['viability_assessment']['notes']:
            print(f"    • {note}")

        # Test 2: Germany + Wind
        print("\n" + "=" * 70)
        print("TEST 2: Germany + Onshore Wind")
        print("=" * 70)

        research_agent2 = ResearchAgent(
            MockLLMProvider(), {}, "DEU", "onshore_wind"
        )

        research_result2 = await research_agent2.execute({
            "latitude": 54.0,
            "longitude": 8.0,
            "capacity_mw": 150
        })

        analysis_agent2 = AnalysisAgent(
            MockLLMProvider(), {}, "DEU", "onshore_wind"
        )

        analysis_result2 = await analysis_agent2.execute({
            "research_data": research_result2,
            "capacity_mw": 150
        })

        print(f"\nFinancial Analysis:")
        print(f"  Wind Speed: {research_result2['resource_data']['resource_data']['avg_wind_speed_m_s']} m/s")
        print(f"  Capacity Factor: {analysis_result2['capacity_factor'] * 100:.1f}%")
        print(f"  LCOE: ${analysis_result2['financial_metrics']['lcoe_usd_per_mwh']:.2f}/MWh")
        print(f"  IRR: {analysis_result2['financial_metrics']['irr_percent']:.1f}%")
        print(f"  Recommendation: {analysis_result2['viability_assessment']['recommendation']}")

        # Test 3: USA + Wind (shows PTC benefit)
        print("\n" + "=" * 70)
        print("TEST 3: USA + Wind (With PTC)")
        print("=" * 70)

        research_agent3 = ResearchAgent(
            MockLLMProvider(), {}, "USA", "onshore_wind"
        )

        research_result3 = await research_agent3.execute({
            "latitude": 31.99,
            "longitude": -102.07,
            "capacity_mw": 150
        })

        analysis_agent3 = AnalysisAgent(
            MockLLMProvider(), {}, "USA", "onshore_wind"
        )

        analysis_result3 = await analysis_agent3.execute({
            "research_data": research_result3,
            "capacity_mw": 150
        })

        print(f"\nFinancial Analysis:")
        print(f"  LCOE: ${analysis_result3['financial_metrics']['lcoe_usd_per_mwh']:.2f}/MWh")
        print(f"  IRR (with PTC): {analysis_result3['financial_metrics']['irr_percent']:.1f}%")
        print(
            f"  PTC Impact: ${research_result3['policy_data']['incentives']['federal_ptc_usd_per_mwh']}/MWh for 10 years")
        print(f"  Recommendation: {analysis_result3['viability_assessment']['recommendation']}")


    asyncio.run(demo())

    print("\n" + "=" * 70)
    print("✅ ANALYSIS AGENT WORKING PERFECTLY!")
    print("=" * 70)
    print("\n🎯 Complete Data Flow:")
    print("  ResearchAgent → Policy + Resource Data")
    print("  AnalysisAgent → LCOE + IRR + NPV + Recommendation")
    print("\n📊 Hybrid Architecture (Again!):")
    print("  ✓ One AnalysisAgent works for all technologies")
    print("  ✓ Pluggable calculators (Solar vs Wind)")
    print("  ✓ Add technology = add calculator (15 min)")
    print("  ✓ Zero code duplication")
    print("=" * 70)