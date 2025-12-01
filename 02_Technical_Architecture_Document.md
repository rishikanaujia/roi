# TECHNICAL ARCHITECTURE DOCUMENT
## ROI POC - Renewable Opportunity Identifier

**Version:** 1.0  
**Date:** December 2025  
**Authors:** Engineering Team  
**Status:** Draft for Review  

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Component Details](#2-component-details)
3. [API Specification](#3-api-specification)
4. [Data Models](#4-data-models)
5. [Design Patterns Implementation](#5-design-patterns-implementation)
6. [Database Schema](#6-database-schema)
7. [Vector Store Design](#7-vector-store-design)
8. [LLM Integration](#8-llm-integration)
9. [Error Handling](#9-error-handling)
10. [Performance Considerations](#10-performance-considerations)
11. [Security](#11-security)
12. [Deployment](#12-deployment)
13. [Monitoring & Logging](#13-monitoring--logging)
14. [Testing Strategy](#14-testing-strategy)

---

## 1. Architecture Overview

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                                                                  │
│  curl / Postman / Python Script / Future UI                     │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTPS
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                         │
│                                                                  │
│  Routes:                                                         │
│  - POST   /api/v1/opportunities                                 │
│  - GET    /api/v1/opportunities/{id}                            │
│  - GET    /health                                               │
│                                                                  │
│  Middleware:                                                     │
│  - Request logging                                              │
│  - Error handling                                               │
│  - Cost tracking                                                │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│               ORCHESTRATION LAYER (LangGraph)                    │
│                                                                  │
│  WorkflowOrchestrator                                           │
│    ├─ State Management (OpportunityState)                       │
│    ├─ Agent Coordination                                        │
│    ├─ Checkpoint Management                                     │
│    └─ Error Recovery                                            │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                ↓           ↓           ↓
┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐
│  RESEARCH AGENT  │ │ANALYSIS AGENT│ │PEER REVIEW AGENT│
│                  │ │              │ │                 │
│ • PolicyAgent    │ │• FinancialAgt│ │• ScoreAggregator│
│ • ResourceAgent  │ │• ValidationAgt│ │• VarianceCheck  │
└────────┬─────────┘ └──────┬───────┘ └────────┬────────┘
         │                  │                   │
         └──────────────────┴───────────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         ↓                  ↓                   ↓
┌──────────────┐  ┌───────────────┐  ┌────────────────┐
│ LLM SERVICE  │  │ DATA SOURCES  │  │ REPOSITORIES   │
│              │  │               │  │                │
│• Claude API  │  │• NASA POWER   │  │• OpportunityRepo│
│• OpenAI API  │  │• Policy Scraper│ │• ReportRepo    │
│• Fallback    │  │• Cache Layer  │  │• LogRepo       │
└──────┬───────┘  └───────┬───────┘  └────────┬───────┘
       │                  │                   │
       └──────────────────┴───────────────────┘
                          │
┌─────────────────────────┴──────────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                       │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐       │
│  │ PostgreSQL   │  │ Redis        │  │ ChromaDB      │       │
│  │              │  │              │  │               │       │
│  │• Metadata    │  │• API Cache   │  │• Embeddings   │       │
│  │• Reports     │  │• Session     │  │• RAG Context  │       │
│  │• Logs        │  │• Rate Limit  │  │• Similarity   │       │
│  └──────────────┘  └──────────────┘  └───────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **API Framework** | FastAPI | 0.104+ | REST API, async support |
| **Language** | Python | 3.11+ | Core application |
| **Orchestration** | LangGraph | Latest | Multi-agent workflow |
| **LLM Client** | LangChain | Latest | LLM abstraction |
| **Primary LLM** | Claude Sonnet 4 | 20250514 | Complex reasoning |
| **Fallback LLM** | GPT-4o | Latest | Cost-effective fallback |
| **Vector DB** | ChromaDB | 0.4.18+ | RAG, embeddings |
| **Metadata DB** | PostgreSQL | 15+ | Structured data |
| **Cache** | Redis | 7+ | Performance |
| **HTTP Client** | aiohttp | 3.9+ | Async HTTP |
| **Validation** | Pydantic | 2.5+ | Data validation |
| **Testing** | pytest | 7.4+ | Unit/integration tests |
| **Container** | Docker | 20+ | Deployment |

### 1.3 Design Principles

**SOLID Principles:**
- ✅ **Single Responsibility:** Each class has one job
- ✅ **Open/Closed:** Extend via inheritance, not modification
- ✅ **Liskov Substitution:** All agents interchangeable via `IAgent`
- ✅ **Interface Segregation:** Small, focused interfaces
- ✅ **Dependency Inversion:** Depend on abstractions

**Design Patterns:**
- ✅ **Factory:** Agent creation via `AgentFactory`
- ✅ **Strategy:** LLM providers swappable via `ILLMProvider`
- ✅ **Repository:** Data access via `IRepository`
- ✅ **Template Method:** `BaseAgent` defines flow
- ✅ **Dependency Injection:** All dependencies injected via constructors

---

## 2. Component Details

### 2.1 API Layer (FastAPI)

**Purpose:** HTTP interface for client interactions

**Key Components:**
- `src/main.py` - FastAPI application
- Request/response models (Pydantic)
- Error handlers
- Middleware (logging, cost tracking)

**Responsibilities:**
1. Request validation
2. Authentication (future)
3. Rate limiting (future)
4. Response formatting
5. Error handling

**Example Route:**
```python
@app.post("/api/v1/opportunities", response_model=OpportunityResponse)
async def create_opportunity(request: OpportunityRequest):
    """Create and analyze a new opportunity"""
    result = await orchestrator.execute_opportunity_analysis(
        request.dict()
    )
    return OpportunityResponse(
        opportunity_id=result["opportunity_id"],
        status=result["status"],
        data=result
    )
```

### 2.2 Orchestration Layer (LangGraph)

**Purpose:** Coordinate multi-agent workflow execution

**Key Components:**
- `src/orchestration/workflow.py` - WorkflowOrchestrator
- State management
- Agent coordination
- Checkpoint persistence

**State Machine:**
```python
class OpportunityState(TypedDict):
    opportunity_id: str
    country: str
    technology: str
    latitude: float
    longitude: float
    research_data: Optional[Dict]
    analysis_data: Optional[Dict]
    peer_review_data: Optional[Dict]
    status: str
    error: Optional[str]
```

**Workflow Graph:**
```python
workflow = StateGraph(OpportunityState)

# Add nodes
workflow.add_node("research", research_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("peer_review", peer_review_node)

# Define edges
workflow.add_edge("research", "analysis")
workflow.add_edge("analysis", "peer_review")
workflow.add_edge("peer_review", END)

# Compile
app = workflow.compile()
```

### 2.3 Agent Layer

**Purpose:** Execute specific analysis tasks

**Architecture:**
```
IAgent (Interface)
  └── BaseAgent (Abstract Base Class)
        ├── ResearchAgent
        ├── AnalysisAgent
        └── PeerReviewAgent
```

**Common Agent Flow (Template Method):**
```python
async def execute(self, input_data):
    # 1. Validate input
    if not self.validate_input(input_data):
        raise ValueError("Invalid input")
    
    # 2. Pre-processing
    processed = await self._preprocess(input_data)
    
    # 3. Core execution (implemented by subclass)
    result = await self._execute_core(processed)
    
    # 4. Post-processing
    final = await self._postprocess(result)
    
    return final
```

**Agent-Specific Implementations:**

**ResearchAgent:**
- Fetches data from NASA POWER API
- Scrapes policy information
- Normalizes data to canonical schema
- Stores embeddings in ChromaDB

**AnalysisAgent:**
- Retrieves context from ChromaDB (RAG)
- Calculates LCOE using financial formulas
- Calculates IRR via cash flow projections
- Validates against industry benchmarks

**PeerReviewAgent:**
- Simulates peer scores (POC only)
- Calculates aggregate scores
- Computes variance
- Flags high disagreement

### 2.4 Service Layer

**LLMService:**
- Manages primary and fallback LLM providers
- Implements circuit breaker for resilience
- Tracks token usage and costs
- Handles retries with exponential backoff

**Example:**
```python
class LLMService:
    def __init__(self, config):
        self.primary = AnthropicProvider(config['primary'])
        self.fallback = OpenAIProvider(config['fallback'])
        self.circuit_breaker = CircuitBreaker()
    
    async def generate(self, prompt, use_fallback=False):
        provider = self.fallback if use_fallback else self.primary
        try:
            return await provider.generate(prompt)
        except Exception as e:
            if not use_fallback and self.fallback:
                logger.warning(f"Primary failed: {e}, using fallback")
                return await self.generate(prompt, use_fallback=True)
            raise
```

### 2.5 Data Source Layer

**Purpose:** Abstract external data fetching

**Interface:**
```python
class IDataSource(ABC):
    @abstractmethod
    async def fetch(self, params: Dict) -> Dict:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
```

**Implementations:**
- `NASAPowerSource` - Solar resource data
- `PolicyScraperSource` - Policy incentives

**Caching Strategy:**
```python
async def fetch(self, params):
    cache_key = self._build_cache_key(params)
    
    # Check Redis cache
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from source
    data = await self._fetch_from_source(params)
    
    # Cache for 30 days
    await redis.setex(cache_key, 2592000, json.dumps(data))
    
    return data
```

### 2.6 Repository Layer

**Purpose:** Abstract database access

**Interface:**
```python
class IRepository(ABC):
    @abstractmethod
    async def create(self, data: Dict) -> UUID:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        pass
    
    @abstractmethod
    async def update(self, id: UUID, data: Dict) -> bool:
        pass
```

**Implementations:**
- `OpportunityRepository` - Opportunity CRUD
- `ReportRepository` - Report versioning
- `ExecutionLogRepository` - Audit logs

---

## 3. API Specification

### 3.1 Endpoints

#### POST /api/v1/opportunities

**Purpose:** Submit new opportunity for analysis

**Request:**
```json
{
  "country": "USA",
  "technology": "Solar PV",
  "latitude": 31.9974,
  "longitude": -102.0779,
  "capacity_mw": 100
}
```

**Response (202 Accepted):**
```json
{
  "opportunity_id": "OPP-USA-a3f8b2c1",
  "status": "PROCESSING",
  "estimated_completion": "2025-12-01T10:15:00Z"
}
```

**Response (200 OK - Synchronous POC):**
```json
{
  "opportunity_id": "OPP-USA-a3f8b2c1",
  "status": "COMPLETED",
  "data": {
    "research_data": {
      "policy_data": {...},
      "resource_data": {...}
    },
    "analysis_data": {
      "lcoe_usd_per_mwh": 42.5,
      "irr_percent": 12.3,
      ...
    },
    "peer_review_data": {
      "average_score": 8.2,
      "variance": 1.2
    }
  }
}
```

**Error Responses:**
- 400 Bad Request - Invalid input
- 500 Internal Server Error - Processing failure
- 503 Service Unavailable - System overload

#### GET /api/v1/opportunities/{opportunity_id}

**Purpose:** Retrieve opportunity status and results

**Response:**
```json
{
  "opportunity_id": "OPP-USA-a3f8b2c1",
  "status": "COMPLETED",
  "created_at": "2025-12-01T10:00:00Z",
  "completed_at": "2025-12-01T10:08:32Z",
  "duration_seconds": 512,
  "cost_usd": 4.25,
  "data": {...}
}
```

#### GET /health

**Purpose:** Health check for load balancers

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "postgres": "connected",
    "redis": "connected",
    "chromadb": "connected",
    "llm_primary": "available"
  }
}
```

### 3.2 Authentication (Future)

**POC:** No authentication (local development only)

**MVP:** JWT-based authentication
```
Authorization: Bearer <jwt_token>
```

---

## 4. Data Models

### 4.1 Pydantic Models

**OpportunityRequest:**
```python
class OpportunityRequest(BaseModel):
    country: str = Field(..., min_length=2, max_length=100)
    technology: str = Field(..., description="Renewable technology type")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    capacity_mw: Optional[float] = Field(None, gt=0)
    
    @validator('technology')
    def validate_technology(cls, v):
        allowed = ['Solar PV', 'Onshore Wind', 'Offshore Wind', 'Hydro', 'Geothermal']
        if v not in allowed:
            raise ValueError(f"Technology must be one of: {allowed}")
        return v
```

**OpportunityResponse:**
```python
class OpportunityResponse(BaseModel):
    opportunity_id: str
    status: str
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    cost_usd: Optional[float] = None
    data: Optional[Dict[str, Any]] = None
```

### 4.2 Internal Data Structures

**ResearchSummary:**
```python
{
  "opportunity_id": str,
  "policy_data": {
    "federal_itc_percentage": float,
    "state_incentives": List[str],
    "confidence": str  # "high" | "medium" | "low"
  },
  "resource_data": {
    "avg_ghi_kwh_m2_day": float,
    "avg_temperature_c": float,
    "confidence": str
  },
  "data_completeness": float,  # 0.0 to 1.0
  "sources": List[str]
}
```

**AnalysisReport:**
```python
{
  "opportunity_id": str,
  "lcoe_usd_per_mwh": float,
  "irr_percent": float,
  "npv_usd_million": Optional[float],
  "resource_quality_score": float,  # 0-10
  "financial_attractiveness_score": float,  # 0-10
  "grid_feasibility_score": float,  # 0-10
  "policy_support_score": float,  # 0-10
  "risk_score": float,  # 0-10
  "assumptions": {
    "capex_usd_per_kw": float,
    "opex_usd_per_kw_year": float,
    "capacity_factor": float,
    "discount_rate": float,
    "project_lifetime_years": int
  },
  "confidence": str
}
```

---

## 5. Design Patterns Implementation

### 5.1 Factory Pattern

**Purpose:** Centralize agent creation logic

**Implementation:**
```python
class AgentFactory:
    _registry = {
        "research": ResearchAgent,
        "analysis": AnalysisAgent,
        "peer_review": PeerReviewAgent
    }
    
    @classmethod
    def create_agent(cls, agent_type: str, llm_provider, config) -> IAgent:
        agent_class = cls._registry.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return agent_class(llm_provider, config)
    
    @classmethod
    def register_agent(cls, agent_type: str, agent_class: type):
        """Allow dynamic registration of new agents"""
        cls._registry[agent_type] = agent_class
```

**Benefits:**
- Open/Closed: Add new agents without modifying existing code
- Single point of configuration
- Easy to test with mocks

### 5.2 Strategy Pattern

**Purpose:** Swap LLM providers transparently

**Implementation:**
```python
class ILLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

class AnthropicProvider(ILLMProvider):
    async def generate(self, prompt: str) -> str:
        return await anthropic_client.messages.create(...)

class OpenAIProvider(ILLMProvider):
    async def generate(self, prompt: str) -> str:
        return await openai_client.chat.completions.create(...)

# Usage
provider: ILLMProvider = AnthropicProvider(config)
result = await provider.generate(prompt)
```

**Benefits:**
- Swap providers at runtime
- A/B testing different models
- Fallback mechanisms

### 5.3 Repository Pattern

**Purpose:** Abstract database access

**Implementation:**
```python
class OpportunityRepository(IRepository):
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    async def create(self, data: Dict) -> UUID:
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO opportunities (...) VALUES (...) RETURNING id",
                ...
            )
            return row["id"]
```

**Benefits:**
- Database-agnostic business logic
- Easy to mock for testing
- Swap database implementations

### 5.4 Dependency Injection

**Purpose:** Decouple dependencies

**Implementation:**
```python
class WorkflowOrchestrator:
    def __init__(
        self,
        agent_factory: AgentFactory,
        llm_service: LLMService,
        opportunity_repo: OpportunityRepository
    ):
        # Dependencies injected, not created internally
        self.agent_factory = agent_factory
        self.llm_service = llm_service
        self.opportunity_repo = opportunity_repo
```

**Benefits:**
- Easy to test (inject mocks)
- Loose coupling
- Configuration-driven behavior

---

## 6. Database Schema

### 6.1 PostgreSQL Tables

**opportunities:**
```sql
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id VARCHAR(255) UNIQUE NOT NULL,
    country VARCHAR(100) NOT NULL,
    technology VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(11, 6) NOT NULL,
    capacity_mw DECIMAL(10, 2),
    status VARCHAR(50) NOT NULL DEFAULT 'INITIALIZED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds DECIMAL(10, 2),
    cost_usd DECIMAL(10, 2),
    metadata JSONB
);

CREATE INDEX idx_opportunities_status ON opportunities(status);
CREATE INDEX idx_opportunities_created_at ON opportunities(created_at);
```

**reports:**
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id VARCHAR(255) REFERENCES opportunities(opportunity_id),
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    report_type VARCHAR(50) NOT NULL,  -- 'research', 'analysis', 'peer_review'
    report_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_opportunity ON reports(opportunity_id);
CREATE INDEX idx_reports_type ON reports(report_type);
```

**execution_logs:**
```sql
CREATE TABLE execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id VARCHAR(255) REFERENCES opportunities(opportunity_id),
    agent_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- 'started', 'completed', 'failed'
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    duration_seconds DECIMAL(10, 2),
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_opportunity ON execution_logs(opportunity_id);
CREATE INDEX idx_logs_agent ON execution_logs(agent_name);
CREATE INDEX idx_logs_status ON execution_logs(status);
```

### 6.2 Redis Keys

**Cache Keys:**
```
nasa_power:{lat}:{lon}:{start_date}:{end_date}
policy:{country}:{technology}
llm_response:{prompt_hash}
```

**Session Keys:**
```
session:{opportunity_id}:state
session:{opportunity_id}:checkpoint:{checkpoint_id}
```

**Rate Limit Keys:**
```
ratelimit:{user_id}:{endpoint}:{window}
```

---

## 7. Vector Store Design

### 7.1 ChromaDB Collections

**Collection: `roi_research_data`**

**Document Structure:**
```python
{
  "id": "USA-Solar-2025-001",
  "embedding": [0.123, 0.456, ...],  # 384-dim vector
  "metadata": {
    "opportunity_id": "OPP-USA-a3f8b2c1",
    "country": "USA",
    "technology": "Solar PV",
    "data_type": "policy" | "resource" | "mixed",
    "source": "NASA POWER",
    "timestamp": "2025-12-01T10:05:00Z"
  },
  "document": "Federal ITC: 30% for solar PV installations..."
}
```

**Embedding Model:**
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Language: English

### 7.2 RAG Workflow

**1. Ingestion (Research Agent):**
```python
# Extract text from research data
text_chunks = [
    "Policy: Federal ITC 30% until 2032",
    "Resource: Average GHI 5.5 kWh/m²/day",
    ...
]

# Generate embeddings and store
for chunk in text_chunks:
    chroma_collection.add(
        documents=[chunk],
        metadatas=[{
            "opportunity_id": opp_id,
            "source": "NASA POWER"
        }],
        ids=[f"{opp_id}-{uuid4()}"]
    )
```

**2. Retrieval (Analysis Agent):**
```python
# Query for relevant context
results = chroma_collection.query(
    query_texts=["What are the policy incentives for solar?"],
    n_results=5,
    where={"opportunity_id": opp_id}
)

# Build context for LLM
context = "\n\n".join(results["documents"][0])
prompt = f"""
Context:
{context}

Question: Calculate LCOE for this solar PV opportunity.
"""
```

---

## 8. LLM Integration

### 8.1 Provider Configuration

**Claude Sonnet 4 (Primary):**
```python
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  "api_key": os.environ["ANTHROPIC_API_KEY"],
  "max_tokens": 10000,
  "temperature": 0.3,
  "timeout": 120,
  "max_retries": 3,
  "retry_delay": 2
}
```

**GPT-4o (Fallback):**
```python
{
  "provider": "openai",
  "model": "gpt-4o",
  "api_key": os.environ["OPENAI_API_KEY"],
  "max_tokens": 10000,
  "temperature": 0.3,
  "timeout": 120,
  "max_retries": 3
}
```

### 8.2 Prompt Engineering

**Prompt Structure:**
```markdown
# Role
You are [AGENT_ROLE].

# Task
[SPECIFIC_TASK]

# Input Data
<data>
{input_data}
</data>

# Output Format
Respond ONLY with valid JSON:
{schema}

# Constraints
- Do not hallucinate
- Cite sources
- Flag uncertainties
```

**Prompt Versioning:**
- Stored in `config/prompts/`
- Format: `{agent_name}_v{VERSION}.md`
- Version logged with each execution

### 8.3 Cost Tracking

**Per-Request:**
```python
async def generate_with_tracking(prompt):
    start_time = time.time()
    
    response = await llm_provider.generate(prompt)
    
    duration = time.time() - start_time
    tokens = len(response) // 4  # Rough estimate
    cost = llm_provider.estimate_cost(tokens)
    
    await log_execution({
        "agent": agent_name,
        "tokens": tokens,
        "cost_usd": cost,
        "duration_seconds": duration
    })
    
    return response
```

**Aggregate Tracking:**
```sql
SELECT 
    DATE(created_at) as date,
    agent_name,
    SUM(cost_usd) as daily_cost,
    SUM(tokens_used) as daily_tokens
FROM execution_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at), agent_name
ORDER BY date DESC, daily_cost DESC;
```

---

## 9. Error Handling

### 9.1 Error Categories

| Error Type | HTTP Code | Recovery Strategy |
|------------|-----------|-------------------|
| Validation Error | 400 | Return error details to user |
| Data Source Timeout | 503 | Retry 3x, use cache, flag incomplete |
| LLM API Failure | 500 | Retry with exponential backoff, fallback |
| Calculation Error | 500 | Return error, flag for manual review |
| Database Error | 500 | Retry transaction, alert admin |

### 9.2 Retry Logic

**Exponential Backoff:**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=32),
    retry=retry_if_exception_type((Timeout, APIError))
)
async def call_llm_with_retry(prompt):
    return await llm_provider.generate(prompt)
```

### 9.3 Circuit Breaker

**Purpose:** Prevent cascading failures

```python
from pybreaker import CircuitBreaker

nasa_power_breaker = CircuitBreaker(
    fail_max=5,          # Open after 5 failures
    timeout_duration=60   # Half-open after 60 seconds
)

@nasa_power_breaker
async def fetch_nasa_power_data(params):
    # If circuit open, immediately fails without calling API
    response = await http_client.get(NASA_POWER_URL, params=params)
    return response.json()
```

**States:**
- **Closed:** Normal operation
- **Open:** All requests fail immediately
- **Half-Open:** One test request allowed

---

## 10. Performance Considerations

### 10.1 Target Benchmarks

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time | <500ms | p95 |
| Research Agent | <60s | p95 |
| Analysis Agent | <30s | p95 |
| Peer Review Agent | <15s | p95 |
| Total Workflow | <10 min | p95 |
| Database Query | <50ms | p95 |
| Cache Hit Rate | >60% | Average |

### 10.2 Optimization Strategies

**1. Parallel Execution:**
```python
# Fetch multiple data sources concurrently
results = await asyncio.gather(
    nasa_power_source.fetch(params),
    policy_scraper_source.fetch(params),
    return_exceptions=True
)
```

**2. Caching:**
- Redis for API responses (30 days TTL)
- ChromaDB for embeddings (persistent)
- LRU cache for prompt templates

**3. Database Connection Pooling:**
```python
db_pool = await asyncpg.create_pool(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    min_size=5,
    max_size=20
)
```

**4. Async Everything:**
- All I/O operations use async/await
- Non-blocking database queries
- Concurrent LLM calls where possible

---

## 11. Security

### 11.1 POC Security (Minimal)

**Current:**
- No authentication (local development)
- No authorization
- Docker network isolation
- Environment variables for secrets

**NOT for Production:**
- Exposed ports on localhost only
- Single-user assumption
- No encryption at rest

### 11.2 MVP Security (Required)

**Must Add:**
- JWT authentication
- API key management
- RBAC (Role-Based Access Control)
- Input sanitization (SQL injection, XSS)
- Rate limiting
- Audit logging
- TLS/HTTPS
- Secret management (Vault/AWS Secrets Manager)

---

## 12. Deployment

### 12.1 Local Development

**Setup:**
```bash
# 1. Clone repo
git clone <repo_url>
cd roi-poc

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with API keys

# 5. Start infrastructure
docker-compose up -d

# 6. Run API
python -m uvicorn src.main:app --reload
```

### 12.2 Docker Deployment

**Build:**
```bash
docker build -t roi-poc:latest .
```

**Run:**
```bash
docker-compose up -d
```

**Services:**
- `postgres` - Metadata database (port 5432)
- `redis` - Cache (port 6379)
- `chromadb` - Vector store (port 8000)
- `api` - FastAPI application (port 8080)

### 12.3 Health Checks

**Docker Compose:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 10s
```

---

## 13. Monitoring & Logging

### 13.1 Logging Strategy

**Log Levels:**
- DEBUG: Detailed diagnostic info
- INFO: Confirmation of expected operation
- WARNING: Unexpected but handled situations
- ERROR: Serious issues preventing operation
- CRITICAL: System failure

**Log Format:**
```
2025-12-01 10:05:32,123 - ResearchAgent - INFO - Starting data fetch for OPP-USA-a3f8b2c1
2025-12-01 10:05:45,678 - NASA POWER - WARNING - API timeout, retrying (1/3)
2025-12-01 10:05:52,345 - AnalysisAgent - ERROR - LCOE calculation failed: division by zero
```

**Log Destinations:**
- Console: INFO and above
- File: DEBUG and above (rotated 10MB, 5 backups)
- Database: ERROR and above (for alerting)

### 13.2 Metrics (Future)

**Prometheus Metrics:**
```python
request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')
llm_cost = Counter('llm_cost_usd_total', 'Total LLM API cost')
error_count = Counter('errors_total', 'Total errors', ['error_type'])
```

**Grafana Dashboards:**
- Workflow success rate
- Average completion time
- Cost per opportunity
- Error rate by agent

---

## 14. Testing Strategy

### 14.1 Test Pyramid

```
    /\
   /UI\ (future)
  /────\
 /Integ.\  <-- E2E workflow tests
/────────\
/  Unit   \  <-- Agent, service, repo tests
─────────────
```

### 14.2 Unit Tests

**Coverage Target:** 80%

**Example:**
```python
@pytest.mark.asyncio
async def test_research_agent_validates_input():
    agent = ResearchAgent(mock_llm, config)
    
    valid = {
        "country": "USA",
        "technology": "Solar PV",
        "latitude": 31.99,
        "longitude": -102.07
    }
    assert agent.validate_input(valid) is True
    
    invalid = {"country": "USA"}  # missing fields
    assert agent.validate_input(invalid) is False
```

### 14.3 Integration Tests

**Test Workflow:**
```python
@pytest.mark.integration
async def test_end_to_end_workflow():
    orchestrator = WorkflowOrchestrator()
    
    result = await orchestrator.execute_opportunity_analysis({
        "country": "USA",
        "technology": "Solar PV",
        "latitude": 31.99,
        "longitude": -102.07
    })
    
    assert result["status"] == "COMPLETED"
    assert "lcoe_usd_per_mwh" in result["analysis_data"]
    assert 20 <= result["analysis_data"]["lcoe_usd_per_mwh"] <= 80
```

### 14.4 Validation Tests

**Expert Comparison:**
```python
def test_lcoe_accuracy_vs_expert():
    """Compare LLM LCOE to expert calculation"""
    llm_lcoe = analysis_result["lcoe_usd_per_mwh"]
    expert_lcoe = expert_ground_truth["lcoe_usd_per_mwh"]
    
    error_pct = abs(llm_lcoe - expert_lcoe) / expert_lcoe * 100
    
    assert error_pct < 15, f"LCOE error {error_pct}% exceeds 15% threshold"
```

---

## Appendix A: API Examples

**Submit Opportunity:**
```bash
curl -X POST "http://localhost:8080/api/v1/opportunities" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "USA",
    "technology": "Solar PV",
    "latitude": 31.9974,
    "longitude": -102.0779,
    "capacity_mw": 100
  }'
```

**Get Status:**
```bash
curl "http://localhost:8080/api/v1/opportunities/OPP-USA-a3f8b2c1"
```

**Health Check:**
```bash
curl "http://localhost:8080/health"
```

---

## Appendix B: Configuration Examples

**app_config.yaml:**
```yaml
llm:
  primary:
    provider: "anthropic"
    model: "claude-sonnet-4-20250514"
    api_key: "${ANTHROPIC_API_KEY}"
    temperature: 0.3
```

**agents/research_agent.yaml:**
```yaml
agent:
  timeout: 120
  max_retries: 3

data_sources:
  - name: "nasa_power"
    enabled: true
    priority: 1
```

---

**END OF DOCUMENT**

**Next Review:** After Week 1 (Day 5) - Update with implementation learnings

**Document Owner:** Engineering Team  
**Last Updated:** December 2025  
**Version:** 1.0
