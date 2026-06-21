# WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01 - Candidate lifecycle engine

## Package

- Package: `WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01`
- Decision: `COMPLETE`
- Package class: lifecycle engine / human-gated candidate packet preparation

## Branch / Base

- Branch: `lab/candidate-lifecycle-engine-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\lab-candidate-lifecycle-engine-01`
- Base: `origin/main` at `4da388a`

## Repo-Truth Discovery

- Current lifecycle-change vocabulary is `proposed`, `in_research`,
  `research_concluded`, `paper_eligible`, `paper_active`, `paper_concluded`,
  `live_eligible`, `live_active`, `halted`, and `archived`.
- The older candidate-lifecycle-registry schema uses a separate conceptual
  vocabulary; the engine uses current lifecycle-change vocabulary for report
  preparation and does not modify either existing validator.
- `docs/status_entries/WP-LAB-ROBUSTNESS-DEPTH-01.md` is not merged in current
  repo truth, so robustness evidence is handled as optional/unavailable in the
  sample fixture.
- Scratch/sample artifacts use a fixture candidate ID and fixture evidence refs
  to avoid implying a real candidate evidence chain.

## Changed Files

- `tools/candidate_lifecycle/__init__.py`
- `tools/candidate_lifecycle/lifecycle_engine.py`
- `tools/candidate_lifecycle/build_candidate_review_packet.py`
- `tests/test_candidate_lifecycle_engine.py`
- `tests/fixtures/candidate_lifecycle_engine/valid_candidate_inputs.json`
- `tests/fixtures/candidate_lifecycle_engine/invalid_auto_promotion.json`
- `tests/fixtures/candidate_lifecycle_engine/missing_evidence_blockers.json`
- `scratch/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01/README.md`
- `scratch/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01/candidate_lifecycle_report.json`
- `scratch/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01/candidate_review_packet.md`
- `scratch/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01/provenance.json`
- `docs/status_entries/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01.md`

## Implementation Summary

- Adds a scratch-only lifecycle engine that loads candidate lifecycle input
  fixtures, validates requested transitions against the current repo lifecycle
  vocabulary, links evidence refs, identifies blockers, and emits a lifecycle
  report plus Markdown review packet.
- Blocks auto-promotion, readiness marking, paper/live starts, live-active
  targets, and evidence mutation requests.
- Emits `human_approval_required` only as a non-authoritative pending packet
  state when a vocabulary-valid transition requires a human gate.
- Preserves required non-authority flags:
  `human_gated`, `not_auto_promotion`, `not_readiness_authority`,
  `not_paper_live`, `not_canonical_evidence_mutation`, and
  `not_execution_authority`.

## Validation

- `python -m pytest tests/test_candidate_lifecycle_engine.py -q`: PASS, 5 tests
  under bare Python 3.14.3.
- `python -m tools.candidate_lifecycle.lifecycle_engine --input tests/fixtures/candidate_lifecycle_engine/valid_candidate_inputs.json --output-dir scratch/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01`: PASS
  under bare Python 3.14.3.
- Bare `python -m pytest -q`: FAILED during collection under Python 3.14.3
  because the bare interpreter lacks repo dependencies (`binance`, `pandas`,
  `numpy`).
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_candidate_lifecycle_engine.py -q`:
  PASS, 5 tests.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.candidate_lifecycle.lifecycle_engine --input tests/fixtures/candidate_lifecycle_engine/valid_candidate_inputs.json --output-dir scratch/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_lab_run_registry.py tests/test_generate_static_dashboard.py -q`:
  PASS, 38 tests.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_candidate_registry`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_lifecycle_changes`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`:
  PASS; forbidden-path matches: none.
- `git diff --check`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`:
  TIMED OUT after approximately 904 seconds with no visible output before
  termination. Full pytest is not counted as a pass; no package-specific failure
  surfaced before timeout.

## Boundary Summary

- No canonical candidate lifecycle registry is created or modified.
- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan,
  trial log, walk-forward evidence, dashboard approval control, or candidate
  registry row is mutated.
- No existing validator, schema, query-layer, runner, compiler, `lib/`, or
  dependency file is changed.
- No runtime, paper/live, OMS, risk, reconciliation, safe-mode, kill-switch,
  broker, exchange, order, credential, or config path is touched.
- The engine and generated scratch outputs create no candidate approval,
  promotion, readiness, paper/live, runtime, execution, broker/exchange, or
  capital authority.
