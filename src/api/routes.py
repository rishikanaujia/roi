"""
API Routes - Endpoint Definitions

NOW USING REAL LLM FROM APP STATE!
"""

from fastapi import APIRouter, HTTPException, status, Request
from typing import Dict, Any

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