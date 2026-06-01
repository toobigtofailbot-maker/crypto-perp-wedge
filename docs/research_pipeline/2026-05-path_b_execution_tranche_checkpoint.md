# Path B Execution Tranche Checkpoint

## 1. Scope

WP-S2c-131 / WP-12fk is a Tier 1 documentation-only tranche checkpoint.
It summarizes the Path B execution tranche and creates no implementation
authority.

This package creates only this checkpoint document and updates
`docs/project_status.md`.

## 2. Authorization basis

Main 4.0 authorized WP-S2c-131 directly after the H-012 decision package.

Post-tranche direction is intentionally not selected in this package.
Mandatory Main/Karl re-engagement occurs after merge.

## 3. Tranche package inventory

- WP-S2c-124 / WP-12fd opened the bounded Path B execution tranche under
  locked Option B and defined the one-candidate sequence.
- WP-S2c-125 / WP-12fe selected the initial design surface:
  `trend_following`, `15m`, `["ohlcv_15m", "funding_8h"]`.
- WP-S2c-126 / WP-12ff registered H-012, created its `HYPOTHESIS.md`, and
  created a scaffold-only `experiment.ipynb`.
- WP-S2c-127a / WP-12fg1 designed the pre-execution EXP integrity refinement
  after the first EXP-only attempt exposed a false positive.
- WP-S2c-127b / WP-12fg2 implemented bounded pre-execution
  EXP-without-REP integrity semantics.
- WP-S2c-127 retry / WP-12fg3 created `EXP-0012`.
- WP-S2c-128 / WP-12fh ran the H-012 baseline, appended the trial-log row,
  created `REP-0032`, and updated the notebook and registry evidence state.
- WP-S2c-129 / WP-12fi created `OL-0032` and `REC-0051`.
- WP-S2c-130 / WP-12fj created `DEC-0011` and concluded H-012 NO-GO.

## 4. H-012 artifact inventory

- Registry row: `research/candidate_registry.jsonl` entry for H-012.
- Hypothesis: `research/hypotheses/2026-05-29_H-012_15m-trend-following-funding-filtered/HYPOTHESIS.md`.
- Notebook: `research/hypotheses/2026-05-29_H-012_15m-trend-following-funding-filtered/experiment.ipynb`.
- EXP: `research/experiments/EXP-0012.plan.json`.
- REP: `research/experiments/REP-0032.report.json`.
- Trial-log row ID: `da2640a4-877b-4fcb-98f4-962d9ba1091d`.
- OL: `research/outcome_ledgers/OL-0032.outcome_ledger.json`.
- REC: `research/reconciliations/REC-0051.reconciliation.json`.
- DEC: `research/decisions/DEC-0011.md`.

## 5. H-012 final state

- `status`: `CONCLUDED`.
- `overall_verdict`: `NO-GO`.
- `pipeline_stage`: `baseline_tested`.
- `decision_record_path`: `research/decisions/DEC-0011.md`.
- `strategy_family`: `trend_following`.
- `timeframe`: `15m`.
- `information_inputs`: `["ohlcv_15m", "funding_8h"]`.
- `free_parameter_count`: `3`.

`ohlcv_15m` acceptance remained bounded convention application against the
locked 15m timeframe and data-catalog source, not taxonomy expansion.

## 6. H-012 result summary

Committed DEC/REP/OL/REC evidence records:

- REP-0032 verdict: `NO-GO`.
- D2-006 gates: 1/8 passed.
- Liquidation to zero equity.
- OOS Sharpe: `-0.8317508855081367`.
- Max drawdown: 100%.
- Final equity: `0.0`.
- REC-0051 verdict: `none_met`.

DEC-0011 records that the funding filter reduced trade count and negative trade
fraction slightly, but worsened Sharpe and liquidation timing versus the pure
15m Donchian comparator.

This is H-012-specific negative evidence. It is not a rejection of all 15m
designs or all funding-context designs.

## 7. Integrity refinement summary

