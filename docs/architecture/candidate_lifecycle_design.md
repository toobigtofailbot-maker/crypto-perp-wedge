# Candidate Lifecycle Design

## Status / Authority Boundary

`WP-CHASSIS-CANDIDATE-LIFECYCLE-DESIGN-01` is a docs-only architecture and
schema-design package.

This document designs a future candidate lifecycle chassis. It does not
implement the lifecycle, create or update a candidate registry row, register a
candidate, create candidate IDs, promote or demote a strategy, approve paper or
live execution, create schemas or validators, change query-layer behavior,
change Strategy Specs, Variant Manifests, Sweep Plans, result populations, or
touch runtime, paper/live, OMS, reconciliation, risk, safe-mode, broker,
exchange, order, config, data-acquisition, runner, compiler, catalog, or `lib/`
paths.

Candidate lifecycle records, if later implemented, would be evidence indexes
and human-review workflow records only. They would not be execution authority.

## Repo-Truth Basis

Current repo truth already separates upstream strategy design, variant planning,
canonical evidence, and downstream decision surfaces:

- Strategy Specs are future or current human-reviewable strategy descriptions,
  not candidate records and not execution authority.
- Variant Manifests and Sweep Plans define bounded research populations and
  execution plans when separately authorized.
- Result populations preserve complete sweep outcomes as evidence input or
  index artifacts, not decisions.
- EXP / REP, trial-log, OL / REC / DEC, and status documents remain the
  canonical evidence and decision chain where repo truth defines them.
- `research/candidate_registry.jsonl` exists as a structured candidate index in
  current repo truth, but this package does not edit it or create a successor
  registry artifact.
- Human gates, D2-006 / D2-007 style promotion discipline, Scope 6 / R2S
  review boundaries, and protected runtime boundaries remain governing
  constraints.

Fact: this document is only design text.

Inference: a future lifecycle model should reference immutable evidence rather
than duplicate metrics or reinterpret artifacts.

Decision in this package: the lifecycle chassis should be append-only,
human-gated, evidence-linked, and non-authoritative unless a later package
explicitly implements a bounded artifact path.

Open question: exact future storage path, schema name, validator, query views,
state enum spelling, and ID format remain deferred.

Future option: a later implementation package may translate this design into
schema-backed artifacts after Main/Karl authorization and protected-boundary
review.

## Design Goals

The lifecycle model should:

- record how a strategy design becomes eligible for human candidate review;
- preserve separation among Strategy Spec, variant population, evidence, and
  candidate status;
- require immutable evidence references for every state;
- make promotion, demotion, rejection, retirement, and exception decisions
  auditable;
- preserve failed, rejected, demoted, and retired candidates instead of hiding
  them;
- locate Monte Carlo and bootstrap robustness in the roadmap without making
  them a premature registration blocker;
- prevent any lifecycle record from becoming paper/live, capital, broker,
  exchange, runtime, OMS, reconciliation, or risk authority.

## Candidate Entity Concept

A future candidate record is a lifecycle index for a reviewed strategy family
and its evidence. It is not Strategy Spec storage, not a result population, not
an order-routing input, and not approval to trade.

Conceptual fields:

| Field group | Conceptual content | Boundary |
|---|---|---|
| Identity | `candidate_id`, display name, strategy family, market, instrument, primary timeframe, allowed confirmation timeframes | ID format and exact enum values are deferred; this package creates no IDs. |
| Source lineage | parent Strategy Spec refs, Variant Manifest refs, Sweep Plan refs, source design docs, approval notes | Registry does not store Strategy Spec content. |
| Canonical evidence | canonical result population refs, EXP / REP refs, trial-log refs, OL / REC / DEC refs, screen diagnostics | Links only; metrics remain in source artifacts. |
| Validation evidence | walk-forward / OOS refs, robustness refs, DSR / PSR / MinTRL refs, sensitivity refs, concentration/cost/funding/drawdown refs | Absence must be explicit rather than silently omitted. |
| Paper/shadow evidence | shadow logs, paper run summaries, parity checks, operational rehearsal evidence, exception records | Future-only; no paper/shadow authority is created here. |
| Status | lifecycle state, state effective timestamp, current gate, blocking reason, required next review | Status is descriptive until future implementation locks semantics. |
| Review metadata | owner, reviewer, Main/Karl gate owner, review due date, decision notes, unresolved questions | Human review stays explicit. |
| Audit/event history | append-only lifecycle event refs with timestamp, actor/gate, reason, evidence refs, non-authority declaration | Events cannot be deleted or rewritten except by future explicit correction protocol. |

