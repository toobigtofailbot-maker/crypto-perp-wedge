# WP-REALISM-SIZING-01a - Sizing realism design

- Package class: T1 design-only / docs-only architecture package.
- Branch: `docs/realism-sizing-01a-design`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/442
- Scope summary: Designs an equity-relative sizing / leverage-cap realism
  surface after `WP-RP6688-SIZING-DIAG-01` classified `RP-6688` as primarily a
  sizing/leverage artifact.
- Authorization basis: Main authorized `WP-REALISM-SIZING-01a` after accepting
  the `WP-RP6688-SIZING-DIAG-01` diagnostic; Karl gate: none for 01a.
- Source diagnostic:
  `docs/research_pipeline/2026-06-rp6688_sizing_leverage_diagnostic.md`.
- Created docs:
  - `docs/research_pipeline/2026-06-realism_sizing_leverage_design.md`
  - `docs/status_entries/WP-REALISM-SIZING-01a.md`
- Modified docs:
  - `docs/project_status.md`
  - `docs/research_pipeline/README.md`
- Design options evaluated:
  - Option 1: runner-side fixed-but-equity-aware sizing.
  - Option 2: lib-core dynamic compounding equity-relative sizing.
  - Option 3: hold / no sizing change.
- Selected design path: Option 1, runner-side fixed-but-equity-aware sizing,
  for further planning only. This selection does not authorize implementation.
- Pipeline-versioning posture: Existing result populations remain valid under
  their recorded model and must not be silently reinterpreted. A new sizing
  realism model requires explicit sizing/pipeline version markers and new
  result populations for future regenerated runs.
- Validation summary:
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - Initial custom integrity helper failed before querying views because it
    used a non-existent private helper; final integrity evidence used the
    repo's public query-layer functions.
  - `git diff --check`: pass.
  - `python tools/dev/diff_scope_summary.py`: pass; expected docs-only scope
    and no forbidden-path matches.
  - Read-only proof: no diff/status for `lib/backtest.py`,
    `lib/evaluation.py`, `tools/research_runner/run_offline_sweep.py`, or
    `research/result_populations/RP-6688.result_population.json`.
  - Full pytest: not run; not required for this T1 docs-only package.
- Authority/finality audit: Completed over changed files. Search hits are
  design option language, selected design path for planning only,
  future-not-authorized implementation split, non-authority caveats,
  forbidden-scope statements, validation command/result references, source
  artifact/status identifiers, limitations, or existing README/project-status
  historical text outside this WP's changed lines. No wording creates
  implementation, ranking, readiness, promotion, paper/live, runtime, or
  trading authority.
- Boundary summary: Docs-only. No `lib/backtest.py`, `lib/evaluation.py`,
  runner, schema, validator, compiler, tests, Strategy Spec, Variant Manifest,
  Sweep Plan, result population, data, candidate registry, dashboard
  implementation, runtime, paper/live, OMS/risk, broker/exchange, or protected
  path changed.
- Auto-progression condition: If this PR is docs-only, validates cleanly, and
  states a design that can be carried into `WP-REALISM-SIZING-01b` without
  immediate `lib/backtest.py` or `lib/evaluation.py` changes, Side may draft
  `WP-REALISM-SIZING-01b` after merge without a Main report-back. If not, stop
  and report.
- Merge status: PR #442 is open as a non-draft PR and GitHub reports
  `mergeable=MERGEABLE`.
- Next authority: `WP-REALISM-SIZING-01b` is conditionally authorized only if
  01a satisfies the auto-progression rule. `WP-REALISM-SIZING-01c`, result
  regeneration, candidate lifecycle work, and code-touching sizing work are not
  authorized here.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 8 | `C:\GitHub\crypto-perp-wedge-realism-sizing-01a` on `docs/realism-sizing-01a-design` | satisfied |
| Verify PR #441 merged and required artifacts exist | WP section 7 | Worktree base `5abdeb9`; source artifacts exist | satisfied |
| Create design doc | WP section 10 | `docs/research_pipeline/2026-06-realism_sizing_leverage_design.md` | satisfied |
| Create status fragment | WP sections 10 and 18 | this file | satisfied |
| Update project status compactly | WP section 19 | `docs/project_status.md` | satisfied |
| Update research pipeline README index | WP section 20 | `docs/research_pipeline/README.md` | satisfied |
| Evaluate Option 1 and Option 2 | WP sections 12 and 13 | design doc option sections | satisfied |
| Select one design path for planning only | WP section 14 | design doc selected path section | satisfied |
| Preserve old result populations under recorded model | WP section 16 | design doc backward compatibility and migration sections | satisfied |
| Propose split without authorizing code | WP section 17 | design doc implementation split section | satisfied |
| Run required validation | WP section 21 | validation summary | satisfied |
| Prove read-only protected/artifact paths unchanged | WP section 22 | validation summary | satisfied |
| Complete authority/finality audit | WP section 23 | authority/finality audit | satisfied |
| Push and open PR with required title | WP section 25 | PR #442 | satisfied |
| Complete final rebase and mergeability gate | WP section 26 | merge status | satisfied |