WP-S2c-127a/b landed because the original EXP-only step exposed an old
`v_integrity_plan_report_pairs` false positive.

Current semantics allow bounded pre-execution EXP-without-REP only for known
`DRAFT` / `PENDING` / `pre_registered` candidates with no `trial_ids` and no
`decision_record_path`.

Broken-pair detection remains preserved. H-012 later moved beyond this state
through REP, OL, REC, and DEC artifacts.

## 8. REC-5 and inference posture

The exact H-012 segment is:

`H-012 / research_oos / post_wp_5b / d2_006_gates = 1`

REC-5 remains `n >= 3` per `candidate_id / outcome_kind / pipeline_version /
expectation_source_type`.

REC-5 is not satisfied for H-012. No cross-segment inference is allowed.
H-012 does not alter the prior WP-S2c-87 broad floor-crossing sufficiency state
for the original cohort because that applied to different segment counts.

## 9. Cross-candidate context

H-012 is the 11th concluded candidate. All 11 concluded candidates are NO-GO.

H-011 remains a reserved draft slot in current repo truth.

The Path B re-prime worked operationally: it registered, tested, reconciled,
and decided one candidate without drift. The result produced no go-signal.

## 10. Deferred items unchanged

- C-shape and F-shape remain DEFER per WP-S2c-123 and are not reopened here.
- Monitoring/dashboard remains deferred unless reauthorized.
- Paper bridge remains unauthorized; no shadow evidence accumulated.
- AUTO bridge remains frozen at WP-S2c-68.
- A2C-001/002 remain closed; A2C-003 remains unauthorized.
- Path B Option B remains locked; A/D/E remain rejected; C/F remain deferred.
- WP-S2c-100 locked criteria, D2-006, D2-007, REC-5, and Phase 9 Decision 9
  remain unchanged.
- WP-S2c-113 Scope 6 lock, WP-S2c-114 schemas, WP-S2c-115 validators,
  WP-S2c-117 query views, and WP-S2c-127b integrity refinement remain
  unchanged.
- SignalProvider Protocol remains unchanged.
- Permanent human gates remain absolute.

## 11. Post-tranche direction options surfaced, not selected

The following are surfaced for later Main/Karl routing only:

- Additional Path B candidate under locked Option B, using a materially
  different candidate surface inside locked taxonomy/timeframe discipline.
- Third cross-candidate diagnostic brief refresh including H-012 inventory.
- Monitoring/dashboard reauthorization design, if a concrete consumer and scope
  are supplied.
- Paper bridge reauthorization, only after required evidence and authorization;
  not near-term from the current H-012 result.
- Path B C-shape or F-shape reopening, still deferred and requiring explicit
  Main/Karl authorization.
- `docs/research_pipeline` index/navigation consolidation.
- Hold / no immediate execution.
- Other Main/Karl-directed option.

No option is selected by this checkpoint.

## 12. Non-claims

This checkpoint does not:

- select a post-tranche direction;
- recommend another candidate;
- rank or score candidates;
- declare readiness, transition, promotion, paper/live, runtime, policy, or
  protected-path authority;
- reopen any earlier package outcome;
- satisfy REC-5;
- support cross-segment inference;
- authorize another WP beyond report-back.

## 13. Boundary confirmations

This checkpoint changes no code, tests, schema, validator, query-view,
registry, trial-log, EXP, REP, OL, REC, DEC, `HYPOTHESIS.md`, notebook,
lifecycle/archive artifact, approval record, shadow evidence, runtime/protected
path, Tier 4, monitoring/dashboard, paper bridge, AUTO bridge, A2C-003, or
other canonical artifact.

It creates no readiness, transition, recommendation, ranking, scoring, or
human-gate execution.

## 14. Stop / report-back requirement

After merge, Side must stop and report to Main/Karl for post-tranche direction.

No further Path B execution package should be drafted without Main/Karl
direction. Main/Karl will route post-tranche direction from the checkpoint's
surfaced state.
