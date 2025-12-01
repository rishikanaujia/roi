# POC KICKOFF PRESENTATION
## Renewable Opportunity Identifier (ROI) - Proof of Concept

---

## Slide 1: Welcome & Agenda

**Welcome to the ROI POC Kickoff!**

**Duration:** 60 minutes

**Agenda:**
1. Project Overview (10 min)
2. POC Objectives & Success Criteria (10 min)
3. Technical Architecture (15 min)
4. Team Roles & Responsibilities (10 min)
5. Timeline & Milestones (5 min)
6. Risks & Mitigation (5 min)
7. Q&A (5 min)

---

## Slide 2: What Problem Are We Solving?

**Current State:**
- Renewable energy opportunity analysis takes 6-8 hours per site
- Requires expensive expert analysts
- Inconsistent methodologies across analysts
- Limited scalability (10-20 opportunities per week max)
- Lack of transparency in decision-making

**Desired State:**
- AI-powered analysis in <30 minutes per opportunity
- 70-90% faster than manual analysis
- Consistent, reproducible methodology
- Scalable to 100+ opportunities per day
- Complete audit trails for compliance

**Business Impact:**
- $2M ARR potential from 3 pilot customers
- 60% reduction in analyst workload
- New competitive differentiator

---

## Slide 3: POC Objectives

**Primary Goal:**
Validate technical feasibility before committing $500K to MVP development

**Specific Validations:**

| What We're Testing | Success Criteria | Go/No-Go Impact |
|-------------------|------------------|-----------------|
| **LLM Accuracy** | LCOE within ±15% of expert | CRITICAL BLOCKER |
| **Performance** | Complete in <10 minutes | CRITICAL BLOCKER |
| **Cost** | <$5 per opportunity | CRITICAL BLOCKER |
| **Expert Trust** | "Would trust for decisions" = YES | CRITICAL BLOCKER |
| **Data Quality** | >75% completeness from automation | High priority |
| **Reliability** | 90% success rate (9/10 workflows) | High priority |

**Investment Decision:**
- ✅ All criteria met → Proceed to $500K MVP
- ❌ Any blocker triggered → Halt or pivot

---

## Slide 4: POC Scope

**IN SCOPE:**
- ✅ 1 Country: USA (Texas)
- ✅ 1 Technology: Solar PV
- ✅ 5 Test Sites (different conditions)
- ✅ 3 Agents: Research, Analysis, Peer Review (simulated)
- ✅ Basic workflow: Research → Analysis → Review → Report
- ✅ Local Docker environment
- ✅ JSON + simple PDF output

**OUT OF SCOPE (Deferred to MVP):**
- ❌ Multiple countries/technologies
- ❌ Real human peer review
- ❌ Hot seat challenges
- ❌ UI (API-only)
- ❌ Production infrastructure
- ❌ Advanced deliverables (Excel, GeoJSON)
- ❌ Temporal workflows (using LangGraph only)

**Why This Scope?**
Focus on highest-risk technical assumptions with minimal complexity

---

## Slide 5: Technical Architecture

```
┌─────────────────────────────────────────────────┐
│           FASTAPI REST API                      │
│  POST /opportunities → GET /opportunities/{id}  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────┐
│      LANGGRAPH WORKFLOW ORCHESTRATOR            │
│  Research Node → Analysis Node → Peer Review    │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┼────────┐
        ↓        ↓        ↓
┌─────────┐ ┌────────┐ ┌──────────┐
│Research │ │Analysis│ │Peer Review│
│Agent    │ │Agent   │ │Agent     │
└────┬────┘ └───┬────┘ └────┬─────┘
     │          │           │
     └──────────┴───────────┘
                │
┌───────────────┴─────────────────────────────────┐
│  DATA LAYER                                     │
│  - PostgreSQL (metadata)                        │
│  - Redis (cache)                                │
│  - ChromaDB (vector store for RAG)              │
└─────────────────────────────────────────────────┘
```

**Key Technologies:**
- **LLM:** Claude Sonnet 4 (primary), GPT-4o (fallback)
- **Orchestration:** LangGraph (multi-agent)
- **Vector Store:** ChromaDB (RAG for context)
- **Database:** PostgreSQL + Redis
- **Framework:** FastAPI (Python 3.11)

**Design Patterns:**
Factory, Strategy, Repository, Dependency Injection, Template Method

---

## Slide 6: Data Flow

**End-to-End Journey:**

1. **User Input:** Submit opportunity (country, technology, lat/lon)
   ↓
