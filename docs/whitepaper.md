# Adaptive Human Decision Routing (AHDR)
## Decision-grade routing for incidents and operational work

**One-line:** We don’t replace PagerDuty. We decide who PagerDuty should page.

### What AHDR does (in 30 seconds)
For each incoming incident/ticket, AHDR produces a **decision artifact** you can trust, audit, and improve:

- **Decision:** primary + backups, confidence, recommended bounded actions
- **Constraints:** deterministic veto checks (e.g., on-call required, separation-of-duties)
- **Evidence:** time-bounded signals tied to observable events (no hallucinated claims)
- **Audit:** full replay of inputs → candidate set → constraint results → scores → choice

Example (illustrative):

```json
{
  "work_item_id": "pd_incident_123",
  "primary_assignee": "human_42",
  "backup_assignees": ["human_18", "human_07"],
  "confidence": 0.71,
  "constraints": [{"name": "on_call_for_sev1", "passed": true}],
  "evidence": [
    {"type": "similar_incident", "time_window": "30d", "source": "incident_history"},
    {"type": "on_call", "time_window": "now", "source": "pagerduty_schedule"}
  ],
  "recommended_actions": ["page_primary", "add_backup", "attach_runbook"],
  "audit_trace_id": "audit_abc"
}
```

**Executive summary**
Organizations have automated observability, but the most expensive operational decision remains largely manual: **who should own this work now**. Today’s routing primitives (on-call schedules, escalation policies, assignment rules) are reliable but brittle: they encode **roles and rotations**, not **capability under context**.

AHDR is a decision layer that:
- Builds evidence-backed, time-aware capability profiles from operational exhaust
- Enforces hard constraints deterministically (veto-only)
- Ranks candidates under uncertainty with interpretable scoring
- Executes bounded, reversible actions via existing tools
- Improves from outcome feedback loops (reassignments, transfers, MTTA/TTM/MTTR)

**Why it wins**
- **Wedge ROI:** Misrouting causes transfer chains and long mitigation. Transfer reduction is measurable and high-frequency.
- **Trust-first design:** Every decision is contextual, evidence-backed, reversible, and replayable.
- **Defensibility:** Outcome-labeled routing decisions compound into an org-specific dataset incumbents can’t easily replicate.

---

## 1) The problem: routing is still manual, and misrouting is multiplicative

### The universal decision
> Given a work item *w* (incident/ticket/approval) in context *x* (service, severity, time, constraints, recent changes), choose assignee(s) *A* and bounded actions to minimize cost and risk.

### How routing happens today
In real operations, routing is a mix of:
- **On-call paging + transfers:** Page whoever is on-call, then transfer until it lands on the right team/person.
- **Rules-based routing:** Deterministic assignment rules work when taxonomies are stable, but fail under drift and hidden expertise.
- **Ad hoc expertise discovery:** “Who knows this?” in chat systems (not auditable, not scalable).

### Why it stays manual even in advanced orgs
- **Expertise is latent and time-varying:** people rotate, ownership shifts, systems evolve.
- **Objectives conflict:** speed vs interruption cost vs fairness vs compliance.
- **Trust is fragile:** if the system pages the wrong person at 3am, it loses legitimacy fast.
- **Interruptions are real operational load:** pages/tickets/interrupts must be actively managed (Google SRE [5]).

### Evidence that misrouting is a first-order cost driver
Research and production deployments show that incorrect assignment is not a minor inefficiency; it can have an **order-of-magnitude effect** on time-to-mitigate.
- DeepTriage (deployed in Azure) frames transfer assistance as valuable at scale and highlights both misassignment costs and the trust barrier for automated routing (DeepTriage [1]).

---

## 2) What we are building: AHDR as a product contract

AHDR is not “insights about people.” It is **decision ownership** over a narrow, high-value allocation decision.

### The output: a structured, auditable decision object
Every decision is a replayable artifact:
- **primary_assignee**
- **backup_assignees[]**
- **confidence** (calibrated, not vibes)
- **constraints_satisfied[]** (and failures)
- **evidence[]** (time-bounded, attributable)
- **recommended_actions[]** (bounded execution)
- **audit_trace_id**

