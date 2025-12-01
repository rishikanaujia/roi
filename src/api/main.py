"""
FastAPI Application - Main Entry Point

Production-ready REST API for ROI (Renewable Opportunity Identifier).

Features:
- Automatic OpenAPI documentation (Swagger UI)
- Request validation
- Response formatting
- Error handling
- CORS support
- Health checks

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

from src.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ROI API - Renewable Opportunity Identifier",
    description="""
    **Analyze renewable energy investment opportunities worldwide.**

    This API provides investment-grade financial analysis for renewable energy projects:
    - 🌍 **3 Countries:** USA, Germany, India
    - ⚡ **2 Technologies:** Solar PV, Onshore Wind
    - 💰 **Financial Metrics:** LCOE, IRR, NPV, Capacity Factor
    - 🎯 **Investment Recommendation:** Automated viability assessment

    ## Features

    - **Fast:** Results in <0.1 seconds
    - **Accurate:** Based on real policy and resource data
    - **Scalable:** Hybrid architecture supports 100+ countries
    - **Production-Ready:** Full error handling and validation

    ## How to Use

    1. **POST /api/v1/analyze** - Analyze an opportunity
    2. Get complete financial analysis
    3. Make data-driven investment decisions

    ## Example
```python
    import requests

    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        json={
            "country": "USA",
            "technology": "solar_pv",
            "latitude": 31.99,
            "longitude": -102.07,
            "capacity_mw": 100
        }
    )

    result = response.json()
    print(f"LCOE: ${result['lcoe']:.2f}/MWh")
    print(f"IRR: {result['irr']:.1f}%")
    print(f"Recommendation: {result['recommendation']}")
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
    Root endpoint - API information.
    """
    return {
        "name": "ROI API",
        "version": "1.0.0",
        "description": "Renewable Opportunity Identifier - Investment-grade analysis API",
        "docs": "/docs",
        "health": "/api/v1/health",
        "analyze": "/api/v1/analyze"
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("🚀 Starting ROI API Server")
    print("=" * 70)
    print("\n📊 API Information:")
    print("  Name: ROI API - Renewable Opportunity Identifier")
    print("  Version: 1.0.0")
    print("  Countries: USA, Germany, India")
    print("  Technologies: Solar PV, Onshore Wind")
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