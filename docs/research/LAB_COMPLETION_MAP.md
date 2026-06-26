# Research-Lab Completion Map

## Status and authority

This is the authoritative committed completion map for the research lab. It
records, for the current phase, what is **built and complete**, what is
**structurally present but inert / deferred-B**, what is **GO-gated execution-
machine work out of scope**, and the **exact boundaries** at which any of the
deferred work may be reauthorized.

This document is **descriptive only**. It executes nothing, runs or generates no
strategy, resumes no edge-search, writes no canonical or candidate-lifecycle
evidence, ranks or recommends nothing, and touches no runtime, paper/live, OMS,
risk, reconciliation, capital, broker, exchange, provider/API, or funding
accounting path. It introduces no new architecture decision. Its purpose is to
make the current phase state explicit so "finish the lab" cannot silently drift
into edge-search, execution-machine work, or speculative autonomous behavior.

## 1. Current phase definition

The current phase is a **human-driven, no-edge-search research lab**. Its job is
to make completed research **legible, auditable, and operator-reviewable** while
preserving locked evidence discipline and permanent human gates.

In this phase the lab:

- consumes already-produced research evidence and exposes it through read-only
  operator surfaces;
- enforces evaluation rigor (replay normalization, walk-forward / OOS gating,
  robustness review reach) on that evidence;
- records conclusions (including NO-GO) with full provenance;
- holds all autonomous behavior, strategy generation, candidate promotion, and
  runtime contact behind explicit separate authorization.

The phase does **not** include: generating new strategy hypotheses, resuming
edge-search, executing canonical crossing, promoting candidates, or any
paper/live/runtime execution. Those are out of phase by design, not by omission.

The conceptual target operating model (the "Side 12" target-state in
`docs/research_pipeline/2026-06-strategy_research_lab_target_operating_model.md`)
remains the long-horizon reference. Current project posture remains at autonomy
levels **L0 / L1** (manual design; assisted drafting) — L2 and above are not
authorized.

## 2. Built and complete (no-edge-search research-lab scope)

The following are built, merged, and complete for this phase.

### 2.1 Research engine and evidence primitives

- **Compiler / primitives and deterministic research runner** — the offline
  research runner and funding-percentile compiler semantics that produced the
  committed Result Populations (`tools/research_runner/`, compiler funding
  percentile semantics). Deterministic, offline, no runtime contact.
- **Result Populations and validators** — committed Result Population artifacts
  (`RP-2009`, `RP-7592`, `RP-2592`, …) with preserved denominators and integrity
  validators surfaced through the query layer.
- **Query layer** — `tools/research_query/` (`run.py`, `query_layer.py`,
  `views.sql`) exposing read-only views over candidates, experiments, gate
  results, outcome ledger, reconciliation, and integrity checks
  (`python -m tools.research_query.run --list-views`).
- **Replay-normalization contract** — family-agnostic Result Population replay
  comparison (`docs/research/RP_REPLAY_NORMALIZATION_CONTRACT.md`,
  `tools/research_replay`).

### 2.2 Evaluation-rigor gates

- **Walk-forward / OOS gate** — non-canonical walk-forward / out-of-sample gate
  contract with decisions `pass` / `fail` / `blocked` / `advisory_only`
  (`docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md`, `tools/oos_gate/`,
  `tools/walkforward/`). Holds no approval/promotion authority.
- **Robustness / candidate-review reach** — generic robustness review reach
  contract with `NO_GO_*` / `BLOCKED_*` reason codes and explicit withheld-
  statistic handling (`docs/research/GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md`,
  `tools/robustness`). Withholds PSR / DSR / MinTRL rather than fabricating them.

### 2.3 Research artifact / status model

- **Coordinator state model** — the canonical read-only state model that all
  operator surfaces consume so they read one status vocabulary
  (`docs/research/LAB_COORDINATOR_STATE_MODEL.md`, `tools/lab_state/`, PR #568).
  Introduces no new state names; resolver reads committed artifacts only.
- **Funding NO-GO conclusion** — `H-FUNDING-RATE-POSITIONING-FADE-01 = NO-GO`
  under the tested price-P&L funding-rate signal interpretation
  (`docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md`). All 36/36
  completed rows failed the 20% primary drawdown screen; scratch-only,
  non-canonical, no candidate registered, no crossing executed.

### 2.4 Operator-facing surfaces (all read-only)

- **Results dashboard** — read-only projection of the state model; shows the
  full denominator (not winners-only), evidence class, withheld statistics,
  NO-GO caveats, artifact drill-down (`docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md`,
  `tools/lab_dashboard/`, PR #569).
- **Daily brief / weekly report** — read-only shaping of the dashboard
  projection into operator-readable artifacts; descriptive-only; charting
  deferred (`docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md`,
  `tools/lab_reporting/`, PR #570).
- **Approval / gate queue** — read-only view of pending human gates, blocked
  validation states, and candidate-review readiness *only when evidence exists*;
  displays gates, does not execute them
  (`docs/research/LAB_APPROVAL_QUEUE_SURFACE.md`, `tools/lab_approval_queue/`,
  PR #572).
- **Scheduler shell (default-off / inert)** — control-plane structure (run
  queue, run-status / retry / block model, artifact-link model, dry-run planner)
  with **no executor**; the only output it can produce is a planned no-op
  (`docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md`,
  `tools/lab_scheduler_shell/`, PR #571).

`WP-LAB-OPERATOR-SURFACE-INTEGRATION-01` (#573) and
`WP-LAB-STATE-MODEL-COVERAGE-AUDIT-01` (#574) are merged. The follow-up
`WP-LAB-COVERAGE-GAP-CLOSE-01` binds the audit-discovered historical evidence
gaps into read-only coordinator/operator visibility: eight coordinator subjects,
107 covered coordinator artifacts, 103 surface-visible artifact references, and
zero unmapped gap artifacts. Candidate-ready remains zero and operator-gate
pending remains zero.

## 3. Inert / default-off surfaces (structurally present, not live)

These are committed and structurally complete but produce **no effect**:

- **Scheduler shell** — every autonomy flag (`autonomous_enabled`,
  `edge_search_enabled`, `run_triggering_enabled`, `notification_firing_enabled`,
  `candidate_lifecycle_writes_enabled`, `runtime_contact_enabled`,
  `paper_live_contact_enabled`) defaults `False`; there is no executor; the
  dry-run planner emits only `no_op` actions with `executed: false`.
- **Approval / gate queue** — displays gates and shows `nothing_candidate_ready`
  honestly; it cannot write an approval or execute a gate.

## 4. Deferred-B behaviors (deferred, with exact reason)

"Deferred-B" means the *structure* for the behavior is present or anticipated
but the behavior is **intentionally not live**. Each requires **separate
operator authorization and real candidate flow** before it could be activated.

| Deferred-B behavior | Why it is deferred |
| --- | --- |
| Autonomous scheduling / run triggering | Scheduler shell is default-off with no executor; turning runs on is an autonomy step that needs explicit operator authorization. |
| Research scout (idea sourcing automation) | Would generate/seek new hypotheses — that is edge-search, which is held. |
| Notification firing | Surfaces are descriptive; `notification_firing_enabled = false`. Firing requires authorization and a real event to fire on. |
| Approval-queue writes | Queue displays gates only; writing an approval is a human-gated lifecycle action it cannot grant. |
| Candidate lifecycle writes | The lifecycle engine exists but is human-gated; no candidate is registered, so there is nothing to write. |
| Coordinator transition execution | The state model is descriptive; executing a transition is owned by the human-gated candidate lifecycle engine, not the model. |
| First real canonical crossing | No candidate has passed human review; crossing is a separately authorized package and has not occurred. |
| Live candidate-flow-dependent behavior | All of the above depend on a real candidate reaching `candidate_ready_for_human_review`; the only committed conclusion to date is NO-GO, so no candidate flow exists yet. |

Activation of any deferred-B behavior **requires separate operator
authorization and real candidate flow**. This document does not grant it.

## 5. GO-gated execution-machine work (out of scope)

The following are **out of scope for the entire lab phase** and require an
explicit GO decision plus the locked execution-machine gates (D2-006, D2-007,
REC-5, Phase 9 / D2-011, Scope 6, permanent human gates):

- paper / shadow / live execution;
- runtime monitoring;
- the execution machine itself;
- broker / exchange / order paths;
- OMS / risk / reconciliation / capital management;
- safe-mode / kill-switch operational authority (governance boundary preserved;
  no operational authority is added by the lab).

None of these is buildable inside the current phase.

## 6. Edge-search hold

**No further edge-search is authorized.** Strategy generation / hypothesis
search remains held until separate operator authorization. The funding NO-GO is
a *conclusion about one tested interpretation*; it does **not** authorize another
edge-search cycle, and this map does not recommend resuming edge-search. New
data-derived families or funding variants require separate Main/operator
authorization.

## 7. What remains buildable now (within phase)

Without resuming edge-search or touching runtime, the in-phase buildable surface
is limited to further **read-only legibility and operator-ergonomics** work over
existing evidence, for example:

- read-only integration / index surfaces that unify the existing surfaces
  (e.g. the in-flight #573);
- read-only coverage / consistency audits over the state model (e.g. #574);
- documentation and traceability improvements.

All such work must remain read-only, deterministic, and non-authoritative.

## 8. What is not buildable without edge-search / live candidate flow

- Any new strategy hypothesis, family, variant, sweep, or backtest.
- Any candidate-flow-dependent surface behavior (real approval queue entries,
  candidate lifecycle writes, canonical crossing, transition execution).
- Autonomous scheduling/scout/notification behavior.

These cannot be built or demonstrated meaningfully because there is no
authorized edge-search and no live candidate flow.

## 9. What is not authorized

- Resuming edge-search or generating strategies.
- Mutating Strategy Specs, Variant Manifests, Sweep Plans, canonical Result
  Populations, trial logs, candidate registry, or candidate lifecycle records.
- Executing canonical crossing; writing approvals, promotions, or readiness
  declarations.
- Enabling autonomous scheduler / scout / coordinator behavior; firing
  notifications.
- Any paper / live / runtime / OMS / risk / reconciliation / capital / broker /
  exchange / order-path contact, or funding P&L / accounting change.

## 10. Definition of done — no-edge-search lab scope

The lab is "finished as intended" for this phase when:

1. Completed research evidence is legible through a coherent read-only state
   model and operator surfaces (dashboard, brief/report, approval queue). ✅
2. Evaluation rigor is enforced and honest: replay normalization, walk-forward /
   OOS gating, robustness review reach, with withheld statistics shown rather
   than fabricated. ✅
3. Conclusions (including the funding NO-GO) are recorded with full provenance
   and no candidate is fabricated. ✅
4. All autonomous / write / execution capability is structurally inert and
   default-off behind explicit authorization. ✅
5. This completion map exists and pins the phase boundaries. ✅

"Done" for this phase explicitly **excludes** generating new edges, promoting a
candidate, or running anything live. Those are future, separately authorized
phases, not unfinished business of this one.

## 11. Drift guardrails

- **No edge-search drift.** "Finish the lab" never means resume strategy
  generation or hypothesis search. A NO-GO conclusion does not authorize a new
  cycle.
- **No execution-machine drift.** Read-only surfaces never gain run / approve /
  promote / retry / scheduler-toggle controls. Deferred-B behaviors stay inert
  until separate operator authorization **and** real candidate flow exist.
- **No authority-by-existence.** No surface, fixture, manifest, scheduler entry,
  dashboard, or stored artifact infers authority from its own existence.
- **Read-only by default.** New in-phase work must be read-only, deterministic,
  and non-authoritative, and must preserve the protected boundaries (OMS, risk,
  reconciliation, kill-switch / safe-mode, Tier 4, `lib/` `src/` `configs/`
  `.claude/` `data/`, permanent human gates).
- **Human gates are permanent.** Any movement toward candidate promotion, R2S /
  S2P, paper/live, or runtime remains human-gated under existing locked gates.
