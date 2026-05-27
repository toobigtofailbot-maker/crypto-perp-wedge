# Phase 3 Architecture Design Opening

## 1. Scope

WP-S2c-88 / WP-12dw is a Tier 1 documentation-only architecture sketch
opening package.

This package opens the Phase 3 architecture sketch tranche as a design surface
only. It creates this document and updates `docs/project_status.md` only.

Validation profile: CS12 T1-doc-narrow.

This package does not authorize Phase 3 transition or implementation.

## 2. Repo-Truth Basis

Reference block:

- Refreshed `main` is at `bb0c5bf`, the PR #271 / WP-12dv merge commit.
- PR #271 / WP-12dv is merged.
- `docs/project_status.md` records WP-12dv / WP-S2c-87 as the latest
  branch-state before this package.
- No open PR was found touching `docs/project_status.md` or relevant
  `docs/research_pipeline` architecture files before this package branch was
  created.
- No remote or local WP-12dw / WP-S2c-88 branch or PR was found before this
  package branch was created.
- `docs/research_pipeline/2026-05-phase3_architecture_design_opening.md` did
  not exist before this package.
- `docs/research_pipeline/2026-05-broad_floor_crossing_sufficiency_decision.md`
  exists and records Karl/user's Yes decision that current selected
  closed-runway breadth is sufficient for Phase 3 transition gating
  consideration.
- The WP-S2c-83 through WP-S2c-86 broad-floor-crossing interpretation tranche
  documents exist and preserve the corrected 14/12/2 structural basis.
- A2C-001 is closed by
  `docs/research_pipeline/2026-05-a2c001_cohort_phase_closure_decision.md`.
- A2C-002 is closed by
  `docs/research_pipeline/2026-05-a2c002_cohort_phase_closure_decision.md`.
- Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge
  canonical-write-path work, approval/readiness/lifecycle, policy/scoring/
  ranking/recommendation, runtime, paper/live, exchange/broker/order contact,
  and downstream authority remain unauthorized.

## 3. Phase 3 Sketch Tranche Purpose

WP-S2c-87 recorded Yes sufficiency for Phase 3 transition gating
consideration. That decision is a gating-input decision only.

The purpose of this tranche is to sketch architecture questions and boundaries
for later review before any Phase 3 transition or implementation decision.

This opening package defines the design surface for:

- shadow deployment architecture;
- monitoring and dashboard architecture;
- paper-trading bridge architecture;
- live-trading boundary architecture;
- a tranche checkpoint and later decision surface.

No option is selected by this document.

## 4. Locked Inputs

### Phase 1 Paper Runtime Baseline

Phase 3 sketches must preserve the locked Phase 1 paper runtime and protected
execution-core posture:

- Paper trader / paper runtime remains the protected live/shadow execution
  path and is not converted into a research replay engine by this tranche.
- Paper ledger accounting remains protected.
- Overlay evaluator semantics remain bounded to `ALLOW`,
  `ALLOW_REDUCED(0.5)`, and `BLOCK`, with fail-open behavior preserved.
- OMS truth remains protected by the locked OMS state machine semantics.
- Reconciliation truth remains protected; reconciliation is the deterministic
  path for resolving exchange/internal uncertainty.
- Kill-switch and safe-mode semantics remain protected.
- D-0001 hard caps remain locked: risk per trade, daily/weekly loss,
  drawdown, turnover, leverage, margin reserve, and related execution policy
  caps are not changed.
- D2-008 overlay bounds remain locked: BLOCK gates only new entries and
  risk-increasing deltas; reductions remain allowed at full size.
- SignalProvider protocol and event-log schema are not modified by this
  package.

### Phase 2 Evidence Base

Phase 3 planning consumes the locked Phase 2 broad-floor-crossing sufficiency
basis:

- 12 selected closed-runway floor-crossed exact segments across six candidates
  are the sufficiency basis.
- 14 all-repo floor-crossed exact segments are structural context.
- 2 H-004 post-WP-5b Track F / historical exact segments are structural
  context only.
- H-004 pre-WP-5b and post-WP-5b rows remain separate by `pipeline_version`.
- The exact-segment key remains
  `candidate_id / outcome_kind / pipeline_version / expectation_source_type`.

### Methodology And Bridge Inputs

R1/R2 methodology and AUTO bridge state remain bounded:

- R1/R2 preserve exact-segment REC-5 discipline and do not create approval,
  readiness, lifecycle, policy, scoring, ranking, recommendation, runtime, or
  downstream authority.
- AUTO bridge implementation is local-only, in-memory, non-canonical,
  candidate-agnostic, and caller-driven.
- AUTO bridge file output, canonical write path, candidate binding, canonical
  evidence use, and further bridge work remain unauthorized.

## 5. Protected Boundaries

Tier 4 and protected execution-core boundaries are absolute for this tranche:

- No real-capital live trading.
- No exchange, broker, order, or execution contact.
- No autonomous deployment to live execution.
- No runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch,
  config, dependency, data, schema, validator, central query-layer, bridge
  code, bridge output, or protected-path modification.
- Permanent human gates remain locked for hypothesis approval, decision
  records, shadow promotion, live promotion, risk parameter changes, kill
  decisions, and novel strategy-family introduction.
- No agent, automation, dashboard, bridge, or sketch output becomes execution
  truth, risk truth, OMS truth, promotion authority, or downstream authority.

## 6. Open Architecture Questions

Later tranche packages may sketch these questions without selecting
implementation:

- What shadow deployment architecture can consume research evidence while
  preserving paper runtime, SignalProvider, overlay, OMS, reconciliation, and
  D-0001 boundaries?
- What monitoring and dashboard architecture can derive visibility from repo
  truth without creating a separate truth source?
- What paper-trading bridge architecture, if any, can be described without
  authorizing bridge code changes, file output, canonical write paths, or
  runtime contact?
- What live-trading boundary must be documented so no Phase 3 sketch implies
  real-capital trading, exchange/broker/order contact, or autonomous live
  deployment?
- What post-tranche implementation decision surface should be presented to
  Main/Karl/user after the sketches are complete?

## 7. Tranche Sequence

Authorized Phase 3 architecture sketch tranche sequence:

1. WP-S2c-89 shadow deployment sketch.
2. WP-S2c-90 monitoring/dashboard sketch.
3. WP-S2c-91 paper-trading bridge sketch.
4. WP-S2c-92 live-trading boundary sketch.
5. WP-S2c-93 tranche checkpoint.

Side may continue after merge to the next authorized sketch package under
refreshed-main preflight unless a stop trigger fires.

WP-S2c-93 will require T1-doc-major-decision profile with full pytest and Main
re-engagement.

## 8. Validation Profile

This package uses CS12 T1-doc-narrow validation because it modifies only
`docs/research_pipeline/` and `docs/project_status.md`, creates an opening
design record, and does not create a major decision-boundary checkpoint.

Required validation is execution validation only:

- exact changed-file scope;
- diff/scope summary against the two allowed files;
- research query view listing;
- all discovered `v_integrity_*` views with JSON output returning `[]`;
- registry validators;
- targeted research-query tests for outcome-ledger and reconciliation views.

No full pytest is required unless a stop trigger or validation-profile
ambiguity fires.

## 9. What Is Not Authorized

This package does not authorize:

- Phase 3 transition;
- Phase 3 implementation;
- selecting among Phase 3 architecture options;
- Path B;
- A2C-003;
- approval/readiness criteria;
- candidate approval, readiness, lifecycle completion, lifecycle transition,
  promotion, demotion, or archive action;
- policy, scoring, ranking, recommendation, or evidence-quality scoring;
- AUTO bridge further work, canonical-write-path design, file output,
  candidate binding, bridge-output promotion, or bridge effectiveness claims;
- runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch,
  exchange, broker, order, execution, config, dependency, data, schema,
  validator, central query-layer, bridge-code, bridge-output, or
  protected-path changes;
- D-0001 hard-cap changes;
- D2-006 promotion-gate changes;
- D2-007 shadow-mode changes;
- D2-008 overlay-bound changes;
- SignalProvider protocol modification;
- event-log schema modification;
- Tier 4 contact;
- canonical artifacts, trial-log rows, tests, or committed data changes;
- downstream authority.

## 10. Next Package Surface

The next package surface after merge is WP-S2c-89, the shadow deployment sketch,
or an authorized E10 bundle if explicitly chosen during drafting.

The next package must start from refreshed `main`, verify no competing
`docs/project_status.md` PR exists, verify current repo truth, and preserve all
protected boundaries unless a stop trigger fires.

## 11. Validation

Pre-edit verification confirmed:

- PR #271 / WP-12dv is merged at `bb0c5bf`.
- Refreshed `main` includes the WP-12dv merge.
- `docs/project_status.md` records WP-12dv / WP-S2c-87 as the latest
  branch-state before this package.
- No open PR was reported.
- No WP-12dw / WP-S2c-88 branch or PR existed before this package branch.
- This opening document did not exist before this package.
- The broad-floor-crossing sufficiency decision and interpretation tranche
  documents exist.
- A2C-001 and A2C-002 cohort phases are closed.
- Query verification confirmed 14 all-repo floor-crossed exact segments across
  six candidates.
- Query verification confirmed 12 selected closed-runway floor-crossed exact
  segments across six candidates.
- Query verification confirmed H-004 pre-WP-5b and post-WP-5b separation.
- `tests/test_research_query_experiment_views.py` is absent from current
  tracked repo truth and was not created.

Package validation results are recorded in the execution report-back and PR.