2. **Research Agent:** Fetch data from NASA POWER API + policy sources
   ↓
3. **Data Normalization:** Store embeddings in ChromaDB for RAG
   ↓
4. **Analysis Agent:** Calculate LCOE, IRR using LLM + context
   ↓
5. **Validation:** Check against industry benchmarks
   ↓
6. **Peer Review Agent:** Simulate 3 peer scores, calculate average
   ↓
7. **Final Report:** Generate JSON + PDF output
   ↓
8. **Storage:** Save to PostgreSQL, return to user

**Total Time Target:** <10 minutes (POC), <30 minutes (MVP)

---

## Slide 7: Team Roles & Responsibilities

| Role | Team Member | Responsibilities | Time Commitment |
|------|-------------|------------------|-----------------|
| **Product Owner** | Rishi Kanaujia | Scope, priorities, go/no-go decision | 20% (3 weeks) |
| **Backend Engineer 1** | TBD | Infrastructure, LangGraph, Research Agent | 100% (3 weeks) |
| **Backend Engineer 2** | TBD | Data pipeline, Analysis Agent, testing | 100% (3 weeks) |
| **Domain Expert** | TBD | Ground truth calculations, validation | Part-time (5 days) |
| **Tech Lead (optional)** | TBD | Code reviews, architecture decisions | 10% (advisory) |

**RACI Matrix:**

| Task | Backend Eng 1 | Backend Eng 2 | Expert | Product Owner |
|------|---------------|---------------|--------|---------------|
| Infrastructure Setup | R | C | - | I |
| Agent Development | R | R | C | I |
| Expert Validation | I | I | R | A |
| Go/No-Go Decision | C | C | C | R/A |

R = Responsible, A = Accountable, C = Consulted, I = Informed

---

## Slide 8: 3-Week Timeline

**Week 1: Infrastructure & Data Pipeline**
- Days 1-2: Docker setup (PostgreSQL, Redis, ChromaDB)
- Day 3: NASA POWER API integration
- Day 4: Policy scraper implementation
- Day 5: Data normalization + ChromaDB storage
- **Checkpoint 1:** ✅ Can fetch/normalize data for 5 sites

**Week 2: Agent Development**
- Day 6: Research Agent implementation
- Day 7: Analysis Agent + LCOE calculator
- Day 8: Prompt engineering (iterate up to 5x)
- Day 9: Peer Review Agent (mock)
- Day 10: LangGraph orchestration
- **Checkpoint 2:** ✅ End-to-end workflow for 1 site

**Week 3: Testing & Validation**
- Day 11: Run all 5 test sites, collect metrics
- Day 12: Expert validation (blind comparison)
- Day 13: Performance profiling
- Day 14: Error handling tests
- Day 15: Final report + GO/NO-GO decision
- **Checkpoint 3:** ✅ Decision made

---

## Slide 9: Test Sites (5 in Texas)

| Site | Location | Characteristics | Expected LCOE |
|------|----------|-----------------|---------------|
| **1. West Texas** | Midland | High GHI (5.5), grid challenges | ~$40/MWh |
| **2. South Texas** | Brownsville | Moderate GHI (5.2), good grid | ~$45/MWh |
| **3. Panhandle** | Amarillo | High GHI (5.6), wind competition | ~$38/MWh |
| **4. Central Texas** | Austin | Moderate GHI (5.1), high land cost | ~$48/MWh |
| **5. East Texas** | Tyler | Low GHI (4.8), forestry competition | ~$52/MWh |

**Validation Approach:**
1. Domain expert calculates LCOE/IRR manually (blind to LLM)
2. LLM calculates independently
3. Compare results: ±15% acceptable, ±25% = blocker

---

## Slide 10: Success Criteria (Scoring Model)

**Quantitative Score (0-100 points):**

| Criterion | Weight | Scoring Method | Points |
|-----------|--------|----------------|--------|
| LCOE Accuracy | 25% | 25 × (1 - mean_error) | /25 |
| IRR Accuracy | 15% | 15 × (1 - mean_error/10) | /15 |
| Performance | 15% | 15 × (10 / actual_minutes) | /15 |
| Cost | 15% | 15 × (5 / actual_cost) | /15 |
| Data Quality | 10% | 10 × completeness | /10 |
| Reliability | 10% | 10 × success_rate | /10 |
| Expert Rating | 10% | 10 × (stars/5) | /10 |

