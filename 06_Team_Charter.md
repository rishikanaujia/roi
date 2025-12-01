# TEAM CHARTER
## ROI POC - Renewable Opportunity Identifier

**Charter Version:** 1.0  
**Effective Date:** [POC Start Date]  
**Duration:** 3 Weeks (Days 1-15)  
**Team:** 2 Engineers + 1 Domain Expert + 1 Product Owner  

---

## Table of Contents

1. [Team Purpose & Mission](#1-team-purpose--mission)
2. [Team Members & Roles](#2-team-members--roles)
3. [Working Agreements](#3-working-agreements)
4. [Communication Protocols](#4-communication-protocols)
5. [Decision-Making Framework](#5-decision-making-framework)
6. [Conflict Resolution](#6-conflict-resolution)
7. [Success Metrics](#7-success-metrics)
8. [Retrospective Plan](#8-retrospective-plan)

---

## 1. Team Purpose & Mission

### 1.1 Mission Statement

> **"Validate the technical feasibility of an AI-powered renewable energy opportunity analyzer in 3 weeks, delivering a go/no-go recommendation for $500K MVP investment."**

### 1.2 Objectives

**Primary Objective:**
- Determine if LLM-based analysis can match expert-level accuracy (±15% LCOE error) while delivering 70-90% faster results

**Secondary Objectives:**
- Build functional multi-agent system (Research, Analysis, Peer Review)
- Validate cost economics (<$5 per opportunity)
- Establish development practices for future MVP
- Create reusable architecture and patterns

### 1.3 Success Criteria

**Quantitative:**
- LCOE accuracy within ±15% of expert calculations
- Workflow completes in <10 minutes (p95)
- Cost per opportunity <$5
- 80% code coverage

**Qualitative:**
- Expert says "I would trust this for decisions" (or "Partially")
- Team delivers on time (Day 15 decision)
- No critical technical blockers identified
- Team learns and documents lessons for MVP

### 1.4 Out of Scope

**What We're NOT Building:**
- Production-ready system
- User interface (API only)
- Real peer review (simulated)
- Multi-country/multi-technology support
- Advanced features (hot seat, strikes, etc.)

**Why These Constraints:**
- Focus on highest-risk validation (LLM accuracy)
- Complete in 3 weeks with small team
- Minimize complexity and cost

---

## 2. Team Members & Roles

### 2.1 Team Roster

| Name | Role | Commitment | Primary Focus | Contact |
|------|------|------------|---------------|---------|
| **[Name]** | Product Owner | 20% (6h/week) | Scope, priorities, go/no-go decision | [email/phone] |
| **[Name]** | Backend Engineer 1 | 100% (40h/week) | Infrastructure, LangGraph, Research Agent | [email/phone] |
| **[Name]** | Backend Engineer 2 | 100% (40h/week) | Data pipeline, Analysis Agent, testing | [email/phone] |
| **[Name]** | Domain Expert | Part-time (5 days) | Ground truth calculations, validation | [email/phone] |

### 2.2 Roles & Responsibilities

#### Product Owner
**Accountabilities:**
- Define and prioritize scope
- Make go/no-go decision (Day 15)
- Unblock resource issues (API keys, budget, expert availability)
- Communicate with stakeholders
- Attend weekly checkpoints (Days 5, 10, 15)

**Time Commitment:**
- Daily standup: 15 min
- Weekly checkpoint: 1 hour
- Ad-hoc unblocking: ~2 hours/week
- **Total: ~6 hours/week**

**Deliverables:**
- Approved POC scope (Day 0)
- Weekly status updates to stakeholders
- Final go/no-go decision (Day 15)

#### Backend Engineer 1 (Infrastructure & Orchestration Lead)
**Accountabilities:**
- Set up development environment (Docker, databases)
- Implement LangGraph workflow orchestration
- Build Research Agent
- Integration testing
- Performance profiling
- Code reviews for Engineer 2

**Time Commitment:**
- Full-time (40 hours/week)

**Deliverables:**
- Working Docker environment (Day 2)
- Research Agent (Day 6)
- LangGraph orchestration (Day 10)
- Integration tests (Day 11)
- Performance report (Day 13)

#### Backend Engineer 2 (Analysis & Testing Lead)
**Accountabilities:**
- Implement data pipeline and normalization
- Build Analysis Agent (LCOE, IRR calculations)
- Build Peer Review Agent
- Unit testing (target 80% coverage)
- Cost tracking implementation
- Code reviews for Engineer 1

**Time Commitment:**
- Full-time (40 hours/week)

**Deliverables:**
- Data pipeline (Day 5)
- Analysis Agent (Day 8)
- Peer Review Agent (Day 9)
- Test suite (Day 10)
- Cost tracking dashboard (Day 14)

#### Domain Expert (Validation Lead)
**Accountabilities:**
- Calculate ground truth LCOE/IRR for 5 test sites
- Validate LLM-generated analyses (blind comparison)
- Provide expert opinion on trustworthiness
- Answer technical questions about renewable energy finance
- Document assumptions and methodology

**Time Commitment:**
- Part-time: ~8 hours/day for 5 days
- Days 8-11: Calculations (3 days)
- Day 12: Validation session (2 hours)
- Day 14: Follow-up review (1 hour)

**Deliverables:**
- Ground truth calculations (5 sites, Day 11)
- Validation questionnaire (Day 12)
- Expert report (Day 14)

### 2.3 RACI Matrix

| Activity | Product Owner | Engineer 1 | Engineer 2 | Expert |
|----------|---------------|------------|------------|--------|
| **Scope Definition** | A/R | C | C | I |
| **Infrastructure Setup** | I | R/A | C | - |
| **Research Agent** | I | R/A | C | C |
| **Analysis Agent** | I | C | R/A | C |
| **Peer Review Agent** | I | C | R/A | - |
| **Unit Testing** | I | A | R | - |
| **Integration Testing** | I | R/A | A | - |
| **Expert Validation** | C | I | I | R/A |
| **Performance Profiling** | I | R/A | C | - |
| **Cost Tracking** | A | C | R | - |
| **Go/No-Go Decision** | R/A | C | C | C |
| **Stakeholder Communication** | R/A | I | I | I |

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

---

## 3. Working Agreements

### 3.1 Core Values

**1. Bias Toward Action**
- When in doubt, ship and iterate
- "Good enough" > "perfect" for POC
- Make reversible decisions quickly

**2. Transparency**
- Share blockers immediately
- Document decisions (Decision Log)
- No surprises at checkpoints

**3. Collaborative Problem-Solving**
- Ask for help early
- Pair programming encouraged
- Knowledge sharing over silos

**4. Focus on Validation**
- POC goal is learning, not production code
- Optimize for speed, not polish
- Technical debt acceptable if documented

**5. Respect for Time**
- Start meetings on time
- Come prepared
- Honor time commitments

### 3.2 Work Schedule

**Core Hours (Overlap Required):**
- 10:00 AM - 3:00 PM local time (Engineers)
- Flexible outside core hours (remote-friendly)

**Availability:**
- Respond to Slack within 2 hours during core hours
- Flag urgent issues immediately (phone call OK)
- No work on weekends unless critical blocker

**Time Off:**
- Notify team 24 hours in advance if possible
- Document handoff for in-progress work
- Update "Out of Office" Slack status

### 3.3 Development Practices

**Code Quality:**
- All code in Git (commit early, commit often)
- Feature branches, PRs for review
- No direct commits to `main`
- PR approval required from one other engineer
- CI runs tests on every PR

**Testing:**
- Write tests alongside code (TDD encouraged)
- Target 80% coverage (flexible for POC)
- Integration tests run nightly
- Manual testing documented in Test Plan

**Documentation:**
- Inline comments for complex logic
- README updated as system evolves
- Decision Log for significant choices
- Architecture diagrams in `docs/`

**Configuration:**
- No hardcoding (all config in YAML files)
- Secrets in `.env` (never committed)
- Environment variables for deployment-specific values

### 3.4 Collaboration Tools

| Tool | Purpose | Access | Owner |
|------|---------|--------|-------|
| **Slack** | Daily communication | #roi-poc channel | All |
| **GitHub** | Code repository | github.com/yourorg/roi-poc | Engineers |
| **Google Docs** | Living documents (status, risks) | Shared folder | Product Owner |
| **Zoom** | Video calls (standups, checkpoints) | Meeting link | Product Owner |
| **Notion/Confluence** | Knowledge base (optional) | Team workspace | All |

---

## 4. Communication Protocols

### 4.1 Meetings

#### Daily Standup (15 minutes)
**Time:** 9:45 AM every weekday  
**Attendees:** All team members (Product Owner optional Days 1-14)  
**Format:**
- What did you accomplish yesterday?
- What will you do today?
- Any blockers?

**Rules:**
- Keep it brief (2 min per person)
- Blockers discussed after standup (offline)
- Use parking lot for detailed discussions

#### Weekly Checkpoint (1 hour)
**Schedule:**
- Week 1: Day 5 (Friday)
- Week 2: Day 10 (Wednesday)
- Week 3: Day 15 (Monday - Decision Meeting)

**Attendees:** All team members  
**Format:**
- Progress update (15 min)
- Demo (15 min)
- Risks & blockers (15 min)
- Next week plan (15 min)

**Rules:**
- Product Owner must attend
- Demos should be live (not slides)
- Document decisions in Decision Log

#### Ad-Hoc Working Sessions
**When:** As needed  
**Purpose:** Pair programming, debugging, design discussions  
**Duration:** 30 min - 2 hours  
**Rules:**
- Schedule via Slack
- Optional attendance
- Share notes after

### 4.2 Communication Channels

#### Slack: #roi-poc
**For:**
- Quick questions
- Status updates
- Blockers
- Celebrations 🎉

**Response Time:** Within 2 hours during core hours

**Guidelines:**
- Use threads to keep conversations organized
- @mention for urgent issues
- Summarize long threads in main channel

**Do NOT use for:**
- Code reviews (use GitHub)
- Long-form documentation (use Google Docs)
- Sensitive information (use direct message)

#### Email
**For:**
- Stakeholder updates (weekly)
- External communication (APIs, vendors)
- Formal approvals

**Response Time:** Within 24 hours

#### GitHub PRs
**For:**
- Code reviews
- Technical discussions on specific changes

**Response Time:** Within 4 hours for review requests

**Guidelines:**
- Provide context in PR description
- Link to related issues
- Add screenshots/videos for UI changes (future)

### 4.3 Status Reporting

**Daily (Informal):**
- Quick update in standup
- Slack message if significant progress/blocker

**Weekly (Formal):**
- Status report (using template)
- Updated metrics dashboard
- Risk register review

**Stakeholder Updates:**
- Product Owner sends weekly email
- Format: Executive summary + metrics + risks
- Distribution: Executive sponsor, key stakeholders

### 4.4 Escalation Path

**Level 1: Team (0-4 hours)**
- Discuss in standup
- Resolve via Slack/working session
- Document in Decision Log

**Level 2: Product Owner (4-24 hours)**
- Blockers requiring resources (API keys, budget)
- Scope clarifications
- Priority conflicts

**Level 3: Executive Sponsor (24+ hours)**
- Budget overruns
- Timeline extension needed
- Major technical pivot

**Critical Issues (Immediate):**
- Security breach → Security Lead + Product Owner
- System down → On-call engineer + Product Owner
- Expert unavailable → Product Owner (backup expert activation)

---

## 5. Decision-Making Framework

### 5.1 Decision Authority

**Product Owner Has Final Say On:**
- Scope (what's in/out of POC)
- Priority (if time constrained, what ships first)
- Budget allocation
- Go/no-go decision (Day 15)

**Engineers Have Final Say On:**
- Technical implementation (which library, pattern, etc.)
- Code quality standards
- Testing approach
- Architecture (within agreed patterns)

**Domain Expert Has Final Say On:**
- Financial model assumptions (CapEx, OpEx, etc.)
- Industry benchmarks
- Validation methodology

### 5.2 Decision Types

**Type 1: Reversible (Fast)**
- Examples: Which library to use, code structure, test approach
- Process: Engineer decides, documents in Decision Log, informs team
- Reversal: Change at any time if better option found

**Type 2: Costly to Reverse (Discuss)**
- Examples: Database choice, LLM provider, orchestration framework
- Process: Propose in Slack → Discuss in meeting → Product Owner approves → Document
- Reversal: Requires Product Owner approval + impact assessment

**Type 3: Critical (Consensus Required)**
- Examples: Pivot architecture, extend timeline, change success criteria
- Process: Document options → Team discussion → Product Owner + stakeholder approval
- Reversal: Requires same approval level

### 5.3 Decision Log

**All Type 2 and Type 3 decisions MUST be logged:**

**Template:**
```markdown
## Decision: [Title]
**Date:** [Date]
**Type:** Type 2 - Costly to Reverse
**Decision Maker:** Product Owner (consensus)

**Context:** Why we're making this decision

**Options Considered:**
1. Option A - Pros/cons
2. Option B - Pros/cons
3. **Option C** (chosen) - Pros/cons

**Decision:** We will do X because Y

**Impact:** What changes, what risks, what opportunities

**Reversible:** Yes/No (and under what conditions)
```

---

## 6. Conflict Resolution

### 6.1 Conflict Types & Resolution

**Technical Disagreements:**
- **Process:** 
  1. Document both perspectives
  2. 30-minute timebox discussion
  3. If no consensus, Engineer 1 decides (tie-breaker)
  4. Implement decision, revisit if issues arise
- **Example:** Which vector DB (ChromaDB vs Weaviate)

**Priority Conflicts:**
- **Process:**
  1. Present to Product Owner with trade-offs
  2. Product Owner decides based on POC goals
  3. Document in Decision Log
- **Example:** Focus on accuracy vs performance optimization

**Resource Conflicts:**
- **Process:**
  1. Escalate to Product Owner immediately
  2. Product Owner secures resources or adjusts scope
- **Example:** Expert unavailable for validation

**Interpersonal Conflicts:**
- **Process:**
  1. Private 1:1 conversation first
  2. If unresolved, involve Product Owner as mediator
  3. Focus on behaviors, not personalities
  4. Document agreements going forward

### 6.2 Conflict Prevention

**Proactive Measures:**
- Clear roles and responsibilities (RACI)
- Transparent decision-making (Decision Log)
- Regular check-ins (standups, checkpoints)
- Psychological safety (no blame culture)

**Ground Rules:**
- Assume positive intent
- Disagree openly but respectfully
- Commit to decisions once made
- Escalate early before issues fester

---

## 7. Success Metrics

### 7.1 Team Performance Metrics

**Velocity:**
- Stories completed per week
- Target: Complete all planned work by Day 15

**Quality:**
- Bug count (P0/P1 bugs found in testing)
- Target: <5 P0 bugs, <10 P1 bugs
- Test coverage: Target 80%

**Collaboration:**
- PR review time (time from PR open to merge)
- Target: <4 hours average
- Meeting effectiveness (rated after each checkpoint)
- Target: 4/5 average rating

**Communication:**
- Standup attendance: Target 95%
- Blocker resolution time: Target <24 hours
- Documentation completeness: Target 100% for key decisions

### 7.2 Individual Contribution

**Engineers:**
- Code contributions (commits, PRs)
- Code review quality (helpful feedback)
- Knowledge sharing (documentation, pairing)
- Attitude (collaboration, problem-solving)

**Product Owner:**
- Clear requirements and priorities
- Timely decision-making
- Stakeholder management
- Support for team

**Domain Expert:**
- Quality of ground truth calculations
- Timeliness of validation (Day 12)
- Constructive feedback on LLM outputs

### 7.3 Team Health

**Weekly Pulse Check (1-5 scale):**
- I understand the POC goals and priorities
- I have the resources I need to succeed
- I feel supported by my teammates
- We are on track to deliver by Day 15
- I would recommend this team to a friend

**Target:** 4/5 average across all questions

---

## 8. Retrospective Plan

### 8.1 Retrospective Schedule

**Mid-POC Retro (Day 8):**
- 30 minutes
- Focus: Process improvements, blocker identification
- Outcome: 1-2 action items for Week 3

**Final Retro (Day 16 or 17):**
- 1 hour
- Focus: Lessons learned, what to carry forward to MVP
- Outcome: Comprehensive lessons learned document

### 8.2 Retrospective Format

**1. Set the Stage (5 min)**
- Review norms (confidentiality, no blame)
- Set focus (what went well, what didn't)

**2. Gather Data (15 min)**
- Each person writes on sticky notes:
  - 🟢 What went well
  - 🔴 What didn't go well
  - 💡 Ideas for improvement

**3. Generate Insights (15 min)**
- Group similar items
- Identify patterns
- Vote on top 3 issues to address

**4. Decide What to Do (15 min)**
- For each top issue, define action item
- Assign owner and deadline
- Document in Retrospective Log

**5. Close (10 min)**
- Appreciate team members
- Commit to actions

### 8.3 Action Item Tracking

**Template:**
```markdown
## Action Item: [Title]
**Retro Date:** Day 8
**Owner:** Backend Engineer 1
**Deadline:** Day 10
**Status:** In Progress

**Problem:** Prompt engineering taking too long (iteration 3, estimated 1 day)
**Action:** Cap at 5 iterations, accept "good enough"
**Success Metric:** Complete by Day 10 regardless of perfection
```

---

## 9. Team Charter Acceptance

### 9.1 Commitment

By signing below, each team member commits to:
- Upholding the team values and working agreements
- Contributing their best effort to achieve POC goals
- Communicating openly and transparently
- Resolving conflicts constructively
- Celebrating successes and learning from failures

### 9.2 Signatures

| Name | Role | Signature | Date |
|------|------|-----------|------|
| [Name] | Product Owner | _______________ | ________ |
| [Name] | Backend Engineer 1 | _______________ | ________ |
| [Name] | Backend Engineer 2 | _______________ | ________ |
| [Name] | Domain Expert | _______________ | ________ |

### 9.3 Charter Review

**This charter is a living document.**

**Review Frequency:**
- Mid-POC (Day 8): Check if adjustments needed
- Final Retro (Day 16): Lessons learned for future teams

**Amendment Process:**
- Any team member can propose changes
- Discuss in standup or checkpoint
- Requires consensus to amend
- Product Owner approves final version

---

## 10. Appendices

### Appendix A: Quick Reference

**Daily Standup:** 9:45 AM, 15 min, all team  
**Weekly Checkpoint:** Days 5, 10, 15  
**Slack Channel:** #roi-poc  
**GitHub Repo:** github.com/yourorg/roi-poc  
**Product Owner:** [Email/Phone]  
**Engineer 1:** [Email/Phone]  
**Engineer 2:** [Email/Phone]  
**Expert:** [Email/Phone]  

### Appendix B: Key Documents

| Document | Location | Owner | Updated |
|----------|----------|-------|---------|
| POC Plan | /outputs/ROI_POC_Document_v1.0.md | Product Owner | Weekly |
| Status Report Template | /outputs/03_Weekly_Status_Report_Template.md | Engineers | Weekly |
| Risk Register | /outputs/04_Risk_Register_and_Decision_Log.md | Product Owner | Daily |
| Decision Log | /outputs/04_Risk_Register_and_Decision_Log.md | Tech Lead | As needed |
| Test Plan | /outputs/05_Test_Plan_and_Validation_Protocol.md | Engineer 2 | Weekly |

### Appendix C: Emergency Contacts

**Product Owner:**
- Email: [email]
- Phone: [phone]
- Slack: @[username]

**Technical Lead (if needed):**
- Email: [email]
- Phone: [phone]

**Executive Sponsor:**
- Email: [email]
- Phone: [phone] (escalations only)

---

## Closing Thoughts

**This team charter represents our commitment to:**
- Clear communication
- Mutual respect
- Collaborative problem-solving
- Focused execution
- Learning and growth

**Let's build something amazing together! 🚀**

---

**Charter Version:** 1.0  
**Effective Date:** [POC Start Date]  
**Next Review:** Day 8 (Mid-POC Retro)  

**Document Owner:** Product Owner  
**Last Updated:** [Date]  

---

**END OF DOCUMENT**
