# Repo-Truth Discovery

## Base

- Package: `WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01`
- Branch: `lab/gate-hardening-wfo-robustness-01`
- Base commit: `9e230d9f9152ddef5c022c3a1858592c5ffcacf5`
- PR #583 prerequisite observed on refreshed `main`: yes.
- Pre-existing local untracked path observed before package work: `build/`. It was left untouched.

## PR #583 Baseline Payload Contracts

Fact: the required files from `WP-LAB-BASELINE-PAYLOAD-DEFINE-01` are present:

- `docs/status_entries/WP-LAB-BASELINE-PAYLOAD-DEFINE-01.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_ground_truth_contract.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/non_promotable_provenance_contract.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/later_consumer_map.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/blocked_or_deferred_requirements.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/validation_summary.txt`

Fact: PR #583 defines three construction payloads: `known_losing_baseline`, `known_neutral_or_no_trade_baseline`, and `known_degenerate_or_invalid_baseline`.

Fact: every PR #583 baseline carries permanent construction-only semantics: `construction_payload=true`, `non_promotable=true`, `candidate_eligible=false`, `promotion_eligible=false`, `paper_live_eligible=false`, and `canonical_crossing_allowed=false`.

Decision: this package consumes those contracts directly and does not convert the baselines into Strategy Specs, Variant Manifests, Sweep Plans, candidates, result populations, or executable inputs.

## Existing WFO/OOS Surfaces

Fact: `docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md` already defines a non-canonical WFO/OOS gate artifact with `pass`, `fail`, `blocked`, and `advisory_only` decisions.

Fact: `docs/research_pipeline/2026-06-walkforward_oos_windowing_design.md` records future chronology, no-lookahead, denominator, purge/embargo, and deferred implementation expectations.

Fact: `tools/walkforward/run_walkforward_scratch.py` exists as a scratch-only helper that writes scratch reports and dashboard fragments. Its module declaration states it does not write Result Populations, trial-log rows, canonical fold manifests, or runtime/paper/live artifacts.

Fact: `tools/walkforward/purged_folds.py` can generate repo-native purged/embargoed scratch fold manifests.

Inference: WFO/OOS semantics can be hardened through docs and scratch contracts here without runner changes.

Decision: no WFO/OOS runner behavior is changed in this package.

## Existing Robustness / MC / PSR / DSR / MinTRL Surfaces

Fact: `docs/research/GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md` defines family-neutral robustness review reach, withheld statistic handling, and unavailable-stat reason codes for PSR, DSR, MinTRL, per-trade rows, OOS folds, and funding PnL.

Fact: `tools/robustness/` exists for bounded robustness diagnostics in prior packages, and existing robustness discovery records that missing per-trade rows and missing fold inputs are withheld rather than synthesized.

Fact: `lib/evaluation.py` and the historical trial log contain D2-006-style gate semantics, including DSR/trial-count discipline and a walk-forward efficiency gate, but `lib/` is protected from this package.

Inference: robustness/MC semantics can be hardened through docs and scratch contracts here without computing new MC, PSR, DSR, or MinTRL values.

Decision: no robustness computation, MC run, DSR/PSR/MinTRL implementation, or `lib/` change is performed in this package.

## Existing Candidate Gate / Review / Crossing Surfaces

Fact: `tools/candidate_lifecycle/` contains scratch-only lifecycle and fixture-only canonical crossing helpers. Their module documentation states they do not grant candidate authority, promotion, readiness, paper/live, runtime, capital, OMS, risk, broker, exchange, or protected-path authority.

Fact: `tools/lab_approval_queue/` provides read-only queue visibility for blocking stages, including validation, replay, OOS, robustness, and review.

Fact: `research/candidate_registry.jsonl` exists but is explicitly forbidden for this package.

Inference: construction baselines must be rejected before candidate eligibility and crossing, but implementing a crossing guard against these baselines would be a later package because PR #583 created no schema-valid executable baseline artifacts.

Decision: no candidate registry, candidate lifecycle, approval queue, or crossing implementation is changed here.

## Existing Lab-State / Dashboard / Reporting Surfaces

Fact: `docs/research/LAB_COORDINATOR_STATE_MODEL.md`, `tools/lab_state/`, `docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md`, `tools/lab_dashboard/`, `docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md`, and `tools/lab_reporting/` define read-only operator visibility surfaces.

Fact: `docs/research/LAB_COMPLETION_MAP.md` states the current lab phase is read-only/no-edge-search, identifies WFO/OOS and robustness as evaluation-rigor gates, and preserves no runtime or candidate-lifecycle authority.

Inference: the correct route is to add a standard gate contract that those future surfaces may cite, not to modify the current dashboards/reporting in this package.

Decision: no lab-state, dashboard, or reporting code/tests are changed here.

## Safe Helper/Test Surface Assessment

Fact: safe read-only helper surfaces exist, but PR #583 baselines are contract-only and not schema-valid executable artifacts.

Inference: asserting baseline gate expectations in code would either require inventing a fixture-artifact schema or changing candidate/gate/crossing consumers, both outside this package.

Decision: implementation is docs/scratch only, plus a docs/research standard contract. Code tests are not added.

## File Families Selected For Update

- `docs/research/LAB_STANDARD_CANDIDATE_GATES.md`
- `docs/status_entries/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01.md`
- `scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/**`

## File Families Intentionally Left Unchanged

- `research/result_populations/**`
- `research/candidate_registry.jsonl`
- `tools/research_runner/**`
- `tools/registry/**`
- `tools/walkforward/**`
- `tools/robustness/**`
- `tools/oos_gate/**`
- `tools/candidate_lifecycle/**`
- `tools/lab_state/**`
- `tools/lab_dashboard/**`
- `tools/lab_reporting/**`
- `tools/lab_approval_queue/**`
- `lib/**`
- `configs/**`
- `data/**`
- runtime, paper/live, OMS, risk, reconciliation, order, exchange, and broker paths

## Repo-Truth Adjustments

Fact: repo truth already has an OOS gate contract with a smaller decision enum (`pass`, `fail`, `blocked`, `advisory_only`).

Decision: this package does not mutate that historical contract. It adds a broader standard gate-outcome vocabulary for future candidate gates while preserving the older artifact's current meaning.

Fact: repo truth already has scratch WFO helpers. The package brief forbids strategy/backtest execution here.

Decision: no WFO helper is invoked, and no strategy execution is authorized here.

## Explicit No-Execution Statement

No strategy execution, backtest, sweep, MC run, canonical Result Population write, candidate lifecycle write, crossing, promotion, paper/live/runtime action, private provider/API access, or data acquisition is authorized or performed by this package.