**Decision Thresholds:**
- **90-100:** STRONG GO (high confidence)
- **75-89:** GO (proceed with normal risk)
- **60-74:** CONDITIONAL GO (mitigation plan required)
- **<60:** NO-GO (halt or pivot)

**Qualitative Veto Power:**
- Expert says "Would NOT trust" → Automatic NO-GO
- Critical unfixable bug → Automatic NO-GO
- Cost >$10/opportunity → Automatic NO-GO

---

## Slide 11: Budget

| Category | Item | Cost | Notes |
|----------|------|------|-------|
| **Labor** | Backend Engineer 1 | $10,000 | Full-time, 3 weeks |
| **Labor** | Backend Engineer 2 | $10,000 | Full-time, 3 weeks |
| **Labor** | Domain Expert | $5,000 | Part-time, 5 days |
| **Tech** | LLM API (Claude + GPT-4o) | $500 | ~100 test runs × $5 |
| **Tech** | Data sources | $0 | NASA POWER free, policy scraping |
| **Tech** | Infrastructure | $0 | Local Docker |
| **Contingency** | Buffer | $500 | Unforeseen issues |
| **TOTAL** | | **$26,000** | |

**Cost per Opportunity (Target):**
- Research Agent: ~$1.50
- Analysis Agent: ~$2.00
- Peer Review Agent: ~$0.50
- Overhead: ~$1.00
- **Total: ~$5.00** (target <$5, blocker >$10)

---

## Slide 12: Key Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **LLM accuracy insufficient** | Medium | CRITICAL | Pivot to human-AI hybrid; focus on data aggregation |
| **Performance too slow** | Medium | High | Parallelize agents, optimize prompts, accept 15 min |
| **Cost exceeds budget** | High | High | Switch to GPT-4o, reduce prompt length, negotiate volume discount |
| **Expert unavailable** | Low | High | Have 2 backup experts on standby |
| **LangGraph too buggy** | Low | High | Simplify to basic Python orchestration |
| **API rate limits** | Medium | Medium | Cache all responses, use static datasets |

**Risk Monitoring:**
- Daily standup to surface blockers
- Weekly risk review
- Go/No-Go decision at Day 15

---

## Slide 13: Communication Plan

**Daily (15 min standup):**
- What did you accomplish yesterday?
- What will you do today?
- Any blockers?

**Weekly (1 hour checkpoint):**
- Week 1 (Day 5): Infrastructure ready?
- Week 2 (Day 10): First workflow complete?
- Week 3 (Day 15): Final decision meeting

**Ad-hoc:**
- Slack channel: #roi-poc
- Code reviews: GitHub PRs
- Blocker escalation: Immediate Slack ping

**Documentation:**
- Daily progress logs in shared doc
- Decision log for key choices
- Risk register updates

---

## Slide 14: What Happens After POC?

**If GO Decision:**
1. Week 4: Formalize MVP requirements, hire team
2. Weeks 5-8: Expand to 25 countries, build UI
3. Month 6: Beta launch to 3 pilot customers
4. Year 1: Scale to 100+ countries, $2M ARR

**If NO-GO Decision:**
1. Week 4: Document lessons learned, root cause analysis
2. Evaluate alternatives:
   - Human-AI hybrid (AI for data only)
   - Fine-tune smaller/cheaper model
   - Partner with existing data provider
   - Pivot to different problem space
3. Week 5-6: Pitch revised approach or close project

**If CONDITIONAL GO:**
1. Extend POC by 2 weeks with $10K additional budget
2. Focus on gap mitigation (accuracy, performance, or cost)
3. Re-run decision framework at Week 5

---

## Slide 15: Success Stories (Target Outcomes)

**What Success Looks Like:**

1. **Speed:** "We analyzed 5 Texas sites in 1 hour vs 2 days manually"
   
2. **Accuracy:** "LLM LCOE matched expert within 10% on 4 of 5 sites"
   
3. **Cost:** "Average $4.50 per opportunity, under target"
   
4. **Trust:** "Expert said: 'I'd use this for screening, then deep-dive on top 3'"
   
5. **Quality:** "Reports caught grid congestion issue our analyst missed"

