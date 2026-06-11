# WP-COMP-BOTHDIR-01b - Lock both-direction semantics

- Package class: T1 docs-only major decision / semantics lock
- Branch: `docs/comp-bothdir-01b-lock`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/434
- Scope summary: Records Main 5's locked `direction: "both"` Strategy Spec semantics as committed repo truth for later schema, validator, and compiler packages to cite.
- Authorization basis: Main 5 accepted `WP-COMP-BOTHDIR-01a` and locked the recommended semantics as-written.
- Changed files:
  - `docs/research_pipeline/2026-06-both_direction_semantics_lock.md`
  - `docs/status_entries/WP-COMP-BOTHDIR-01b.md`
  - `docs/research_pipeline/README.md`
  - `docs/project_status.md`
- Lock summary: Main 5 locks explicit side-labeled long/short entry groups with no compiler mirroring, flat/no-entry on simultaneous long+short entry fire while flat, side-specific exits, single-stream long XOR short XOR flat mutual exclusivity, no silent opposite-side flip while already in position, and preservation of closed grammar with no expression language, no new operators, and depth <= 3.
- Validation summary:
  - `git diff --check`: pass.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches.
  - Initial `python -m pytest -q` attempt exceeded a 15-minute tool timeout before a summary was emitted.
  - Final `python -m pytest -q`: environment-only failure, 1276 passed / 1 failed / 6 warnings; `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window` requires gitignored `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`, which is absent from the isolated worktree.
  - `git diff --cached --check`: pass.
  - `git diff --cached --name-only`: pass, expected four files.
- Boundary summary: Docs/status only. No schema, validator, compiler, test, Strategy Spec, variant manifest, sweep plan, result population, catalog, dashboard, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path change.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| lock document created | `docs/research_pipeline/2026-06-both_direction_semantics_lock.md` | satisfied |
| Main 5 locked semantics recorded exactly | lock doc locked semantics section | satisfied |
| explicit side-labeled groups locked | lock doc representation lock | satisfied |
| no compiler mirroring locked | lock doc representation lock | satisfied |
| simultaneous-fire no-entry rule locked | lock doc conflict rule lock | satisfied |
| side-specific exits locked | lock doc exit lock | satisfied |
| single-stream mutual exclusivity locked | lock doc locked semantics and determinism sections | satisfied |
| no silent flip locked | lock doc no-flip lock | satisfied |
| closed grammar / no expression / depth <= 3 locked | lock doc determinism and closed grammar section | satisfied |
| downstream 01c/01d gates recorded without authorization | lock doc downstream package gates | satisfied |
| status fragment created | this file | satisfied |
| README index entry added | `docs/research_pipeline/README.md` | satisfied |
| project-status pointer added | `docs/project_status.md` | satisfied |
| no implementation files changed | final changed-file list | satisfied |
| full pytest run | validation summary in this fragment | satisfied with environment-only missing-data failure |
| T1 validation run | validation summary in this fragment | satisfied |
| PR body/status finality clean | PR body, status fragment, and final readiness gate | satisfied |
| no forbidden paths touched | final diff scope | satisfied |

- Merge status: PR #434 is open, non-draft, and GitHub reports `mergeable=MERGEABLE`.
- Next authority: After this PR merges, Side may draft `WP-COMP-BOTHDIR-01c` only from refreshed `origin/main`, with this lock document present and no competing `docs/project_status.md` PR open. This package does not authorize `01c` execution before `01b` merge.
