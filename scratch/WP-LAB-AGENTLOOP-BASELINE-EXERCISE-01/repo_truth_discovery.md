# WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01 Repo Truth Discovery

## Base

- Branch created from refreshed `main`.
- Base commit: `849da960a81c93381cf150a61ae2cf0278882e00`.
- Pre-existing local untracked path observed before package work: `build/`; left unchanged and unstaged.

## Prerequisite Artifacts Observed

- PR #583 baseline payload definition:
  - `docs/status_entries/WP-LAB-BASELINE-PAYLOAD-DEFINE-01.md`
  - `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json`
  - `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_ground_truth_contract.json`
  - `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/non_promotable_provenance_contract.md`
  - `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/later_consumer_map.md`
- PR #584 gate hardening:
  - `docs/status_entries/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01.md`
  - `docs/research/LAB_STANDARD_CANDIDATE_GATES.md`
  - `scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/gate_hardening_contract.json`
  - `scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/baseline_gate_expectations.json`
- PR #585 crossing guard:
  - `docs/status_entries/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01.md`
  - `docs/research/LAB_NONPROMOTABLE_CROSSING_GUARD.md`
  - `scratch/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01/guard_contract.json`
  - `scratch/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01/adversarial_fixture_matrix.json`
  - `scratch/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01/guard_validation_summary.json`
  - `tools/candidate_lifecycle/canonical_crossing_build.py`

## Existing Surfaces Inspected

- Agent/lab surfaces:
  - `tools/agent_sandbox/**`
  - `tools/agents/**`
  - `tools/lab_state/**`
  - `tools/lab_dashboard/**`
  - `tools/lab_reporting/**`
  - `tools/lab_approval_queue/**`
- Candidate lifecycle and review surfaces:
  - `tools/candidate_lifecycle/lifecycle_engine.py`
  - `tools/candidate_lifecycle/build_candidate_review_packet.py`
  - `tools/candidate_lifecycle/canonical_crossing_build.py`
- Focused tests:
  - `tests/test_agent_canonical_crossing_build.py`
  - `tests/test_candidate_lifecycle_engine.py`
  - `tests/test_agent_candidate_review_packet.py`
  - `tests/test_lab_dashboard.py`
  - `tests/test_lab_reporting.py`

## Safe Fixture Carrier

Fact: `tools/candidate_lifecycle/canonical_crossing_build.py` already contains the PR #585 non-promotable construction guard and rejects PR #583 baseline references with `reason_code=reject_by_construction`.

Fact: the helper's committed output prefix is scoped to `scratch/WP-AGENT-CANONICAL-CROSSING-BUILD-01/outputs/**`, not this package's scratch directory.

Decision: exercise the existing guard in a temporary fixture root and commit only package-local scratch/status evidence. This avoids writing non-package scratch outputs while still proving the merged guard behavior.

Selected route: acceptable route from the package brief. The fixture input consumes the PR #583 baseline catalog semantics and PR #584 gate expectations, then the PR #585 crossing guard is exercised against that fixture-only candidate-review packet.

## Files Intentionally Left Unchanged

- `research/candidate_registry.jsonl`
- `research/result_populations/**`
- `tools/research_runner/**`
- `tools/registry/**`
- `lib/**`
- `configs/**`
- `data/**`
- runtime, paper/live, OMS, risk, reconciliation, broker, exchange, and order paths
- `build/` pre-existing local untracked path

## Boundary Statement

No real strategy execution, real backtest, real sweep, real WFO/OOS, real robustness/MC compute, canonical Result Population write, candidate registry write, real crossing, promotion, readiness, paper/live/runtime action, private provider/API access, or protected-path change is authorized or performed by this package.
