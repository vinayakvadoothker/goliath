Idea 1: Adaptive Human Decision Routing (AHDR)


Mission: Build decision-grade models that allocate human judgment to the right work at the right time, and take responsibility for outcomes.
Abstract
Organizations have automated system observability, but the most expensive operational decision remains largely manual: who should own this work now.
Today’s primitives (on-call schedules, escalation policies, static assignment rules) are reliable but brittle: they encode roles and rotations, not capability under context. PagerDuty escalation policies/schedules and ServiceNow assignment rules explicitly reflect this “static routing” pattern.  ServiceNow
Research and production evidence shows misrouting is a first-order cost driver: DeepTriage reports that incorrect assignment can increase time-to-mitigate by 10×, and it has been deployed in Azure since 2017 and used by thousands of teams daily. arXiv
AHDR is a decision layer that (1) builds evidence-backed human capability profiles from operational exhaust, (2) enforces hard constraints deterministically, (3) ranks candidates under uncertainty, (4) executes bounded actions via existing systems, and (5) improves using outcome feedback loops (transfers, reassignments, MTTA/TTM/MTTR).
The problem (what’s still manual, and why nobody fully owns it)
The universal, repeated decision:
“Given work item w (incident/ticket/review/approval) in context x (service, severity, time, constraints, recent changes), choose assignee(s) A and actions π that minimize cost and risk.”


What teams actually do in real life:
Page whoever is on-call, then transfer until it lands on the right team/person (PagerDuty). support.pagerduty.com
Route tickets via conditional assignment rules (ServiceNow), which can be correct for stable taxonomies but fail under drift and hidden expertise. ServiceNow
Ask in Slack and rely on “who knows this” culture (not auditable, not scalable).


Why it stays manual even in advanced orgs:
Expertise is latent and time-varying (people rotate, services evolve, ownership shifts).
Objectives conflict: speed vs interruption vs fairness vs compliance.
Trust is hard: if the system pages the wrong person at 3am, it loses legitimacy fast. DeepTriage explicitly calls out “gaining engineers’ trust” as a core challenge for automated triage at scale. arXiv
Interruptions are real operational load; Google’s SRE guidance treats pages/tickets/interrupts as a workload category that must be actively managed. Google SRE
On-call fatigue and pager fatigue are recognized failure modes; even “low priority alerts every hour” can induce fatigue and degrade response quality. USENIX
What AHDR sells (the product contract)
AHDR is not “insights about people.” It is decision ownership over a narrow set of allocation decisions.
The output is a structured, auditable decision object:
primary_assignee, backup_assignees[], confidence, constraints_satisfied[], evidence[], recommended_actions[], audit_trace_id
Evidence is not vibes; it is anchored to observable signals:
Similar incidents and who resolved them (transfer/triage signal). arXiv
Extracted entities/relations from incident text to ground “incident class” and stabilize retrieval (SoftNER). arXiv
Temporal expertise drift and long-tail contributors modeled via time slicing (IssueCourier). arXiv
Execution is bounded and reversible:
Assign, page, add backup, open channel, attach runbook, request missing fields.
Always supports human override and captures it as a training signal.
Initial ICP and wedge
ICP: software-heavy organizations with 24/7 reliability obligations and mature incident tooling.
Wedge use case: incident transfer reduction + faster mitigation
DeepTriage is direct validation that transfer assistance is feasible, valuable, and production-scalable, and that misassignment has multiplicative cost on mitigation time. arXiv
Why this wedge is better than recruiting as a first surface:
Dense feedback loops (resolution, transfers, reassignments) vs sparse hiring outcomes.
High frequency and high urgency create clear ROI.
Technical truth is measurable (MTTA/TTM/MTTR), not subjective.
Market map and competition
Status quo: “rules + rotations”
PagerDuty escalations/schedules route notifications reliably but do not learn org-specific capability beyond those constructs. support.pagerduty.com
ServiceNow assignment rules route records based on conditions at record open time; it’s deterministic and depends on stable taxonomies. ServiceNow


Adjacent tools (incident workflow/coordination):
They optimize communication and process, not “best human now” as a learning system (your differentiation is decision ownership + outcome learning).


The “platform risk” question (“why doesn’t PagerDuty just do it?”):
Platforms can add heuristics; what’s hard to ship is a capability model that is: (1) org-specific, (2) time-aware, (3) constraint-safe, (4) outcome-trained, and (5) auditable across political boundaries.
DeepTriage shows even inside Microsoft, this is non-trivial engineering with trust/scaling challenges. arXiv
Moat and defensibility (what compounds, what doesn’t)


The compounding asset is decision-grade outcome-labeled routing data:


context snapshot + candidate set + applied constraints + chosen assignee(s) + execution + outcome + transfers.


This dataset does not exist cleanly today and cannot be fully backfilled because availability, load, and human override reasons are time-local.


Structural moat: temporal, heterogeneous human-work graphs


SoftNER demonstrates production mining of incident knowledge graphs from incident reports, enabling structured signals and downstream models. arXiv


IssueCourier shows modeling multi-relational heterogeneous temporal graphs with time slicing improves assignment performance and addresses long-tail contributors and activity drift. arXiv


Trust moat: auditable decisions


Systems that can explain and be replayed win in high-stakes orgs; DeepTriage explicitly highlights trust as a primary deployment barrier. arXiv


Pricing (simple, defensible, aligned with value)


Don’t price per seat; price per decision surface and decision volume.


Suggested structure:


Platform fee (integrations, audit, policy engine, storage)


Volume fee (# decisions routed)


Premium for high-severity/high-regret decisions (Sev-1, security, compliance)


ROI narrative that survives scrutiny:


Reduce misassignment and transfers; avoid long-tail MTTR events; reduce paging waste and operational load. arXiv



Engineering
AHDR as a composable, constraint-safe, outcome-learning decision system.


Core framing (category theory → ontologies → reasoners → ranking)


Category theory as the mental model:


Systems are defined by objects and morphisms, and the critical property is composition (how transformations chain). The SEP entry describes categories via objects, morphisms, and composition. Stanford Encyclopedia of Philosophy


AHDR mapping:


Objects: Human, WorkItem, Service, Component, Constraint, Outcome


Morphisms: assigned_to, resolved_by, transferred_to, eligible_for, touched, co_worked


Composition: WorkItem → Human → Outcome is the thing you optimize and learn over time.


Ontologies: the meaning layer


OWL 2 is a formally defined ontology language designed to represent classes, properties, individuals, and enable reasoning. w3.org


Reasoners: hard-constraint enforcement


ELK is an OWL 2 EL reasoner, designed for scalable reasoning; it supports incremental updates where results can be updated by recomputing only what depends on changed axioms. Live Ontologies
Incremental reasoning literature (Kazakov & Klinov) motivates incremental approaches for frequent small ontology changes and shows efficiency for OWL EL incremental classification, which maps to “policies change, keep reasoning fast.” University of Ulm


Boundary rule (per your operating constraints):


Reasoners veto; they do not choose winners. Winners are chosen by ranking under constraints.



Requirements (what must be true)


Latency:


Decisions for paging/assignment must complete within tight budgets (sub-second to a few seconds depending on the surface).


Safety:


Hard constraints must never be violated (eligibility, on-call, separation-of-duties).


Auditability:


Every decision must be replayable from logged inputs, constraints, candidate set, and scores.


Learning:


Must improve on outcome metrics (transfer rate, MTTA/TTM/MTTR), not just generate plausible text.



Architecture (end-to-end)


Ingestion plane (event streams)


PagerDuty incident lifecycle: create/ack/reassign/resolve; reassignment can override escalation policy and notify selected targets. support.pagerduty.com


ServiceNow ticket/incident routing primitives: assignment rules set assigned_to and assignment_group based on conditions and run when opening a record. ServiceNow


Knowledge plane (truth maintenance)


Temporal heterogeneous graph store (people–work–systems–outcomes).


Vector index for similarity retrieval (work items, incident classes, human expertise embeddings).


Feature store for time-windowed aggregates (recency, success rate, load).


Decision plane (real-time)


Candidate generation (retrieve plausible assignees)


Constraint filtering (reasoner + policy engine)


Re-ranking (predict success / regret under context)


Execution (bounded actions)


Logging (immutable audit trace)


Feedback plane (learning loop)


Outcome collection: transfers, reassignments, mitigation time, reopen.


Policy updates: confidence calibration, weights, guardrails.


Data model (minimal ontology + maximal evidence)


Minimal entity set (stay disciplined):


Human, WorkItem, Service/Component, Constraint, Outcome


Canonical relations (time-stamped edges):


RESOLVED(h, w, t)


TRANSFERRED(w, from, to, t)


TOUCHED(h, component, t)


ONCALL(h, schedule, t)


CO_WORKED(h1, h2, w, t)


Why time matters:


Expertise and activity drift; IssueCourier explicitly addresses changes in developer activity and uses temporal slicing into time-based subgraphs to learn stage-specific patterns. arXiv


Smart partitioning (how to stay fast)


Goal: reason/rank on the smallest subgraph that is decision-relevant.


Partition strategy for incidents:


Incident → service → component → (similar incidents in last N days) → responders


Temporal slicing:


Maintain “hot” subgraphs per service over rolling windows; mirrors the principle used in IssueCourier’s time slicing. arXiv


Caching:


Cache candidate neighborhoods, embedding centroids for incident classes, and constraint-eligible sets per schedule.



Knowledge extraction (incident text → stable keys)


Problem: incident titles are noisy; “same class” looks different.


SoftNER approach (production validated):


Multi-task BiLSTM-CRF that uses semantic context plus data types to extract named entities, then mines relations to construct knowledge graphs; evaluated on months of incidents and deployed at Microsoft with high precision. arXiv


AHDR usage:


Entities become anchors for similarity retrieval (“incident class”), routing features, and explanations.


Routing model (what is scored, what is learned)


Baseline premise (validated by research):


Misassignment drives reroutes and delays; DeepTriage frames incorrect assignment as a major multiplier on mitigation time and treats trust and scaling as primary challenges. arXiv


Joint modeling of assignment + transfers:


UFTR explicitly models initial assignment and inter-group transfer jointly and shows interaction features matter. arXiv


Two-stage approach (production friendly):


Candidate generation: retrieve likely assignees via similarity + graph neighborhood


Constraint filtering: eliminate ineligible candidates


Re-ranking: score remaining candidates with interpretable features


Feature families (concrete):


Expertise: match incident entities/service to human history


Recency: time decay on relevant edges


Success: conditional probability of “resolve without transfer”


Availability/load: on-call now, pages in last 24h/7d, active incidents


Risk controls: penalize high interruption cost for low severity


Interpretable triage assistance with LLMs (bounded role):


Microsoft Research reports LLMs can provide accurate and interpretable incident triage and notes rule coverage limitations; LLMs are best used for structured explanation and feature extraction, not unconstrained decision authority. Microsoft

Constraint engine


OWL 2 provides the formally defined semantics for expressing policy/eligibility constraints. w3.org


OWL 2 EL + ELK gives tractable reasoning and incremental updates (critical when policies or role assignments change frequently). Live Ontologies


Practical pattern:


Generate candidates fast → apply reasoner as a veto filter → rank survivors → log constraints and explanations.


Learning loop


Logging contract (non-negotiable):


Work context snapshot, candidate set, constraints applied, scores, chosen assignee(s), execution actions, and outcome events (transfer/reassign/resolve times).


Training signals:


Positive: resolved quickly without transfer/reassign


Negative: transfer chain, repeated reassignments, long time-to-mitigate


Trust-first rollout:


Shadow mode first; DeepTriage highlights trust as a core adoption challenge, so you earn it with evidence and reversibility. arXiv



Evidence-first UX 
Never show global rankings.


Always show:


“For this work item, under these constraints, here’s the recommended assignee and evidence.”


Operational load rationale:


Google SRE explicitly frames pages/tickets as operational load; your UX should surface “interruption cost” and respect it. Google SRE
Evaluation 
Offline replay:


Top-k routing accuracy; transfer-aware evaluation (would the model reduce transfers given historical sequences)


UFTR’s framing makes transfer dynamics part of the evaluation, not an afterthought. arXiv


Online A/B:


Transfer rate per incident


MTTA / TTM / MTTR deltas


Reassignment frequency (PagerDuty reassignment events exist and are observable). support.pagerduty.com
Page volume / interruption budget proxies (pager fatigue literature motivates minimizing noisy pages). USENIX
References


DeepTriage (incident transfer assistance, 10× mitigation penalty for misassignment; deployed in Azure). arXiv


UFTR (joint modeling of assignment + transfer; interaction features matter). arXiv


SoftNER (incident text → knowledge graph; deployed at Microsoft; high precision reported). arXiv


IssueCourier (heterogeneous temporal graph + time slicing; improvements on issue assignment). arXiv


PagerDuty escalation policies/schedules and incident assignment/reassignment mechanics. support.pagerduty.com


ServiceNow assignment rules concept and incident assignment rule docs. ServiceNow


OWL 2 overview/primer (formally defined ontology language). w3.org


ELK reasoner and incremental reasoning references. SpringerLink


Category theory (objects, morphisms, composition) as a compositional semantics lens. Stanford Encyclopedia of Philosophy


Google SRE on-call and interrupts/overload framing. Google SRE


On-call/pager fatigue discussion and alert fatigue risks. USENIX


LLM incident triage interpretability work (bounded use in AHDR). Microsoft

Competitive Analysis
1. Category map (where everyone actually sits)
Axes
X-axis: Owns the assignment decision (left = no, right = yes)


Y-axis: Learns from outcomes over time (bottom = no, top = yes)
↑ Learns from outcomes
|
|          (empty)
|                 AHDR
|                   ●
|
|     DeepTriage (internal)
|         ●
|
|   FireHydrant / Rootly
|       ●
|
| PagerDuty / ServiceNow
|     ●
|
+--------------------------------→ Owns decision
    no ownership              full ownership


Product / System
Owns assignment decision
Learns from outcomes
Contextual (per incident)
Constraint-safe
Auditable
Politically safe
AHDR
YES
YES
YES
YES
YES
YES
PagerDuty
NO (escalation only)
NO
PARTIAL
YES
PARTIAL
YES
ServiceNow ITSM
NO (rules-based)
NO
PARTIAL
YES
YES
YES
FireHydrant
NO (workflow only)
NO
YES
PARTIAL
PARTIAL
YES
Rootly
NO
NO
YES
PARTIAL
PARTIAL
YES
OpsGenie
NO
NO
PARTIAL
YES
PARTIAL
YES
“AI Copilot for Ops” tools
NO
NO
YES
NO
NO
NO
Recruiting / Talent Graph tools
NO
WEAK
NO
NO
NO
NO

Key insight
AHDR expands by reusing the same decision engine.


Others expand by adding workflows or rules.
Repo plan for 5 people with zero dependencies until final wiring


Everyone works in their own directory and only shares contracts (types + OpenAPI) and docker-compose.


Integration happens in the last 2 hours by pointing env vars at service URLs.


Monorepo layout


/contracts/


types.ts (the only shared TS import)


openapi.yaml (optional, but keeps everyone aligned)


schemas/ (zod/json-schema copies if you want)


/services/ingest/ (Person 1)


/services/decision/ (Person 1)


/services/learner/ (Person 2)


/services/executor/ (Person 3)


/services/explain/ (Person 4)


/apps/ui/ (Person 5)


/infra/


docker-compose.yml


.env.example


/scripts/


seed_demo_data.ts


demo_fire_incident.sh


demo_replay.sh


Integration contracts (only these exist)


HTTP calls only (no shared DB, no message bus).


Every service includes:


GET /healthz


JSON logs


Zod validation


Correlation IDs:


x-correlation-id header is passed through every call.



Person assignments
Person 1 (Team lead + lead engineer): Ingest + Decision + audit + resilience
You give Person 1 the “real engineering” that makes it fundable:


deterministic candidate generation


constraint gating (veto-only)


scoring + confidence calibration


audit trace / replay


fallbacks and failure modes


Person 1 deliverables


/services/ingest


POST /webhooks/pagerduty (real webhook ingest)


POST /ingest/demo (demo incident injection)


GET /work-items


GET /work-items/:id


POST /work-items/:id/outcome (reassigned/resolved)


SQLite persistence: raw payload + normalized WorkItem + outcomes


/services/decision


POST /decide (work item → decision)


GET /decisions/:work_item_id


SQLite persistence: candidates, constraints per candidate, score breakdown, decision object


Calls:


learner GET /profiles?service=...


explain POST /explainDecision


executor POST /executeDecision


Person 1 “hard challenges” (explicit acceptance tests)


Deterministic candidate generation


Input: service, severity


Output: 3–10 candidates stable across runs (given same state)


Uses:


learner stats


optional GitHub committers (cached)


service→repo mapping config


Constraint filter (veto-only)


Enforces:


on-call required for sev1/sev2 (unless none exist)


interruption threshold veto


exclude incident creator if present


Must output constraint reasons for each filtered candidate


Score + confidence


score = weighted interpretable features


confidence = monotonic function of top1–top2 margin


Must log a score breakdown for audit


Failure modes


If GitHub fails, fall back to cached/seeded


If learner fails, fall back to local cached profiles


If zero candidates pass constraints, relax exactly one constraint and record that as a constraint failure in audit


Audit trace / replay


GET /audit/:work_item_id shows full decision reasoning inputs/outputs


Must be replayable: same inputs → same decision (except time-varying load)



Person 2: Learner (human canonical schema + outcome learning)


/services/learner


SQLite tables:


humans (identity/contact)


human_service_stats (fit_score, resolves, transfers, recency proxy)


human_load (pages_7d, active_items)


outcomes_dedupe (event_id)


Endpoints:


GET /profiles?service= → candidates + stats used in scoring


POST /outcomes → updates stats idempotently


GET /stats?human_id= → UI display


Seed tool:


scripts/seed_demo_data.ts generates realistic distributions (2–3 services, 8–12 humans)



Person 3: Executor (bounded agentic action)


/services/executor


POST /executeDecision


Slack post in channel (primary + backup mentions + evidence)


If Slack disabled: store “rendered message” in SQLite


Optional:


Slack interactive buttons:


“Wrong owner” (posts reassigned outcome to ingest)


“Resolved” (posts resolved outcome to ingest)


Must be safe:


no free-form text entry


only bounded actions



Person 4: Explain (deterministic evidence compiler)


/services/explain


POST /explainDecision


Input: WorkItem + candidate features + top2 margin + constraint results


Output:


5–7 evidence bullets (time-bound)


1–2 “why not next best”


constraints summary lines


Rules:


No hallucinated evidence


No global claims (“best engineer”)


Always contextual (“for this incident”)



Person 5: UI (evidence-first, reversible)


/apps/ui


Pages:


Work items list


Work item detail (decision, evidence, constraints, audit)


Actions:


override owner (posts reassigned outcome)


mark resolved (posts resolved outcome)


Anti-politics:


no global people pages


no search for experts


no ranking tables



Literal hour-by-hour checklist (Hour 0–24)
Hour 0–1 (All hands)


Person 1


Init repo, pnpm workspace, tsconfig base, eslint


Add /contracts/types.ts minimal types


Add /infra/docker-compose.yml skeleton services + ports


Person 2


PR: add learner-facing types (Profile, OutcomeEvent)


Person 3


PR: add executor request/response types


Person 4


PR: add explain request/response types


Person 5


UI skeleton PR with routes + API client placeholders


Hour 1–3 (Skeleton services)


Person 1


Scaffold ingest + decision services (Fastify + Zod + SQLite)


Add healthz + request logging + correlation id


Person 2


Scaffold learner service + SQLite schema


Person 3


Scaffold executor service + SQLite message table


Person 4


Scaffold explain service + deterministic stub


Person 5


Scaffold UI pages with mock data and empty states


Hour 3–6 (Ingest + Decision v0)


Person 1


Ingest: demo endpoint creates WorkItem + persists


Decision: accept WorkItem, call learner for candidates, return placeholder decision


Persist audit record


Person 2


Learner: GET /profiles?service= returns seeded humans


Implement seeding script


Person 3


Executor: accept decision, log message, persist rendered message


Person 4


Explain: produce evidence bullets from provided stats (no LLM)


Person 5


UI: list work items (calls ingest) and detail page (calls decision)


Hour 6–9 (Real candidate gen + scoring)


Person 1


Implement candidate generation using:


learner profiles


service_map.json


optional GitHub signals


Implement veto constraints + reasons per candidate


Implement scoring and confidence


Implement decision persistence endpoint


Person 2


Ensure learner returns all fields needed (resolves, transfers, pages_7d, active_items)


Person 3


Slack integration behind flag; fallback to DB logs


Person 4


Add “why not next best” and constraint summary lines


Person 5


Show constraints table + audit trace drawer


Hour 9–12 (Outcome loop)


Person 1


Ingest: POST /work-items/:id/outcome forwards to learner


Decision: incorporate fit_score into scoring


Person 2


Implement learning updates + dedupe by event_id


Expose GET /stats?human_id=


Person 3


If time: Slack interactive buttons → call ingest outcome endpoint


Person 4


Ensure evidence includes “learned from outcomes” language only when true


Person 5


UI: override workflow posts reassigned event, refreshes view, shows updated stats


Hour 12–15 (Hardening)


Person 1


Determinism check: same WorkItem replay yields same choice (unless load changed)


Implement fallback paths (learner down / github down)


Add /audit endpoint


Person 2


Improve seeding realism (make one “true owner” per service)


Person 3


Improve Slack formatting, include override link


Person 4


Make bullets extremely specific and time-scoped


Person 5


UI polish: evidence-first, no rankings, reversibility visible


Hour 15–18 (End-to-end integration test)


All


Docker-compose up, seed


Trigger demo incident


Verify decision appears + executor output + UI shows everything


Test override → learner stats update → re-run changes decision/confidence


Hour 18–20 (Demo rehearsal + failure demo)


Person 1


Prepare “GitHub down fallback still works” run


Person 3


Confirm Slack is working; have DB-log fallback ready


Person 5


Lock UI flow


Person 2


Prepare visible metric deltas for learning


Person 4


Make explanations crisp enough to read aloud


Hour 20–22 (Pitch packaging)


All


Write final demo script (below) into README


Add “judge Q&A” section


Freeze scope


Hour 22–24 (Final run + backup plan)


All


Full demo run-through twice


Backup: if Slack fails, show executor message logs in UI


Full README.md 
AHDR MVP: Decision-grade incident routing
AHDR assigns the best available human for a specific incident, with evidence and hard constraint checks, executes a bounded action (Slack notification), and learns from outcomes (override/reassign).


What you can do in this demo


Trigger an incident (demo endpoint or PagerDuty webhook)


See a decision (primary + backup + evidence + constraints)


Watch it execute (Slack message or executor log)


Override the decision


Watch the system update its fit stats and change confidence/assignee on replay


Inspect a full audit trace


Architecture


ingest → decision → explain → executor


ingest → learner (outcomes)


UI reads ingest + decision + learner


Run


cp infra/.env.example infra/.env


docker compose -f infra/docker-compose.yml up --build


seed:


pnpm seed (or node scripts/seed_demo_data.ts)


trigger incident:


bash scripts/demo_fire_incident.sh


open UI:


http://localhost:5173


Optional integrations
Recommended integration order 
PagerDuty (read-only → execute)


Ingest incidents


Recommend assignee


Post to Slack


Optional: reassign via API


Slack


Execution surface


Human acknowledgment


Override capture


Jira


Outcome tracking


Learning signals


Post-incident routing


GitHub


Evidence signals (commits, ownership)


ServiceNow


Enterprise expansion only after trust



What “first integrator” actually means for your product


You are not “integrating with PagerDuty”


You are:


Hooking into the assignment decision


Owning the most expensive mistake: wrong person paged


That is why PagerDuty is the correct first surface



One sentence you should reuse verbatim


“We don’t replace PagerDuty. We decide who PagerDuty should page.”

Slack:


set SLACK_ENABLED=true and token/channel in .env


PagerDuty webhook:


configure webhook to /webhooks/pagerduty


GitHub signals:


set GITHUB_ENABLED=true and token


Demo success criteria


Decision appears <2 seconds after incident ingest


Evidence-first explanation is shown


Override works and produces a learning update


Replay changes confidence or assignee


Audit trace is inspectable and coherent


Guardrails (non-negotiable)


No global rankings


No “expert search”


No free-form natural language


Decisions are contextual, reversible, and auditable


CURSOR_RULES.md (coding agent rules)
Scope rules


Work only in your directory:


P1: /services/ingest, /services/decision, /infra, /contracts


P2: /services/learner, /scripts/seed_demo_data.ts, /contracts


P3: /services/executor, /contracts


P4: /services/explain, /contracts


P5: /apps/ui, /contracts


Do not edit other people’s directories.


Contract rules


If you need fields changed:


open a PR updating /contracts/types.ts


All endpoints must match the contract.


Safety rules


No leaderboards, rankings, or people search.


Explanations must be contextual and time-bounded.


Reasoning must be derived from provided evidence only.


Reliability rules


Every service must:


expose /healthz


validate inputs with Zod


never fail the whole pipeline due to Slack/GitHub outage (fallback required)


Audit rules


Decision must store:


candidate set


filtered reasons


score breakdown


final choice


correlation id


Output rules


All logs structured JSON


Never log secrets


Hackathon demo script
0:00–0:20 Opening line


“Every incident tool can page someone. None can consistently page the right person. Wrong paging creates transfers and long mitigation.”


“AHDR is a decision OS that picks the best responder for this incident with evidence, executes the action, and learns when it’s wrong.”


0:20–0:45 Trigger incident live


Run bash scripts/demo_fire_incident.sh


Show ingest logs: “WorkItem created” with correlation id


0:45–1:30 Show decision + evidence (UI)


Open incident detail:


Primary + backup


Confidence


Evidence bullets (recent commits, past resolves, on-call, low load)


Constraints table


Say: “This is decision-grade: constraints veto, ranking chooses, audit makes it replayable.”


1:30–1:55 Show execution (Slack or executor log)


Show Slack message tagging primary/backup, with override link


If Slack fails: show executor message log in UI


Say: “We don’t replace PagerDuty. We sit above it and execute bounded actions.”


1:55–2:45 Show reversibility + learning loop


Click override in UI, choose different owner


System posts reassigned outcome


Show learner stats changed (fit down/up)


Replay incident (or press replay button)


Show confidence changed or assignee changes


Say: “This is the moat: outcome-labeled routing data. It compounds per customer.”


2:45–3:20 Show audit replay


Expand audit trace:


candidate set


filtered reasons


score breakdown


Say: “This is how you earn trust in ops: everything is explainable, time-bounded, and reversible.”


3:20–3:45 Close (funding hook)


“Incumbents orchestrate workflows; copilots summarize. We own the decision.”


“We start in shadow mode, then take ownership one surface at a time.”


“Same engine expands to ticket routing, security triage, approvals.”



Judge Q&A
“Isn’t this politically sensitive?”


“Yes, so we prohibit global rankings. Every output is scoped to a specific incident decision, reversible, and evidence-backed.”


“Why won’t PagerDuty build this?”


“They sell primitives for paging. We sell outcome ownership and compounding decision data per org.”


“What’s your north star?”


“Transfer reduction for incidents.”
1. Human Canonical Schema
Purpose: decide who can own work now, safely and fairly.
Why it exists


Humans are dynamic, political, and stateful.


You cannot rely on resumes, titles, or self-reported skills.


Decisions must be replayable without judging people globally.


Canonical fields


Identity


human_id


display_name


contact_handles (Slack, email, pager target)


Availability state (dynamic)


on_call_status


current_load


recent_interruptions


working_hours_window


Eligibility constraints (hard vetoes)


eligible_for(work_type, severity)


certifications


separation_of_duties_flags


Outcome history (ground truth)


resolved(work_item, time)


reassigned_from / reassigned_to


ack_latency


Derived contextual capability (ephemeral)


capability(service, time_window)


success_rate(context)


transfer_rate(context)


System interaction footprint


times_selected


times_overridden


Explicitly excluded


No global skill rankings


No personality traits


No seniority labels


Nothing screenshot-able or HR-usable


2. Work Item Canonical Schema
Purpose: define what decision is being made and bound context.
Why it exists


Decisions must be scoped.


Without this, you drift into global people judgments.


This is the “decision container.”


Canonical fields


work_item_id


type (incident, ticket, alert, request)


service / domain


severity / priority


description


created_at


origin_system


creator


constraints (explicit requirements)


links (PagerDuty, Jira, GitHub, etc.)


Key property


Every decision must reference exactly one Work Item.


No free-floating recommendations.


3. Decision Canonical Schema
Purpose: own responsibility for choosing and make it auditable.
Why it exists


Suggestions do not create learning.


Decisions create outcomes.


This is the core object the system is accountable for.


Canonical fields


decision_id


work_item_id


primary_human


backup_humans


confidence


constraints_checked[]


created_at


decision_version


Properties


Deterministic given the same inputs


Time-scoped


Reversible


4. Evidence Canonical Schema
Purpose: explain why this decision happened without hallucination.
Why it exists


Trust is earned via evidence, not model confidence.


Evidence must be local, factual, and bounded.


Canonical fields


evidence_id


decision_id


type


recent_resolution


recent_commit


on_call


load_state


similar_incident


source


time_window


weight


text


Rules


Evidence is derived, never asserted.


No evidence survives outside its decision context.


5. Constraint Canonical Schema
Purpose: prevent dangerous or invalid decisions.
Why it exists


Ranking alone is unsafe.


Constraints encode non-negotiables.


Canonical fields


constraint_id


name


applies_to (human, work_item, system)


passed


failure_reason


Examples


Not on call


Exceeds interruption threshold


Separation of duties violation


Certification missing


Critical rule


Constraints only veto.


They never rank.


6. Outcome Canonical Schema
Purpose: create the learning loop and the moat.
Why it exists


Without outcomes, the system is static.


This is where intelligence compounds.


Canonical fields


outcome_id


decision_id


type


resolved


reassigned


escalated


actor (human/system)


timestamp


notes (bounded, optional)


Properties


Idempotent


Append-only


Never rewritten


7. Audit Canonical Schema
Purpose: replay decisions and defend them later.
Why it exists


You must be able to answer:


“Why did this happen?”


“What would happen again?”


Especially in outages or postmortems.


Canonical fields


audit_id


decision_id


inputs_snapshot


candidate_set


filtered_candidates


score_breakdown


constraint_results


final_selection


correlation_id


8. Capability Projection Schema (derived, not stored long-term)
Purpose: temporarily estimate fitness without freezing it.
Why it exists


Capability is time-varying.


Storing it permanently creates politics.


Canonical fields


human_id


context


time_window


confidence_band


supporting_evidence_ids


Key rule


This schema expires.


It is recomputed, not trusted.


9. System State Canonical Schema
Purpose: prevent self-harm and runaway automation.
Why it exists


Systems must know their own limits.


Canonical fields


mode (shadow, advisory, execution)


error_rate


override_rate


confidence_calibration


last_manual_review


How these schemas fit together (important)
Work Item defines scope


Human schema defines eligibility and state


Decision binds them


Evidence justifies it


Constraints protect it


Outcomes teach it


Audit defends it


Capability projections enable ranking without permanence


System state governs autonomy


The one rule that ties everything together
No schema exists unless it directly participates in a decision.


No schema survives outside its context.


If you add a schema and cannot point to:
the decision it enables


the failure it prevents
you should delete it.
Canonical schemas are not about modeling reality.
 They are about making responsibility computable without destroying trust.