### Evidence is anchored to observable signals
Examples of evidence signals (all scoped to the specific work item):
- Similar incidents and who resolved them (transfer/triage signal)
- Extracted entities/relations from incident text (to stabilize “incident class”) (SoftNER [4])
- Temporal expertise drift and long-tail contributors modeled via time slicing (IssueCourier [3])
- Availability and load state (on-call now, pages recently, active incidents)

AHDR’s principle: **explanations are derived from evidence; evidence is never asserted.**

---

## 3) How it works (investor-level architecture)

AHDR is a composable decision system with a strict boundary:
- **Reasoners/policies veto** (hard constraints)
- **Rankers choose** (best available under uncertainty)

### End-to-end flow
1. **Ingest**: Receive work item lifecycle events (PagerDuty, Jira, ServiceNow, etc.)
2. **Candidate generation**: Retrieve a plausible set of assignees (fast)
3. **Constraint filtering (veto-only)**: Enforce eligibility/safety constraints deterministically
4. **Re-ranking**: Score remaining candidates using interpretable features and calibrated confidence
5. **Execution**: Take bounded, reversible actions (page/assign/add backup/open channel/attach runbook)
6. **Audit logging**: Log immutable inputs, constraints, scores, and outputs
7. **Outcome collection**: Capture transfers, overrides, mitigation times, reopen, etc.
8. **Learning loop**: Update time-windowed capability features and calibration

### What we ship first (MVP wedge)
We start where feedback is dense and ROI is obvious:
- **Surface:** incident routing (PagerDuty first, then ITSM)
- **Mode:** shadow → advisory → execution
- **Primary metric:** transfer rate per incident

The MVP does not require replacing core tools. It plugs into existing event streams and executes bounded actions while logging a full audit trace.

---

## 4) Research-backed foundations (what we believe, and why)

### 4.1 Transfer-aware routing is the right objective
Routing isn’t just “pick the right team once.” Transfers and reassignment dynamics matter.
- UFTR models routing as a unified problem of assignment and transfer and shows interaction features materially improve routing performance (UFTR [2]).

### 4.2 Expertise is temporal and long-tail
Operational capability drifts; the best responder for a service changes over time.
- IssueCourier models developer activity drift via temporal slicing of heterogeneous graphs and improves assignment performance in dynamic settings (IssueCourier [3]).

### 4.3 Incident text needs normalization into stable keys
Incident titles/descriptions are noisy; similarity requires structure.
- SoftNER mines knowledge graphs from service incident reports; it is production-validated at Microsoft and enables structured retrieval features for downstream triage (SoftNER [4]).

### 4.4 Trust and operational load are first-class constraints
Paging and tickets are “interrupts” and must be managed as operational load, not treated as free.
- Google SRE guidance formalizes pages/tickets/interrupts as operational load and emphasizes protecting engineering capacity and avoiding overload (Google SRE [5]).
- USENIX discusses alert fatigue and how frequent low-priority alerts can degrade attention and response quality (USENIX login [6]).

### 4.5 LLMs are powerful, but should be bounded
We use LLMs for **structured extraction and explanation**, not unconstrained decision authority.
- Microsoft Research shows LLMs can provide accurate and interpretable incident triage when paired with structure and guardrails (COMET [7]).

### 4.6 Deterministic constraints are non-negotiable
Ranking alone is unsafe. AHDR treats constraints as a **veto layer** that never “chooses winners” and can be evaluated deterministically.

In practice, constraints should support fast incremental updates when policies change. Incremental reasoning approaches for OWL EL (as implemented by ELK) motivate this design style in frequently changing environments (Kazakov & Klinov [8]).

---

## 5) Why now