Docs-only conceptual example:

```json
{
  "candidate_id": "<future_candidate_id>",
  "strategy_family": "<strategy_family>",
  "source_refs": {
    "strategy_spec": "<strategy_spec_ref>",
    "variant_manifest": "<variant_manifest_ref>",
    "sweep_plan": "<sweep_plan_ref>"
  },
  "evidence_refs": {
    "canonical_result_populations": ["<rp_ref>"],
    "walk_forward_oos": [],
    "robustness": [],
    "paper_shadow": []
  },
  "status": "<lifecycle_state>",
  "owner_review": {
    "owner": "<human_or_team>",
    "gate_owner": "Main/Karl"
  },
  "audit_events": ["<append_only_event_ref>"],
  "non_authority": "No paper/live/runtime/capital/exchange authority."
}
```

The example is illustrative only. It is not a schema, fixture, candidate record,
or implementation contract.

## Lifecycle States

State names are conceptual. A later package may rename or split them, but it
must preserve the evidence, gate, and non-authority intent.

| State | Entry criteria | Exit criteria | Allowed transitions | Forbidden transitions | Required evidence | Required gate owner |
|---|---|---|---|---|---|---|
| `proposed` | Human identifies a reviewed strategy design or lab output as worth candidate consideration. Source Strategy Spec / design refs exist or are explicitly pending. | Candidate has canonical research evidence or is rejected as insufficient. | `validated_research`, `rejected`, `retired` | `paper_candidate`, `paper_running`, `promoted_live` | Source design refs, scope note, unresolved questions, non-authority declaration | Main/Karl or delegated human reviewer |
| `validated_research` | Canonical trial screen and baseline research evidence are linked; full denominator and no-file-drawer posture are inspectable. | Walk-forward/OOS and robustness posture either pass future required criteria or fail. | `paper_candidate`, `rejected`, `retired`, `proposed` for clarification only | `paper_running`, `promoted_live` | RP refs, EXP/REP/trial-log refs where applicable, diagnostics, DSR/PSR/MinTRL posture if available | Main/Karl |
| `paper_candidate` | Research evidence, walk-forward/OOS evidence, robustness evidence, and Main/Karl review support paper/shadow qualification. | Paper/shadow package is separately authorized and started, or candidate is demoted/rejected/retired. | `paper_running`, `demoted`, `rejected`, `retired` | `promoted_live` without completed paper/shadow gate | Research evidence, walk-forward/OOS refs, robustness refs, Monte Carlo/bootstrap refs if required by future gate, paper/shadow approval record | Main/Karl, with protected-boundary review |
| `paper_running` | A separate package has authorized bounded paper/shadow observation and created the required operational evidence path. | Paper/shadow evidence completes, fails, expires, or triggers demotion/halt. | `promoted_live`, `demoted`, `rejected`, `retired`, `paper_candidate` | Direct runtime/live changes outside authorized gate | Paper/shadow logs, parity evidence, run summaries, exceptions, halt/demotion triggers | Main/Karl plus runtime/protected-boundary owner where applicable |
| `promoted_live` | Live gate is passed by explicit human decision under separately authorized package scope and protected runtime controls. | Live evidence triggers halt, demotion, retirement, or continued review. | `demoted`, `retired`, `paper_candidate` after halt, `rejected` if thesis invalidated | Any autonomous live promotion or risk change | Live approval record, paper/shadow evidence, risk/reconciliation review, operational readiness evidence | Main/Karl and runtime/risk owners |
| `rejected` | Evidence fails required criteria, source thesis is invalid, data is unavailable, overfit risk is unacceptable, or protected boundaries would be violated. | Only reopened by a future explicit exception/reconsideration event. | `proposed` by explicit reopen event, `retired` | `paper_candidate`, `paper_running`, `promoted_live` without new review | Rejection reason, failed evidence refs, denominator/trial context, no-deletion statement | Main/Karl or delegated rejection owner |
| `demoted` | Paper/live evidence, operational issue, risk breach, data integrity issue, or review decision removes a candidate from its higher state. | Candidate is routed to research/paper candidate status, rejected, retired, or reapproved by a later gate. | `validated_research`, `paper_candidate`, `rejected`, `retired` | `promoted_live` without new live gate | Demotion event, triggering evidence, halt status if applicable, remediation requirements | Main/Karl plus relevant protected-boundary owner |
| `retired` | Candidate is intentionally closed due to age, supersession, strategic irrelevance, duplicate status, or long-term non-use. | Only reopened by explicit future exception event. | `proposed` by explicit reopen event | `paper_candidate`, `paper_running`, `promoted_live` without full requalification | Retirement reason, preservation refs, superseding refs if any | Main/Karl or delegated lifecycle owner |

