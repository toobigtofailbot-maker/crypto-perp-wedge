# WP-FUTURE-STRATEGY-CAPABILITY-MATRIX-01

- Package class: docs-only / architecture-memory inventory.
- Branch: `docs/future-strategy-capability-matrix-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-FUTURE-STRATEGY-CAPABILITY-MATRIX-01`.
- Base commit: `e8e0e4e9c9ae`.
- Changed files:
  - `docs/architecture/future_strategy_capability_matrix.md`
  - `docs/status_entries/WP-FUTURE-STRATEGY-CAPABILITY-MATRIX-01.md`

## Summary

This package adds a non-authoritative future strategy capability matrix that preserves future strategy, indicator, crypto/perp data, simulator/execution-realism, and agent/automation lanes as repo memory while the project pursues the fastest safe path for one promising candidate family.

The matrix separates current/near-current OHLCV families, compiler/indicator upgrades, data packages, simulator upgrades, paper/live guardrail surfaces, and deferred/rejected examples. It records that future items still need scoped packages, validation plans, changed-file boundaries, and explicit authorization before implementation or evidence production.

## Boundary

- No implementation.
- No sequencing authority.
- No first-live prerequisite expansion.
- No data acquisition.
- No Strategy Spec, Variant Manifest, Sweep Plan, or Result Population changes.
- No candidate, paper/live, runtime, or capital authority.
- No protected paths touched.
- No `docs/project_status.md` update by design for parallel safety.

## Validation

- `git status --short`: PASS; only the two staged new docs/status files.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no forbidden-path matches.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_variant_sweep_artifacts`: PASS.
- `python -m tools.registry.validate_indicator_catalogs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.registry.validate_candidate_registry`: PASS.
- `python -m tools.registry.validate_paper_state`: PASS.
- `python -m tools.research_query.run --list-views`: PASS; 118 views listed.
- `python tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000 --json`: PASS; 55 integrity views clean.
- `python -m pytest tests/test_research_query.py -q`: PASS; 64 passed in 461.97s.
- Full sharded pytest: NOT RUN - docs-only new-file package; no code, schema, validator, query-layer, runner, data, runtime, or protected-path changes.

## Remaining blocker

The matrix is preserved memory only. Every future item still needs its own scoped package, validation plan, changed-file boundary, and explicit authorization before it can become implementation or evidence.
