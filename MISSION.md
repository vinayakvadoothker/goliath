# Goliath: Mission, Vision, and Why

## 🎯 Mission

**Build decision-grade incident routing that learns from outcomes and gets smarter over time.**

Goliath is an intelligent incident routing system that automatically assigns incidents to the right people at the right time, learns from every assignment and outcome, and provides full auditability and explainability.

---

## ❓ Why This Exists: The Problem

### The Universal, Repeated Decision

Every organization faces the same problem, thousands of times per day:

> **"Given this incident/work item in this context, who should handle it now?"**

### What Teams Actually Do Today

1. **Page whoever is on-call** → Transfer until it lands on the right person (PagerDuty)
2. **Use static assignment rules** → Work for stable taxonomies, fail under drift (ServiceNow)
3. **Ask in Slack** → Rely on "who knows this" culture (not auditable, not scalable)

### Why It Stays Manual

- **Expertise is latent and time-varying**: People rotate, services evolve, ownership shifts
- **Objectives conflict**: Speed vs interruption vs fairness vs compliance
- **Trust is hard**: If the system pages the wrong person at 3am, it loses legitimacy fast
- **Interruptions are real operational load**: On-call fatigue degrades response quality
- **No learning**: Systems don't improve from mistakes or successes

### The Cost of Misrouting

Research shows that **incorrect assignment can increase time-to-mitigate by 10×**. Every transfer, every reassignment, every "who should handle this?" Slack message is wasted time and lost trust.

---

## 🚀 What Goliath Does: The Solution

Goliath is **not** "insights about people." It is **decision ownership** over incident routing.

### The Output: A Structured, Auditable Decision

Every routing decision includes:
- **Primary assignee** + backup assignees
- **Confidence score** (0-1)
- **Evidence bullets** (5-7 contextual explanations)
- **Constraints checked** (on-call, capacity, interruption thresholds)
- **Full audit trail** (candidates, scores, reasoning)

### Evidence is Not Vibes

Evidence is anchored to observable signals:
- **Similar incidents** and who resolved them (vector similarity)
- **Capability profiles** built from actual work (Jira closed tickets)
- **Temporal expertise** (recency matters - expertise decays)
- **Load signals** (pages_7d, active_items, capacity)
- **Outcome learning** (resolved vs transferred - asymmetric learning)

### Execution is Bounded and Reversible

- Creates Jira issues with assigned assignees
- Supports human override (captured as training signal)
- All actions are auditable and reversible

---

## 🧠 How It Works: The Architecture

### 1. **Ingest** (Single Source of Truth)
- Normalizes work items from multiple sources (monitoring, Jira, manual)
- LLM preprocesses descriptions (cleans, normalizes, extracts entities)
- Stores in PostgreSQL (knowledge graph) and Weaviate (vector search)

### 2. **Decision Engine** (The Brain)
- Generates candidates via Learner service
- Applies constraint filtering (veto-only: on-call, capacity, interruption thresholds)
- Scores candidates (fit_score, recency, availability, severity match, capacity)
- Calculates confidence (top1-top2 margin)
- Calls Explain service for evidence generation
- Returns structured Decision with full audit trail

### 3. **Learner** (The Memory)
- **Builds capability profiles** from Jira closed tickets (who worked on what, when)
- **Learns from outcomes**:
  - Jira issue completed → fit_score increases (+0.1), resolves_count increases
  - Reassigned/transferred → fit_score decreases (-0.15), transfers_count increases
- **Time-aware**: Stats decay over time (expertise drifts)
- **Asymmetric learning**: Transfers are worse than resolves (penalty is larger)

### 4. **Executor** (The Hands)
- Executes decisions by creating Jira issues with assigned assignees
- Links back to WorkItem
- Optional Slack notifications

### 5. **Explain** (The Justification)
- Generates contextual evidence bullets using LLM
- Explains "why this person" and "why not next best"
- All evidence is factual, time-bounded, and contextual

### 6. **Monitoring** (The Simulator)
- Simulates monitoring/observability systems
- Continuously logs and detects errors
- Creates WorkItems automatically (for demo/testing)

---

## 🎯 The Core Differentiator: The Learning Loop

**This is what makes Goliath special:**

### The Learning Loop

1. **System routes incident** → Person A assigned
2. **Person A completes it** → fit_score increases (+0.1)
3. **Next similar incident** → Person A is more likely to be chosen
4. **If Person A transfers it** → fit_score decreases (-0.15)
5. **Next similar incident** → System learned from mistake

### Why This Matters

- **Without learning**: Goliath is just a routing system
- **With learning**: Goliath is an intelligent system that gets better over time
- **The moat**: System gets smarter with every assignment/completion
- **Trust**: People see the system learning from their work

