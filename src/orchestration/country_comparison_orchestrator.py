"""
Country Comparison Orchestrator

Handles multi-country analysis workflow:
1. Takes list of country names/codes
2. Loads representative locations for each country
3. Analyzes each location in parallel
4. Aggregates results by country
5. Passes to ranking agent
6. Gets verification from verification agent
7. Returns complete comparison with verified ranking

This is the main entry point for country comparison feature.
"""

import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.orchestration.workflow_orchestrator import WorkflowOrchestrator


class CountryComparisonOrchestrator:
    """
    Orchestrates multi-country comparison analysis.

    Features:
    - Loads representative locations from database
    - Parallel analysis of all locations
    - Country-level aggregation
    - AI-powered ranking (coming in next file)
    - Bias verification (coming in next file)
    """

    def __init__(self, llm_provider=None):
        """
        Initialize country comparison orchestrator.

        Args:
            llm_provider: LLM provider for AI insights (optional)
        """
        self.llm_provider = llm_provider
        self.logger = self._create_logger()

        # Load representative locations database
        self.locations_db = self._load_locations_database()

        self.logger.info(
            f"Country Comparison Orchestrator initialized with "
            f"{len(self.locations_db)} countries in database"
        )

    def _load_locations_database(self) -> Dict[str, Any]:
        """
        Load representative locations database.

        Returns:
            Dictionary with country data
        """
        try:
            # Path from orchestration/country_comparison_orchestrator.py
            # to data/country_representative_locations.json
            current_file = Path(__file__)
            db_file = current_file.parent.parent.parent / "data" / "country_representative_locations.json"

            if not db_file.exists():
                self.logger.error(f"Locations database not found: {db_file}")
                return {}

            with open(db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.logger.info(f"Loaded {len(data)} countries from database")
            return data

        except Exception as e:
            self.logger.error(f"Failed to load locations database: {str(e)}")
            return {}

    async def compare_countries(
            self,
            country_codes: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple countries for renewable energy investment.

        This is the main entry point for country comparison.

        Args:
            country_codes: List of country codes ["USA", "IND", "DEU", "BRA", "AUS"]

        Returns:
            Complete comparison with ranking and verification
        """
        start_time = datetime.now()

        self.logger.info(f"Starting country comparison for: {', '.join(country_codes)}")

        # Step 1: Validate countries
        validated_countries = self._validate_countries(country_codes)

        if not validated_countries:
            return {
                "error": "No valid countries provided",
                "supported_countries": list(self.locations_db.keys())
            }

        # Step 2: Get representative locations for each country
        all_locations = self._get_representative_locations(validated_countries)

        self.logger.info(f"Analyzing {len(all_locations)} total locations across {len(validated_countries)} countries")

        # Step 3: Analyze all locations in parallel
        location_analyses = await self._analyze_all_locations(all_locations)

        # Step 4: Aggregate results by country
        country_reports = self._aggregate_by_country(location_analyses, validated_countries)

        # Step 5: Rank countries using AI (or fallback if no LLM)
        #ranking = await self._create_ranking(country_reports)

        # Step 6: Verify ranking using AI (or fallback if no LLM)
        #verification = await self._create_verification(ranking, country_reports)

        # Step 5 & 6: Rank countries with iterative verification
        ranking_result = await self._create_ranking_with_verification(country_reports)

        # Extract final ranking and verification
        ranking = ranking_result['final_ranking']
        verification = ranking_result['final_verification']

        elapsed_time = (datetime.now() - start_time).total_seconds()

        self.logger.info(f"Country comparison completed in {elapsed_time:.2f}s")

        return {
            "comparison_summary": {
                "total_countries_analyzed": len(validated_countries),
                "total_locations_analyzed": len(all_locations),
                "analysis_time_seconds": elapsed_time,
                "timestamp": datetime.now().isoformat()
            },
            "country_reports": country_reports,
            "ranking": ranking,
            "verification": verification,
            "ranking_iterations": ranking_result.get('all_iterations', []),
            "improvement_summary": ranking_result.get('improvement_summary', {}),
            "ranking_statistics": ranking_result.get('statistics', {}),
            "methodology": {
                "description": "Multi-location analysis with representative sites per country",
                "location_selection": "Each country analyzed using 2 representative locations (solar + wind)",
                "aggregation": "Country metrics averaged across all locations",
                "ranking_criteria": "Financial performance (40%), Resource quality (25%), Policy stability (20%), Market maturity (15%)",
                "bias_prevention": "Iterative verification with feedback loop - up to 3 ranking attempts until verification passes"
            }
        }

    def _validate_countries(self, country_codes: List[str]) -> List[str]:
        """
        Validate that requested countries exist in database.

        Args:
            country_codes: List of country codes

        Returns:
            List of valid country codes
        """
        validated = []
        invalid = []

        for code in country_codes:
            code_upper = code.upper()
            if code_upper in self.locations_db:
                validated.append(code_upper)
            else:
                invalid.append(code)

        if invalid:
            self.logger.warning(
                f"Invalid countries requested (skipping): {', '.join(invalid)}"
            )
            self.logger.info(
                f"Supported countries: {', '.join(self.locations_db.keys())}"
            )

        return validated

    def _get_representative_locations(
            self,
            country_codes: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get representative locations for each country.

        Args:
            country_codes: List of valid country codes

        Returns:
            List of location analysis configs
        """
        all_locations = []

        for country_code in country_codes:
            country_data = self.locations_db[country_code]

            for location in country_data['representative_locations']:
                analysis_config = {
                    "name": f"{country_data['country_name']} - {location['name']}",
                    "country": country_code,
                    "country_name": country_data['country_name'],
                    "technology": location['technology'],
                    "latitude": location['latitude'],
                    "longitude": location['longitude'],
                    "capacity_mw": location['capacity_mw'],
                    "location_rationale": location['rationale'],
                    "selection_criteria": location['selection_criteria']
                }
                all_locations.append(analysis_config)

        return all_locations

    async def _analyze_all_locations(
            self,
            locations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze all locations in parallel.

        Args:
            locations: List of location configs

        Returns:
            List of analysis results
        """
        self.logger.info(f"Starting parallel analysis of {len(locations)} locations...")

        # Create analysis tasks
        tasks = [
            self._analyze_single_location(location)
            for location in locations
        ]

        # Run all analyses in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors
        successful = []
        failed = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(
                    f"Analysis failed for {locations[i]['name']}: {str(result)}"
                )
                failed += 1
            else:
                successful.append(result)

        self.logger.info(
            f"Parallel analysis complete: {len(successful)} successful, {failed} failed"
        )

        return successful

    async def _analyze_single_location(
            self,
            location_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a single location using workflow orchestrator.

        Args:
            location_config: Location analysis configuration

        Returns:
            Complete analysis result
        """
        try:
            # Create workflow orchestrator for this analysis
            orchestrator = WorkflowOrchestrator(llm_provider=self.llm_provider)

            # Run analysis using correct method name
            result = await orchestrator.analyze_opportunity(
                country=location_config['country'],
                technology=location_config['technology'],
                latitude=location_config['latitude'],
                longitude=location_config['longitude'],
                capacity_mw=location_config['capacity_mw']
            )

            # Add metadata
            result['location_name'] = location_config['name']
            result['location_rationale'] = location_config['location_rationale']
            result['selection_criteria'] = location_config['selection_criteria']

            return result

        except Exception as e:
            self.logger.error(
                f"Failed to analyze {location_config['name']}: {str(e)}"
            )
            raise

    def _aggregate_by_country(
            self,
            location_analyses: List[Dict[str, Any]],
            country_codes: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate location results by country.

        Args:
            location_analyses: List of location analysis results
            country_codes: List of country codes being analyzed

        Returns:
            Dictionary with aggregated country reports
        """
        country_reports = {}

        for country_code in country_codes:
            # Get all analyses for this country
            country_analyses = [
                analysis for analysis in location_analyses
                if analysis['project']['country'] == country_code
            ]

            if not country_analyses:
                continue

            # Get country data from database
            country_data = self.locations_db[country_code]

            # Calculate aggregate metrics
            avg_lcoe = sum(a['lcoe'] for a in country_analyses) / len(country_analyses)
            avg_irr = sum(a['irr'] for a in country_analyses) / len(country_analyses)
            avg_npv = sum(a['npv'] for a in country_analyses) / len(country_analyses)
            avg_cf = sum(a['capacity_factor'] for a in country_analyses) / len(country_analyses)

            # Determine overall recommendation
            viable_count = sum(
                1 for a in country_analyses
                if a['recommendation'] in ['HIGHLY VIABLE', 'VIABLE']
            )

            if viable_count == len(country_analyses):
                overall_recommendation = "HIGHLY ATTRACTIVE"
            elif viable_count >= len(country_analyses) / 2:
                overall_recommendation = "ATTRACTIVE"
            elif viable_count > 0:
                overall_recommendation = "MODERATELY ATTRACTIVE"
            else:
                overall_recommendation = "CHALLENGING"

            # Aggregate AI insights from all locations
            all_insights = []
            all_risks = []
            all_opportunities = []

            for analysis in country_analyses:
                if 'ai_insights' in analysis:
                    all_insights.extend(analysis['ai_insights'].get('key_insights', []))
                    all_risks.extend(analysis['ai_insights'].get('risks', []))
                    all_opportunities.extend(analysis['ai_insights'].get('opportunities', []))

            # Create country report
            country_reports[country_code] = {
                "country_code": country_code,
                "country_name": country_data['country_name'],

                # Aggregate financial metrics
                "aggregate_metrics": {
                    "average_lcoe": round(avg_lcoe, 2),
                    "average_irr": round(avg_irr, 2),
                    "average_npv": round(avg_npv, 2),
                    "average_capacity_factor": round(avg_cf, 4),
                    "locations_analyzed": len(country_analyses)
                },

                # Best performing location
                "best_location": max(
                    country_analyses,
                    key=lambda x: x['irr']
                )['location_name'],

                # Overall recommendation
                "overall_recommendation": overall_recommendation,

                # Market characteristics from database
                "market_characteristics": country_data['market_characteristics'],

                # Investment context
                "investment_context": country_data['investment_context'],

                # Detailed location results
                "location_results": [
                    {
                        "name": a['location_name'],
                        "technology": a['project']['technology'],
                        "lcoe": a['lcoe'],
                        "irr": a['irr'],
                        "npv": a['npv'],
                        "capacity_factor": a['capacity_factor'],
                        "recommendation": a['recommendation'],
                        "rationale": a['location_rationale']
                    }
                    for a in country_analyses
                ],

                # Aggregated AI insights
                "aggregated_insights": {
                    "key_insights": all_insights[:5],  # Top 5
                    "key_risks": all_risks[:5],
                    "key_opportunities": all_opportunities[:5]
                }
            }

        return country_reports

    async def _create_ranking(
            self,
            country_reports: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create ranking using AI if available, otherwise fallback.

        Args:
            country_reports: Country analysis reports

        Returns:
            Ranking with justification
        """
        if self.llm_provider:
            # Use AI ranking agent
            try:
                from src.agents.ranking.ranking_agent import RankingAgent

                self.logger.info("Using AI Ranking Agent (GPT-4)...")
                ranking_agent = RankingAgent(self.llm_provider)
                return await ranking_agent.rank_countries(country_reports)

            except Exception as e:
                self.logger.error(f"AI ranking failed: {str(e)}, using fallback")
                return self._create_basic_ranking(country_reports)
        else:
            # No LLM provider - use basic ranking
            self.logger.info("No LLM provider - using basic algorithmic ranking")
            return self._create_basic_ranking(country_reports)

    async def _create_ranking_with_verification(
            self,
            country_reports: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create ranking with iterative verification loop.

        Args:
            country_reports: Country analysis reports

        Returns:
            Complete result with final ranking, verification, and all iterations
        """
        if self.llm_provider:
            # Use iterative ranking with verification loop
            try:
                from src.orchestration.iterative_ranking_orchestrator import IterativeRankingOrchestrator

                self.logger.info("Using Iterative Ranking with Verification Loop...")

                # Create iterative orchestrator
                iterative_orchestrator = IterativeRankingOrchestrator(
                    llm_provider=self.llm_provider,
                    max_iterations=3  # Allow up to 3 attempts
                )

                # Run iterative ranking
                result = await iterative_orchestrator.rank_with_verification_loop(
                    country_reports
                )

                # Log results
                stats = result['statistics']
                self.logger.info(
                    f"Iterative ranking completed: {stats['total_iterations']} iterations, "
                    f"{'VERIFIED ✓' if stats['final_verified'] else 'UNVERIFIED ✗'}"
                )

                return result

            except Exception as e:
                self.logger.error(f"Iterative ranking failed: {str(e)}, using fallback")
                # Fallback to basic ranking
                ranking = self._create_basic_ranking(country_reports)
                verification = self._create_basic_verification(ranking, country_reports)
                return {
                    "final_ranking": ranking,
                    "final_verification": verification,
                    "all_iterations": [],
                    "improvement_summary": {"message": "Fallback ranking used"},
                    "statistics": {"total_iterations": 1, "final_verified": False}
                }
        else:
            # No LLM provider - use basic ranking + verification
            self.logger.info("No LLM provider - using basic ranking + verification")
            ranking = self._create_basic_ranking(country_reports)
            verification = self._create_basic_verification(ranking, country_reports)
            return {
                "final_ranking": ranking,
                "final_verification": verification,
                "all_iterations": [],
                "improvement_summary": {"message": "Basic ranking used (no LLM)"},
                "statistics": {"total_iterations": 1, "final_verified": False}
            }

    def _create_basic_ranking(
            self,
            country_reports: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create basic ranking based on metrics.

        This is a placeholder - will be replaced by AI ranking agent.

        Args:
            country_reports: Country analysis reports

        Returns:
            Basic ranking
        """
        # Calculate simple scores based on metrics
        scores = []

        for country_code, report in country_reports.items():
            metrics = report['aggregate_metrics']

            # Simple scoring: higher IRR better, lower LCOE better
            # Normalize IRR (assume 0-20% range)
            irr_score = min(metrics['average_irr'] / 20.0, 1.0) * 40

            # Normalize LCOE (assume $20-100/MWh range, lower is better)
            lcoe_normalized = max(0, 100 - metrics['average_lcoe']) / 80.0
            lcoe_score = lcoe_normalized * 25

            # Capacity factor score (0-1 range)
            cf_score = metrics['average_capacity_factor'] * 25

            # Policy/market score from ratings
            policy_rating = report['market_characteristics']['policy_stability_rating']
            policy_map = {'very_high': 10, 'high': 8, 'medium': 6, 'low': 4}
            policy_score = policy_map.get(policy_rating, 5)

            total_score = irr_score + lcoe_score + cf_score + policy_score

            scores.append({
                "country_code": country_code,
                "country_name": report['country_name'],
                "total_score": round(total_score, 2),
                "component_scores": {
                    "financial_score": round(irr_score, 2),
                    "cost_score": round(lcoe_score, 2),
                    "resource_score": round(cf_score, 2),
                    "policy_score": round(policy_score, 2)
                },
                "metrics": metrics
            })

        # Sort by total score (highest first)
        scores.sort(key=lambda x: x['total_score'], reverse=True)

        # Add ranks
        for i, score in enumerate(scores, 1):
            score['rank'] = i

        return {
            "ranking_type": "basic_scoring",
            "methodology": "Weighted scoring: Financial 40%, Cost 25%, Resource 25%, Policy 10%",
            "note": "This is basic algorithmic ranking. AI ranking agent will provide detailed justification.",
            "ranked_countries": scores
        }

    async def _create_verification(
            self,
            ranking: Dict[str, Any],
            country_reports: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify ranking using AI if available, otherwise fallback.

        Args:
            ranking: Ranking results
            country_reports: Country analysis reports

        Returns:
            Verification results
        """
        if self.llm_provider:
            # Use AI verification agent
            try:
                from src.agents.verification.verification_agent import VerificationAgent

                self.logger.info("Using AI Verification Agent (GPT-4)...")
                verification_agent = VerificationAgent(self.llm_provider)
                return await verification_agent.verify_ranking(ranking, country_reports)

            except Exception as e:
                self.logger.error(f"AI verification failed: {str(e)}, using fallback")
                return self._create_basic_verification(ranking, country_reports)
        else:
            # No LLM provider - use basic verification
            self.logger.info("No LLM provider - using basic rule-based verification")
            return self._create_basic_verification(ranking, country_reports)

    def _create_basic_verification(
            self,
            ranking: Dict[str, Any],
            country_reports: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create basic verification results.

        This is a placeholder - will be replaced by verification agent.

        Args:
            ranking: Ranking results
            country_reports: Country analysis reports

        Returns:
            Basic verification
        """
        # Check for obvious inconsistencies
        issues = []

        ranked = ranking['ranked_countries']

        # Build metrics lookup from country reports
        metrics_by_country = {
            code: report['aggregate_metrics']
            for code, report in country_reports.items()
        }

        for i in range(len(ranked) - 1):
            higher = ranked[i]
            lower = ranked[i + 1]

            # Get metrics for comparison
            higher_code = higher.get('country_code')
            lower_code = lower.get('country_code')

            if higher_code in metrics_by_country and lower_code in metrics_by_country:
                higher_metrics = metrics_by_country[higher_code]
                lower_metrics = metrics_by_country[lower_code]

                # Check if lower ranked country has significantly better IRR
                if lower_metrics['average_irr'] > higher_metrics['average_irr'] + 2.0:  # 2% threshold
                    issues.append(
                        f"{lower['country_name']} has significantly higher IRR "
                        f"({lower_metrics['average_irr']:.1f}%) than "
                        f"{higher['country_name']} ({higher_metrics['average_irr']:.1f}%) "
                        f"but ranked lower - may be justified by other factors"
                    )

        return {
            "verification_type": "basic_consistency_check",
            "verified": len(issues) == 0,
            "issues_found": len(issues),
            "issues": issues,
            "note": "This is basic rule-based verification. AI verification agent will provide comprehensive bias detection.",
            "recommendation": "Ranking appears consistent" if len(
                issues) == 0 else "Ranking has potential inconsistencies that may be justified by risk factors"
        }

    def get_supported_countries(self) -> List[Dict[str, str]]:
        """
        Get list of supported countries.

        Returns:
            List of country info dicts
        """
        return [
            {
                "code": code,
                "name": data['country_name'],
                "locations": len(data['representative_locations']),
                "total_capacity_gw": data['market_characteristics']['total_installed_capacity_gw']
            }
            for code, data in self.locations_db.items()
        ]

    def _create_logger(self) -> logging.Logger:
        """Create logger instance."""
        logger = logging.getLogger("CountryComparisonOrchestrator")

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

    print("=" * 70)
    print("🌍 Country Comparison Orchestrator Demo")
    print("=" * 70)


    async def demo():
        # Create orchestrator
        orchestrator = CountryComparisonOrchestrator()

        print(f"\n📊 Supported Countries:")
        for country in orchestrator.get_supported_countries():
            print(f"  • {country['name']} ({country['code']}): "
                  f"{country['locations']} locations, "
                  f"{country['total_capacity_gw']} GW installed")

        print("\n" + "=" * 70)
        print("🚀 Comparing: USA, India, Germany")
        print("=" * 70)

        # Run comparison
        result = await orchestrator.compare_countries(["USA", "IND", "DEU"])

        print(f"\n⏱️  Analysis Time: {result['comparison_summary']['analysis_time_seconds']:.2f}s")
        print(f"📍 Locations Analyzed: {result['comparison_summary']['total_locations_analyzed']}")

        print("\n🏆 RANKING:")
        for country in result['ranking']['ranked_countries']:
            print(f"\n  {country['rank']}. {country['country_name']}")
            print(f"     Score: {country['total_score']:.1f}/100")
            print(f"     Avg IRR: {country['metrics']['average_irr']:.1f}%")
            print(f"     Avg LCOE: ${country['metrics']['average_lcoe']:.2f}/MWh")
            print(f"     Avg CF: {country['metrics']['average_capacity_factor'] * 100:.1f}%")

        print("\n✅ Verification:")
        print(f"  Status: {'PASSED' if result['verification']['verified'] else 'FAILED'}")
        print(f"  {result['verification']['recommendation']}")

        print("\n" + "=" * 70)
        print("✅ Country Comparison Orchestrator Working!")
        print("=" * 70)


    asyncio.run(demo())