**Team Learnings:**
- Prompt engineering insights (what works/doesn't)
- LangGraph best practices
- ChromaDB RAG effectiveness data
- Realistic performance benchmarks

---

## Slide 16: Questions for Discussion

**Open Questions:**

1. **Expert Recruitment:** Who should be our domain expert? Need name by Day 0.

2. **Test Data:** Do we have access to recent Texas solar projects for ground truth?

3. **API Keys:** Who will provide Anthropic API key? OpenAI key for fallback?

4. **Work Environment:** Remote, hybrid, or co-located for 3 weeks?

5. **Post-POC:** If GO, are we funded for MVP? ($500K budget approved?)

6. **Stakeholders:** Who needs to be informed of progress? Weekly or final only?

**Decision Needed Today:**
- ✅ Approve POC budget ($26K)
- ✅ Assign engineers (names & start date)
- ✅ Confirm expert availability
- ✅ Set kickoff date (ideally next Monday)

---

## Slide 17: Call to Action

**Immediate Next Steps (This Week):**

| Action | Owner | Deadline |
|--------|-------|----------|
| Finalize POC team (2 engineers + expert) | Product Owner | Friday |
| Secure API keys (Anthropic, OpenAI) | Product Owner | Friday |
| Set up Slack channel #roi-poc | Product Owner | Today |
| Create shared docs (decision log, risk register) | Backend Eng 1 | Monday |
| Kickoff meeting (Day 0) | Everyone | Next Monday 10am |

**For Engineers:**
- Review setup script (setup_roi_poc.sh)
- Familiarize with LangGraph documentation
- Set up local dev environment over weekend (optional)

**For Product Owner:**
- Draft weekly status report template
- Schedule weekly checkpoints (Days 5, 10, 15)
- Prepare stakeholder communication

---

## Slide 18: Thank You + Q&A

**Contact Information:**
- Product Owner: Rishi Kanaujia (rishi@example.com)
- Slack: #roi-poc
- GitHub: github.com/yourorg/roi-poc (to be created)

**Resources:**
- POC Document: /outputs/ROI_POC_Document_v1.0.md
- Setup Script: /outputs/setup_roi_poc.sh
- BRD (Full MVP): /outputs/ROI_BRD_Complete_v2.0.md

**Questions?**
- Technical architecture questions?
- Timeline concerns?
- Resource availability?
- Success criteria clarification?

**Let's build something amazing! 🚀**

---

## Appendix: Technical Deep-Dive Slides

*(Optional slides for technical discussion)*

### A1: Design Patterns

**Factory Pattern:**
```python
agent = AgentFactory.create_agent("research", llm_provider, config)
# Easy to add new agents without modifying existing code
```

**Strategy Pattern:**
```python
llm_service = LLMService(config)
result = await llm_service.generate(prompt, use_fallback=False)
# Swap LLM providers (Claude ↔ GPT-4o) transparently
```

**Repository Pattern:**
```python
opportunity_repo = OpportunityRepository(db_pool)
await opportunity_repo.create(data)
# Database access abstracted, easy to swap DB
```

### A2: SOLID Principles in Practice

**Single Responsibility:**
- `ResearchAgent` only fetches data
- `AnalysisAgent` only calculates LCOE/IRR
- Each class has one reason to change

**Open/Closed:**
- New agents added via `AgentFactory.register_agent()`
- No modification to existing code

**Liskov Substitution:**
- All agents implement `IAgent` interface
- Can substitute any agent anywhere `IAgent` is expected

**Interface Segregation:**
- `IAgent`, `IDataSource`, `IRepository` are focused
- No fat interfaces with unused methods

**Dependency Inversion:**
- High-level modules (Orchestrator) depend on `IAgent`
- Not on concrete implementations (ResearchAgent)

### A3: Sample Code Walkthrough

**Creating an Agent:**
```python
from src.core.factories.agent_factory import AgentFactory
from src.services.llm_service import LLMService

# Initialize LLM service
llm_service = LLMService(config)

# Create agent via factory
research_agent = AgentFactory.create_agent(
    agent_type="research",
    llm_provider=llm_service.primary_provider,
    config=research_config
)

# Execute agent
result = await research_agent.execute({
    "country": "USA",
    "technology": "Solar PV",
    "latitude": 31.99,
    "longitude": -102.07
})
```

### A4: Testing Strategy

**Unit Tests:**
- Test each agent in isolation with mocked LLM
- Test data sources with mocked APIs
- Test orchestrator with mocked agents

**Integration Tests:**
- End-to-end workflow with real LLM (dev API key)
- Database integration tests
- ChromaDB integration tests

**Validation Tests:**
- Expert comparison (5 test sites)
- Performance benchmarks (10 runs)
- Cost tracking (all API calls logged)

**Coverage Target:** 80% for POC (lower than production but sufficient)

---

**END OF PRESENTATION**
