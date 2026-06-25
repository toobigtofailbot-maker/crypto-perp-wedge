# WP-LAB-COORDINATOR-STATE-MODEL-01 — Read-only lab coordinator state model

## Package

- Package: `WP-LAB-COORDINATOR-STATE-MODEL-01`
- Decision: `COMPLETE`
- Package class: research-lab operator/control-plane foundation.
- Execution mode: repo-first, fresh isolated worktree, read-only state model,
  no edge-search.

## Branch / Base

- Branch: `lab/coordinator-state-model-01`.
- Base: `origin/main` after PRs #564, #565, #566, #567 (worktree HEAD at merge of
  PR #565 `1bca3ce`, which already contains #564/#566/#567).

## Objective

Define the canonical read-only research-lab coordinator state model that all
operator surfaces consume, spanning idea intake, formalization, experiment run,
replay normalization, walk-forward/OOS gate, robustness, candidate-review reach,
reporting, and operator gate. The model creates a shared status vocabulary and a
read-only resolver over existing repo/scratch artifacts. It executes no
transition.

## Repo-Truth Discovery

Recorded in
`scratch/WP-LAB-COORDINATOR-STATE-MODEL-01/repo_truth_discovery.md`. Key finding:
the lab already defines per-stage vocabularies (replay normalization #565, OOS
`gate_decision` enum #567, generic robustness review reach output fields and
reason-code families #566, candidate lifecycle human-gated states). The model
composes these into one vocabulary and introduces **no new status names**.

## Delivered

- `docs/research/LAB_COORDINATOR_STATE_MODEL.md` — canonical contract.
- `docs/status_entries/WP-LAB-COORDINATOR-STATE-MODEL-01.md` — this entry.
- `tools/lab_state/model.py` — read-only state vocabulary, stages, reason codes,
  OOS-decision mapping, non-authority declaration, edge-search hold.
- `tools/lab_state/resolver.py` — read-only per-stage resolvers, artifact
  reference model, fail-closed missing-artifact handling, overall-state
  precedence, snapshot assembly.
- `tools/lab_state/run.py` — CLI that prints a static lab state snapshot.
- `tools/lab_state/__init__.py`.
- `tests/test_lab_state_model.py`, `tests/test_lab_state_resolver.py` — 15 tests.
- `scratch/WP-LAB-COORDINATOR-STATE-MODEL-01/repo_truth_discovery.md`
- `scratch/WP-LAB-COORDINATOR-STATE-MODEL-01/state_model_contract.json`
- `scratch/WP-LAB-COORDINATOR-STATE-MODEL-01/state_snapshot_fixture.json`
- `scratch/WP-LAB-COORDINATOR-STATE-MODEL-01/validation_summary.txt`
- `scratch/WP-LAB-COORDINATOR-STATE-MODEL-01/main_report_back_guardrail.txt`

## State Fixture

The committed snapshot fixture binds the funding NO-GO / replay / OOS /
robustness scratch artifacts end-to-end for
`H-FUNDING-RATE-POSITIONING-FADE-01`: `formalized` → `experiment_complete` →
`replay_checked` → `oos_gate_blocked` (dry-run-only) → `robustness_advisory` →
`candidate_review_not_created` (`NO_GO_PRIMARY_RISK_SCREEN_FAILED`) → `reported`
→ operator gate not pending; overall `no_go`. A second subject exercises
`oos_gate_fail` from the OOS gate fixture (`RP-2592`).

## Edge-Search Hold

No further edge-search is authorized by the coordinator state model. Strategy
generation/search remains held until separate operator authorization.

## Boundary Summary

- No transition executed; descriptive read-only model only.
- No strategy run/generation, no edge-search, no backtest (resolver reads
  committed JSON/markdown only).
- No Strategy Spec, Variant Manifest, Sweep Plan, canonical Result Population,
  trial log, candidate registry, or candidate lifecycle write.
- No canonical crossing, approval, or promotion.
- No runtime, paper/live, OMS, risk, reconciliation, capital, broker, exchange,
  provider/API/network, funding accounting, scheduler/scout/coordinator
  autonomy, dashboard execution control, or large tracked data change.

## Validation

Recorded in `scratch/WP-LAB-COORDINATOR-STATE-MODEL-01/validation_summary.txt`.
Package-required checks passed: scoped pytest (15 passed), research query
`--list-views`, diff scope summary (in-scope after reverting a harness-added
local settings line), and `git diff --check`. Conditional registry validators
(`validate_result_populations`, `validate_candidate_registry`) also passed. Full
repo pytest was not run to completion and is not claimed as passed; the new code
is stdlib-only and its targeted suite passes.

## Merge Status

Ready for review after push.