### The Learning Loop Must Be Visible

- When Jira issue is completed → fit_score must increase (visible in UI stats)
- When reassigned → fit_score must decrease (visible in UI stats)
- Next decision must use updated fit_score (different assignee or confidence)
- **This is THE core differentiator - if this doesn't work, demo fails**

---

## 🏗️ Technical Approach

### Decision-Grade, Not Heuristic

- **Deterministic**: Same inputs → same outputs (except time-varying load)
- **Auditable**: Every step logged (candidates, constraints, scores)
- **Explainable**: Evidence must be clear and contextual
- **Production-ready**: Uses vector similarity, knowledge graphs, LLM for flexibility

### No Hardcoding

- **LLM handles variations**: Entity extraction, evidence generation, log preprocessing
- **Vector search handles similarity**: Similar incidents, capability matching
- **Knowledge graph handles relationships**: Temporal, multi-relational graphs

### Bounded Execution

- **No free-form text**: Only structured Jira API calls
- **Reversible**: Jira issues can be reassigned (triggers outcome)
- **Safe**: All actions are auditable and bounded

---

## 🎯 Success Criteria

### MVP Must Have

- ✅ Decision appears <2 seconds after incident ingest
- ✅ Evidence-first explanation (5-7 bullets)
- ✅ **Learning loop works**: Jira issue completed → fit_score increases → visible in stats
- ✅ **Next decision uses updated fit_score**: Replay shows different decision/confidence
- ✅ Override works and produces visible learning update
- ✅ Audit trace is inspectable and coherent

**The learning loop is THE core differentiator. If it doesn't work, demo fails.**

---

## 🚀 The Vision

### Short Term (MVP)

Build a working system that demonstrates:
- Evidence-backed assignment
- Bounded execution
- Outcome learning
- Audit replay

### Long Term

- **Org-specific capability models** that learn from operational exhaust
- **Time-aware expertise tracking** that adapts to rotation and drift
- **Constraint-safe routing** that respects on-call, capacity, interruption thresholds
- **Outcome-trained decisions** that improve from every assignment
- **Auditable across political boundaries** (trust through transparency)

### The Moat

The compounding asset is **decision-grade outcome-labeled routing data**:
- Context snapshot + candidate set + applied constraints + chosen assignee(s) + execution + outcome + transfers

This dataset does not exist cleanly today and cannot be fully backfilled because availability, load, and human override reasons are time-local.

---

## 🤝 Who This Is For

### Initial ICP

Software-heavy organizations with:
- 24/7 reliability obligations
- Mature incident tooling (Jira, PagerDuty, ServiceNow)
- High incident volume (dense feedback loops)
- Need for faster mitigation and reduced transfers

### The Wedge Use Case

**Incident transfer reduction + faster mitigation**

- Dense feedback loops (resolution, transfers, reassignments)
- High frequency and high urgency create clear ROI
- Technical truth is measurable (MTTA/TTM/MTTR), not subjective

---

## 📊 Market Position

### Status Quo: "Rules + Rotations"

- **PagerDuty**: Escalations/schedules route notifications reliably but don't learn org-specific capability
- **ServiceNow**: Assignment rules route based on conditions at record open time; deterministic but depends on stable taxonomies

### Goliath's Differentiation

- **Decision ownership**: Not just suggestions, but actual routing decisions
- **Outcome learning**: System gets better from every assignment
- **Evidence-first**: Clear explanations for every decision
- **Auditable**: Full trace of reasoning and outcomes
- **Org-specific**: Learns from your team's actual work

### Why Platforms Don't Do This

Platforms can add heuristics; what's hard to ship is a capability model that is:
1. **Org-specific** (learns from your team)
2. **Time-aware** (expertise drifts)
3. **Constraint-safe** (respects on-call, capacity)
4. **Outcome-trained** (learns from results)
5. **Auditable** (trust through transparency)

---

## 🎓 Research Foundation

Goliath is built on production-validated research:

- **DeepTriage** (Microsoft Azure, 2017): Transfer assistance is feasible, valuable, and production-scalable. Misassignment has multiplicative cost on mitigation time.
- **SoftNER**: Production mining of incident knowledge graphs from incident reports, enabling structured signals and downstream models.
- **IssueCourier**: Modeling multi-relational heterogeneous temporal graphs with time slicing improves assignment performance and addresses long-tail contributors and activity drift.

---

## 🚦 Getting Started

**Ready to build?**

1. **Read the main README**: [README.md](README.md) - Quick start and setup
2. **Find your developer guide**: `for_developer_docs/person[1-5]_*.md`
3. **Start coding**: Build your service according to the plan

**The learning loop is THE core differentiator. Build it well.**

---

**Built with ❤️ for intelligent incident routing.**

