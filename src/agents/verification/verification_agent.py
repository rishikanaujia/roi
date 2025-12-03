"""
Verification Agent - AI-Powered Ranking Validation

Uses GPT-4 to verify country rankings for:
- Logical consistency (better metrics should rank higher)
- Bias detection (country favoritism despite worse metrics)
- Methodology compliance (weights applied correctly)
- Justification quality (uses specific data, not generic statements)

Provides detailed audit trail and pass/fail verdict.
"""

import logging
from typing import Dict, Any, List, Optional
import json


class VerificationAgent:
    """
    AI-powered verification agent for ranking validation.

    Uses GPT-4 to ensure rankings are objective, unbiased, and data-driven.
    """

    def __init__(self, llm_provider):
        """
        Initialize verification agent.

        Args:
            llm_provider: LLM provider (OpenAI GPT-4)
        """
        self.llm_provider = llm_provider
        self.logger = self._create_logger()

        self.logger.info("Verification Agent initialized with GPT-4")

    async def verify_ranking(
            self,
            ranking: Dict[str, Any],
            country_reports: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify ranking for bias and consistency.

        Args:
            ranking: Ranking results from ranking agent
            country_reports: Country analysis reports with metrics

        Returns:
            Verification results with pass/fail verdict
        """
        self.logger.info(f"Verifying ranking of {len(ranking['ranked_countries'])} countries...")

        try:
            # Build verification prompt
            prompt = self._build_verification_prompt(ranking, country_reports)

            # Get GPT-4 verification
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
                temperature=0.1,  # Very low temperature for objective verification
                max_tokens=1500
            )

            # Parse verification results
            verification = self._parse_json_response(response)

            # Add metadata
            verification['verification_type'] = 'ai_powered'
            verification['verifier'] = 'GPT-4'

            status = "PASSED" if verification.get('verified', False) else "FAILED"
            self.logger.info(f"Verification complete: {status}")

            if not verification.get('verified', False):
                self.logger.warning(f"Verification failed: {verification.get('summary', 'Unknown reason')}")

            return verification

        except Exception as e:
            self.logger.error(f"Verification failed: {str(e)}")
            # Return basic verification as fallback
            return self._create_fallback_verification(ranking, country_reports)

    def extract_actionable_feedback(
            self,
            verification_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract actionable feedback for ranking agent.

        Args:
            verification_result: Full verification result

        Returns:
            Structured feedback for ranking improvement
        """
        if verification_result.get('verified', False):
            # No feedback needed - ranking passed
            return {
                "needs_improvement": False,
                "message": "Ranking passed verification - no changes needed"
            }

        # Extract critical feedback
        feedback = {
            "needs_improvement": True,
            "summary": verification_result.get('summary', ''),
            "critical_issues": [],
            "moderate_issues": [],
            "specific_actions": []
        }

        # Categorize issues by severity
        for issue in verification_result.get('issues_found', []):
            issue_summary = {
                "severity": issue['severity'],
                "problem": issue['issue'],
                "action": issue['recommendation']
            }

            if issue['severity'] == 'critical':
                feedback['critical_issues'].append(issue_summary)
            else:
                feedback['moderate_issues'].append(issue_summary)

            feedback['specific_actions'].append(issue['recommendation'])

        # Extract failed checks
        feedback['failed_checks'] = [
            {
                "type": check['check_type'],
                "finding": check['finding']
            }
            for check in verification_result.get('checks_performed', [])
            if check['status'] == 'failed'
        ]

        self.logger.info(
            f"Extracted feedback: {len(feedback['critical_issues'])} critical, "
            f"{len(feedback['moderate_issues'])} moderate issues"
        )

        return feedback

    def _get_system_prompt(self) -> str:
        """Get system prompt for verification."""
        return """You are an expert auditor specializing in validating investment ranking methodologies for institutional investors. Your job is to verify that country rankings are:

1. **LOGICALLY CONSISTENT**: Better metrics should generally rank higher (unless justified by risk factors)
2. **UNBIASED**: No country favoritism - rankings must be purely data-driven
3. **METHODOLOGICALLY SOUND**: Stated weights (Financial 40%, Resource 25%, Policy 20%, Market 15%) applied correctly
4. **WELL-JUSTIFIED**: Justifications reference specific numbers, not generic statements

You are STRICT but FAIR. You understand that:
- Lower IRR might be acceptable if offset by policy stability and lower risk
- Higher LCOE might be acceptable in markets with better grid infrastructure
- Developing markets may score lower on execution risk despite good resources

Your verification must be OBJECTIVE and DATA-DRIVEN. Flag real inconsistencies, not just different weighting preferences."""

    def _build_verification_prompt(
            self,
            ranking: Dict[str, Any],
            country_reports: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Build comprehensive verification prompt.

        Args:
            ranking: Ranking results
            country_reports: Country metrics

        Returns:
            Complete verification prompt
        """
        prompt = """Verify the following country ranking for bias, consistency, and methodology compliance.

RANKING TO VERIFY:
"""

        # Add ranked countries
        for country in ranking['ranked_countries']:
            prompt += f"""
{'=' * 70}
Rank {country['rank']}: {country['country_name']} ({country.get('country_code', 'N/A')})

Overall Score: {country['overall_score']}/100

Component Scores:
- Financial: {country['component_scores']['financial_score']}/100
- Resource: {country['component_scores']['resource_score']}/100  
- Policy: {country['component_scores']['policy_score']}/100
- Market: {country['component_scores']['market_score']}/100

Justification:
{country['justification']}

Key Differentiators:
"""
            if 'key_differentiators' in country:
                for diff in country['key_differentiators']:
                    prompt += f"  • {diff}\n"

        prompt += f"""
{'=' * 70}

ACTUAL METRICS (Ground Truth):
"""

        # Add actual metrics for verification
        for country_code, report in country_reports.items():
            metrics = report['aggregate_metrics']
            market = report['market_characteristics']

            prompt += f"""
{report['country_name']} ({country_code}) - ACTUAL METRICS:
- Average IRR: {metrics['average_irr']:.2f}%
- Average LCOE: ${metrics['average_lcoe']:.2f}/MWh
- Average NPV: ${metrics['average_npv']:,.0f}
- Average Capacity Factor: {metrics['average_capacity_factor'] * 100:.1f}%
- Policy Stability: {market['policy_stability_rating']}
- Grid Maturity: {market['grid_maturity_rating']}
- Market Maturity: {market['market_maturity']}
- Total Installed Capacity: {market['total_installed_capacity_gw']} GW

"""

        prompt += f"""
{'=' * 70}

STATED METHODOLOGY:
{ranking.get('methodology_applied', 'Not provided')}

Weights: Financial 40%, Resource 25%, Policy 20%, Market 15%

{'=' * 70}

VERIFICATION TASKS:

1. **CONSISTENCY CHECK**: 
   - Are countries with significantly better financial metrics (IRR, LCOE, NPV) ranked appropriately?
   - If a lower-ranked country has better metrics, is there clear justification based on risk factors?
   - Check each pair of adjacent countries - is the ranking order justified?

2. **BIAS CHECK**:
   - Does any country appear to be favored despite worse metrics?
   - Are justifications specific to the data, or generic/biased toward certain countries?
   - Is there unexplained preference for developed vs developing markets (or vice versa)?

3. **METHODOLOGY CHECK**:
   - Do component scores align with stated weights?
   - Are scores internally consistent (e.g., if IRR is 5% and typical is 8-15%, is financial score appropriately low)?
   - Is the overall score a reasonable weighted average of component scores?

4. **JUSTIFICATION CHECK**:
   - Does each justification reference specific numbers from the metrics?
   - Are comparisons direct and data-driven (e.g., "X's IRR of 5% vs Y's 8%")?
   - Are risk factors (policy uncertainty, grid delays, payment issues) properly considered?

OUTPUT FORMAT (JSON only, no markdown):
{{
  "verified": true/false,
  "summary": "One sentence verdict on whether ranking passed verification",
  "checks_performed": [
    {{
      "check_type": "consistency/bias/methodology/justification",
      "status": "passed/failed/warning",
      "description": "What was checked",
      "finding": "What was found (specific, with numbers)"
    }}
  ],
  "issues_found": [
    {{
      "severity": "critical/moderate/minor",
      "issue": "Specific issue description with country names and metrics",
      "recommendation": "How to fix it"
    }}
  ],
  "strengths": [
    "What the ranking did well (be specific)"
  ],
  "overall_assessment": "2-3 sentence assessment of ranking quality and trustworthiness"
}}

Be SPECIFIC in your findings. Reference actual numbers. If you find an issue, explain it with data.

Example of GOOD finding:
"Germany ranked #1 despite lower IRR (5.78% vs USA's 8-15%) is justified by superior policy stability (EEG 20-year tariffs vs IRA uncertainty post-2032) and grid maturity. This is appropriate risk-adjustment."

Example of BAD finding:
"Germany's ranking seems reasonable."

CRITICAL: Be strict but fair. Flag real bias or inconsistency, but accept valid risk-based reasoning.
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

    def _create_fallback_verification(
            self,
            ranking: Dict[str, Any],
            country_reports: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create fallback verification if AI fails.

        Uses rule-based consistency checks.
        """
        self.logger.warning("Using fallback verification (AI verification failed)")

        issues = []
        checks = []

        ranked = ranking['ranked_countries']

        # Build metrics lookup
        metrics_by_country = {
            code: report['aggregate_metrics']
            for code, report in country_reports.items()
        }

        # Check consistency between adjacent ranks
        for i in range(len(ranked) - 1):
            higher = ranked[i]
            lower = ranked[i + 1]

            higher_code = higher.get('country_code')
            lower_code = lower.get('country_code')

            if higher_code in metrics_by_country and lower_code in metrics_by_country:
                higher_metrics = metrics_by_country[higher_code]
                lower_metrics = metrics_by_country[lower_code]

                # Check IRR consistency (with 2% threshold for risk adjustment)
                if lower_metrics['average_irr'] > higher_metrics['average_irr'] + 2.0:
                    checks.append({
                        "check_type": "consistency",
                        "status": "warning",
                        "description": f"IRR comparison: {higher['country_name']} vs {lower['country_name']}",
                        "finding": f"{lower['country_name']} has higher IRR ({lower_metrics['average_irr']:.1f}%) than {higher['country_name']} ({higher_metrics['average_irr']:.1f}%) but ranked lower. May be justified by risk factors."
                    })
                else:
                    checks.append({
                        "check_type": "consistency",
                        "status": "passed",
                        "description": f"IRR comparison: {higher['country_name']} vs {lower['country_name']}",
                        "finding": f"Ranking order consistent with IRR metrics"
                    })

        # Overall verdict
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        verified = len(critical_issues) == 0

        return {
            "verified": verified,
            "verification_type": "fallback_rule_based",
            "verifier": "Rule-based consistency checker",
            "summary": f"Fallback verification {'passed' if verified else 'failed'}. {len(critical_issues)} critical issues found.",
            "checks_performed": checks,
            "issues_found": issues,
            "strengths": ["Basic consistency checks performed"],
            "overall_assessment": "This is fallback verification. AI verification recommended for comprehensive bias detection and methodology validation.",
            "note": "AI verification failed - using rule-based fallback. This provides basic consistency checks but not comprehensive bias detection."
        }

    def _create_logger(self) -> logging.Logger:
        """Create logger instance."""
        logger = logging.getLogger("VerificationAgent")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger


# Demo / Testing
if __name__ == "__main__":
    import asyncio
    from src.llm.factory import LLMProviderFactory

    print("=" * 70)
    print("🔍 Verification Agent Demo")
    print("=" * 70)


    async def demo():
        # Create LLM provider
        llm_provider = LLMProviderFactory.create('openai', model='gpt-4o')

        # Create verification agent
        agent = VerificationAgent(llm_provider)

        # Mock ranking data for demo
        mock_ranking = {
            "ranked_countries": [
                {
                    "rank": 1,
                    "country_code": "DEU",
                    "country_name": "Germany",
                    "overall_score": 82.5,
                    "component_scores": {
                        "financial_score": 75,
                        "resource_score": 90,
                        "policy_score": 95,
                        "market_score": 85
                    },
                    "justification": "Germany ranks first due to exceptional policy stability (EEG 20-year tariffs) and world-class wind resources (9.02 m/s). Despite lower IRR (6.5%), superior grid infrastructure and zero-subsidy potential justify top ranking.",
                    "key_differentiators": [
                        "EEG 2023 provides 20-year revenue certainty",
                        "World-class offshore wind (45% capacity factor)"
                    ]
                },
                {
                    "rank": 2,
                    "country_code": "USA",
                    "country_name": "United States",
                    "overall_score": 78.5,
                    "component_scores": {
                        "financial_score": 80,
                        "resource_score": 80,
                        "policy_score": 80,
                        "market_score": 75
                    },
                    "justification": "USA ranks second with strong IRA incentives (30% ITC) and excellent resources. Grid interconnection delays (3-5 years) and policy uncertainty post-2032 impact ranking vs Germany's stable framework.",
                    "key_differentiators": [
                        "IRA 30% ITC with bonuses through 2032",
                        "Active corporate PPA market (Amazon 10 GW)"
                    ]
                }
            ],
            "methodology_applied": "Weighted scoring: Financial 40%, Resource 25%, Policy 20%, Market 15%"
        }

        mock_reports = {
            "DEU": {
                "country_name": "Germany",
                "aggregate_metrics": {
                    "average_irr": 5.75,
                    "average_lcoe": 85.27,
                    "average_npv": -64483733,
                    "average_capacity_factor": 0.283
                },
                "market_characteristics": {
                    "policy_stability_rating": "very_high",
                    "grid_maturity_rating": "very_high",
                    "market_maturity": "very_high",
                    "total_installed_capacity_gw": 148
                }
            },
            "USA": {
                "country_name": "United States",
                "aggregate_metrics": {
                    "average_irr": 5.0,
                    "average_lcoe": 61.48,
                    "average_npv": -79053922,
                    "average_capacity_factor": 0.305
                },
                "market_characteristics": {
                    "policy_stability_rating": "high",
                    "grid_maturity_rating": "high",
                    "market_maturity": "very_high",
                    "total_installed_capacity_gw": 335
                }
            }
        }

        print("\n🔍 Running verification...")
        verification = await agent.verify_ranking(mock_ranking, mock_reports)

        print(f"\n{'=' * 70}")
        print(f"✅ VERIFICATION: {'PASSED' if verification['verified'] else 'FAILED'}")
        print(f"{'=' * 70}")
        print(f"\n📊 Summary: {verification['summary']}")

        print(f"\n🔎 Checks Performed ({len(verification['checks_performed'])}):")
        for check in verification['checks_performed']:
            status_icon = "✓" if check['status'] == 'passed' else "⚠" if check['status'] == 'warning' else "✗"
            print(f"  {status_icon} {check['check_type'].upper()}: {check['finding']}")

        if verification.get('issues_found'):
            print(f"\n⚠️  Issues Found ({len(verification['issues_found'])}):")
            for issue in verification['issues_found']:
                print(f"  • [{issue['severity'].upper()}] {issue['issue']}")
                print(f"    → {issue['recommendation']}")

        if verification.get('strengths'):
            print(f"\n💪 Strengths:")
            for strength in verification['strengths']:
                print(f"  • {strength}")

        print(f"\n📋 Overall Assessment:")
        print(f"   {verification['overall_assessment']}")

        print("\n" + "=" * 70)
        print("✅ Verification Agent Working!")
        print("=" * 70)


    asyncio.run(demo())