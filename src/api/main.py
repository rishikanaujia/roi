"""
FastAPI Application - Main Entry Point with Real LLM Support

Production-ready REST API for ROI (Renewable Opportunity Identifier).

NEW: Supports multiple LLM providers via environment variables!

Environment Variables:
    LLM_PROVIDER: "mock" (default), "openai", "anthropic"
    LLM_MODEL: Model name (optional, uses provider default)
    OPENAI_API_KEY: For OpenAI provider
    ANTHROPIC_API_KEY: For Anthropic provider

Start server:
    uvicorn src.api.main:app --reload

Access docs:
    http://localhost:8000/docs
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
import os

from src.api.routes import router
from src.llm.factory import LLMProviderFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize LLM provider from environment
LLM_PROVIDER_TYPE = os.getenv('LLM_PROVIDER', 'mock')
LLM_MODEL = os.getenv('LLM_MODEL')

logger.info(f"Initializing API with LLM provider: {LLM_PROVIDER_TYPE}")

try:
    llm_provider = LLMProviderFactory.create_from_env()
    logger.info(f"LLM provider initialized: {llm_provider.get_provider_name()}")
except Exception as e:
    logger.error(f"Failed to initialize LLM provider: {str(e)}")
    logger.warning("Falling back to Mock provider")
    llm_provider = LLMProviderFactory.create("mock")

# Store provider in app state (will be accessed by routes)
app_state = {
    "llm_provider": llm_provider
}

# Create FastAPI app
app = FastAPI(
    title="ROI API - Renewable Opportunity Identifier",
    description=f"""
    **Analyze renewable energy investment opportunities worldwide with AI-powered insights.**

    This API provides investment-grade financial analysis for renewable energy projects:
    - 🌍 **3 Countries:** USA, Germany, India
    - ⚡ **2 Technologies:** Solar PV, Onshore Wind
    - 💰 **Financial Metrics:** LCOE, IRR, NPV, Capacity Factor
    - 🤖 **AI Insights:** {llm_provider.get_provider_name()} (Powered by real AI!)
    - 🎯 **Investment Recommendation:** Automated viability assessment
    - 🛰️ **Real Data:** NASA POWER satellite data (30-year climatology)

    ## Features

    - **Fast:** Results in <3 seconds
    - **Accurate:** Based on real NASA satellite data
    - **Intelligent:** AI-powered insights and recommendations
    - **Scalable:** Hybrid architecture supports 100+ countries
    - **Production-Ready:** Full error handling and validation

    ## How to Use

    1. **POST /api/v1/analyze** - Analyze an opportunity
    2. Get complete financial analysis with AI insights
    3. Make data-driven investment decisions

    ## AI Provider

    Current AI Provider: **{llm_provider.get_provider_name()}**

    To use different AI providers, set environment variables:
    - `LLM_PROVIDER`: "mock", "openai", "anthropic"
    - `OPENAI_API_KEY`: For GPT-4 insights (~$0.006 per analysis)
    - `LLM_MODEL`: Optional model name (e.g., "gpt-4o")

    ## Example
```python
    import requests

    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        json={{
            "country": "USA",
            "technology": "solar_pv",
            "latitude": 31.99,
            "longitude": -102.07,
            "capacity_mw": 100
        }}
    )
    
    data = response.json()
    print(f"LCOE: ${{data['lcoe']:.2f}}/MWh")
    print(f"IRR: {{data['irr']:.1f}}%")
    print(f"AI Insight: {{data['ai_insights']['key_insights'][0]}}")
```
    """,
    version="1.0.0",
    contact={
        "name": "ROI API",
        "email": "api@roi-energy.com"
    },
    license_info={
        "name": "MIT"
    }
)

# Store app state
app.state.llm_provider = llm_provider

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 3))
    return response


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "status_code": 422
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "status_code": 500
        }
    )


# Include routers
app.include_router(router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information with AI provider status.
    """
    # Get usage stats if available
    usage_stats = None
    if hasattr(llm_provider, 'get_usage_stats'):
        try:
            usage_stats = llm_provider.get_usage_stats()
        except:
            pass

    response = {
        "name": "ROI API",
        "version": "1.0.0",
        "description": "Renewable Opportunity Identifier - Investment-grade analysis API with AI",
        "ai_provider": llm_provider.get_provider_name(),
        "data_source": "NASA POWER (30-year satellite climatology)",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/v1/health",
            "analyze": "/api/v1/analyze",
            "supported": "/api/v1/supported"
        }
    }

    if usage_stats:
        response["ai_usage"] = {
            "total_requests": usage_stats.get('total_requests', 0),
            "total_cost_usd": usage_stats.get('estimated_cost_usd', 0),
            "cost_per_request": usage_stats.get('cost_per_request', 0)
        }

    return response


if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("🚀 Starting ROI API Server with Real AI")
    print("=" * 70)
    print("\n📊 API Information:")
    print("  Name: ROI API - Renewable Opportunity Identifier")
    print("  Version: 1.0.0")
    print("  Countries: USA, Germany, India")
    print("  Technologies: Solar PV, Onshore Wind")
    print("  Data Source: NASA POWER (Real satellite data)")
    print(f"\n🤖 AI Provider:")
    print(f"  Provider: {llm_provider.get_provider_name()}")
    print(f"  Type: {LLM_PROVIDER_TYPE}")
    if LLM_MODEL:
        print(f"  Model: {LLM_MODEL}")

    if LLM_PROVIDER_TYPE == "openai":
        print(f"  Cost: ~$0.006 per analysis")
        print(f"  Quality: Investment-grade insights")
    elif LLM_PROVIDER_TYPE == "mock":
        print(f"  Cost: Free")
        print(f"  Quality: Basic insights")
        print(f"\n💡 For better insights, set:")
        print(f"     export LLM_PROVIDER='openai'")
        print(f"     export OPENAI_API_KEY='sk-...'")

    print("\n🌐 Server URLs:")
    print("  API: http://localhost:8000")
    print("  Docs (Swagger): http://localhost:8000/docs")
    print("  ReDoc: http://localhost:8000/redoc")
    print("  Health: http://localhost:8000/api/v1/health")
    print("\n⚡ Quick Test:")
    print("  curl -X POST http://localhost:8000/api/v1/analyze \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{")
    print('      "country": "USA",')
    print('      "technology": "solar_pv",')
    print('      "latitude": 31.99,')
    print('      "longitude": -102.07,')
    print('      "capacity_mw": 100')
    print("    }'")
    print("\n" + "=" * 70)
    print("Starting server... Press Ctrl+C to stop")
    print("=" * 70 + "\n")

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )