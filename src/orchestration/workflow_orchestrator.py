"""
Workflow Orchestrator - Multi-Agent Coordination with AI

Enhanced with AI-powered insights:
- Investment insights generation
- Risk assessment
- Data quality analysis
- Natural language recommendations

This orchestrator manages the complete workflow:
    Input → Research → Analysis → AI Insights → Output
"""

import logging
import time
from typing import Dict, Any, Optional
from enum import Enum

from src.agents.research.research_agent import ResearchAgent
from src.agents.analysis.analysis_agent import AnalysisAgent
from src.llm.mock_provider import MockLLMProvider


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RESEARCH_IN_PROGRESS = "research_in_progress"
    RESEARCH_COMPLETE = "research_complete"
    ANALYSIS_IN_PROGRESS = "analysis_in_progress"
    ANALYSIS_COMPLETE = "analysis_complete"
    AI_INSIGHTS_IN_PROGRESS = "ai_insights_in_progress"
    AI_INSIGHTS_COMPLETE = "ai_insights_complete"
    COMPLETE = "complete"
    FAILED = "failed"


class WorkflowOrchestrator:
    """
    Orchestrates multi-agent workflow with AI enhancement.

    Pipeline:
    1. ResearchAgent - Fetch policy and resource data
    2. AnalysisAgent - Calculate financial metrics
    3. AI Insights - Generate investment insights (NEW!)
    4. Format and return results
    """

    def __init__(
            self,
            llm_provider=None,
            config: Optional[Dict[str, Any]] = None,
            logger: Optional[logging.Logger] = None,
            max_retries: int = 2,
            enable_ai_insights: bool = True
    ):
        """
        Initialize Workflow Orchestrator.

        Args:
            llm_provider: LLM provider for AI features (optional, defaults to Mock)
            config: Base configuration (optional)
            logger: Logger instance (optional)
            max_retries: Maximum retry attempts per agent (default: 2)
            enable_ai_insights: Enable AI-generated insights (default: True)
        """
        self.llm_provider = llm_provider or MockLLMProvider()
        self.config = config or {}
        self.logger = logger or self._create_logger()
        self.max_retries = max_retries
        self.enable_ai_insights = enable_ai_insights

        # Execution tracking
        self._current_status = WorkflowStatus.PENDING
        self._execution_metrics = {}

        self.logger.info(
            f"WorkflowOrchestrator initialized "
            f"(AI insights: {enable_ai_insights}, "
            f"LLM: {self.llm_provider.get_provider_name()})"
        )

    async def analyze_opportunity(
            self,
            country: str,
            technology: str,
            latitude: float,
            longitude: float,
            capacity_mw: float = 100.0,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze a renewable energy opportunity (ONE CALL!).

        Enhanced with AI insights!
        """
        workflow_start = time.time()

        try:
            self.logger.info(
                f"Starting workflow: {country} + {technology} at "
                f"({latitude:.2f}, {longitude:.2f})"
            )

            # Step 1: Research
            self._update_status(WorkflowStatus.RESEARCH_IN_PROGRESS)
            research_result = await self._execute_research(
                country, technology, latitude, longitude, capacity_mw, **kwargs
            )
            self._update_status(WorkflowStatus.RESEARCH_COMPLETE)

            # Validate research results
            if not self._validate_research_results(research_result):
                raise ValueError("Research results validation failed")

            # Step 2: Analysis
            self._update_status(WorkflowStatus.ANALYSIS_IN_PROGRESS)
            analysis_result = await self._execute_analysis(
                country, technology, research_result, capacity_mw, **kwargs
            )
            self._update_status(WorkflowStatus.ANALYSIS_COMPLETE)

            # Step 3: AI Insights (NEW!)
            self._update_status(WorkflowStatus.AI_INSIGHTS_IN_PROGRESS)
            ai_data = await self._generate_ai_insights(analysis_result, research_result)
            self._update_status(WorkflowStatus.AI_INSIGHTS_COMPLETE)

            # Step 4: Format final results
            final_result = self._format_final_results(
                country, technology, latitude, longitude, capacity_mw,
                research_result, analysis_result, ai_data
            )

            # Add execution metrics
            workflow_time = time.time() - workflow_start
            final_result['execution_metrics'] = {
                **self._execution_metrics,
                'total_time_seconds': round(workflow_time, 2)
            }

            self._update_status(WorkflowStatus.COMPLETE)
            self.logger.info(f"Workflow complete in {workflow_time:.2f}s")

            return final_result

        except Exception as e:
            self._update_status(WorkflowStatus.FAILED)
            self.logger.error(f"Workflow failed: {str(e)}")
            raise

    async def _execute_research(
            self,
            country: str,
            technology: str,
            latitude: float,
            longitude: float,
            capacity_mw: float,
            **kwargs
    ) -> Dict[str, Any]:
        """Execute research phase with retry logic."""
        research_start = time.time()

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Research attempt {attempt}/{self.max_retries}")

                # Create research agent
                research_agent = ResearchAgent(
                    llm_provider=self.llm_provider,
                    config=self.config,
                    country_code=country,
                    technology=technology
                )

                # Execute research
                result = await research_agent.execute({
                    "latitude": latitude,
                    "longitude": longitude,
                    "capacity_mw": capacity_mw,
                    **kwargs
                })

                # Track metrics
                research_time = time.time() - research_start
                self._execution_metrics['research_time_seconds'] = round(research_time, 2)
                self._execution_metrics['research_attempts'] = attempt

                self.logger.info(f"Research successful in {research_time:.2f}s")
                return result

            except Exception as e:
                self.logger.warning(f"Research attempt {attempt} failed: {str(e)}")

                if attempt == self.max_retries:
                    self.logger.error("Research failed after all retries")
                    raise

                # Wait before retry (exponential backoff)
                await self._wait_before_retry(attempt)

        raise RuntimeError("Research failed unexpectedly")

    async def _execute_analysis(
            self,
            country: str,
            technology: str,
            research_result: Dict[str, Any],
            capacity_mw: float,
            **kwargs
    ) -> Dict[str, Any]:
        """Execute analysis phase with retry logic."""
        analysis_start = time.time()

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Analysis attempt {attempt}/{self.max_retries}")

                # Create analysis agent
                analysis_agent = AnalysisAgent(
                    llm_provider=self.llm_provider,
                    config=self.config,
                    country_code=country,
                    technology=technology
                )

                # Execute analysis
                result = await analysis_agent.execute({
                    "research_data": research_result,
                    "capacity_mw": capacity_mw,
                    **kwargs
                })

                # Track metrics
                analysis_time = time.time() - analysis_start
                self._execution_metrics['analysis_time_seconds'] = round(analysis_time, 2)
                self._execution_metrics['analysis_attempts'] = attempt

                self.logger.info(f"Analysis successful in {analysis_time:.2f}s")
                return result

            except Exception as e:
                self.logger.warning(f"Analysis attempt {attempt} failed: {str(e)}")

                if attempt == self.max_retries:
                    self.logger.error("Analysis failed after all retries")
                    raise

                # Wait before retry
                await self._wait_before_retry(attempt)

        raise RuntimeError("Analysis failed unexpectedly")

    async def _generate_ai_insights(
            self,
            analysis_result: Dict[str, Any],
            research_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI insights and assess data quality.

        NEW! AI-powered enhancement.

        Args:
            analysis_result: Analysis results
            research_result: Research results

        Returns:
            Dictionary with AI insights and quality assessment
        """
        if not self.enable_ai_insights:
            self.logger.info("AI insights disabled, skipping")
            return {}

        try:
            ai_start = time.time()
            self.logger.info("Generating AI insights...")

            # Generate investment insights
            insights = await self.llm_provider.generate_insights(analysis_result)

            # Assess data quality
            quality = await self.llm_provider.assess_data_quality(research_result)

            # Track metrics
            ai_time = time.time() - ai_start
            self._execution_metrics['ai_insights_time_seconds'] = round(ai_time, 2)

            self.logger.info(f"AI insights generated in {ai_time:.2f}s")

            return {
                "ai_insights": insights,
                "data_quality": quality
            }

        except Exception as e:
            self.logger.warning(f"AI insight generation failed: {str(e)}")
            return {}

    def _validate_research_results(self, research_result: Dict[str, Any]) -> bool:
        """Validate research results before passing to analysis."""
        required_fields = ['policy_data', 'resource_data', 'data_completeness']

        if not all(field in research_result for field in required_fields):
            self.logger.error("Research results missing required fields")
            return False

        # Check data completeness
        completeness = research_result.get('data_completeness', {})
        if not completeness.get('ready_for_analysis', False):
            self.logger.warning("Research data may not be ready for analysis")
            # Don't fail, but log warning

        return True

    def _format_final_results(
            self,
            country: str,
            technology: str,
            latitude: float,
            longitude: float,
            capacity_mw: float,
            research_result: Dict[str, Any],
            analysis_result: Dict[str, Any],
            ai_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Format final results in clean, user-friendly structure.

        Enhanced with AI insights!
        """
        # Extract key metrics
        financial_metrics = analysis_result['financial_metrics']
        viability = analysis_result['viability_assessment']

        # Create clean output
        result = {
            # Project Information
            "project": {
                "country": country,
                "technology": technology,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "capacity_mw": capacity_mw
            },

            # Key Financial Metrics (Easy Access!)
            "lcoe": financial_metrics['lcoe_usd_per_mwh'],
            "irr": financial_metrics['irr_percent'],
            "npv": financial_metrics['npv_usd'],
            "capacity_factor": analysis_result['capacity_factor'],
            "payback_years": financial_metrics['payback_period_years'],

            # Recommendation
            "recommendation": viability['recommendation'],
            "confidence": viability['confidence'],

            # Resource Summary
            "resource_summary": self._extract_resource_summary(
                research_result, technology
            ),

            # Policy Summary
            "policy_summary": self._extract_policy_summary(
                research_result, country
            ),

            # AI Insights (NEW!)
            "ai_insights": ai_data.get("ai_insights") if ai_data else None,
            "data_quality": ai_data.get("data_quality") if ai_data else None,

            # Detailed Results (for deep dive)
            "detailed_research": research_result,
            "detailed_analysis": analysis_result,

            # Workflow Status
            "status": self._current_status.value,
            "workflow_complete": True
        }

        return result

    def _extract_resource_summary(
            self,
            research_result: Dict[str, Any],
            technology: str
    ) -> Dict[str, Any]:
        """Extract key resource metrics for summary."""
        resource_data = research_result['resource_data']['resource_data']

        if technology == "solar_pv":
            return {
                "ghi_kwh_m2_day": resource_data.get('avg_ghi_kwh_m2_day'),
                "temperature_c": resource_data.get('avg_temperature_c'),
                "quality": research_result['resource_data']['quality']['confidence']
            }
        elif "wind" in technology:
            return {
                "wind_speed_m_s": resource_data.get('avg_wind_speed_m_s'),
                "wind_power_density_w_m2": resource_data.get('wind_power_density_w_m2'),
                "quality": research_result['resource_data']['quality']['confidence']
            }
        else:
            return {"raw": resource_data}

    def _extract_policy_summary(
            self,
            research_result: Dict[str, Any],
            country: str
    ) -> Dict[str, Any]:
        """Extract key policy metrics for summary."""
        policy_data = research_result['policy_data']
        incentives = policy_data.get('incentives', {})

        summary = {
            "tax_rate": policy_data.get('tax_rate'),
            "confidence": policy_data.get('confidence')
        }

        # Country-specific incentives
        if country == "USA":
            summary['federal_itc'] = incentives.get('federal_itc_percentage')
            summary['federal_ptc'] = incentives.get('federal_ptc_usd_per_mwh', 0)
        elif country == "DEU":
            summary['eeg_tariff'] = incentives.get('base_tariff_eur_per_mwh')
        elif country == "IND":
            summary['gbi_rate'] = incentives.get('gbi_rate_inr_per_kwh', 0)

        return summary

    async def _wait_before_retry(self, attempt: int):
        """Wait before retry with exponential backoff."""
        import asyncio
        wait_time = 2 ** attempt  # 2s, 4s, 8s...
        self.logger.info(f"Waiting {wait_time}s before retry...")
        await asyncio.sleep(wait_time)

    def _update_status(self, status: WorkflowStatus):
        """Update current workflow status."""
        self._current_status = status
        self.logger.debug(f"Status updated: {status.value}")

    def get_status(self) -> str:
        """Get current workflow status."""
        return self._current_status.value

    def _create_logger(self) -> logging.Logger:
        """Create logger instance."""
        logger = logging.getLogger("WorkflowOrchestrator")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger

    def _create_mock_llm(self):
        """Create mock LLM provider for demo."""
        return MockLLMProvider()


# Demo
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("🤖 WORKFLOW ORCHESTRATOR - NOW WITH AI! 🤖")
    print("=" * 70)


    async def demo():
        # Create orchestrator with AI enabled
        orchestrator = WorkflowOrchestrator(enable_ai_insights=True)

        # Test 1: USA + Solar PV with AI insights
        print("\n" + "=" * 70)
        print("TEST 1: Complete Workflow with AI Insights - USA + Solar PV")
        print("=" * 70)

        result1 = await orchestrator.analyze_opportunity(
            country="USA",
            technology="solar_pv",
            latitude=31.99,
            longitude=-102.07,
            capacity_mw=100
        )

        print("\n📊 Financial Results:")
        print(f"  LCOE: ${result1['lcoe']:.2f}/MWh")
        print(f"  IRR: {result1['irr']:.1f}%")
        print(f"  Recommendation: {result1['recommendation']}")

        # Show AI insights!
        if result1.get('ai_insights'):
            ai = result1['ai_insights']
            print("\n🤖 AI-Generated Insights:")
            print(f"  Key Insights:")
            for insight in ai['key_insights']:
                print(f"    • {insight}")

            print(f"\n  Top Risks:")
            for risk in ai['risks'][:2]:
                print(f"    • {risk}")

            print(f"\n  Opportunities:")
            for opp in ai['opportunities'][:2]:
                print(f"    • {opp}")

            print(f"\n  Summary: {ai['recommendation_summary'][:200]}...")

        # Show data quality
        if result1.get('data_quality'):
            quality = result1['data_quality']
            print(f"\n📈 Data Quality Assessment:")
            print(f"  Overall Quality: {quality['overall_quality']}")
            print(f"  Confidence Score: {quality['confidence_score']}")
            print(f"  Data Gaps: {quality['data_gaps'][0]}")

        print(f"\n⏱️  Execution Time: {result1['execution_metrics']['total_time_seconds']}s")
        if 'ai_insights_time_seconds' in result1['execution_metrics']:
            print(f"  AI Insights Time: {result1['execution_metrics']['ai_insights_time_seconds']}s")


    asyncio.run(demo())

    print("\n" + "=" * 70)
    print("✅ WORKFLOW ORCHESTRATOR WITH AI WORKING PERFECTLY!")
    print("=" * 70)