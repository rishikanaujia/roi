# TEST PLAN & VALIDATION PROTOCOL
## ROI POC - Renewable Opportunity Identifier

**Version:** 1.0  
**Date:** December 2025  
**Test Lead:** Backend Engineer 2  
**Validation Lead:** Domain Expert  

---

## Table of Contents

1. [Testing Overview](#1-testing-overview)
2. [Test Strategy](#2-test-strategy)
3. [Unit Testing](#3-unit-testing)
4. [Integration Testing](#4-integration-testing)
5. [Expert Validation Protocol](#5-expert-validation-protocol)
6. [Performance Testing](#6-performance-testing)
7. [Cost Tracking](#7-cost-tracking)
8. [Test Data](#8-test-data)
9. [Test Schedule](#9-test-schedule)
10. [Success Criteria](#10-success-criteria)

---

## 1. Testing Overview

### 1.1 Purpose

This test plan defines the approach for validating the ROI POC system across multiple dimensions:
- **Functional Correctness:** Do agents produce expected outputs?
- **LLM Accuracy:** Are calculations within acceptable error bounds?
- **Performance:** Does system meet timing requirements?
- **Cost:** Is cost per opportunity within budget?
- **Expert Trust:** Would domain expert rely on this for decisions?

### 1.2 Test Pyramid

```
       /\
      /UI\ (0 tests - no UI in POC)
     /────\
    /E2E(5)\  <-- End-to-end workflow tests (5 test sites)
   /────────\
  /Integ.(15)\  <-- Integration tests (agents, DB, LLM)
 /────────────\
/  Unit (40)   \  <-- Unit tests (functions, classes)
───────────────────
```

**Total Tests:** ~60 (40 unit + 15 integration + 5 end-to-end)  
**Coverage Target:** 80% for POC

### 1.3 Test Environment

| Environment | Purpose | Data | Infra |
|-------------|---------|------|-------|
| **Local Dev** | Development & unit tests | Mock/fixtures | Docker Compose |
| **Integration** | Integration tests | Test sites (5) | Docker Compose |
| **Validation** | Expert comparison | Real sites (5) | Docker Compose |

**Note:** POC uses single environment (local). MVP will add staging/production.

---

## 2. Test Strategy

### 2.1 Testing Principles

1. **Test Early, Test Often**
   - Unit tests written alongside code (TDD where possible)
   - Integration tests on Day 10 (after agents complete)
   - Expert validation on Day 12 (after integration tests pass)

2. **Automate Where Possible**
   - All unit tests automated (pytest)
   - Integration tests automated
   - Expert validation is manual (one-time)

3. **Prioritize Critical Path**
   - Focus on LLM accuracy (highest risk)
   - Performance testing secondary
   - UI testing out of scope (no UI)

4. **Mock External Dependencies**
   - Mock LLM responses for unit tests (avoid API costs)
   - Mock NASA POWER API (use cached responses)
   - Real LLM for integration tests (budget $50 for testing)

### 2.2 Test Types

| Test Type | Scope | Tools | Owner | Timeline |
|-----------|-------|-------|-------|----------|
| **Unit Tests** | Individual functions, classes | pytest | Both Engineers | Days 6-10 |
| **Integration Tests** | Multi-agent workflows | pytest-asyncio | Engineer 1 | Days 10-11 |
| **Expert Validation** | LLM accuracy vs ground truth | Manual comparison | Expert | Day 12 |
| **Performance Tests** | Runtime, throughput | pytest + profiling | Engineer 1 | Day 13 |
| **Cost Tracking** | API usage, budget adherence | Logs + dashboard | Engineer 2 | Continuous |

---

## 3. Unit Testing

### 3.1 Coverage Requirements

**Target Coverage:** 80% line coverage

**Priority:**
- **P0 (Must Cover):** Agent core logic, data validation, error handling
- **P1 (Should Cover):** Utility functions, config loading
- **P2 (Nice to Have):** Edge cases, exotic error paths

### 3.2 Unit Test Cases

#### Research Agent Tests

**Test File:** `tests/unit/test_research_agent.py`

**Test Cases:**

| Test ID | Test Case | Input | Expected Output | Priority |
|---------|-----------|-------|-----------------|----------|
| **RA-UT-001** | Valid input validation | Valid opportunity data | True | P0 |
| **RA-UT-002** | Invalid input (missing country) | {technology: "Solar"} | False | P0 |
| **RA-UT-003** | Invalid input (bad lat/lon) | lat=200, lon=500 | False | P0 |
| **RA-UT-004** | Data fetching (mocked) | Mock NASA POWER response | Normalized data | P0 |
| **RA-UT-005** | Data completeness calculation | Partial data | Completeness score 0-1 | P0 |
| **RA-UT-006** | Error handling (API timeout) | Mocked timeout | Retry 3x, log error | P1 |

**Example Test:**
```python
@pytest.mark.asyncio
async def test_research_agent_validates_input(mock_llm, config):
    """Test RA-UT-001: Valid input validation"""
    agent = ResearchAgent(mock_llm, config)
    
    valid_input = {
        "country": "USA",
        "technology": "Solar PV",
        "latitude": 31.99,
        "longitude": -102.07
    }
    
    assert agent.validate_input(valid_input) is True

@pytest.mark.asyncio
async def test_research_agent_rejects_invalid_input(mock_llm, config):
    """Test RA-UT-002: Invalid input (missing country)"""
    agent = ResearchAgent(mock_llm, config)
    
    invalid_input = {
        "technology": "Solar PV",
        "latitude": 31.99,
        "longitude": -102.07
        # Missing "country"
    }
    
    assert agent.validate_input(invalid_input) is False
```

#### Analysis Agent Tests

**Test File:** `tests/unit/test_analysis_agent.py`

| Test ID | Test Case | Input | Expected Output | Priority |
|---------|-----------|-------|-----------------|----------|
| **AA-UT-001** | LCOE calculation (known input) | Mock research data | LCOE within ±5% | P0 |
| **AA-UT-002** | IRR calculation (known input) | Mock cash flows | IRR within ±1pp | P0 |
| **AA-UT-003** | LCOE validation (out of range) | LCOE = 150 USD/MWh | Validation error | P0 |
| **AA-UT-004** | IRR validation (negative) | IRR = -5% | Validation error | P0 |
| **AA-UT-005** | Scoring (resource quality) | High GHI (5.5) | Score 8-10 | P1 |
| **AA-UT-006** | JSON parsing error | Invalid JSON from LLM | Retry + error log | P1 |

#### Peer Review Agent Tests

**Test File:** `tests/unit/test_peer_review_agent.py`

| Test ID | Test Case | Input | Expected Output | Priority |
|---------|-----------|-------|-----------------|----------|
| **PR-UT-001** | Score aggregation | 3 peer scores | Average score | P0 |
| **PR-UT-002** | Variance calculation | Varied scores | Correct variance | P0 |
| **PR-UT-003** | High variance flag | Variance > 2.5 | Flag = True | P0 |

#### LLM Service Tests

**Test File:** `tests/unit/test_llm_service.py`

| Test ID | Test Case | Input | Expected Output | Priority |
|---------|-----------|-------|-----------------|----------|
| **LLM-UT-001** | Primary provider call | Prompt | Response from Claude | P0 |
| **LLM-UT-002** | Fallback on failure | Prompt + primary fails | Response from GPT-4o | P0 |
| **LLM-UT-003** | Cost estimation | 10K tokens | ~$0.50 | P1 |
| **LLM-UT-004** | Retry with backoff | Prompt + transient error | Retry 3x, then fail | P1 |

#### Data Source Tests

**Test File:** `tests/unit/test_data_sources.py`

| Test ID | Test Case | Input | Expected Output | Priority |
|---------|-----------|-------|-----------------|----------|
| **DS-UT-001** | NASA POWER fetch (mocked) | Lat/lon | GHI data | P0 |
| **DS-UT-002** | Cache hit | Cached data exists | Return cached, no API call | P0 |
| **DS-UT-003** | Cache miss | No cached data | Fetch from API, cache result | P0 |
| **DS-UT-004** | API timeout handling | Mocked timeout | Retry, use fallback | P1 |

### 3.3 Running Unit Tests

**Command:**
```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_research_agent.py -v

# Run specific test
pytest tests/unit/test_research_agent.py::test_research_agent_validates_input -v
```

**Expected Output:**
```
tests/unit/test_research_agent.py::test_research_agent_validates_input PASSED
tests/unit/test_research_agent.py::test_research_agent_rejects_invalid_input PASSED
tests/unit/test_analysis_agent.py::test_lcoe_calculation PASSED
...
===================== 40 passed in 5.23s =====================
```

---

## 4. Integration Testing

### 4.1 Integration Test Cases

**Test File:** `tests/integration/test_workflow.py`

| Test ID | Test Case | Description | Expected Outcome | Priority |
|---------|-----------|-------------|------------------|----------|
| **IT-001** | End-to-end workflow | Submit opp → complete | Status = COMPLETED | P0 |
| **IT-002** | Database persistence | Submit opp → query DB | Opportunity record exists | P0 |
| **IT-003** | Agent coordination | Research → Analysis → PR | All agents execute in order | P0 |
| **IT-004** | Error recovery | Simulate LLM failure | Retry → fallback → success | P1 |
| **IT-005** | ChromaDB integration | Store → retrieve embeddings | Correct context retrieved | P1 |
| **IT-006** | Cache effectiveness | Submit 2x same site | 2nd call uses cache (faster) | P1 |
| **IT-007** | Concurrent requests | Submit 2 opps in parallel | Both complete successfully | P2 |

**Example Test:**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_workflow(test_db, test_redis, test_chroma):
    """Test IT-001: Complete end-to-end workflow"""
    orchestrator = WorkflowOrchestrator()
    
    input_data = {
        "country": "USA",
        "technology": "Solar PV",
        "latitude": 31.9974,
        "longitude": -102.0779
    }
    
    # Execute workflow
    result = await orchestrator.execute_opportunity_analysis(input_data)
    
    # Assertions
    assert result["status"] == "COMPLETED"
    assert "opportunity_id" in result
    assert "research_data" in result
    assert "analysis_data" in result
    assert "peer_review_data" in result
    
    # Check LCOE is reasonable
    lcoe = result["analysis_data"]["lcoe_usd_per_mwh"]
    assert 20 <= lcoe <= 80, f"LCOE {lcoe} outside expected range"
    
    # Check IRR is reasonable
    irr = result["analysis_data"]["irr_percent"]
    assert 5 <= irr <= 25, f"IRR {irr} outside expected range"
    
    # Check database persistence
    opp_record = await test_db.fetchrow(
        "SELECT * FROM opportunities WHERE opportunity_id = $1",
        result["opportunity_id"]
    )
    assert opp_record is not None
    assert opp_record["status"] == "COMPLETED"
```

### 4.2 Integration Test Setup

**Fixtures (`tests/conftest.py`):**
```python
@pytest.fixture
async def test_db():
    """PostgreSQL connection pool for testing"""
    pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        database="roi_poc_test",
        user="postgres",
        password="postgres"
    )
    yield pool
    await pool.close()

@pytest.fixture
async def test_redis():
    """Redis client for testing"""
    redis = await aioredis.from_url("redis://localhost:6379/1")
    yield redis
    await redis.flushdb()  # Clean up after test
    await redis.close()

@pytest.fixture
async def test_chroma():
    """ChromaDB client for testing"""
    client = chromadb.Client(
        Settings(
            persist_directory="./test_chromadb",
            anonymized_telemetry=False
        )
    )
    yield client
    # Clean up collections after test
```

### 4.3 Running Integration Tests

**Command:**
```bash
# Run all integration tests
pytest tests/integration/ -v -s

# Run with real LLM (costs money!)
pytest tests/integration/ -v --use-real-llm

# Run specific test
pytest tests/integration/test_workflow.py::test_end_to_end_workflow -v
```

**Expected Runtime:** 5-10 minutes (includes real LLM calls)

---

## 5. Expert Validation Protocol

### 5.1 Validation Objective

**Primary Question:** Would domain expert trust LLM-generated analysis for investment decisions?

**Validation Dimensions:**
1. LCOE accuracy (quantitative)
2. IRR accuracy (quantitative)
3. Logical consistency (qualitative)
4. Assumption appropriateness (qualitative)
5. Overall trust (qualitative)

### 5.2 Validation Process

**Phase 1: Expert Calculations (Pre-LLM, Blind)**

**Timeline:** Days 8-11 (parallel with POC development)

**Expert Tasks:**
1. Receive 5 test site descriptions (country, tech, lat/lon, basic data)
2. Calculate LCOE, IRR, scores for each site **independently**
3. Document assumptions (CapEx, OpEx, capacity factor, etc.)
4. Rate confidence in calculations (High/Medium/Low)
5. Submit results in standardized template

**Template:**
```yaml
Site: West Texas (Midland)
Expert Calculations:
  LCOE: $39.8/MWh
  IRR: 13.2%
  Resource Quality Score: 9/10
  Financial Attractiveness: 8/10
  
Assumptions:
  CapEx: $1,200/kW
  OpEx: $15/kW/year
  Capacity Factor: 25.5%
  Discount Rate: 8%
  Project Lifetime: 25 years
  
Confidence: High
Notes: High irradiance, but grid congestion risk noted
```

**Phase 2: LLM Execution**

**Timeline:** Day 11 (after expert submits)

**Process:**
1. Run LLM analysis for all 5 test sites
2. Generate reports with same format as expert template
3. **Do NOT** share with expert yet (blind comparison)

**Phase 3: Blind Comparison (Day 12)**

**Validation Session (2 hours):**

**Agenda:**
1. Review expert results (no LLM results yet) - 15 min
2. Review LLM results (de-identified as "Analyst A") - 30 min
3. Side-by-side comparison - 45 min
4. Questionnaire completion - 30 min

**Comparison Table:**
```
Site: West Texas (Midland)

Metric           | Expert  | LLM (Analyst A) | Abs Error | % Error |
-----------------+---------+-----------------+-----------+---------|
LCOE ($/MWh)     | 39.8    | 41.2            | 1.4       | +3.5%   |
IRR (%)          | 13.2    | 12.8            | 0.4       | -3.0%   |
Resource Score   | 9.0     | 8.5             | 0.5       | -5.6%   |
Financial Score  | 8.0     | 8.0             | 0.0       | 0.0%    |
```

### 5.3 Validation Questionnaire

**Quantitative Assessment:**

| Site | Expert LCOE | LLM LCOE | Error % | Expert IRR | LLM IRR | Error pp | Pass/Fail |
|------|-------------|----------|---------|------------|---------|----------|-----------|
| West TX | $39.8 | $41.2 | +3.5% | 13.2% | 12.8% | -0.4pp | ✅ PASS |
| South TX | $44.2 | $48.5 | +9.7% | 11.8% | 10.9% | -0.9pp | ✅ PASS |
| Panhandle | $38.1 | $36.8 | -3.4% | 14.1% | 14.5% | +0.4pp | ✅ PASS |
| Central TX | $47.5 | TBD | TBD | 10.2% | TBD | TBD | ⏳ |
| East TX | $51.2 | TBD | TBD | 9.8% | TBD | TBD | ⏳ |

**Pass Criteria:**
- LCOE error ≤15% → ✅ PASS
- LCOE error >15%, <25% → 🟡 MARGINAL
- LCOE error ≥25% → ❌ FAIL

**Qualitative Assessment:**

**Question 1:** Can you distinguish LLM analysis from human analysis? (Blind test)
- [ ] Yes, obvious differences
- [ ] Somewhat, noticed a few patterns
- [ ] No, indistinguishable

**Question 2:** Rate the quality of LLM analysis on each dimension (1-5 scale):

| Dimension | Rating (1-5) | Comments |
|-----------|--------------|----------|
| Data completeness | ⚪⚪⚪⚪⚪ | |
| Calculation accuracy | ⚪⚪⚪⚪⚪ | |
| Assumption appropriateness | ⚪⚪⚪⚪⚪ | |
| Logical consistency | ⚪⚪⚪⚪⚪ | |
| Actionability of recommendations | ⚪⚪⚪⚪⚪ | |
| **Overall quality** | ⚪⚪⚪⚪⚪ | |

**Question 3:** What impressed you about the LLM analysis?
_[Free text]_

**Question 4:** What concerned you about the LLM analysis?
_[Free text]_

**Question 5 (Critical):** Would you trust this analysis for making investment decisions?
- [ ] Yes, I would trust it for decisions (with normal due diligence)
- [ ] Partially, I would use it for screening, but deep-dive manually on top candidates
- [ ] No, I would NOT trust it for decisions

**Question 6:** If you answered "No" or "Partially" above, what would need to improve?
_[Free text]_

**Question 7:** Rank your confidence in the LLM analysis for different use cases:

| Use Case | Confidence (1-5) |
|----------|------------------|
| Initial screening (100 opps → 20 promising) | ⚪⚪⚪⚪⚪ |
| Detailed analysis (20 opps → 5 finalists) | ⚪⚪⚪⚪⚪ |
| Final investment decision (5 → 1-2) | ⚪⚪⚪⚪⚪ |

### 5.4 Validation Success Criteria

**GO Criteria:**
- ✅ Mean LCOE error ≤15% across all 5 sites
- ✅ Mean IRR error ≤2 pp across all 5 sites
- ✅ Expert overall quality rating ≥3.5/5
- ✅ Expert trust = "Yes" or "Partially" (not "No")
- ✅ No systematic biases detected (e.g., always overestimates)

**NO-GO Criteria:**
- ❌ Mean LCOE error >25%
- ❌ Any single site with LCOE error >40%
- ❌ Expert trust = "No, I would NOT trust it"
- ❌ Logical contradictions flagged (e.g., high risk + high recommendation)

---

## 6. Performance Testing

### 6.1 Performance Benchmarks

**Target Metrics:**

| Metric | Target | Measurement | Test Method |
|--------|--------|-------------|-------------|
| API Response (sync) | <500ms | p95 | Apache Bench |
| Research Agent | <60s | p95 | Time profiling |
| Analysis Agent | <30s | p95 | Time profiling |
| Peer Review Agent | <15s | p95 | Time profiling |
| **Total Workflow** | **<10 min** | **p95** | **End-to-end timing** |
| Database Query | <50ms | p95 | SQL profiling |
| Cache Hit Rate | >60% | Average | Redis stats |

### 6.2 Performance Test Cases

**Test File:** `tests/performance/test_benchmarks.py`

| Test ID | Test Case | Method | Success Criteria |
|---------|-----------|--------|------------------|
| **PT-001** | Workflow timing (single) | Run 1 workflow, measure time | <10 min |
| **PT-002** | Workflow timing (10 runs) | Run 10 workflows, measure p95 | p95 <10 min |
| **PT-003** | Agent profiling | Profile each agent separately | Identify bottlenecks |
| **PT-004** | Database query performance | Run 100 queries, measure p95 | p95 <50ms |
| **PT-005** | Cache effectiveness | Run same query 2x, compare times | 2nd call >5x faster |
| **PT-006** | Concurrent workflows | Run 2 workflows in parallel | No degradation |

**Example Test:**
```python
@pytest.mark.performance
@pytest.mark.asyncio
async def test_workflow_performance_single():
    """Test PT-001: Single workflow timing"""
    orchestrator = WorkflowOrchestrator()
    
    start_time = time.time()
    
    result = await orchestrator.execute_opportunity_analysis({
        "country": "USA",
        "technology": "Solar PV",
        "latitude": 31.99,
        "longitude": -102.07
    })
    
    duration = time.time() - start_time
    
    assert result["status"] == "COMPLETED"
    assert duration < 600, f"Workflow took {duration}s, exceeds 10 min target"
    
    print(f"Workflow completed in {duration:.2f} seconds")
```

### 6.3 Profiling

**Python Profiler:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run workflow
await orchestrator.execute_opportunity_analysis(data)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest functions
```

**Expected Output:**
```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.003    0.003  512.456  512.456 workflow.py:45(execute)
        3    2.134    0.711  485.234  161.744 llm_service.py:78(generate)
        1   15.234   15.234   25.456   25.456 nasa_power.py:34(fetch)
        ...
```

**Bottleneck Analysis:**
1. Identify functions with high `cumtime` (cumulative time)
2. Check if time is spent in LLM calls (expected) or elsewhere (optimize)
3. Parallelize independent operations where possible

---

## 7. Cost Tracking

### 7.1 Cost Tracking Methodology

**Tracking Granularity:** Per-agent, per-opportunity

**Data Collection:**
- Log all LLM API calls with token counts
- Calculate cost using provider pricing
- Aggregate by agent, by day, by opportunity

**Storage:**
```sql
CREATE TABLE execution_logs (
    id UUID PRIMARY KEY,
    opportunity_id VARCHAR(255),
    agent_name VARCHAR(100),
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost_usd DECIMAL(10, 4),
    created_at TIMESTAMP
);
```

### 7.2 Cost Tracking Tests

| Test ID | Test Case | Method | Success Criteria |
|---------|-----------|--------|------------------|
| **CT-001** | Cost per opportunity | Run 5 workflows, measure avg cost | <$5 avg |
| **CT-002** | Cost by agent | Aggregate cost by agent | Research <$2, Analysis <$2.5 |
| **CT-003** | Total POC budget | Sum all costs | <$500 total |
| **CT-004** | Cost trend | Compare daily costs | Not increasing |

**Query:**
```sql
-- Cost per opportunity
SELECT 
    opportunity_id,
    SUM(cost_usd) as total_cost
FROM execution_logs
GROUP BY opportunity_id
ORDER BY total_cost DESC;

-- Cost by agent
SELECT 
    agent_name,
    COUNT(*) as calls,
    SUM(cost_usd) as total_cost,
    AVG(cost_usd) as avg_cost
FROM execution_logs
GROUP BY agent_name
ORDER BY total_cost DESC;
```

### 7.3 Cost Dashboard

**Metrics to Track:**
- Daily LLM spend
- Cost per opportunity (trend)
- Cost by agent (breakdown)
- Projected POC total cost
- Budget remaining

**Alert Thresholds:**
- Single opportunity >$10 → Alert product owner
- Daily spend >$100 → Alert immediately
- Projected total >$700 → Alert with mitigation plan

---

## 8. Test Data

### 8.1 Test Sites (5 in Texas)

**Site 1: West Texas (Midland)**
- **Coordinates:** 31.9974° N, 102.0779° W
- **GHI:** 5.5 kWh/m²/day (high)
- **Grid:** ERCOT West, moderate congestion
- **Land:** Low cost, minimal competing uses
- **Policy:** Federal ITC 30%
- **Expected LCOE:** ~$40/MWh
- **Characteristics:** Best resource, grid challenges

**Site 2: South Texas (Brownsville)**
- **Coordinates:** 25.9017° N, 97.4975° W
- **GHI:** 5.2 kWh/m²/day (moderate-high)
- **Grid:** ERCOT South, good capacity
- **Land:** Agricultural competition, moderate cost
- **Expected LCOE:** ~$45/MWh
- **Characteristics:** Good grid, lower resource

**Site 3: Panhandle (Amarillo)**
- **Coordinates:** 35.2220° N, 101.8313° W
- **GHI:** 5.6 kWh/m²/day (highest)
- **Grid:** ERCOT North, good capacity
- **Land:** Low cost, wind farm competition
- **Expected LCOE:** ~$38/MWh
- **Characteristics:** Best overall site

**Site 4: Central Texas (Austin)**
- **Coordinates:** 30.2672° N, 97.7431° W
- **GHI:** 5.1 kWh/m²/day (moderate)
- **Grid:** ERCOT Central, some congestion
- **Land:** High cost near urban areas
- **Expected LCOE:** ~$48/MWh
- **Characteristics:** Urban proximity tradeoffs

**Site 5: East Texas (Tyler)**
- **Coordinates:** 32.3513° N, 95.3011° W
- **GHI:** 4.8 kWh/m²/day (lowest)
- **Grid:** ERCOT East, good capacity
- **Land:** Forestry competition, moderate cost
- **Expected LCOE:** ~$52/MWh
- **Characteristics:** Worst resource, testing edge case

### 8.2 Ground Truth Data

**Expert Calculations (Pre-Computed):**

Located in: `tests/fixtures/expert_ground_truth.json`

```json
{
  "west_texas": {
    "lcoe_usd_per_mwh": 39.8,
    "irr_percent": 13.2,
    "resource_score": 9.0,
    "financial_score": 8.0,
    "assumptions": {
      "capex_usd_per_kw": 1200,
      "opex_usd_per_kw_year": 15,
      "capacity_factor": 0.255,
      "discount_rate": 0.08
    }
  },
  // ... other sites
}
```

---

## 9. Test Schedule

### 9.1 Testing Timeline

```
Week 1 (Days 1-5): Infrastructure
  Day 1-2: Docker setup
  Day 3-5: Data pipeline + unit tests

Week 2 (Days 6-10): Agent Development + Unit Testing
  Day 6: Research Agent + tests
  Day 7: Analysis Agent + tests
  Day 8-9: Peer Review Agent + tests
  Day 10: Integration tests

Week 3 (Days 11-15): Validation + Performance
  Day 11: End-to-end tests (all 5 sites)
  Day 12: Expert validation session
  Day 13: Performance profiling + optimization
  Day 14: Final test runs + cost analysis
  Day 15: Results compilation + go/no-go decision
```

### 9.2 Daily Test Execution

**Continuous Testing (Days 6-14):**
- Run unit tests after each code change
- Run integration tests nightly (automated)
- Track test coverage daily (target 80%)

**Test Execution Commands:**
```bash
# Daily: Run all tests
pytest tests/ -v --cov=src

# Daily: Quick smoke test
pytest tests/integration/test_workflow.py::test_end_to_end_workflow -v

# Day 11: Full validation suite
pytest tests/ -v --use-real-llm --cov-report=html

# Day 13: Performance profiling
pytest tests/performance/ -v -s
```

---

## 10. Success Criteria

### 10.1 Test Pass Criteria

**Unit Tests:**
- ✅ 100% of P0 tests pass
- ✅ 90% of P1 tests pass
- ✅ 80% code coverage

**Integration Tests:**
- ✅ All 5 test sites complete successfully
- ✅ No critical bugs (system hangs, data corruption)
- ✅ Graceful error handling demonstrated

**Expert Validation:**
- ✅ Mean LCOE error ≤15%
- ✅ Mean IRR error ≤2 pp
- ✅ Expert trust = "Yes" or "Partially"
- ✅ Overall rating ≥3.5/5 stars

**Performance:**
- ✅ p95 workflow runtime <10 min
- ✅ p95 API response <500ms
- ✅ Cache hit rate >60%

**Cost:**
- ✅ Average cost per opportunity <$5
- ✅ Total POC cost <$500
- ✅ No single opportunity >$10

### 10.2 Final Test Report

**Template:**

```markdown
# ROI POC - Final Test Report

## Summary
- Total Tests: 60
- Passed: 58
- Failed: 2
- Coverage: 82%

## Unit Tests: ✅ PASS
- P0 Tests: 30/30 passed
- P1 Tests: 8/10 passed (2 edge cases failed, non-critical)
- Coverage: 82%

## Integration Tests: ✅ PASS
- End-to-end workflows: 5/5 passed
- Error handling: 3/3 passed
- Database integration: 2/2 passed

## Expert Validation: ✅ PASS
- Mean LCOE error: 6.8% (threshold: 15%)
- Mean IRR error: 0.6 pp (threshold: 2 pp)
- Expert trust: "Yes, with normal due diligence"
- Overall rating: 4.2/5 stars

## Performance: ✅ PASS
- p95 runtime: 8.5 min (threshold: 10 min)
- Cache hit rate: 87% (threshold: 60%)

## Cost: ✅ PASS
- Avg cost/opportunity: $4.20 (threshold: $5.00)
- Total POC cost: $385 (threshold: $500)

## Recommendation: GO
All critical success criteria met. Proceed to MVP.
```

---

## 11. Test Artifacts

### 11.1 Deliverables

| Artifact | Location | Owner | Due Date |
|----------|----------|-------|----------|
| Unit test suite | `tests/unit/` | Engineers | Day 10 |
| Integration test suite | `tests/integration/` | Engineers | Day 11 |
| Test coverage report | `htmlcov/index.html` | Engineers | Day 11 |
| Expert validation results | `outputs/validation_report.pdf` | Expert | Day 12 |
| Performance profiling report | `outputs/performance_report.md` | Engineer 1 | Day 13 |
| Cost analysis dashboard | `outputs/cost_analysis.xlsx` | Engineer 2 | Day 14 |
| Final test report | `outputs/final_test_report.md` | Test Lead | Day 15 |

---

## Sign-Off

**Test Plan Approved By:**
- Test Lead: _________________ Date: _______
- Product Owner: _________________ Date: _______
- Domain Expert: _________________ Date: _______

**Document Version:** 1.0  
**Last Updated:** [Date]  
**Next Review:** After MVP (if GO decision)

---

**END OF DOCUMENT**
