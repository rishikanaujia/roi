"""
API Models - Request and Response Schemas

Pydantic models for:
- Request validation
- Response formatting
- API documentation (automatic via FastAPI)
- Type safety
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


class AnalyzeRequest(BaseModel):
    """
    Request model for opportunity analysis.

    Example:
        {
            "country": "USA",
            "technology": "solar_pv",
            "latitude": 31.99,
            "longitude": -102.07,
            "capacity_mw": 100
        }
    """
    country: str = Field(
        ...,
        description="Country code (ISO 3166-1 alpha-3)",
        example="USA",
        min_length=3,
        max_length=3
    )

    technology: str = Field(
        ...,
        description="Technology code",
        example="solar_pv"
    )

    latitude: float = Field(
        ...,
        description="Location latitude (decimal degrees)",
        ge=-90,
        le=90,
        example=31.99
    )

    longitude: float = Field(
        ...,
        description="Location longitude (decimal degrees)",
        ge=-180,
        le=180,
        example=-102.07
    )

    capacity_mw: float = Field(
        default=100.0,
        description="Project capacity in megawatts",
        gt=0,
        example=100.0
    )

    state: Optional[str] = Field(
        None,
        description="State/region code (optional, for country-specific data)",
        example="TX"
    )

    @validator('country')
    def country_uppercase(cls, v):
        """Ensure country code is uppercase."""
        return v.upper()

    @validator('technology')
    def technology_lowercase(cls, v):
        """Ensure technology code is lowercase."""
        return v.lower()

    class Config:
        schema_extra = {
            "example": {
                "country": "USA",
                "technology": "solar_pv",
                "latitude": 31.99,
                "longitude": -102.07,
                "capacity_mw": 100.0,
                "state": "TX"
            }
        }


class FinancialMetrics(BaseModel):
    """Financial metrics."""
    lcoe_usd_per_mwh: float = Field(..., description="Levelized Cost of Energy ($/MWh)")
    irr_percent: float = Field(..., description="Internal Rate of Return (%)")
    npv_usd: float = Field(..., description="Net Present Value ($)")
    capacity_factor: float = Field(..., description="Capacity factor (0-1)")
    payback_years: float = Field(..., description="Simple payback period (years)")


class ResourceSummary(BaseModel):
    """Resource summary (technology-specific)."""
    quality: str = Field(..., description="Data quality/confidence")

    # Solar-specific (optional)
    ghi_kwh_m2_day: Optional[float] = Field(None, description="Global Horizontal Irradiance")
    temperature_c: Optional[float] = Field(None, description="Average temperature (°C)")

    # Wind-specific (optional)
    wind_speed_m_s: Optional[float] = Field(None, description="Average wind speed (m/s)")
    wind_power_density_w_m2: Optional[float] = Field(None, description="Wind power density (W/m²)")


class PolicySummary(BaseModel):
    """Policy summary (country-specific)."""
    tax_rate: float = Field(..., description="Effective tax rate")
    confidence: str = Field(..., description="Policy data confidence")

    # USA-specific (optional)
    federal_itc: Optional[float] = Field(None, description="Federal Investment Tax Credit (%)")
    federal_ptc: Optional[float] = Field(None, description="Federal Production Tax Credit ($/MWh)")

    # Germany-specific (optional)
    eeg_tariff: Optional[float] = Field(None, description="EEG feed-in tariff (€/MWh)")


class AnalyzeResponse(BaseModel):
    """
    Response model for opportunity analysis.

    Contains all key metrics and detailed results.
    """
    # Project info
    project: Dict[str, Any] = Field(..., description="Project information")

    # Key metrics (easy access)
    lcoe: float = Field(..., description="LCOE ($/MWh)")
    irr: float = Field(..., description="IRR (%)")
    npv: float = Field(..., description="NPV ($)")
    capacity_factor: float = Field(..., description="Capacity factor (0-1)")
    payback_years: float = Field(..., description="Payback period (years)")

    # Recommendation
    recommendation: str = Field(..., description="Viability recommendation")
    confidence: str = Field(..., description="Overall confidence")

    # Summaries
    resource_summary: ResourceSummary = Field(..., description="Resource data summary")
    policy_summary: PolicySummary = Field(..., description="Policy data summary")

    # Execution metrics
    execution_metrics: Dict[str, Any] = Field(..., description="Execution metrics")

    # Status
    status: str = Field(..., description="Workflow status")
    workflow_complete: bool = Field(..., description="Workflow completion status")

    class Config:
        schema_extra = {
            "example": {
                "project": {
                    "country": "USA",
                    "technology": "solar_pv",
                    "location": {"latitude": 31.99, "longitude": -102.07},
                    "capacity_mw": 100.0
                },
                "lcoe": 81.17,
                "irr": 5.0,
                "npv": -77362040,
                "capacity_factor": 0.179,
                "payback_years": 30.0,
                "recommendation": "NOT VIABLE",
                "confidence": "low",
                "resource_summary": {
                    "ghi_kwh_m2_day": 5.0,
                    "temperature_c": 15.0,
                    "quality": "very_high"
                },
                "policy_summary": {
                    "federal_itc": 30.0,
                    "tax_rate": 0.21,
                    "confidence": "high"
                },
                "execution_metrics": {
                    "research_time_seconds": 0.01,
                    "analysis_time_seconds": 0.01,
                    "total_time_seconds": 0.02
                },
                "status": "complete",
                "workflow_complete": True
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    supported_countries: List[str] = Field(..., description="Supported countries")
    supported_technologies: List[str] = Field(..., description="Supported technologies")


class SupportedOptionsResponse(BaseModel):
    """Supported countries and technologies."""
    countries: List[Dict[str, str]] = Field(..., description="Supported countries")
    technologies: List[Dict[str, str]] = Field(..., description="Supported technologies")
    total_combinations: int = Field(..., description="Total possible combinations")

