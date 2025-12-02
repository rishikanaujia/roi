"""
Mock LLM Provider - Simulated AI for Demo/Testing

Provides realistic AI-generated insights without calling external APIs.

Perfect for:
- Development and testing
- Demos without API costs
- Offline operation
- Proof of concept

In production, replace with:
- OpenAIProvider (GPT-4)
- AnthropicProvider (Claude)
"""

import asyncio
from typing import Dict, Any, List
from src.core.interfaces.llm_provider_interface import ILLMProvider


class MockLLMProvider(ILLMProvider):
    """
    Mock LLM provider that generates realistic insights.

    Simulates AI-generated content based on analysis patterns.
    No external API calls - fully self-contained.
    """

    def __init__(self):
        """Initialize mock provider."""
        self.call_count = 0

    async def generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float = 0.7,
            max_tokens: int = 500
    ) -> str:
        """
        Generate mock completion.

        Simulates API delay and returns contextual response.
        """
        self.call_count += 1

        # Simulate API latency
        await asyncio.sleep(0.05)

        # Extract context from messages
        user_message = next(
            (m['content'] for m in messages if m['role'] == 'user'),
            ""
        )

        # Generate contextual response
        if "solar" in user_message.lower():
            return "Solar projects benefit from strong irradiance and declining equipment costs."
        elif "wind" in user_message.lower():
            return "Wind projects show competitive LCOE with modern turbine technology."
        else:
            return "Renewable energy projects offer sustainable returns with policy support."

    async def generate_insights(
            self,
            analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate investment insights from analysis data.

        Creates realistic insights based on actual metrics.
        """
        # Extract key metrics - handle both direct values and nested structure
        lcoe = analysis_data.get('lcoe', analysis_data.get('financial_metrics', {}).get('lcoe_usd_per_mwh', 0))
        irr = analysis_data.get('irr', analysis_data.get('financial_metrics', {}).get('irr_percent', 0))
        capacity_factor = analysis_data.get('capacity_factor', 0)
        recommendation = analysis_data.get('recommendation',
                                           analysis_data.get('viability_assessment', {}).get('recommendation',
                                                                                             'UNKNOWN'))

        # Extract project info
        project = analysis_data.get('project', {})
        technology = project.get('technology', 'renewable energy')
        country = project.get('country', 'this region')

        # Generate insights based on metrics
        insights = []
        risks = []
        opportunities = []

        # Key insights
        if lcoe < 50:
            insights.append(f"Excellent LCOE of ${lcoe:.2f}/MWh indicates strong cost competitiveness")
        elif lcoe < 70:
            insights.append(f"Competitive LCOE of ${lcoe:.2f}/MWh aligns with market standards")
        else:
            insights.append(f"LCOE of ${lcoe:.2f}/MWh may require policy support for viability")

        if irr > 12:
            insights.append(f"Strong IRR of {irr:.1f}% exceeds typical renewable energy project returns")
        elif irr > 8:
            insights.append(f"Acceptable IRR of {irr:.1f}% meets minimum investment thresholds")
        else:
            insights.append(f"IRR of {irr:.1f}% below typical 8% threshold may deter investors")

        if capacity_factor > 0.35:
            insights.append(f"High capacity factor of {capacity_factor * 100:.1f}% maximizes revenue generation")
        elif capacity_factor > 0.25:
            insights.append(f"Moderate capacity factor of {capacity_factor * 100:.1f}% is typical for {technology}")
        else:
            insights.append(f"Low capacity factor of {capacity_factor * 100:.1f}% may impact project economics")

        # Risks
        if irr < 8:
            risks.append("Below-threshold returns may struggle to attract institutional capital")

        if country == "USA" and technology == "solar_pv":
            risks.append("ITC phase-down scheduled for 2033-2034 reduces future incentive value")

        if lcoe > 60:
            risks.append("Electricity price volatility could impact project bankability")

        risks.append("Policy changes or regulatory shifts could affect long-term returns")

        if technology == "onshore_wind":
            risks.append("Wind resource variability requires robust forecasting and risk mitigation")

        # Opportunities
        if country == "USA":
            opportunities.append("Federal tax credits (ITC/PTC) provide significant value enhancement")
            opportunities.append("Growing corporate PPA market offers alternative revenue streams")

        if country == "IND":
            opportunities.append("India's 500 GW renewable target by 2030 creates strong policy tailwinds")
            opportunities.append("Declining equipment costs improve project economics")

        if country == "DEU":
            opportunities.append("Germany's Energiewende provides stable long-term policy framework")
            opportunities.append("High electricity prices support renewable energy economics")

        if capacity_factor > 0.30:
            opportunities.append("Strong resource quality enables premium project returns")

        # Technology-specific opportunities
        if technology == "solar_pv":
            opportunities.append("Solar module costs continuing to decline, improving future project economics")
            opportunities.append("Battery storage integration potential for enhanced value capture")
        elif "wind" in technology:
            opportunities.append("Larger turbines with higher capacity factors available for repowering")
            opportunities.append("Offshore wind expansion opportunities in coastal regions")

        # Recommendation summary
        if recommendation == "HIGHLY VIABLE":
            summary = (
                f"This {technology} project in {country} presents a highly attractive investment opportunity "
                f"with strong financial metrics (IRR {irr:.1f}%, LCOE ${lcoe:.2f}/MWh). "
                f"The combination of favorable resource conditions and supportive policy framework "
                f"creates compelling risk-adjusted returns. Recommend proceeding with detailed due diligence."
            )
        elif recommendation == "VIABLE":
            summary = (
                f"This {technology} project in {country} demonstrates viable economics "
                f"with acceptable returns (IRR {irr:.1f}%, LCOE ${lcoe:.2f}/MWh). "
                f"While not exceptional, the project meets minimum investment thresholds. "
                f"Consider optimization strategies and risk mitigation measures before proceeding."
            )
        elif recommendation == "MARGINALLY VIABLE":
            summary = (
                f"This {technology} project in {country} shows marginal viability "
                f"with borderline economics (IRR {irr:.1f}%, LCOE ${lcoe:.2f}/MWh). "
                f"Project requires careful structuring, policy support, or technological improvements "
                f"to achieve acceptable returns. Significant risk mitigation needed."
            )
        else:  # NOT VIABLE
            summary = (
                f"This {technology} project in {country} does not currently meet investment criteria "
                f"with insufficient returns (IRR {irr:.1f}%, LCOE ${lcoe:.2f}/MWh). "
                f"Consider alternative locations with better resource quality, await policy improvements, "
                f"or explore technology cost reductions before investment. Not recommended at this time."
            )

        return {
            "key_insights": insights[:3],  # Top 3 insights
            "risks": risks[:3],  # Top 3 risks
            "opportunities": opportunities[:3],  # Top 3 opportunities
            "recommendation_summary": summary
        }

    async def assess_data_quality(
            self,
            research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess quality of research data.

        Evaluates data completeness and confidence.
        """
        # Extract data completeness info
        completeness = research_data.get('data_completeness', {})
        policy_confidence = completeness.get('policy_confidence', 'unknown')
        resource_confidence = completeness.get('resource_confidence', 'unknown')
        overall_confidence = completeness.get('overall_confidence', 'unknown')

        # Map confidence to quality
        confidence_map = {
            'very_high': 'excellent',
            'high': 'good',
            'medium': 'acceptable',
            'low': 'poor',
            'unknown': 'insufficient'
        }

        overall_quality = confidence_map.get(overall_confidence, 'unknown')

        # Identify data gaps
        gaps = []
        if policy_confidence in ['low', 'unknown']:
            gaps.append("Limited policy data availability - may affect accuracy of incentive calculations")

        if resource_confidence in ['low', 'unknown']:
            gaps.append("Resource data quality concerns - recommend additional site assessment")

        if not completeness.get('has_policy_data', True):
            gaps.append("Missing critical policy information")

        if not completeness.get('has_resource_data', True):
            gaps.append("Missing resource assessment data")

        # Calculate numeric confidence score
        confidence_scores = {
            'very_high': 0.95,
            'high': 0.85,
            'medium': 0.70,
            'low': 0.50,
            'unknown': 0.30
        }

        policy_score = confidence_scores.get(policy_confidence, 0.5)
        resource_score = confidence_scores.get(resource_confidence, 0.5)
        confidence_score = (policy_score + resource_score) / 2

        # Generate quality notes
        if overall_quality in ['excellent', 'good']:
            notes = (
                f"Data quality is {overall_quality} with {policy_confidence} policy confidence "
                f"and {resource_confidence} resource confidence. Analysis results are reliable "
                f"for investment decision-making."
            )
        elif overall_quality == 'acceptable':
            notes = (
                f"Data quality is {overall_quality}. While analysis provides directional guidance, "
                f"additional site-specific data collection recommended before final investment decision."
            )
        else:
            notes = (
                f"Data quality is {overall_quality}. Analysis should be considered preliminary only. "
                f"Comprehensive due diligence and data collection required before proceeding."
            )

        return {
            "overall_quality": overall_quality,
            "confidence_score": round(confidence_score, 2),
            "data_gaps": gaps if gaps else ["No significant data gaps identified"],
            "quality_notes": notes,
            "policy_data_quality": policy_confidence,
            "resource_data_quality": resource_confidence
        }

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "MockLLM"


# Demo
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("🤖 Mock LLM Provider Demo")
    print("=" * 70)


    async def demo():
        provider = MockLLMProvider()

        print(f"\nProvider: {provider.get_provider_name()}")

        # Test 1: Generate completion
        print("\n1. Testing completion generation:")
        messages = [
            {"role": "system", "content": "You are a renewable energy analyst."},
            {"role": "user", "content": "Analyze this solar PV project in Texas."}
        ]
        completion = await provider.generate_completion(messages)
        print(f"   Response: {completion}")

        # Test 2: Generate insights (viable project)
        print("\n2. Testing insight generation (VIABLE project):")
        viable_analysis = {
            "lcoe": 45.5,
            "irr": 12.3,
            "capacity_factor": 0.38,
            "recommendation": "VIABLE",
            "project": {
                "technology": "solar_pv",
                "country": "USA"
            }
        }

        insights = await provider.generate_insights(viable_analysis)
        print(f"   Key Insights:")
        for insight in insights['key_insights']:
            print(f"     • {insight}")

        print(f"\n   Top Risks:")
        for risk in insights['risks'][:2]:
            print(f"     • {risk}")

        print(f"\n   Opportunities:")
        for opp in insights['opportunities'][:2]:
            print(f"     • {opp}")

        print(f"\n   Summary: {insights['recommendation_summary'][:150]}...")

        # Test 3: Assess data quality
        print("\n3. Testing data quality assessment:")
        research_data = {
            "data_completeness": {
                "policy_confidence": "high",
                "resource_confidence": "very_high",
                "overall_confidence": "high",
                "has_policy_data": True,
                "has_resource_data": True
            }
        }

        quality = await provider.assess_data_quality(research_data)
        print(f"   Overall Quality: {quality['overall_quality']}")
        print(f"   Confidence Score: {quality['confidence_score']}")
        print(f"   Data Gaps: {quality['data_gaps'][0]}")
        print(f"   Notes: {quality['quality_notes'][:100]}...")

        # Test 4: Different scenarios
        print("\n4. Testing NOT VIABLE scenario:")
        not_viable = {
            "lcoe": 95.0,
            "irr": 4.2,
            "capacity_factor": 0.15,
            "recommendation": "NOT VIABLE",
            "project": {
                "technology": "solar_pv",
                "country": "DEU"
            }
        }

        insights2 = await provider.generate_insights(not_viable)
        print(f"   Summary: {insights2['recommendation_summary'][:150]}...")

        print(f"\n   Call Count: {provider.call_count}")


    asyncio.run(demo())

    print("\n" + "=" * 70)
    print("✅ Mock LLM Provider working correctly!")
    print("=" * 70)
    print("\nKey Features:")
    print("  • Generates realistic AI insights")
    print("  • Assesses data quality")
    print("  • Provides risk assessment")
    print("  • Identifies opportunities")
    print("  • Creates natural language summaries")
    print("  • Zero external API calls")
    print("=" * 70)