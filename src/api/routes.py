"""
API Routes - Endpoint Definitions

Defines all API endpoints:
- POST /analyze - Analyze opportunity
- GET /health - Health check
- GET /supported - Get supported options
"""

from fastapi import APIRouter, HTTPException, status
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

# Create orchestrator (singleton)
orchestrator = WorkflowOrchestrator()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Renewable Energy Opportunity",
    description="""
    Analyze a renewable energy investment opportunity.

    This endpoint orchestrates:
    1. Research Agent - Fetches policy and resource data
    2. Analysis Agent - Calculates financial metrics (LCOE, IRR, NPV)
    3. Returns investment-grade analysis with recommendation

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
async def analyze_opportunity(request: AnalyzeRequest):
    """
    Analyze a renewable energy opportunity.

    Returns complete financial analysis with recommendation.
    """
    try:
        # Call orchestrator
        result = await orchestrator.analyze_opportunity(
            country=request.country,
            technology=request.technology,
            latitude=request.latitude,
            longitude=request.longitude,
            capacity_mw=request.capacity_mw,
            state=request.state
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
async def health_check():
    """
    Health check endpoint.

    Returns service status and supported options.
    """
    countries = PolicyHandlerFactory.get_supported_countries()
    technologies = ResourceFetcherFactory.get_supported_technologies()

    return {
        "status": "healthy",
        "version": "1.0.0",
        "supported_countries": countries,
        "supported_technologies": technologies
    }


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