## Transition Model

All lifecycle transitions are stop-and-report by default. No state transition
auto-progresses unless a later package explicitly implements a bounded,
human-approved workflow for a specific transition. The live gate can never
auto-progress.

Conceptual transition rules:

| From | To | Required gate | Notes |
|---|---|---|---|
| `proposed` | `validated_research` | Canonical trial screen gate | Requires immutable research evidence and denominator honesty. |
| `proposed` | `rejected` | Source/research intake gate | Valid when source is unsupported, data is unavailable, or design violates boundaries. |
| `validated_research` | `paper_candidate` | Walk-forward/OOS and robustness gate | Must include Main/Karl review and required robustness artifacts. |
| `validated_research` | `rejected` | Research rejection gate | Evidence fails or cannot support further work. |
| `paper_candidate` | `paper_running` | Paper/shadow start gate | Requires separate paper/shadow authorization; this design does not grant it. |
| `paper_candidate` | `demoted` | Paper qualification failure gate | Candidate remains preserved with failure evidence. |
| `paper_running` | `promoted_live` | Live gate | Requires explicit live authorization and protected-boundary readiness. |
| `paper_running` | `demoted` | Paper/shadow demotion gate | Triggered by failed parity, operational issues, stale evidence, or risk concerns. |
| `promoted_live` | `demoted` | Halt/demotion gate | Live halt or demotion must preserve evidence and reason. |
| Any non-terminal state | `rejected` | Rejection gate | Rejection does not delete source evidence. |
| Any state | `retired` | Retirement gate | Retirement preserves history and may reference successor candidates. |
| Terminal state | `proposed` | Reopen/exception gate | Requires explicit override/exception event and fresh review scope. |

Forbidden transition principles:

- no direct `proposed` to `paper_candidate`, `paper_running`, or
  `promoted_live`;
- no direct `validated_research` to `paper_running` or `promoted_live`;
- no `paper_candidate` to `promoted_live` without paper/shadow completion and a
  live gate;
- no `rejected`, `demoted`, or `retired` candidate can be silently restored;
- no Strategy Spec approval, advisory ranking, result-population success flag,
  dashboard display, agent output, or high score can substitute for a lifecycle
  gate.

## Gate Model

Gate names are conceptual. Exact thresholds, formulas, and artifact schemas are
deferred unless current repo truth already defines them.

| Gate | Purpose | Evidence inputs | Required artifacts | Integrity / validator requirements | Main/Karl review | Auto-progress posture |
|---|---|---|---|---|---|---|
| Canonical trial screen | Determine whether canonical research evidence is even eligible for candidate review. | Strategy Spec / VM / Sweep Plan refs, RP refs, EXP/REP/trial-log refs, screen diagnostics, costs, drawdown, trade count, denominator. | Canonical RP or committed evidence equivalent, diagnostic/report, trial accounting refs. | Existing artifact validators and integrity views where applicable; no missing denominator; no hidden failed variants. | Required. | Stop/report only. |
| Walk-forward / OOS survival | Test chronology-aware survival after selection decisions. | Windowed OOS results, fold definitions, selection/evaluation boundaries, gap posture, costs, drawdown, trade count. | Future window manifest/results or equivalent committed report. | Chronology/no-lookahead checks, denominator reconciliation, data lineage and gap checks. | Required. | Stop/report only. |
| Robustness / anti-overfit | Test whether evidence survives multiple-testing, sensitivity, concentration, and robustness review. | DSR / PSR / MinTRL outputs, sensitivity surfaces, full-population failure accounting, cost/funding/slippage stress, concentration diagnostics. | Robustness report or equivalent committed diagnostic. | Formula input completeness checks; full-population lineage; no winner-only review. | Required. | Stop/report only. |
| Monte Carlo / bootstrap | Estimate path, drawdown, loss, ruin, return-interval, and Sharpe uncertainty after initial GO evidence. | Trade-level returns or bar-level equity/return series, sample length, drawdown path, cost/fill assumptions, trial count / selection count. | Monte Carlo/bootstrap report if required by future package. | Reproducible seed/protocol, source-return identity, sample-size disclosure, cost/fill assumption disclosure. | Required before paper or live if future gate locks it; otherwise report as unavailable/deferred. | Stop/report only. |
| Paper/shadow qualification | Decide whether a research candidate may enter bounded paper/shadow observation. | Research gate results, walk-forward/OOS, robustness, Monte Carlo/bootstrap if required, operational assumptions, parity plan. | Paper/shadow approval record and future operational evidence plan. | Protected-boundary review; no runtime behavior change unless separately authorized. | Required. | Stop/report only. |
| Live gate | Decide whether a paper-running candidate can be considered for live promotion. | Paper/shadow logs, parity checks, operational rehearsal, halt/demotion tests, risk/reconciliation evidence, unresolved exceptions. | Live approval record under separate package, readiness packet, rollback/halt plan. | Strongest applicable runtime/protected-path validation under future explicit scope. | Required; cannot be delegated to automation. | Never auto-progress. |

