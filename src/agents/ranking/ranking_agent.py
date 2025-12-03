"""
Ranking Agent - AI-Powered Country Comparison

Uses GPT-4 to intelligently rank countries based on comprehensive analysis:
- Financial metrics (LCOE, IRR, NPV, capacity factor)
- Resource quality assessment
- Policy environment stability
- Market maturity and characteristics
- Risk factors and opportunities

Provides detailed justification referencing specific data points.
Unbiased, transparent, source-backed reasoning.
"""

import logging
from typing import Dict, Any, List, Optional
import json


class RankingAgent:
    """
    AI-powered ranking agent for country comparison.

    Uses GPT-4 to create intelligent rankings with detailed justification.
    Considers multiple factors beyond simple financial metrics.
    """

    def __init__(self, llm_provider):
        """
        Initialize ranking agent.

        Args:
            llm_provider: LLM provider (OpenAI GPT-4)
        """
        self.llm_provider = llm_provider
        self.logger = self._create_logger()

        # Ranking criteria weights
        self.weights = {
            "financial_performance": 0.40,  # 40%
            "resource_quality": 0.25,  # 25%
            "policy_stability": 0.20,  # 20%
            "market_maturity": 0.15  # 15%
        }

        self.logger.info(
            f"Ranking Agent initialized with GPT-4 "
            f"(weights: Financial 40%, Resource 25%, Policy 20%, Market 15%)"
        )


    async def rank_countries(
            self,
            country_reports: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Rank countries using AI analysis.

        Args:
            country_reports: Dictionary of country analysis reports

        Returns:
            Ranking with detailed justification
        """
        self.logger.info(f"Ranking {len(country_reports)} countries with AI...")

        try:
            # Build comprehensive prompt
            prompt = self._build_ranking_prompt(country_reports)

            # Get GPT-4 ranking
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            response = await self.llm_provider.generate_completion(
                messages,
                temperature=0.2,  # Low temperature for consistent, objective analysis
                max_tokens=2000  # Enough for detailed justifications
            )

            # Parse JSON response
            ranking = self._parse_json_response(response)

            # Add metadata
            ranking['methodology'] = self._get_methodology_description()
            ranking['ranking_type'] = 'ai_powered'
            ranking['weights'] = self.weights

            self.logger.info(f"AI ranking complete: {len(ranking['ranked_countries'])} countries ranked")

            return ranking

        except Exception as e:
            self.logger.error(f"AI ranking failed: {str(e)}")
            # Fallback to basic ranking
            return self._create_fallback_ranking(country_reports)

    async def rank_countries_with_feedback(
                self,
                country_reports: Dict[str, Dict[str, Any]],
                previous_ranking: Optional[Dict[str, Any]] = None,
                verification_feedback: Optional[Dict[str, Any]] = None,
                iteration: int = 1
        ) -> Dict[str, Any]:
            """
            Rank countries with optional feedback from verification agent.

            This method improves ranking based on verification feedback.

            Args:
                country_reports: Dictionary of country analysis reports
                previous_ranking: Previous ranking attempt (if any)
                verification_feedback: Feedback from verification agent
                iteration: Current iteration number

            Returns:
                Ranking with detailed justification
            """
            self.logger.info(
                f"Ranking countries (iteration {iteration})"
                f"{' with feedback' if verification_feedback else ''}"
            )

            try:
                # Build prompt with or without feedback
                if verification_feedback and previous_ranking:
                    prompt = self._build_feedback_ranking_prompt(
                        country_reports,
                        previous_ranking,
                        verification_feedback,
                        iteration
                    )
                else:
                    # First attempt - no feedback
                    prompt = self._build_ranking_prompt(country_reports)

                # Get GPT-4 ranking
                messages = [
                    {
                        "role": "system",
                        "content": self._get_system_prompt_with_feedback()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

                response = await self.llm_provider.generate_completion(
                    messages,
                    temperature=0.2,  # Low temperature for consistent, objective analysis
                    max_tokens=2000
                )

                # Parse JSON response
                ranking = self._parse_json_response(response)

                # Add metadata
                ranking['methodology'] = self._get_methodology_description()
                ranking['ranking_type'] = 'ai_powered'
                ranking['weights'] = self.weights
                ranking['iteration'] = iteration
                ranking['improved_from_feedback'] = verification_feedback is not None

                self.logger.info(
                    f"AI ranking complete (iteration {iteration}): "
                    f"{len(ranking['ranked_countries'])} countries ranked"
                )

                return ranking

            except Exception as e:
                self.logger.error(f"AI ranking failed (iteration {iteration}): {str(e)}")
                # Fallback to basic ranking
                return self._create_fallback_ranking(country_reports)

    def _get_system_prompt_with_feedback(self) -> str:
            """Get system prompt that accepts feedback."""
            return """You are an expert renewable energy investment analyst with 20 years of experience ranking countries for institutional investors. Your rankings must be:

    1. **OBJECTIVE**: Based solely on data provided, no country bias
    2. **JUSTIFIED**: Every ranking decision explained with specific numbers
    3. **COMPREHENSIVE**: Consider financial, resource, policy, and market factors
    4. **TRANSPARENT**: Show your reasoning for why Country A ranks above Country B
    5. **ACTIONABLE**: Provide insights investors can act on
    6. **RESPONSIVE TO FEEDBACK**: If verification feedback is provided, address ALL issues raised

    You rank countries using these weighted criteria:
    - Financial Performance (40%): IRR, LCOE, NPV, project economics
    - Resource Quality (25%): Capacity factors, GHI/wind speed, resource reliability
    - Policy Stability (20%): Incentive stability, regulatory clarity, government support
    - Market Maturity (15%): Grid infrastructure, supply chain, development ecosystem

    **CRITICAL WHEN FEEDBACK PROVIDED:**
    - Address EVERY issue raised by verification
    - Adjust rankings if better metrics were ranked lower
    - Provide stronger data-driven justification
    - Reference specific numbers from the feedback
    - Explain why previous ranking was incorrect and how you've corrected it

    You MUST provide specific justification comparing countries directly."""

    def _build_feedback_ranking_prompt(
                self,
                country_reports: Dict[str, Dict[str, Any]],
                previous_ranking: Dict[str, Any],
                verification_feedback: Dict[str, Any],
                iteration: int
        ) -> str:
            """
            Build ranking prompt with verification feedback.

            Args:
                country_reports: Country analysis reports
                previous_ranking: Previous ranking attempt
                verification_feedback: Feedback from verification
                iteration: Current iteration number

            Returns:
                Complete prompt string with feedback
            """
            prompt = f"""This is ITERATION {iteration} of country ranking.

    VERIFICATION FEEDBACK FROM PREVIOUS RANKING (Iteration {iteration - 1}):

    {'=' * 70}
    PREVIOUS RANKING WAS: {"REJECTED" if not verification_feedback.get('verified') else "ACCEPTED"}
    {'=' * 70}

    Summary: {verification_feedback.get('summary', 'No summary provided')}

    CRITICAL ISSUES TO ADDRESS:
    """

            # Add issues from verification
            if verification_feedback.get('issues_found'):
                for i, issue in enumerate(verification_feedback['issues_found'], 1):
                    prompt += f"""
    Issue {i} [{issue['severity'].upper()}]:
      Problem: {issue['issue']}
      You must: {issue['recommendation']}
    """

            # Add checks that failed
            if verification_feedback.get('checks_performed'):
                prompt += "\n\nCHECKS THAT FAILED:\n"
                for check in verification_feedback['checks_performed']:
                    if check['status'] == 'failed':
                        prompt += f"  ✗ {check['check_type'].upper()}: {check['finding']}\n"

            prompt += f"""
    {'=' * 70}

    PREVIOUS RANKING (that was rejected):
    """

            # Show previous ranking
            for country in previous_ranking['ranked_countries']:
                prompt += f"""
    Rank {country['rank']}: {country['country_name']}
      Score: {country['overall_score']}
      Justification: {country['justification']}
    """

            prompt += f"""
    {'=' * 70}

    NOW, CREATE A NEW RANKING that addresses ALL the issues above.

    You have access to the same country data:
    """

            # Add country data (same as original prompt)
            for country_code, report in country_reports.items():
                metrics = report['aggregate_metrics']
                market = report['market_characteristics']
                investment = report['investment_context']

                prompt += f"""
    {'=' * 70}
    {report['country_name']} ({country_code}) - COMPLETE DATA
    {'=' * 70}

    FINANCIAL METRICS (40% weight):
    - Average IRR: {metrics['average_irr']:.2f}%
    - Average LCOE: ${metrics['average_lcoe']:.2f}/MWh
    - Average NPV: ${metrics['average_npv']:,.0f}
    - Average Capacity Factor: {metrics['average_capacity_factor'] * 100:.1f}%

    POLICY ENVIRONMENT (20% weight):
    - Policy Stability: {market['policy_stability_rating']}
    - Typical IRR Range: {investment['typical_project_irr_range']}

    MARKET CHARACTERISTICS (15% weight):
    - Grid Maturity: {market['grid_maturity_rating']}
    - Market Maturity: {market['market_maturity']}
    - Financing: {investment['financing_availability']}

    RESOURCE QUALITY (25% weight):
    - Capacity Factor: {metrics['average_capacity_factor'] * 100:.1f}%
    """

            prompt += f"""
    {'=' * 70}

    INSTRUCTIONS FOR NEW RANKING:

    1. **ADDRESS ALL VERIFICATION ISSUES**: Fix every problem raised
    2. **USE SPECIFIC NUMBERS**: Reference actual metrics in justifications
    3. **COMPARE DIRECTLY**: Explain why A > B with data (e.g., "USA's LCOE of $61/MWh vs Germany's $85/MWh")
    4. **JUSTIFY CAREFULLY**: If lower financial metrics ranked higher, explain with risk factors
    5. **BE OBJECTIVE**: No country bias - purely data-driven

    OUTPUT FORMAT (JSON only, no markdown):
    {{
      "ranked_countries": [
        {{
          "rank": 1,
          "country_code": "XXX",
          "country_name": "Country Name",
          "overall_score": 85.5,
          "component_scores": {{
            "financial_score": 88,
            "resource_score": 82,
            "policy_score": 90,
            "market_score": 78
          }},
          "justification": "Detailed justification with SPECIFIC NUMBERS comparing to other countries and ADDRESSING FEEDBACK",
          "key_differentiators": [
            "Specific differentiator with data",
            "Another differentiator with numbers"
          ],
          "feedback_addressed": "How this ranking addresses the verification issues raised"
        }}
      ],
      "ranking_summary": "Summary explaining how this ranking differs from previous iteration and addresses all feedback",
      "methodology_applied": "Brief description of how weights were applied"
    }}

    REMEMBER: This ranking will be verified again. Make it bulletproof!
    """

            return prompt


    def _get_system_prompt(self) -> str:
        """Get system prompt for AI ranking."""
        return """You are an expert renewable energy investment analyst with 20 years of experience ranking countries for institutional investors. Your rankings must be:

1. **OBJECTIVE**: Based solely on data provided, no country bias
2. **JUSTIFIED**: Every ranking decision explained with specific numbers
3. **COMPREHENSIVE**: Consider financial, resource, policy, and market factors
4. **TRANSPARENT**: Show your reasoning for why Country A ranks above Country B
5. **ACTIONABLE**: Provide insights investors can act on

You rank countries using these weighted criteria:
- Financial Performance (40%): IRR, LCOE, NPV, project economics
- Resource Quality (25%): Capacity factors, GHI/wind speed, resource reliability
- Policy Stability (20%): Incentive stability, regulatory clarity, government support
- Market Maturity (15%): Grid infrastructure, supply chain, development ecosystem

You MUST provide specific justification comparing countries directly."""

    def _build_ranking_prompt(
            self,
            country_reports: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Build comprehensive ranking prompt with all country data.

        Args:
            country_reports: Country analysis reports

        Returns:
            Complete prompt string
        """
        prompt = """Rank the following countries for renewable energy investment based on comprehensive analysis:

RANKING CRITERIA & WEIGHTS:
1. Financial Performance (40%): IRR, LCOE, NPV, project viability
2. Resource Quality (25%): Capacity factors, resource reliability
3. Policy Stability (20%): Incentive stability, regulatory environment
4. Market Maturity (15%): Infrastructure, supply chain, execution risk

COUNTRY DATA:
"""

        # Add each country's data
        for i, (country_code, report) in enumerate(country_reports.items(), 1):
            metrics = report['aggregate_metrics']
            market = report['market_characteristics']
            investment = report['investment_context']

            prompt += f"""
{'=' * 70}
COUNTRY {i}: {report['country_name']} ({country_code})
{'=' * 70}

FINANCIAL METRICS (40% weight):
- Average IRR: {metrics['average_irr']:.2f}%
- Average LCOE: ${metrics['average_lcoe']:.2f}/MWh
- Average NPV: ${metrics['average_npv']:,.0f}
- Locations Analyzed: {metrics['locations_analyzed']}
- Best Location: {report['best_location']}
- Overall Recommendation: {report['overall_recommendation']}

RESOURCE QUALITY (25% weight):
- Average Capacity Factor: {metrics['average_capacity_factor'] * 100:.1f}%

LOCATION DETAILS:
"""
            for loc in report['location_results']:
                prompt += f"""  • {loc['name']} ({loc['technology']}):
    LCOE ${loc['lcoe']:.2f}/MWh, IRR {loc['irr']:.1f}%, CF {loc['capacity_factor'] * 100:.1f}%
    Rationale: {loc['rationale']}
"""

            prompt += f"""
POLICY ENVIRONMENT (20% weight):
- Total Installed Capacity: {market['total_installed_capacity_gw']} GW
- Target 2030: {market.get('target_2030_gw', 'N/A')} GW
- Policy Stability: {market['policy_stability_rating']}
- Market Maturity: {market['market_maturity']}

KEY STRENGTHS:
"""
            for strength in market['key_strengths']:
                prompt += f"  • {strength}\n"

            prompt += "\nKEY CHALLENGES:\n"
            for challenge in market['key_challenges']:
                prompt += f"  • {challenge}\n"

            prompt += f"""
MARKET CHARACTERISTICS (15% weight):
- Grid Maturity: {market['grid_maturity_rating']}
- Financing Availability: {investment['financing_availability']}
- Typical IRR Range: {investment['typical_project_irr_range']}
- Offtake Market: {investment['offtake_market']}
"""

        prompt += f"""
{'=' * 70}
RANKING INSTRUCTIONS
{'=' * 70}

Rank ALL {len(country_reports)} countries from BEST (rank 1) to WORST (rank {len(country_reports)}).

For each country provide:
1. **Rank**: 1 to {len(country_reports)}
2. **Overall Score**: 0-100 based on weighted criteria
3. **Component Scores**: Financial, Resource, Policy, Market (each 0-100)
4. **Detailed Justification**: 3-5 sentences explaining:
   - Why this country earned this rank
   - Specific metrics that support the ranking
   - Direct comparison to other countries (why higher/lower than others)
   - Key strengths and weaknesses

5. **Key Differentiators**: What makes this country unique (2-3 points)

CRITICAL REQUIREMENTS:
- Use SPECIFIC NUMBERS from the data above
- COMPARE countries directly (e.g., "USA's IRR of X% exceeds Germany's Y%")
- Be OBJECTIVE - rank based on data, not country name
- Explain EVERY ranking decision with data
- If two countries are close, explain the tie-breaker clearly

OUTPUT FORMAT (JSON only, no markdown):
{{
  "ranked_countries": [
    {{
      "rank": 1,
      "country_code": "XXX",
      "country_name": "Country Name",
      "overall_score": 85.5,
      "component_scores": {{
        "financial_score": 88,
        "resource_score": 82,
        "policy_score": 90,
        "market_score": 78
      }},
      "justification": "Detailed 3-5 sentence explanation with specific numbers comparing to other countries",
      "key_differentiators": [
        "Specific differentiator 1 with data",
        "Specific differentiator 2 with data"
      ]
    }}
  ],
  "ranking_summary": "2-3 sentence overview of the ranking results and key findings",
  "methodology_applied": "Brief description of how weights were applied to reach this ranking"
}}

Remember: OBJECTIVITY is paramount. Rank based on data only.
"""

        return prompt

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from GPT-4.

        Handles markdown code blocks.
        """
        response = response.strip()

        # Remove markdown code blocks
        if response.startswith('```'):
            lines = response.split('\n')
            lines = lines[1:]  # Remove ```json
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]  # Remove closing ```
            response = '\n'.join(lines)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                json_str = response[start:end + 1]
                return json.loads(json_str)
            raise

    def _create_fallback_ranking(
            self,
            country_reports: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create fallback ranking if AI fails.

        Uses simple weighted scoring.
        """
        self.logger.warning("Using fallback ranking (AI ranking failed)")

        scores = []

        for country_code, report in country_reports.items():
            metrics = report['aggregate_metrics']
            market = report['market_characteristics']

            # Financial score (normalize IRR 0-20% range)
            financial = min(metrics['average_irr'] / 20.0, 1.0) * 100 * self.weights['financial_performance']

            # Resource score (capacity factor 0-1)
            resource = metrics['average_capacity_factor'] * 100 * self.weights['resource_quality']

            # Policy score from rating
            policy_map = {'very_high': 100, 'high': 80, 'medium': 60, 'low': 40}
            policy = policy_map.get(market['policy_stability_rating'], 60) * self.weights['policy_stability']

            # Market score from rating
            market_map = {'very_high': 100, 'high': 80, 'medium': 60, 'low': 40}
            market_score = market_map.get(market['market_maturity'], 60) * self.weights['market_maturity']

            total = financial + resource + policy + market_score

            scores.append({
                "rank": 0,  # Will be set after sorting
                "country_code": country_code,
                "country_name": report['country_name'],
                "overall_score": round(total, 1),
                "component_scores": {
                    "financial_score": round(financial / self.weights['financial_performance'], 1),
                    "resource_score": round(resource / self.weights['resource_quality'], 1),
                    "policy_score": round(policy / self.weights['policy_stability'], 1),
                    "market_score": round(market_score / self.weights['market_maturity'], 1)
                },
                "justification": f"Fallback ranking based on weighted scoring. Financial: {round(financial, 1)}, Resource: {round(resource, 1)}, Policy: {round(policy, 1)}, Market: {round(market_score, 1)}",
                "key_differentiators": [
                    f"Average IRR: {metrics['average_irr']:.1f}%",
                    f"Policy Stability: {market['policy_stability_rating']}"
                ]
            })

        # Sort by score
        scores.sort(key=lambda x: x['overall_score'], reverse=True)

        # Add ranks
        for i, score in enumerate(scores, 1):
            score['rank'] = i

        return {
            "ranked_countries": scores,
            "ranking_type": "fallback_scoring",
            "methodology_applied": "Simple weighted scoring used due to AI ranking failure",
            "ranking_summary": f"{len(scores)} countries ranked using algorithmic fallback",
            "weights": self.weights
        }

    def _get_methodology_description(self) -> str:
        """Get methodology description."""
        return (
            "AI-powered ranking using GPT-4 with weighted criteria: "
            f"Financial Performance ({self.weights['financial_performance'] * 100:.0f}%), "
            f"Resource Quality ({self.weights['resource_quality'] * 100:.0f}%), "
            f"Policy Stability ({self.weights['policy_stability'] * 100:.0f}%), "
            f"Market Maturity ({self.weights['market_maturity'] * 100:.0f}%). "
            "Each country ranked with detailed justification and direct comparisons."
        )

    def _create_logger(self) -> logging.Logger:
        """Create logger instance."""
        logger = logging.getLogger("RankingAgent")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger