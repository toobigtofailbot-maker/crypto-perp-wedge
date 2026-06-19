# EXT-WORKFLOW-HYPEROPT-PILOT-01 - Repo-Native Workflow Hyperopt Pilot

## Branch / PR

- Branch: `ext/workflow-hyperopt-pilot-01`
- PR: pending

## Package Class

External-adoption pilot / workflow ergonomics / research-lab artifact
authoring acceleration.

## Precondition

- `EXT-ROBUSTNESS-MC-PILOT-01` / PR #511 is merged on refreshed `main`.
- Verification evidence: `git log --oneline --grep="EXT-ROBUSTNESS-MC-PILOT-01" -n 10`
  returned merge commit `842e751` for PR #511.
- Branch started from refreshed `main` after `git pull --ff-only origin main`.

## Scope Summary

This package adds a standard-library-only generator that converts an explicit
repo-native parameter-space JSON file into scratch-only, schema-shaped Strategy
Spec snapshot, Variant Manifest, and Sweep Plan artifacts. The generated VM and
Sweep artifacts are validated through the existing repo validators using
caller-supplied scratch directories, so the pilot demonstrates large-grid
authoring without mutating canonical Strategy Specs, Variant Manifests, Sweep
Plans, Result Populations, trial logs, runner behavior, or runtime paths.

The pilot source-extracts only broad concepts: deterministic finite parameter
spaces from hyperopt-style workflows and experiment grouping/indexing from
experiment-tracking workflows. It does not inspect, vendor, install, or invoke
Freqtrade, Qlib, or any external runtime tool.

## Changed Files

- `tools/external_pilots/workflow_hyperopt_pilot.py`
- `tests/test_external_workflow_hyperopt_pilot.py`
- `docs/status_entries/EXT-WORKFLOW-HYPEROPT-PILOT-01.md`
- `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/parameter_space.json`
- `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_strategy_specs/STRAT-SPEC-9001.strategy_spec.json`
- `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_variant_manifests/VM-9001.variant_manifest.json`
- `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_sweep_plans/SWEEP-PLAN-9001.sweep_plan.json`
- `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/workflow_hyperopt_report.json`
- `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/workflow_hyperopt_report.md`
- `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_artifacts.sha256`

## Generated Demo

- Source Strategy Spec anchor:
  `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- Parameter-space input:
  `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/parameter_space.json`
- Generated scratch Strategy Spec snapshot:
  `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_strategy_specs/STRAT-SPEC-9001.strategy_spec.json`
- Generated scratch Variant Manifest:
  `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_variant_manifests/VM-9001.variant_manifest.json`
- Generated scratch Sweep Plan:
  `scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_sweep_plans/SWEEP-PLAN-9001.sweep_plan.json`
- Variant count: `150`
- Ordering: explicit `axis_order`, then deterministic Cartesian product
  left-to-right.
- Seed: none; the grid is deterministic and not random.
- Deterministic artifact checksum:
  `sha256:53d157b29821c086eaab477bc5205920a42b1f2959d686969cede3bd76a93ea2`
- Report output checksum:
  `sha256:054cf0109bb7da55a63dab852161848bbe0f28aa5e8e7bf696990b25209bf1d1`

Artifact checksums:

| artifact | checksum |
|---|---|
| parameter-space input | `sha256:0a1d9b70fed66c7769367c77fce902e3efbddc5d3c7226dd7c54c451f6fbac5b` |
| scratch Strategy Spec snapshot | `sha256:8a5a53309ea48e35e20aafb8ae739219b0f6bd458381a3ccf9e888b234a6ade5` |
| scratch Variant Manifest | `sha256:1e82471dab2c95ba762ab99ef595d9d075fab09a1c29ae76ace6d689d9c22aa4` |
| scratch Sweep Plan | `sha256:f4597df363c13b3ba80b7033e2326660e9a9919c3cb27db1714305c34fde0a9c` |

## Validator Authority

- Strategy Spec validator command:
  `python -m tools.registry.validate_strategy_specs --strategy-specs-dir scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_strategy_specs`
- VM/Sweep validator command:
  `python -m tools.registry.validate_variant_sweep_artifacts --variant-manifests-dir scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_variant_manifests --sweep-plans-dir scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_sweep_plans --strategy-specs-dir scratch/EXT-WORKFLOW-HYPEROPT-PILOT-01/generated_strategy_specs`
- Generated artifacts pass validators: `YES`.
- Validator authority remains repo-owned; generator output alone is not treated
  as sufficient.

## Validation Summary

- `.\.venv\Scripts\python.exe -m pytest tests/test_external_workflow_hyperopt_pilot.py -q`:
  `PASS`, 11 passed.
- `.\.venv\Scripts\python.exe -m tools.external_pilots.workflow_hyperopt_pilot`:
  `PASS`; generated 150 variants, validator booleans true.
- `.\.venv\Scripts\python.exe -m tools.registry.validate_strategy_specs --strategy-specs-dir scratch\EXT-WORKFLOW-HYPEROPT-PILOT-01\generated_strategy_specs`:
  `PASS`.
- `.\.venv\Scripts\python.exe -m tools.registry.validate_variant_sweep_artifacts --variant-manifests-dir scratch\EXT-WORKFLOW-HYPEROPT-PILOT-01\generated_variant_manifests --sweep-plans-dir scratch\EXT-WORKFLOW-HYPEROPT-PILOT-01\generated_sweep_plans --strategy-specs-dir scratch\EXT-WORKFLOW-HYPEROPT-PILOT-01\generated_strategy_specs`:
  `PASS`.
- `.\.venv\Scripts\python.exe -m pytest tests/test_validate_strategy_specs.py tests/test_validate_variant_sweep_artifacts.py -q`:
  `PASS`, 144 passed.
- `.\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`:
  `PASS`, 64 passed.
- `.\.venv\Scripts\python.exe tools\dev\verify.py --integrity-views --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --full-pytest-timeout-seconds 900`:
  `PASS`; diff checks, forbidden-scope check, result-population validator,
  query view listing, 4 pytest shards over 74 test files, and all discovered
  integrity views passed/clean.

## Boundary Summary

- External dependency added: `NO`.
- External runtime tool invoked: `NO`.
- Canonical Result Population write: `NO`.
- Canonical Strategy Spec mutation: `NO`.
- Canonical Variant Manifest mutation: `NO`.
- Canonical Sweep Plan mutation: `NO`.
- Scratch Strategy Spec snapshot generated: `YES`; non-canonical and under
  `scratch/`.
- Trial log mutation: `NO`.
- Candidate registry mutation: `NO`.
- Runner / backtester changed: `NO`.
- Runtime / paper / live / OMS / risk / reconciliation / credential / order
  paths touched: `NO`.
- Screen-gate authority created: `NO`.
- Promotion / readiness authority created: `NO`.
- Candidate-evidence authority created: `NO`.
- Machine-local absolute paths in committed outputs: `NO`.

## Recommendation

`ADOPT_AS_WORKFLOW_ACCELERATOR`.

Rationale: the helper reduces large-grid authoring friction by generating a
150-variant draft VM/Sweep family from a compact parameter-space spec, while
preserving deterministic ordering, scratch-only placement, repo-relative paths,
and existing validator authority. It does not introduce optimizer, ranking,
promotion, or runtime authority.

Broader adoption taxonomy: `adopt`.

Next gated WP suggestion: narrow design for promoting scratch-generated draft
VM/Sweep artifacts into canonical pre-registration only after explicit human ID
assignment and validator gates.