Gate failures must create lifecycle evidence. A failed gate should preserve the
candidate, source artifacts, denominator, exact failure reason, and future
reconsideration conditions if any.

## Evidence Link Requirements

Every lifecycle state must point to immutable evidence appropriate to that
state. The candidate record should link evidence; it should not copy source
metrics as a parallel truth store.

Required or conditionally required evidence families:

- RP IDs and result-population identity hashes where result populations exist;
- screen diagnostics and canonical trial-screen verdicts;
- EXP / REP refs and trial-log refs where current repo truth uses them;
- walk-forward / OOS results and window definitions when available;
- robustness reports, sensitivity diagnostics, and denominator accounting;
- DSR / PSR / MinTRL outputs or explicit unavailable/deferred reason;
- Monte Carlo/bootstrap reports where applicable;
- paper/shadow logs, parity reports, run summaries, halt events, and exception
  records when later paper/shadow evidence exists;
- live approval, halt, demotion, and retirement evidence only if a later live
  path is separately authorized.

No evidence link may imply execution authority. A link means "review this
artifact"; it does not mean "trade this strategy".

## Demotion, Rejection, Halt, and Retirement Logic

Reject a candidate when:

- canonical trial evidence fails required criteria;
- walk-forward/OOS survival fails;
- robustness, DSR / PSR / MinTRL, sensitivity, concentration, cost, drawdown,
  or sample-size evidence is insufficient;
- Monte Carlo/bootstrap evidence, when required, shows unacceptable path risk,
  loss probability, ruin probability, or uncertainty;
- source thesis is invalidated;
- required data is unavailable or unauthorized;
- protected-boundary compliance would require unauthorized runtime, paper/live,
  OMS, reconciliation, risk, safe-mode, broker, exchange, or order changes;
- evidence is stale and not supportable under current repo truth.

Demote a paper or live candidate when:

- paper/shadow/live evidence diverges materially from expected behavior;
- parity, reconciliation, operational, or data-quality checks fail;
- runtime/risk/protected-boundary owners require halt or review;
- drawdown, cost, slippage, funding, exposure, concentration, or trade-quality
  evidence violates a later locked threshold;
- upstream research evidence is invalidated by data lineage, schema, or
  methodology correction;
- candidate assumptions are superseded and require requalification.

Live halt or demotion must:

- preserve all evidence and event history;
- identify whether trading is halted, reduced, or routed to paper/research
  review under future authorized procedures;
- avoid deleting or rewriting prior approval evidence;
- avoid silent rollback to a higher-authority state.

No deletion / no file-drawer rule:

- rejected, demoted, failed, retired, duplicate, and superseded candidates stay
  visible;
- failed gates remain linked;
- reopening requires an append-only exception event;
- replacement candidates must link to predecessor evidence instead of hiding
  it.

## Append-Only Audit Trail

A future lifecycle audit trail should be append-only. It may be embedded as
event refs in a candidate record or stored as a separate event log if later
authorized.

Conceptual event types:

