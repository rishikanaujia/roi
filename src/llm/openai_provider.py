"""
OpenAI Provider - Real GPT-4 Integration

Provides production-grade AI insights using OpenAI's GPT-4.

Features:
- Investment insights generation
- Risk assessment
- Data quality analysis
- Natural language recommendations
- Cost tracking

Cost: ~$0.03 per analysis (GPT-4-turbo)
API Key: Get from https://platform.openai.com/api-keys

Environment Variable:
    export OPENAI_API_KEY='sk-...'
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import asyncio

try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.core.interfaces.llm_provider_interface import ILLMProvider


class OpenAIProvider(ILLMProvider):
    """
    OpenAI GPT-4 provider for production AI insights.

    Models Available:
    - gpt-4o: Latest, fastest, cheapest ($2.50/1M input, $10/1M output)
    - gpt-4-turbo: Very good, fast ($10/1M input, $30/1M output)
    - gpt-4: Original, best reasoning ($30/1M input, $60/1M output)

    Recommended: gpt-4o (best price/performance)
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            model: str = "gpt-4o",
            logger: Optional[logging.Logger] = None
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (optional, reads from env)
            model: Model to use (default: gpt-4o)
            logger: Logger instance (optional)

        Raises:
            ImportError: If openai package not installed
            ValueError: If API key not provided
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter. Get key at: https://platform.openai.com/api-keys"
            )

        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.logger = logger or self._create_logger()

        # Cost tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0

        self.logger.info(f"OpenAI provider initialized with model: {model}")

    async def generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float = 0.7,
            max_tokens: int = 500
    ) -> str:
        """
        Generate completion using GPT-4.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            self.logger.info(f"Generating completion with {self.model}")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Track usage
            self.total_input_tokens += response.usage.prompt_tokens
            self.total_output_tokens += response.usage.completion_tokens
            self.total_requests += 1

            self.logger.info(
                f"Completion generated "
                f"(input: {response.usage.prompt_tokens} tokens, "
                f"output: {response.usage.completion_tokens} tokens)"
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"OpenAI completion error: {str(e)}")
            raise

    async def generate_insights(
            self,
            analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate investment insights using GPT-4."""
        try:
            self.logger.info("Generating investment insights with GPT-4...")

            # Extract metrics - handle BOTH flat and nested structures
            # Check if we have flat structure (from formatted result)
            if 'lcoe' in analysis_data:
                # Flat structure (preferred)
                lcoe = analysis_data.get('lcoe', 0)
                irr = analysis_data.get('irr', 0)
                npv = analysis_data.get('npv', 0)
                capacity_factor = analysis_data.get('capacity_factor', 0)
                recommendation = analysis_data.get('recommendation', 'UNKNOWN')
                project = analysis_data.get('project', {})
                resource_summary = analysis_data.get('resource_summary', {})
                policy_summary = analysis_data.get('policy_summary', {})
            else:
                # Nested structure (from raw analysis result)
                financial = analysis_data.get('financial_metrics', {})
                lcoe = financial.get('lcoe_usd_per_mwh', 0)
                irr = financial.get('irr_percent', 0)
                npv = financial.get('npv_usd', 0)
                capacity_factor = analysis_data.get('capacity_factor', 0)

                viability = analysis_data.get('viability_assessment', {})
                recommendation = viability.get('recommendation', 'UNKNOWN')

                # Project info from analysis context
                project = {
                    'technology': analysis_data.get('technology', 'renewable energy'),
                    'country': analysis_data.get('country', 'this region'),
                    'capacity_mw': analysis_data.get('capacity_mw', 0)
                }

                # These won't be in raw analysis result
                resource_summary = {}
                policy_summary = {}

            # DEBUG: Log what we extracted
            self.logger.info(
                f"Extracted metrics - LCOE: ${lcoe:.2f}/MWh, IRR: {irr:.1f}%, "
                f"CF: {capacity_factor * 100:.1f}%"
            )

            # Extract project info
            technology = project.get('technology', 'renewable energy')
            country = project.get('country', 'this region')
            capacity_mw = project.get('capacity_mw', 0)

            # Get resource and policy data
            resource_summary = analysis_data.get('resource_summary', {})
            policy_summary = analysis_data.get('policy_summary', {})

            # Build comprehensive prompt
            prompt = self._build_insights_prompt(
                technology, country, capacity_mw,
                lcoe, irr, npv, capacity_factor, recommendation,
                resource_summary, policy_summary
            )

            # DEBUG: Log a snippet of the prompt
            self.logger.info(f"Prompt contains: LCOE ${lcoe:.2f}/MWh, IRR {irr:.1f}%")
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert renewable energy investment analyst with 20 years "
                        "of experience in project finance, resource assessment, and policy analysis. "
                        "You provide data-driven, actionable insights for institutional investors."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # Generate insights
            response = await self.generate_completion(
                messages,
                temperature=0.3,  # Lower temperature for consistent, factual output
                max_tokens=1000
            )

            # Parse JSON response (handle markdown wrapping)
            insights = self._parse_json_response(response)

            self.logger.info("Investment insights generated successfully")
            return insights

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse GPT-4 response as JSON: {str(e)}")
            # Fallback to mock-style response
            return self._fallback_insights(analysis_data)

        except Exception as e:
            self.logger.error(f"Insight generation error: {str(e)}")
            raise

    def _build_insights_prompt(
            self,
            technology: str,
            country: str,
            capacity_mw: float,
            lcoe: float,
            irr: float,
            npv: float,
            capacity_factor: float,
            recommendation: str,
            resource_summary: Dict[str, Any],
            policy_summary: Dict[str, Any]
    ) -> str:
        """Build comprehensive prompt for insights generation."""

        # Build resource details
        resource_details = ""
        if technology == "solar_pv":
            ghi = resource_summary.get('ghi_kwh_m2_day', 0)
            temp = resource_summary.get('temperature_c', 0)
            resource_details = f"  - GHI: {ghi:.2f} kWh/m²/day\n  - Temperature: {temp:.1f}°C"
        elif "wind" in technology:
            wind_speed = resource_summary.get('wind_speed_m_s', 0)
            power_density = resource_summary.get('wind_power_density_w_m2', 0)
            resource_details = f"  - Wind Speed: {wind_speed:.2f} m/s\n  - Power Density: {power_density:.0f} W/m²"

        # Build policy details
        policy_details = ""
        if country == "USA":
            itc = policy_summary.get('federal_itc', 0)
            ptc = policy_summary.get('federal_ptc', 0)
            if itc:
                policy_details = f"  - Federal ITC: {itc}%"
            if ptc:
                policy_details = f"  - Federal PTC: ${ptc}/MWh"
        elif country == "DEU":
            eeg = policy_summary.get('eeg_tariff', 0)
            if eeg:
                policy_details = f"  - EEG Tariff: €{eeg}/MWh"
        elif country == "IND":
            gbi = policy_summary.get('gbi_rate', 0)
            if gbi:
                policy_details = f"  - GBI Rate: ₹{gbi}/kWh"

        prompt = f"""Analyze this renewable energy investment opportunity:

PROJECT DETAILS:
- Technology: {technology}
- Country: {country}
- Capacity: {capacity_mw} MW
- Current Recommendation: {recommendation}

FINANCIAL METRICS:
- LCOE: ${lcoe:.2f}/MWh
- IRR: {irr:.1f}%
- NPV: ${npv:,.0f}
- Capacity Factor: {capacity_factor * 100:.1f}%

RESOURCE QUALITY:
{resource_details if resource_details else "  - Data not available"}

POLICY ENVIRONMENT:
{policy_details if policy_details else "  - Data not available"}

Provide a comprehensive investment analysis with:

1. **Key Insights** (3 insights):
   - Focus on financial viability and competitive positioning
   - Compare to industry benchmarks (solar LCOE: $40-80/MWh, wind: $30-60/MWh)
   - Highlight strengths or weaknesses relative to typical projects
   - Be specific about WHY metrics are good or concerning

2. **Risks** (3 major risks):
   - Financial risks (returns, bankability, market)
   - Technical risks (resource variability, technology)
   - Policy/regulatory risks (incentive changes, permits)
   - Be concrete and actionable

3. **Opportunities** (3 opportunities):
   - Ways to improve project economics
   - Market opportunities (PPAs, merchant, storage)
   - Policy optimization strategies
   - Technology or structure improvements
   - Be specific and actionable

4. **Investment Recommendation Summary** (2-3 sentences):
   - Clear recommendation aligned with current status
   - Specific reasoning based on metrics
   - Concrete next steps or conditions for investment

OUTPUT FORMAT (JSON only, no markdown):
{{
  "key_insights": [
    "Insight 1 with specific numbers and reasoning",
    "Insight 2 with specific numbers and reasoning",
    "Insight 3 with specific numbers and reasoning"
  ],
  "risks": [
    "Risk 1 with specific concerns and impact",
    "Risk 2 with specific concerns and impact",
    "Risk 3 with specific concerns and impact"
  ],
  "opportunities": [
    "Opportunity 1 with specific potential and approach",
    "Opportunity 2 with specific potential and approach",
    "Opportunity 3 with specific potential and approach"
  ],
  "recommendation_summary": "2-3 sentence summary with specific reasoning and next steps"
}}

IMPORTANT: 
- Be specific with numbers and comparisons
- Reference actual project metrics in your analysis
- Provide actionable, concrete recommendations
- Keep professional investment analyst tone
- Output ONLY valid JSON, no other text
"""

        return prompt

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response, handling markdown code blocks.

        GPT-4 sometimes wraps JSON in ```json ... ``` blocks.
        This parser handles that gracefully.
        """
        # Remove markdown code blocks
        response = response.strip()

        # Remove ```json and ``` markers
        if response.startswith('```'):
            # Find the actual JSON content
            lines = response.split('\n')
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            response = '\n'.join(lines)

        # Try to parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object in response
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                json_str = response[start:end + 1]
                return json.loads(json_str)
            raise

    async def assess_data_quality(
            self,
            research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess data quality using GPT-4.

        Args:
            research_data: Research results

        Returns:
            Dictionary with quality assessment
        """
        try:
            self.logger.info("Assessing data quality with GPT-4...")

            # Extract completeness info
            completeness = research_data.get('data_completeness', {})
            policy_confidence = completeness.get('policy_confidence', 'unknown')
            resource_confidence = completeness.get('resource_confidence', 'unknown')

            prompt = f"""Assess the quality of this renewable energy project data:

DATA COMPLETENESS:
- Policy Data Confidence: {policy_confidence}
- Resource Data Confidence: {resource_confidence}
- Has Policy Data: {completeness.get('has_policy_data', False)}
- Has Resource Data: {completeness.get('has_resource_data', False)}
- Ready for Analysis: {completeness.get('ready_for_analysis', False)}

Provide a data quality assessment:

OUTPUT FORMAT (JSON only):
{{
  "overall_quality": "excellent|good|acceptable|poor|insufficient",
  "confidence_score": 0.85,
  "data_gaps": [
    "Specific gap 1 if any",
    "Specific gap 2 if any"
  ],
  "quality_notes": "2-3 sentence assessment of data reliability for investment decisions",
  "policy_data_quality": "{policy_confidence}",
  "resource_data_quality": "{resource_confidence}"
}}

Guidelines:
- overall_quality based on both confidence levels
- confidence_score: 0.3-0.5 (poor), 0.5-0.7 (acceptable), 0.7-0.85 (good), 0.85-1.0 (excellent)
- data_gaps: Specific missing elements that would improve analysis
- If both high/very_high: excellent quality
- If one low: acceptable quality with gaps noted
- If both low: poor quality

Output ONLY valid JSON.
"""

            messages = [
                {
                    "role": "system",
                    "content": "You are a data quality analyst for renewable energy projects."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            response = await self.generate_completion(
                messages,
                temperature=0.2,
                max_tokens=500
            )

            quality = self._parse_json_response(response)

            self.logger.info("Data quality assessment completed")
            return quality

        except Exception as e:
            self.logger.error(f"Data quality assessment error: {str(e)}")
            # Fallback to simple assessment
            return self._fallback_quality_assessment(research_data)

    def _fallback_insights(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback insights if GPT-4 parsing fails."""
        return {
            "key_insights": [
                "Analysis completed with available data",
                "Review detailed metrics for investment decision",
                "Consider site-specific due diligence"
            ],
            "risks": [
                "Standard renewable energy project risks apply",
                "Market and policy uncertainty",
                "Technology and resource variability"
            ],
            "opportunities": [
                "Optimize project structure",
                "Explore incentive programs",
                "Consider technology improvements"
            ],
            "recommendation_summary": (
                "Project analysis complete. Review financial metrics and conduct "
                "detailed due diligence before proceeding."
            )
        }

    def _fallback_quality_assessment(
            self,
            research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback quality assessment."""
        completeness = research_data.get('data_completeness', {})

        return {
            "overall_quality": "acceptable",
            "confidence_score": 0.70,
            "data_gaps": ["Assessment based on available data"],
            "quality_notes": "Data quality acceptable for preliminary analysis.",
            "policy_data_quality": completeness.get('policy_confidence', 'medium'),
            "resource_data_quality": completeness.get('resource_confidence', 'medium')
        }

    def get_provider_name(self) -> str:
        """Get provider name."""
        return f"OpenAI-{self.model}"

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics and cost estimates.

        Returns:
            Dictionary with usage and cost info
        """
        # Pricing (as of Dec 2024)
        pricing = {
            "gpt-4o": {"input": 2.50, "output": 10.0},  # per 1M tokens
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-4": {"input": 30.0, "output": 60.0}
        }

        prices = pricing.get(self.model, pricing["gpt-4o"])

        # Calculate costs
        input_cost = (self.total_input_tokens / 1_000_000) * prices["input"]
        output_cost = (self.total_output_tokens / 1_000_000) * prices["output"]
        total_cost = input_cost + output_cost

        return {
            "model": self.model,
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "cost_per_request": (
                round(total_cost / self.total_requests, 4)
                if self.total_requests > 0 else 0
            )
        }

    def _create_logger(self) -> logging.Logger:
        """Create logger instance."""
        logger = logging.getLogger("OpenAIProvider")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger


# Demo
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("🤖 OpenAI Provider Demo")
    print("=" * 70)


    async def demo():
        # Check for API key
        api_key = os.getenv('OPENAI_API_KEY')

        if not api_key:
            print("\n❌ OPENAI_API_KEY not set!")
            print("\nTo use this provider:")
            print("1. Get API key: https://platform.openai.com/api-keys")
            print("2. Set environment variable:")
            print("   export OPENAI_API_KEY='sk-...'")
            print("3. Run this demo again")
            return

        print(f"\n✅ API key found: {api_key[:20]}...")

        try:
            # Create provider
            provider = OpenAIProvider(model="gpt-4o")
            print(f"✅ Provider initialized: {provider.get_provider_name()}")

            # Test insights generation
            print("\n" + "=" * 70)
            print("TEST: Generating Investment Insights")
            print("=" * 70)

            test_analysis = {
                "project": {
                    "technology": "solar_pv",
                    "country": "USA",
                    "capacity_mw": 100
                },
                "lcoe": 72.76,
                "irr": 5.0,
                "npv": -70587166,
                "capacity_factor": 0.20,
                "recommendation": "NOT VIABLE",
                "resource_summary": {
                    "ghi_kwh_m2_day": 5.58,
                    "temperature_c": 18.1
                },
                "policy_summary": {
                    "federal_itc": 30.0,
                    "tax_rate": 0.21
                }
            }

            insights = await provider.generate_insights(test_analysis)

            print("\n🎯 AI-Generated Insights:")
            print(f"\nKey Insights:")
            for i, insight in enumerate(insights['key_insights'], 1):
                print(f"  {i}. {insight}")

            print(f"\nRisks:")
            for i, risk in enumerate(insights['risks'], 1):
                print(f"  {i}. {risk}")

            print(f"\nOpportunities:")
            for i, opp in enumerate(insights['opportunities'], 1):
                print(f"  {i}. {opp}")

            print(f"\nRecommendation:")
            print(f"  {insights['recommendation_summary']}")

            # Show usage stats
            print("\n" + "=" * 70)
            print("💰 Usage Statistics")
            print("=" * 70)
            stats = provider.get_usage_stats()
            print(f"  Model: {stats['model']}")
            print(f"  Requests: {stats['total_requests']}")
            print(f"  Total Tokens: {stats['total_tokens']:,}")
            print(f"  Estimated Cost: ${stats['estimated_cost_usd']:.4f}")
            print(f"  Cost per Request: ${stats['cost_per_request']:.4f}")

            print("\n✅ OpenAI Provider Working!")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


    asyncio.run(demo())

    print("\n" + "=" * 70)
