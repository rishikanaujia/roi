"""
API Routes - Endpoint Definitions

NOW USING REAL LLM FROM APP STATE!
"""
import logging

from fastapi import APIRouter, HTTPException, status, Request, Query
from typing import Dict, Any, List

from src.api.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    ErrorResponse,
    HealthResponse,
    SupportedOptionsResponse
)
from src.orchestration.workflow_orchestrator import WorkflowOrchestrator
from src.agents.research.policy_handlers.factory import PolicyHandlerFactory
from src.agents.research.resource_fetchers.factory import ResourceFetcherFactory

# Create router
router = APIRouter(prefix="/api/v1", tags=["Analysis"])
logger = logging.getLogger(__name__)


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Renewable Energy Opportunity",
    description="""
    Analyze a renewable energy investment opportunity with AI-powered insights.

    This endpoint orchestrates:
    1. Research Agent - Fetches REAL NASA satellite data
    2. Analysis Agent - Calculates financial metrics (LCOE, IRR, NPV)
    3. AI Agent - Generates professional investment insights (GPT-4 if configured)
    4. Returns investment-grade analysis with recommendation

    **Data Sources:**
    - NASA POWER: 30-year satellite climatology (free, global)
    - Policy databases: Country-specific incentives and regulations

    **AI Provider:**
    - Configured via environment: LLM_PROVIDER, OPENAI_API_KEY
    - Default: Mock (basic insights)
    - With GPT-4: Investment-grade insights (~$0.006/analysis)

    **Supported Countries:** USA, DEU (Germany), IND (India)
    **Supported Technologies:** solar_pv, onshore_wind

    **Example Request:**
```json
    {
        "country": "USA",
        "technology": "solar_pv",
        "latitude": 31.99,
        "longitude": -102.07,
        "capacity_mw": 100
    }
```
    """,
    responses={
        200: {"description": "Successful analysis", "model": AnalyzeResponse},
        400: {"description": "Invalid request", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def analyze_opportunity(request_data: AnalyzeRequest, request: Request):
    """
    Analyze a renewable energy opportunity.

    NOW USES REAL LLM FROM APP STATE!
    """
    try:
        # Get LLM provider from app state
        llm_provider = request.app.state.llm_provider

        # Create orchestrator with LLM provider
        orchestrator = WorkflowOrchestrator(
            llm_provider=llm_provider,
            enable_ai_insights=True
        )

        # Call orchestrator
        result = await orchestrator.analyze_opportunity(
            country=request_data.country,
            technology=request_data.technology,
            latitude=request_data.latitude,
            longitude=request_data.longitude,
            capacity_mw=request_data.capacity_mw,
            state=request_data.state
        )

        return result

    except ValueError as e:
        # Invalid input (e.g., unsupported country/technology)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Internal error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check API health and get supported options"
)
async def health_check(request: Request):
    """
    Health check endpoint with AI provider info.
    """
    countries = PolicyHandlerFactory.get_supported_countries()
    technologies = ResourceFetcherFactory.get_supported_technologies()

    # Get LLM provider info
    llm_provider = request.app.state.llm_provider
    ai_provider_name = llm_provider.get_provider_name()

    response = {
        "status": "healthy",
        "version": "1.0.0",
        "ai_provider": ai_provider_name,
        "data_source": "NASA POWER (30-year satellite climatology)",
        "supported_countries": countries,
        "supported_technologies": technologies
    }

    # Add cost info if using paid provider
    if hasattr(llm_provider, 'get_usage_stats'):
        try:
            stats = llm_provider.get_usage_stats()
            response["ai_usage"] = {
                "total_requests": stats.get('total_requests', 0),
                "total_cost_usd": stats.get('estimated_cost_usd', 0),
                "cost_per_request": stats.get('cost_per_request', 0)
            }
        except:
            pass

    return response


@router.get(
    "/supported",
    response_model=SupportedOptionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Supported Options",
    description="Get detailed list of supported countries and technologies"
)
async def get_supported_options():
    """
    Get supported countries and technologies.

    Returns detailed information about all supported options.
    """
    # Country mappings
    country_info = {
        "USA": {"code": "USA", "name": "United States"},
        "DEU": {"code": "DEU", "name": "Germany"},
        "IND": {"code": "IND", "name": "India"}
    }

    # Technology mappings
    tech_info = {
        "solar_pv": {"code": "solar_pv", "name": "Solar Photovoltaic"},
        "onshore_wind": {"code": "onshore_wind", "name": "Onshore Wind"}
    }

    countries = PolicyHandlerFactory.get_supported_countries()
    technologies = ResourceFetcherFactory.get_supported_technologies()

    return {
        "countries": [
            country_info.get(c, {"code": c, "name": c})
            for c in countries
        ],
        "technologies": [
            tech_info.get(t, {"code": t, "name": t})
            for t in technologies
        ],
        "total_combinations": len(countries) * len(technologies)
    }


@router.post(
    "/analyze/batch",
    status_code=status.HTTP_200_OK,
    summary="Batch Analyze Multiple Opportunities",
    description="""
    Analyze multiple renewable energy opportunities IN PARALLEL.

    Perfect for comparing opportunities across different:
    - Countries (USA vs India vs Germany)
    - Technologies (Solar vs Wind)
    - Locations (different coordinates)

    **Key Features:**
    - Runs analyses in parallel (much faster than sequential!)
    - Returns comparison summary
    - All benefit from real NASA data + GPT-4 insights

    **Example Request:**
```json
    {
        "analyses": [
            {
                "name": "West Texas Solar",
                "country": "USA",
                "technology": "solar_pv",
                "latitude": 31.99,
                "longitude": -102.07,
                "capacity_mw": 100
            },
            {
                "name": "Gujarat Solar",
                "country": "IND",
                "technology": "solar_pv",
                "latitude": 23.0,
                "longitude": 72.0,
                "capacity_mw": 100
            },
            {
                "name": "Germany Wind",
                "country": "DEU",
                "technology": "onshore_wind",
                "latitude": 54.0,
                "longitude": 8.0,
                "capacity_mw": 150
            }
        ]
    }
```

    **Performance:**
    - Sequential: 3 analyses × 13s = 39 seconds
    - Parallel: ~15 seconds (3x faster!)
    """,
    responses={
        200: {"description": "Successful batch analysis"},
        400: {"description": "Invalid request"},
        500: {"description": "Internal server error"}
    }
)
async def analyze_batch(batch_request: Dict[str, Any], request: Request):
    """
    Analyze multiple opportunities in parallel.

    This runs all analyses simultaneously using asyncio.gather(),
    making it much faster than sequential processing!
    """
    import asyncio
    from datetime import datetime

    try:
        # Extract analyses list
        analyses = batch_request.get('analyses', [])

        if not analyses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No analyses provided. Include 'analyses' array in request body."
            )

        if len(analyses) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 analyses per batch request."
            )

        # Get LLM provider from app state
        llm_provider = request.app.state.llm_provider

        # Create orchestrator
        orchestrator = WorkflowOrchestrator(
            llm_provider=llm_provider,
            enable_ai_insights=True
        )

        # Define async analysis function
        async def analyze_one(analysis_request: Dict[str, Any]) -> Dict[str, Any]:
            """Analyze one opportunity."""
            try:
                name = analysis_request.get('name', 'Unnamed Project')
                result = await orchestrator.analyze_opportunity(
                    country=analysis_request['country'],
                    technology=analysis_request['technology'],
                    latitude=analysis_request['latitude'],
                    longitude=analysis_request['longitude'],
                    capacity_mw=analysis_request.get('capacity_mw', 100),
                    state=analysis_request.get('state')
                )
                result['name'] = name
                result['success'] = True
                return result
            except Exception as e:
                return {
                    'name': analysis_request.get('name', 'Unnamed Project'),
                    'success': False,
                    'error': str(e),
                    'country': analysis_request.get('country'),
                    'technology': analysis_request.get('technology')
                }

        # Track timing
        start_time = datetime.now()

        # Run all analyses in parallel!
        results = await asyncio.gather(*[analyze_one(req) for req in analyses])

        # Calculate total time
        total_time = (datetime.now() - start_time).total_seconds()

        # Separate successful and failed analyses
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]

        # Create comparison summary
        comparison = _create_comparison_summary(successful)

        # Build response
        response = {
            'total_analyses': len(analyses),
            'successful': len(successful),
            'failed': len(failed),
            'total_time_seconds': round(total_time, 2),
            'avg_time_per_analysis': round(total_time / len(analyses), 2) if analyses else 0,
            'comparison_summary': comparison,
            'detailed_results': successful,
            'errors': failed if failed else None
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )


def _create_comparison_summary(results: list) -> Dict[str, Any]:
    """
    Create comparison summary from multiple results.

    Args:
        results: List of analysis results

    Returns:
        Comparison summary with rankings and insights
    """
    if not results:
        return {}

    # Extract key metrics
    projects = []
    for result in results:
        projects.append({
            'name': result.get('name', 'Unknown'),
            'country': result['project']['country'],
            'technology': result['project']['technology'],
            'lcoe': result['lcoe'],
            'irr': result['irr'],
            'npv': result['npv'],
            'capacity_factor': result['capacity_factor'],
            'recommendation': result['recommendation'],
            'resource_quality': result['resource_summary'].get('quality', 'unknown')
        })

    # Sort by IRR (descending - best first)
    by_irr = sorted(projects, key=lambda x: x['irr'], reverse=True)

    # Sort by LCOE (ascending - lowest first)
    by_lcoe = sorted(projects, key=lambda x: x['lcoe'])

    # Sort by capacity factor (descending - best first)
    by_cf = sorted(projects, key=lambda x: x['capacity_factor'], reverse=True)

    # Find best overall
    viable_projects = [p for p in projects if 'VIABLE' in p['recommendation']]
    best_overall = by_irr[0] if by_irr else None

    return {
        'total_projects': len(projects),
        'viable_projects': len(viable_projects),
        'best_irr': {
            'project': by_irr[0]['name'],
            'value': by_irr[0]['irr']
        } if by_irr else None,
        'lowest_lcoe': {
            'project': by_lcoe[0]['name'],
            'value': by_lcoe[0]['lcoe']
        } if by_lcoe else None,
        'highest_capacity_factor': {
            'project': by_cf[0]['name'],
            'value': by_cf[0]['capacity_factor'] * 100
        } if by_cf else None,
        'recommended_project': viable_projects[0]['name'] if viable_projects else None,
        'rankings': {
            'by_irr': [{'rank': i + 1, 'name': p['name'], 'irr': p['irr']} for i, p in enumerate(by_irr[:5])],
            'by_lcoe': [{'rank': i + 1, 'name': p['name'], 'lcoe': p['lcoe']} for i, p in enumerate(by_lcoe[:5])],
            'by_capacity_factor': [{'rank': i + 1, 'name': p['name'], 'cf': round(p['capacity_factor'] * 100, 1)} for
                                   i, p in enumerate(by_cf[:5])]
        },
        'comparison_table': [
            {
                'name': p['name'],
                'country': p['country'],
                'technology': p['technology'],
                'lcoe': round(p['lcoe'], 2),
                'irr': round(p['irr'], 1),
                'capacity_factor': round(p['capacity_factor'] * 100, 1),
                'recommendation': p['recommendation']
            }
            for p in projects
        ]
    }