- `proposed`;
- `validated`;
- `paper_candidate_approved`;
- `paper_started`;
- `paper_completed`;
- `promoted`;
- `rejected`;
- `demoted`;
- `retired`;
- `override_exception`.

Every event should include:

| Field | Purpose |
|---|---|
| `timestamp_utc` | When the event was recorded. |
| `actor` | Human, role, or explicitly authorized process recording the event. |
| `gate` | Gate or review step responsible for the transition. |
| `from_status` / `to_status` | Prior and resulting conceptual state. |
| `reason` | Short, reviewable reason. |
| `related_artifact_refs` | Immutable evidence refs that justify or contextualize the event. |
| `blocking_or_exception_refs` | Open blockers or exception approvals if applicable. |
| `non_authority` | Required declaration that the event does not create execution authority unless a separately authorized protected-path package says so. |

Docs-only conceptual example:

```json
{
  "event_type": "paper_candidate_approved",
  "timestamp_utc": "<timestamp>",
  "actor": "Main/Karl",
  "gate": "paper_shadow_qualification",
  "from_status": "validated_research",
  "to_status": "paper_candidate",
  "reason": "<human_review_reason>",
  "related_artifact_refs": ["<rp_ref>", "<walk_forward_ref>", "<robustness_ref>"],
  "non_authority": "Approval for candidate lifecycle state only; no runtime, paper/live, capital, broker, exchange, OMS, or risk authority."
}
```

The example is illustrative only and creates no event schema or event instance.

## Monte Carlo / Bootstrap Placement

Monte Carlo and bootstrap robustness are not required before candidate
registration unless Main/Karl later decide otherwise for a specific package or
candidate class.

Recommended roadmap placement:

1. Use canonical trial screen evidence to determine whether a strategy has
   enough initial merit to continue.
2. Use walk-forward/OOS testing and DSR / PSR / MinTRL style diagnostics to
   test chronology and statistical credibility.
3. Use Monte Carlo/bootstrap before paper promotion or before live promotion,
   depending on the future gate lock and available source data.
4. Preserve Monte Carlo/bootstrap reports as evidence links; do not turn them
   into automatic paper/live approval.

Inputs should include:

- trade-level returns or bar-level equity/return series;
- source result-population or report identity;
- sample length and trade count;
- drawdown path and time-under-water context;
- fees, funding, slippage, fill, and liquidation assumptions;
- candidate selection count and trial count;
- regime labels or window labels if available;
- random seed and resampling protocol if stochastic.

Outputs should include:

- drawdown distribution;
- probability-of-loss and risk-of-ruin estimates;
- bootstrap return confidence interval;
- Sharpe uncertainty;
- path-dependence stress;
- regime-resampled performance if available;
- caveats for sample size, dependency, serial correlation, and cost/fill
  assumptions.

Monte Carlo/bootstrap can strengthen or block a paper/live review. It cannot
create paper/live authority, live promotion, risk changes, or runtime behavior.

## Non-Authority Boundaries

This design explicitly does not:

- implement a lifecycle artifact, schema, validator, query view, dashboard, or
  workflow;
- create or edit a real candidate registry file;
- register any candidate;
- create candidate IDs;
- approve, promote, demote, reject, retire, or reopen any real strategy;
- approve paper, shadow, or live trading;
- create capital, collateral, broker, exchange, order, OMS, reconciliation,
  risk, safe-mode, kill-switch, or runtime authority;
- change Strategy Specs, Variant Manifests, Sweep Plans, result populations,
  data, compiler, runner, query, catalog, schema, validator, config, or `lib/`
  behavior;
- treat result-population success, advisory ranking, agent output, dashboard
  display, or score as lifecycle authority;
- weaken human gates or protected runtime boundaries.

## Future Implementation Package Shape

A safe future sequence would likely split work into narrow packages:

1. docs-only lifecycle decision lock with exact state names, gate names, and
   owner responsibilities;
2. schema/validator design for a lifecycle record and append-only event trail;
3. optional artifact implementation with fixtures that do not register real
   candidates;
4. migration/backfill design for existing candidate registry rows, if needed;
5. read-only query/integrity surfaces after schema-backed artifacts exist;
6. separate paper/shadow/live gate packages only if Main/Karl explicitly
   authorize protected-boundary work.

Each package must start from refreshed repo truth, inspect actual changed
files, validate exact scope, and stop on protected-boundary conflict.
