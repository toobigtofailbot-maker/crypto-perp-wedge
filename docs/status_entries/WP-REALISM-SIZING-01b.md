# WP-REALISM-SIZING-01b - Sizing realism implementation-readiness map

- Package class: T1 docs-only / read-only implementation-readiness package.
- Branch: `docs/realism-sizing-01b-impact-map`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/443
- Scope summary: Maps file-level implementation impact for the
  `WP-REALISM-SIZING-01a` sizing-realism design and classifies whether Option 1
  can be implemented runner/spec-side without immediate `lib/backtest.py` or
  `lib/evaluation.py` changes.
- Authorization basis: Main conditionally authorized
  `WP-REALISM-SIZING-01b` after 01a, with stop/report required after this
  docs-only impact map.
- Source design:
  `docs/research_pipeline/2026-06-realism_sizing_leverage_design.md`.
- Created docs:
  - `docs/research_pipeline/2026-06-realism_sizing_implementation_impact_map.md`
  - `docs/status_entries/WP-REALISM-SIZING-01b.md`
- Modified docs:
  - `docs/project_status.md`
  - `docs/research_pipeline/README.md`
- File-level impact classification: Runner/spec-side Option 1 likely touches
  `tools/research_runner/run_offline_sweep.py` and
  `tests/test_offline_research_runner.py` in a future package. Schema,
  validator, query, and dashboard files are maybe-touch surfaces only if future
  structured declarations, metadata, integrity, or display-only surfacing is
  authorized. Canonical artifacts and protected runtime paths remain no-touch.
- Protected-path classification:
  - `lib/backtest.py`: not required for Option 1 implementation.
  - `lib/evaluation.py`: not required for Option 1 implementation.
- Proposed implementation split: Future 01c candidate for runner/spec-side
  sizing resolution; future 01d candidate for result/reporting metadata; future
  lib-core package only if dynamic compounding equity-relative sizing is later
  reviewed by Main/Karl.
- Test plan summary: Future implementation packages should cover target
  leverage resolution, reference-price selection/fallback, invalid leverage and
  reference price rejection, deterministic resolved order size, identity-scope
  inclusion when canonical metadata changes, old result-population validation,
  `RP-6688` unchanged, no canonical artifact mutation, denominator
  preservation, and cost-to-equity fields if added.
- Migration/back-compat summary: Existing result populations remain valid and
  are not reinterpreted. New sizing model runs require new result populations
  and new identity hashes. Comparisons across old/new sizing models require
  visible sizing-model context. Any regenerated STRAT-SPEC-0002 / VM-0002 /
  SWEEP-PLAN-0002 run under new sizing must produce a new RP ID and preserve
  original `RP-6688`.
- Validation summary:
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - Initial PowerShell heredoc integrity attempt failed before Python ran; a
    second Python attempt used a non-existent helper. Final integrity evidence
    used the repo's public query-layer functions.
  - `git diff --check`: pass.
  - `python tools/dev/diff_scope_summary.py`: pass; expected docs-only scope
    and no forbidden-path matches.
  - Read-only proof: no diff/status for `lib/backtest.py`,
    `lib/evaluation.py`, `tools/research_runner/run_offline_sweep.py`,
    `research/result_populations/RP-6688.result_population.json`,
    `research/schemas`, `tools/registry`, or `tests`.
  - Full pytest: not run; not required for this T1 docs-only package.
- Authority/finality audit: Completed over changed files. Hits are
  impact-map classification, future-not-authorized implementation split,
  non-authority caveats, forbidden-scope statements, validation
  command/result references, source artifact/status identifiers, limitations,
  quoted audit terms, or historical existing README/project-status text outside
  this WP's new lines. No wording authorizes 01c, code changes, schema
  changes, validator changes, test changes, artifact mutation, reruns,
  candidate registration, ranking, readiness, promotion, paper/live, runtime,
  or execution authority.
- Boundary summary: Docs-only. No `lib/backtest.py`, `lib/evaluation.py`,
  runner, schema, validator, compiler, tests, Strategy Specs, Variant
  Manifests, sweep plans, result populations, data, candidate registry,
  dashboard implementation, runtime, paper/live, OMS/risk, broker/exchange, or
  protected path changed.
- Merge status: PR #443 is open as a non-draft PR. Final local rebase onto
  `origin/main` completed with no conflicts; required validation and read-only
  proof passed after that rebase check.
- Next authority: `WP-REALISM-SIZING-01c` is not authorized by this package.
  Main/Karl review is mandatory before any code-touching implementation
  package.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 8 | `C:\GitHub\crypto-perp-wedge-realism-sizing-01b` on `docs/realism-sizing-01b-impact-map` | satisfied |
| Verify PR #442 merged and 01a artifacts exist | WP section 7 | Worktree base `2d56fb9`; source artifacts exist | satisfied |
| Create implementation-readiness map | WP sections 10-17 | `docs/research_pipeline/2026-06-realism_sizing_implementation_impact_map.md` | satisfied |
| Create status fragment | WP section 18 | this file | satisfied |
| Update project status compactly | WP section 19 | `docs/project_status.md` | satisfied |
| Update research pipeline README index | WP section 20 | `docs/research_pipeline/README.md` | satisfied |
| Run required validation | WP section 21 | validation summary | satisfied |
| Prove read-only protected/artifact paths unchanged | WP section 22 | validation summary | satisfied |
| Complete authority/finality audit | WP section 23 | authority/finality audit | satisfied |
| Push and open PR with required title | WP section 25 | PR #443 | satisfied |
| Complete final rebase and mergeability gate | WP section 26 | merge status | satisfied |
