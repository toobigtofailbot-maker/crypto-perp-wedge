# WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01 Repo Truth Discovery

## Fact

- Base commit: `63b5b1646bf1b2913491266c062e3ead9b2e818e`.
- Branch: `lab/crossing-nonpromotable-guard-01`.
- PR #583 artifacts observed:
  - `docs/status_entries/WP-LAB-BASELINE-PAYLOAD-DEFINE-01.md`
  - `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json`
  - `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_ground_truth_contract.json`
  - `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/non_promotable_provenance_contract.md`
- PR #584 artifacts observed:
  - `docs/status_entries/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01.md`
  - `docs/research/LAB_STANDARD_CANDIDATE_GATES.md`
  - `scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/gate_hardening_contract.json`
  - `scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/baseline_gate_expectations.json`
  - `scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/deferred_implementation_requirements.json`

## Candidate And Crossing Entry Points

Fact: `tools/candidate_lifecycle/lifecycle_engine.py` builds scratch-only lifecycle reports and review packets. It does not write canonical evidence, approve candidates, start paper/live execution, or create readiness authority.

Fact: `tools/candidate_lifecycle/canonical_crossing_build.py` is the current candidate-review packet crossing surface. It is fixture-only, uses `ToolContext`, writes only under `scratch/WP-AGENT-CANONICAL-CROSSING-BUILD-01/outputs/`, validates a fake registry copy, and explicitly creates no real candidate registry, promotion, readiness, paper/live, runtime, capital, OMS, risk, broker, exchange, credential, provider/API, or network authority.

Fact: `research/candidate_registry.jsonl` exists as canonical candidate registry truth and is forbidden for this package.

## Machinery Classification

Decision: current crossing/candidate machinery is mixed:

- `canonical_crossing_build.py` is fixture-only and safe to harden.
- `lifecycle_engine.py` is scratch-only lifecycle reporting and not the crossing action point.
- `research/candidate_registry.jsonl` and `research/result_populations/**` are canonical and left untouched.

## Selected Guard Location

Decision: the guard belongs in `tools/candidate_lifecycle/canonical_crossing_build.py`, before approval validation and before the `BUILD_FIXTURE_CANONICAL_CROSSING` action is authorized.

Inference: this is the narrowest repo-native location because it is the only existing fixture-safe crossing action point and already owns packet preflight, fake registry output, failure audit, and candidate-registry validator checks for fixture crossing outputs.

## Selected Test Location

Decision: adversarial tests belong in `tests/test_agent_canonical_crossing_build.py`, beside the existing fixture-only crossing tests.

## Files Intentionally Left Unchanged

- `research/candidate_registry.jsonl`
- `research/result_populations/**`
- `tools/research_runner/**`
- `tools/registry/**`
- `tools/lab_approval_queue/**`
- `lib/**`
- `configs/**`
- `data/**`
- paper/live/runtime, OMS, risk, reconciliation, broker, exchange, and order paths

## Explicit Non-Authority Statement

No real crossing or candidate lifecycle write is authorized by this package. No candidate is registered, promoted, ranked, readied, paper-traded, live-traded, or advanced toward operator GO semantics.

