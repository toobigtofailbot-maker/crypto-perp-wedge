# EXT-INTEG-WORKFLOW-GEN-01 - Productionized Draft Grid Generator

## Branch / PR

- Branch: `ext/integ-workflow-gen-01`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/516`

## Package Class

T3 workflow / draft artifact-generation tooling.

## Scope Summary

This package adds a repo-owned deterministic draft grid generator under
`tools/research_workflow/`. The generator reads a compact parameter-space JSON
spec, expands it into stable Cartesian draft variants, writes scratch-only
Strategy Spec / Variant Manifest / Sweep Plan-style artifacts, and validates
those generated artifacts with the existing structural repo validators.

Generated outputs are labeled as:

- `DRAFT WORKFLOW OUTPUT`
- `NOT CANONICAL PREREGISTRATION`
- `NOT CANDIDATE EVIDENCE`
- `NOT SCREEN-GATE OR PROMOTION AUTHORITY`
- `VALIDATED ONLY AGAINST STRUCTURAL REPO VALIDATORS`
- `NOT PAPER / LIVE / RUNTIME AUTHORITY`

## Changed Files

- `tools/research_workflow/draft_grid_generator.py`
- `tests/test_draft_grid_generator.py`
- `docs/status_entries/EXT-INTEG-WORKFLOW-GEN-01.md`
- `scratch/EXT-INTEG-WORKFLOW-GEN-01/parameter_space.json`
- `scratch/EXT-INTEG-WORKFLOW-GEN-01/generated_strategy_specs/STRAT-SPEC-9101.strategy_spec.json`
- `scratch/EXT-INTEG-WORKFLOW-GEN-01/generated_variant_manifests/VM-9101.variant_manifest.json`
- `scratch/EXT-INTEG-WORKFLOW-GEN-01/generated_sweep_plans/SWEEP-PLAN-9101.sweep_plan.json`
- `scratch/EXT-INTEG-WORKFLOW-GEN-01/draft_grid_generation_report.json`
- `scratch/EXT-INTEG-WORKFLOW-GEN-01/draft_grid_generation_report.md`
- `scratch/EXT-INTEG-WORKFLOW-GEN-01/generated_artifacts.sha256`

## Generated Demo

- Source Strategy Spec anchor:
  `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- Parameter-space input:
  `scratch/EXT-INTEG-WORKFLOW-GEN-01/parameter_space.json`
- Generated scratch Strategy Spec snapshot:
  `scratch/EXT-INTEG-WORKFLOW-GEN-01/generated_strategy_specs/STRAT-SPEC-9101.strategy_spec.json`
- Generated scratch Variant Manifest:
  `scratch/EXT-INTEG-WORKFLOW-GEN-01/generated_variant_manifests/VM-9101.variant_manifest.json`
- Generated scratch Sweep Plan:
  `scratch/EXT-INTEG-WORKFLOW-GEN-01/generated_sweep_plans/SWEEP-PLAN-9101.sweep_plan.json`
- Variant count: `150`
- Ordering: explicit `axis_order`, then deterministic Cartesian product
  left-to-right.
- Seed: none; the grid is deterministic and not random.
- Deterministic artifact checksum:
  `sha256:35b394113dc302ec5f0832c660e6a2a1980e96fd899729f77d1b2e7665dd6188`
- Report output checksum:
  `sha256:6c97b8aed780e98b3565df1c4f545ca22ee31b5a3193394bfdc79899ff3a3047`

Artifact checksums:

| artifact | checksum |
|---|---|
| parameter-space input | `sha256:57d1ca1cde437d2c542c7dac57af0c43683692b5d666d8d83dda2493a29d898c` |
| scratch Strategy Spec snapshot | `sha256:d388e0639c1b5bb90db34a1b7e1a636b7b6fbc7b129806e36a21ca0a23fa5710` |
| scratch Variant Manifest | `sha256:596b4aa0ca1355a80401362f27f5cc05e196a16af27145c7a21a6795b41cd8d4` |
| scratch Sweep Plan | `sha256:39b40576258200d19d096066cebb3fd6571644344abf3f3c04159e10f349c8dc` |

## Validation Summary

- `python -m pytest tests/test_draft_grid_generator.py -q`: `PASS`, 11 passed.
- `python -m tools.research_workflow.draft_grid_generator`: `PASS`; generated 150 variants and both validator booleans were true.
- `python -m tools.registry.validate_strategy_specs --strategy-specs-dir scratch\EXT-INTEG-WORKFLOW-GEN-01\generated_strategy_specs`: `PASS`.
- `python -m tools.registry.validate_variant_sweep_artifacts --variant-manifests-dir scratch\EXT-INTEG-WORKFLOW-GEN-01\generated_variant_manifests --sweep-plans-dir scratch\EXT-INTEG-WORKFLOW-GEN-01\generated_sweep_plans --strategy-specs-dir scratch\EXT-INTEG-WORKFLOW-GEN-01\generated_strategy_specs`: `PASS`.
- `python -m tools.research_query.run --list-views`: `PASS`.
- `v_integrity_*` single-process query-layer check: `PASS`, clean across 55 views.
- `python tools/dev/diff_scope_summary.py`: `PASS`; no forbidden-path matches.
- `python -m pytest -q`: `PASS`, 1654 passed, 1 skipped, 6 warnings.
- Validation environment note: the isolated worktree needed the gitignored local file `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv` copied from the root checkout for `tests/test_external_simulator_pilot.py`; the file remains ignored and is not part of the package diff.

## Boundary Summary

- Runtime / paper / live / OMS / risk / reconciliation / safe-mode /
  kill-switch / broker / exchange / order paths touched: `NO`.
- Private APIs, credentials, balances, positions, or orders touched: `NO`.
- Canonical Result Population write: `NO`.
- Canonical Strategy Spec mutation: `NO`.
- Canonical Variant Manifest mutation: `NO`.
- Canonical Sweep Plan mutation: `NO`.
- Runner / backtester / `lib` mutation: `NO`.
- External dependency added: `NO`.
- Optimizer, ranking, recommendation, readiness, screen-gate, promotion, or
  candidate-evidence authority created: `NO`.

## Active-WP Requirement Traceability

| Active-WP requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Dedicated branch/worktree from refreshed `origin/main` | Parallel execution requirements | `ext/integ-workflow-gen-01` at `893fdb4` | satisfied |
| Repo-owned generator under scoped path | Scope / Objective | `tools/research_workflow/draft_grid_generator.py` | satisfied |
| Compact parameter-space to deterministic Cartesian variants | Implementation requirements | `tests/test_draft_grid_generator.py`; generated report | satisfied |
| Stable ordering and provenance | Implementation requirements | `variant_assignments`; generated report | satisfied |
| Scratch-only outputs | Scope / forbidden scope | `scratch/EXT-INTEG-WORKFLOW-GEN-01/*` | satisfied |
| Existing validators run on generated artifacts | Implementation requirements / Validation | Validation Summary | satisfied |
| Non-authority labels present | Implementation requirements | Generated report and artifacts | satisfied |
| No canonical Strategy Spec / VM / Sweep mutation | Forbidden scope | Boundary Summary and diff scope | satisfied |
| No runtime, paper/live, OMS/risk, credentials, or orders | Global forbidden scope | Boundary Summary and diff scope | satisfied |

## Merge Status

- Decision label: `ADOPT_AS_WORKFLOW_ACCELERATOR`.
- Merge status: PR #516 is open and ready for review.
- Next dependency / runway note: future draft-to-canonical promotion remains
  separately human-gated and is not authorized by this package.
