"""
Iterative Ranking Orchestrator

Manages feedback loop between Ranking Agent and Verification Agent:
1. Ranking Agent creates initial ranking
2. Verification Agent checks for bias/errors
3. If failed → Extract feedback → Pass to Ranking Agent → Retry
4. Repeat up to max_iterations or until verification passes
5. Save all iterations for complete audit trail

This enables self-improving rankings that get better with each iteration.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class IterativeRankingOrchestrator:
    """
    Orchestrates iterative ranking with verification feedback loop.

    Features:
    - Multi-iteration ranking improvement
    - Automatic feedback extraction and application
    - Complete version history tracking
    - Detailed improvement summary
    """

    def __init__(self, llm_provider, max_iterations: int = 3):
        """
        Initialize iterative ranking orchestrator.

        Args:
            llm_provider: LLM provider for AI agents
            max_iterations: Maximum ranking attempts (default: 3)
        """
        self.llm_provider = llm_provider
        self.max_iterations = max_iterations
        self.logger = self._create_logger()

        self.logger.info(
            f"Iterative Ranking Orchestrator initialized "
            f"(max_iterations: {max_iterations})"
        )

    async def rank_with_verification_loop(
            self,
            country_reports: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Rank countries with iterative verification feedback.

        This is the main method that manages the feedback loop:
        1. Ranking Agent creates ranking
        2. Verification Agent verifies
        3. If failed, extract feedback and retry
        4. Repeat until verified or max_iterations reached

        Args:
            country_reports: Dictionary of country analysis reports

        Returns:
            Complete result with all iterations and final ranking
        """
        start_time = datetime.now()

        self.logger.info(
            f"Starting iterative ranking for {len(country_reports)} countries "
            f"(max {self.max_iterations} iterations)"
        )

        # Initialize agents
        from src.agents.ranking.ranking_agent import RankingAgent
        from src.agents.verification.verification_agent import VerificationAgent

        ranking_agent = RankingAgent(self.llm_provider)
        verification_agent = VerificationAgent(self.llm_provider)

        # Track all iterations
        iterations = []

        # Variables for loop
        previous_ranking = None
        verification_feedback = None
        final_ranking = None
        final_verification = None

        # Iterative improvement loop
        for iteration in range(1, self.max_iterations + 1):
            self.logger.info(f"{'=' * 70}")
            self.logger.info(f"ITERATION {iteration}/{self.max_iterations}")
            self.logger.info(f"{'=' * 70}")

            # Step 1: Generate ranking (with feedback if available)
            iteration_start = datetime.now()

            ranking = await ranking_agent.rank_countries_with_feedback(
                country_reports=country_reports,
                previous_ranking=previous_ranking,
                verification_feedback=verification_feedback,
                iteration=iteration
            )

            ranking_time = (datetime.now() - iteration_start).total_seconds()

            self.logger.info(
                f"Ranking generated in {ranking_time:.2f}s "
                f"({'with feedback' if verification_feedback else 'initial attempt'})"
            )

            # Step 2: Verify ranking
            verification_start = datetime.now()

            verification = await verification_agent.verify_ranking(
                ranking=ranking,
                country_reports=country_reports
            )

            verification_time = (datetime.now() - verification_start).total_seconds()

            status = "PASSED ✓" if verification.get('verified', False) else "FAILED ✗"
            self.logger.info(
                f"Verification completed in {verification_time:.2f}s: {status}"
            )

            # Step 3: Save this iteration
            iteration_record = {
                "iteration": iteration,
                "timestamp": datetime.now().isoformat(),
                "ranking": ranking,
                "verification": verification,
                "timing": {
                    "ranking_seconds": ranking_time,
                    "verification_seconds": verification_time,
                    "total_seconds": ranking_time + verification_time
                },
                "status": "passed" if verification.get('verified', False) else "failed"
            }

            iterations.append(iteration_record)

            # Step 4: Check if we're done
            if verification.get('verified', False):
                self.logger.info(f"✓ Ranking PASSED verification on iteration {iteration}!")
                final_ranking = ranking
                final_verification = verification
                break

            # Step 5: Extract feedback for next iteration
            if iteration < self.max_iterations:
                self.logger.warning(
                    f"✗ Ranking FAILED verification on iteration {iteration}"
                )

                feedback = verification_agent.extract_actionable_feedback(verification)

                self.logger.info(
                    f"Extracted feedback: {len(feedback.get('critical_issues', []))} critical issues, "
                    f"{len(feedback.get('moderate_issues', []))} moderate issues"
                )

                # Prepare for next iteration
                previous_ranking = ranking
                verification_feedback = verification

            else:
                # Max iterations reached
                self.logger.error(
                    f"✗ Max iterations ({self.max_iterations}) reached without passing verification"
                )
                final_ranking = ranking
                final_verification = verification

        # Calculate final stats
        total_time = (datetime.now() - start_time).total_seconds()

        # Create improvement summary
        improvement_summary = self._create_improvement_summary(iterations)

        self.logger.info(f"{'=' * 70}")
        self.logger.info(f"Iterative ranking completed in {total_time:.2f}s")
        self.logger.info(f"Total iterations: {len(iterations)}")
        self.logger.info(f"Final status: {'VERIFIED ✓' if final_verification.get('verified') else 'UNVERIFIED ✗'}")
        self.logger.info(f"{'=' * 70}")

        return {
            "final_ranking": final_ranking,
            "final_verification": final_verification,
            "all_iterations": iterations,
            "improvement_summary": improvement_summary,
            "statistics": {
                "total_iterations": len(iterations),
                "iterations_until_success": len(iterations) if final_verification.get('verified') else None,
                "final_verified": final_verification.get('verified', False),
                "total_time_seconds": total_time,
                "average_iteration_time": total_time / len(iterations) if iterations else 0
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "max_iterations_allowed": self.max_iterations,
                "countries_analyzed": len(country_reports)
            }
        }

    def _create_improvement_summary(
            self,
            iterations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create summary of improvements across iterations.

        Args:
            iterations: List of all iteration records

        Returns:
            Summary of how ranking improved
        """
        if not iterations:
            return {"message": "No iterations completed"}

        summary = {
            "total_attempts": len(iterations),
            "successful": iterations[-1]['status'] == 'passed',
            "iterations_detail": []
        }

        for i, iteration in enumerate(iterations, 1):
            detail = {
                "iteration": i,
                "status": iteration['status'],
                "verification_summary": iteration['verification'].get('summary', ''),
                "issues_found": len(iteration['verification'].get('issues_found', [])),
                "timing": iteration['timing']['total_seconds']
            }

            # Add what changed from previous iteration
            if i > 1:
                prev_ranking = iterations[i - 2]['ranking']['ranked_countries']
                curr_ranking = iteration['ranking']['ranked_countries']

                # Check for rank changes
                rank_changes = []
                for country in curr_ranking:
                    prev_country = next(
                        (c for c in prev_ranking if c['country_code'] == country['country_code']),
                        None
                    )
                    if prev_country and prev_country['rank'] != country['rank']:
                        rank_changes.append(
                            f"{country['country_name']}: "
                            f"Rank {prev_country['rank']} → {country['rank']}"
                        )

                detail['changes_from_previous'] = rank_changes if rank_changes else [
                    "Justifications refined, ranks unchanged"]

            summary['iterations_detail'].append(detail)

        # Overall improvement narrative
        if summary['successful']:
            summary['conclusion'] = (
                f"Ranking achieved verification after {len(iterations)} iteration(s). "
                f"Iterative feedback improved ranking quality and objectivity."
            )
        else:
            summary['conclusion'] = (
                f"Ranking did not achieve verification after {len(iterations)} attempts. "
                f"Manual review recommended."
            )

        return summary

    def save_iterations_to_file(
            self,
            result: Dict[str, Any],
            filepath: str
    ) -> None:
        """
        Save all iterations to a JSON file for audit trail.

        Args:
            result: Complete result from rank_with_verification_loop
            filepath: Path to save JSON file
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved complete iteration history to: {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to save iterations to file: {str(e)}")
            raise

    def _create_logger(self) -> logging.Logger:
        """Create logger instance."""
        logger = logging.getLogger("IterativeRankingOrchestrator")

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
    print("🔄 Iterative Ranking Orchestrator Demo")
    print("=" * 70)


    async def demo():
        # Create LLM provider
        llm_provider = LLMProviderFactory.create('openai', model='gpt-4o')

        # Create orchestrator
        orchestrator = IterativeRankingOrchestrator(
            llm_provider=llm_provider,
            max_iterations=3
        )

        # Mock country reports (simplified for demo)
        mock_reports = {
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
                },
                "investment_context": {
                    "typical_project_irr_range": "8-15%",
                    "financing_availability": "Excellent"
                }
            },
            "DEU": {
                "country_name": "Germany",
                "aggregate_metrics": {
                    "average_irr": 5.78,
                    "average_lcoe": 85.27,
                    "average_npv": -64483733,
                    "average_capacity_factor": 0.283
                },
                "market_characteristics": {
                    "policy_stability_rating": "very_high",
                    "grid_maturity_rating": "very_high",
                    "market_maturity": "very_high",
                    "total_installed_capacity_gw": 148
                },
                "investment_context": {
                    "typical_project_irr_range": "6-10%",
                    "financing_availability": "Excellent"
                }
            }
        }

        print("\n🚀 Running iterative ranking with verification loop...")
        print(f"Countries: {', '.join(mock_reports.keys())}")
        print(f"Max iterations: 3\n")

        result = await orchestrator.rank_with_verification_loop(mock_reports)

        print(f"\n{'=' * 70}")
        print("📊 RESULTS")
        print(f"{'=' * 70}")

        stats = result['statistics']
        print(f"\nTotal Iterations: {stats['total_iterations']}")
        print(f"Final Status: {'✓ VERIFIED' if stats['final_verified'] else '✗ UNVERIFIED'}")
        print(f"Total Time: {stats['total_time_seconds']:.2f}s")

        if stats['iterations_until_success']:
            print(f"Success on Iteration: {stats['iterations_until_success']}")

        print(f"\n{'=' * 70}")
        print("🔄 IMPROVEMENT SUMMARY")
        print(f"{'=' * 70}")

        summary = result['improvement_summary']
        for detail in summary['iterations_detail']:
            status_icon = "✓" if detail['status'] == 'passed' else "✗"
            print(f"\nIteration {detail['iteration']}: {status_icon} {detail['status'].upper()}")
            print(f"  Issues: {detail['issues_found']}")
            print(f"  Time: {detail['timing']:.2f}s")
            if 'changes_from_previous' in detail:
                print(f"  Changes: {', '.join(detail['changes_from_previous'])}")

        print(f"\n{summary['conclusion']}")

        # Save to file
        orchestrator.save_iterations_to_file(
            result,
            'iterative_ranking_demo.json'
        )

        print(f"\n{'=' * 70}")
        print("✅ Demo complete! Check 'iterative_ranking_demo.json' for full history")
        print(f"{'=' * 70}")


    asyncio.run(demo())