@router.post("/compare-countries", response_model=Dict[str, Any])
async def compare_countries(
        request: Request,
        countries: List[str] = Query(
            ...,
            description="List of country codes to compare (e.g., ['USA', 'IND', 'DEU'])",
            min_items=2,
            max_items=10
        )
):
    """
    Compare multiple countries for renewable energy investment.

    This endpoint:
    1. Analyzes representative locations for each country
    2. Aggregates results by country
    3. Uses AI to rank countries with detailed justification
    4. Verifies ranking for bias and consistency

    Example request:
```
    POST /api/v1/compare-countries?countries=USA&countries=IND&countries=DEU
```

    Returns:
    - Country-level analysis reports
    - AI-powered ranking with justification
    - Verification results
    - Methodology description
    """
    try:
        logger.info(f"Comparing countries: {', '.join(countries)}")

        # Get LLM provider from app state
        llm_provider = getattr(request.app.state, 'llm_provider', None)

        # Create orchestrator
        from src.orchestration.country_comparison_orchestrator import CountryComparisonOrchestrator
        orchestrator = CountryComparisonOrchestrator(llm_provider=llm_provider)

        # Run comparison
        result = await orchestrator.compare_countries(countries)

        logger.info(
            f"Country comparison complete: {result['comparison_summary']['total_countries_analyzed']} countries"
        )

        return result

    except Exception as e:
        logger.error(f"Country comparison failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Country comparison failed: {str(e)}"
        )