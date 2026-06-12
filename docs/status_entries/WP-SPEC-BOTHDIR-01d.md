# WP-SPEC-BOTHDIR-01d - RP-6688 descriptive checkpoint

- Package class: T1 docs-only result-interpretation checkpoint.
- Branch: `docs/spec-bothdir-01d-rp6688-checkpoint`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/440
- Scope summary: Creates a descriptive, non-authoritative checkpoint over
  `RP-6688`, consuming the complete committed result population read-only and
  describing raw population-level outcome patterns without choosing a variant
  or asserting strategy quality.
- Authorization basis: Main 5 accepted `WP-SPEC-BOTHDIR-01c` and authorized
  `WP-SPEC-BOTHDIR-01d` as a docs-only descriptive checkpoint over `RP-6688`;
  Karl gate: none.
- Source artifact:
  `research/result_populations/RP-6688.result_population.json`.
- Created docs:
  - `docs/research_pipeline/2026-06-rp6688_both_direction_sma_band_checkpoint.md`
  - `docs/status_entries/WP-SPEC-BOTHDIR-01d.md`
- Modified docs:
  - `docs/project_status.md`
  - `docs/research_pipeline/README.md`
- Denominator: committed denominator 10; result rows 10; outcome counts sum
  10; all variants retained; no successful-only denominator.
- Key clarification: `successful=10` means all 10 variants ran to completion;
  it does not mean profitable, validated as an edge, ready, or good.
- Data provenance: `canonical_real_data` over the BTCUSDT 15m OHLCV D4 catalog
  ref
  `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
  and D4 slice identity
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.
- Identity:
  - `input_identity_hash`:
    `sha256:ea9ea760ef7a5d30956a4573fc4ca0c39b43a533803667370219f5e3f7ffe386`
  - `result_population_identity_hash`:
    `sha256:7ee08cc1f30e26c318b39d571b90d25406072329ce4a67bd7c94ec35f98fcdbc`
  - parent artifacts: `STRAT-SPEC-0002` / `VM-0002` /
    `SWEEP-PLAN-0002`
- Validation summary:
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `git diff --check`: pass.
  - `python tools/dev/diff_scope_summary.py`: pass; expected docs-only
    changed-file scope and no forbidden-path matches.
  - `git diff --cached --check`: pass.
  - `git diff --cached --name-only`: expected four docs only.
  - Full pytest: not run; not required for this T1 docs-only package.
  - Initial per-view CLI loop timed out before completion; the final integrity
    evidence used the same query-layer view registry in one Python process and
    confirmed zero rows for all 55 integrity views.
- Authority/finality audit: changed-files audit completed. Search hits are
  non-authority caveats, forbidden-scope statements,
  validation-command/result references, limitations, or source artifact/status
  identifiers; no wording describes a variant favorably as a selection,
  recommendation, readiness, promotion, or edge.
- Boundary summary: No result-population mutation; no Strategy Spec, Variant
  Manifest, Sweep Plan, schema, validator, compiler, runner, catalog, data,
  candidate registry, dashboard implementation, runtime, paper/live, OMS/risk,
  broker/exchange, or protected-path change.
- Merge status: PR #440 open for review; merge not performed by this package.
- Next authority: After this PR merges, report back to Main 5. Robustness,
  DSR/PSR/MinTRL, expressiveness primitives, candidate lifecycle,
  registration, and promotion remain future options only unless separately
  authorized.

## Active-WP requirement traceability

| Requirement | Evidence | Status |
|---|---|---|
| Dedicated worktree from refreshed `origin/main` | `C:\GitHub\crypto-perp-wedge-spec-bothdir-01d` on `docs/spec-bothdir-01d-rp6688-checkpoint` | satisfied |
| PR #439 merged before start | worktree base `401b5ab`, merge commit for PR #439 | satisfied |
| `RP-6688` exists | `research/result_populations/RP-6688.result_population.json` | satisfied |
| `WP-SPEC-BOTHDIR-01c` status exists | `docs/status_entries/WP-SPEC-BOTHDIR-01c.md` | satisfied |
| project status records 01c / RP-6688 | `docs/project_status.md` | satisfied |
| Result population ID is `RP-6688` | source artifact | satisfied |
| Parent artifacts are `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` | source artifact | satisfied |
| Committed denominator = 10 | source artifact | satisfied |
| Result row count = 10 | source artifact | satisfied |
| Outcome counts sum = 10 | source artifact | satisfied |
| Provenance is `canonical_real_data` over BTCUSDT 15m D4A data | source artifact | satisfied |
| Create checkpoint doc only under scoped path | changed-file list | satisfied |
| Create status fragment | changed-file list | satisfied |
| Update `docs/project_status.md` compactly | changed-file list | satisfied |
| Update `docs/research_pipeline/README.md` index only | changed-file list | satisfied |
| No forbidden files touched | changed-file list and diff-scope validation | satisfied |
| Required validators and integrity views pass | validation commands | satisfied |
| Authority/finality text audit complete | semantic audit | satisfied |