Several shifts make AHDR viable now:
- **Tooling standardization:** PagerDuty/ServiceNow/Jira/Slack adoption creates stable execution surfaces.
- **Data exhaust is finally usable:** work item lifecycles, reassignment events, and resolution metadata can be ingested and normalized.
- **Modeling + retrieval maturity:** embeddings and graph features can make candidate generation fast, while constraints remain deterministic.
- **Trust-first patterns are understood:** shadow mode, auditability, and reversibility are recognized adoption requirements (DeepTriage [1]).

---

## 6) The moat: what compounds

### 6.1 The compounding asset: outcome-labeled routing decisions
The dataset AHDR produces (and learns from) is structurally rare:
- context snapshot
- candidate set considered
- constraints applied (and which vetoed whom)
- chosen assignee(s)
- execution action taken
- outcomes (transfer chain, reassignment, mitigation time)

This cannot be fully backfilled because availability/load/override reasons are time-local and policy-dependent.

### 6.2 Trust moat: auditable decisions
In high-stakes environments, “it seems right” isn’t enough.
AHDR’s audit traces are replayable and defensible in:
- incident postmortems
- compliance reviews
- reliability governance

### 6.3 Why incumbents struggle
Incumbents can ship heuristics. What’s hard to ship is a capability model that is simultaneously:
- org-specific and time-aware
- constraint-safe
- outcome-trained
- auditable
- politically safe (no leaderboards or global “best engineer” claims)

---

## 7) Go-to-market wedge and expansion

### Initial ICP
Software-heavy organizations with 24/7 reliability obligations and mature incident tooling.

### Wedge use case (first surface)
**Incident transfer reduction + faster mitigation**
- High-frequency decision, dense feedback loops
- Measurable outcomes (transfer rate, MTTA/TTM/MTTR)
- Clear operational ROI and credibility in diligence

### Expansion surfaces (same engine, new work types)
Once trust is earned, AHDR expands by reusing the same decision engine:
- ticket routing (ITSM)
- security triage
- approvals/reviews

---

## 8) Rollout, evaluation, and safety

### Deployment phases
1. **Shadow mode:** AHDR generates recommendations + audit traces; humans decide.
2. **Advisory mode:** AHDR recommends and can execute low-regret actions (e.g., add backups, attach runbooks).
3. **Execution mode:** AHDR executes bounded routing under strict guardrails.

### Success metrics (online)
- **Transfer rate per incident** (north star)
- **MTTA / TTM / MTTR deltas**
- **Reassignment frequency**
- **Override rate** (should fall over time; spikes indicate drift/policy issues)
- **Page volume / interruption proxies**

### Evaluation (offline replay)
- Top-k routing accuracy
- Transfer-aware evaluation (would this reduce transfers on historical sequences?)

### Non-negotiable guardrails
- No global rankings, leaderboards, or “expert search”
- Explanations are contextual, time-bounded, and evidence-derived
- Constraints veto; they never rank
- All actions are bounded and reversible

---

## 9) Business model (aligned with value)

Principle: don’t price per seat; price per decision surface and decision volume.
- **Platform fee:** integrations, audit/replay, policy engine, storage
- **Volume fee:** number of decisions routed
- **Premium tiers:** high-severity/high-regret decisions (Sev-1, security, compliance)

ROI narrative that survives scrutiny:
- reduce misassignment and transfer chains
- reduce long-tail MTTR events
- reduce paging waste and operational load

---

## 10) Risks and mitigations (what can go wrong, and how we design for it)

### Trust and adoption risk
- **Risk:** one bad page can destroy credibility.
- **Mitigation:** shadow mode first, bounded execution, always-on audit, and evidence-first UX; DeepTriage highlights trust as a primary deployment barrier in practice (DeepTriage [1]).

### Politics and perceived “people scoring”
- **Risk:** systems that look like global performance ranking trigger internal resistance.
- **Mitigation:** prohibit global leaderboards and expert search; scope everything to a single work item decision; store outcomes for learning, not HR.

### Data quality and taxonomy drift
- **Risk:** routing signals degrade as services and ownership evolve.
- **Mitigation:** time-windowed features, transfer-aware objectives, and continuous calibration; normalize text into stable keys (e.g., incident KG signals) (SoftNER [4]).

### Latency and reliability
- **Risk:** routing decisions must be fast and must not fail closed.
- **Mitigation:** deterministic candidate generation, caching, fallbacks (e.g., advisory-only when dependencies are down), and “bounded action” execution surfaces.

---

## Appendix A: Canonical schemas (disciplined, decision-scoped)

### A.1 Human (eligibility + state, not global judgment)
- identity: human_id, display_name, contact_handles
- availability: on_call_status, working_hours_window
- load: recent_interruptions, active_items
- constraints: eligible_for(work_type, severity), separation_of_duties_flags
- outcomes: resolves, transfers, reassignments

Explicit exclusions:
- no global skill rankings
- no personality traits
- nothing HR-usable

### A.2 WorkItem (the decision container)
- work_item_id, type, service, severity, description, created_at, origin_system, creator
- constraints (explicit requirements)
- links (PagerDuty/Jira/GitHub/etc.)

### A.3 Decision
- decision_id, work_item_id
- primary_human, backup_humans
- confidence
- constraints_checked[]
- created_at, decision_version

Properties:
- deterministic given same inputs (except explicitly time-varying load)
- time-scoped and reversible

### A.4 Evidence
- evidence_id, decision_id, type, source, time_window, weight, text

Rule:
- evidence is derived, never asserted; it does not survive outside its decision context.

### A.5 Constraint
- constraint_id, name, applies_to, passed, failure_reason

Rule:
- constraints only veto; they never rank.

### A.6 Outcome
- outcome_id, decision_id, type (resolved/reassigned/escalated), actor, timestamp, notes (bounded)

Properties:
- idempotent, append-only, never rewritten

### A.7 Audit
- audit_id, decision_id
- inputs_snapshot, candidate_set, filtered_candidates
- score_breakdown, constraint_results, final_selection
- correlation_id

---

## Appendix B: Competitive positioning (category map)

| System | Owns assignment decision | Learns from outcomes | Constraint-safe | Auditable | Politically safe |
|---|---:|---:|---:|---:|---:|
| AHDR | Yes | Yes | Yes | Yes | Yes |
| PagerDuty (escalations/schedules) | No | No | Partial | Partial | Yes |
| ServiceNow ITSM (assignment rules) | No | No | Yes | Yes | Yes |
| Incident workflow tools (FireHydrant/Rootly) | No | No | Partial | Partial | Yes |
| “AI copilot for ops” summarizers | No | No | No | No | No |

---

## References

1. DeepTriage: Automated Transfer Assistance for Incidents in Cloud Services. arXiv:2012.03665. `https://arxiv.org/abs/2012.03665`
2. UFTR: A Unified Framework for Ticket Routing. arXiv:2003.00703. `https://arxiv.org/abs/2003.00703`
3. IssueCourier: Multi-Relational Heterogeneous Temporal Graph Neural Network for Open-Source Issue Assignment. arXiv:2505.11205. `https://arxiv.org/abs/2505.11205`
4. SoftNER: Mining Knowledge Graphs from Cloud Service Incident Reports. arXiv:2101.05961. `https://arxiv.org/abs/2101.05961`
5. Google SRE Workbook: Overload. `https://sre.google/workbook/overload/`
6. USENIX ;login: (Oct 2015 issue): discussion of alert fatigue and impact of frequent low-priority alerts. `https://www.usenix.org/system/files/login/issues/login_oct15_issue.pdf`
7. Large Language Models Can Provide Accurate and Interpretable Incident Triage (Microsoft Research). `https://www.microsoft.com/en-us/research/publication/large-language-models-can-provide-accurate-and-interpretable-incident-triage-2/`
8. Kazakov & Klinov (2013): Incremental Reasoning in OWL EL without Bookkeeping. `https://www.uni-ulm.de/fileadmin/website_uni_ulm/iui.inst.090/Publikationen/2013/KazKli13Incremental_ISWC.pdf`
