# WP-REALISM-SIZING-02a - Dynamic sizing design and protected-path scope

- Package class: T1 docs-only design + read-only protected-path scope surfacing.
- Branch: `docs/realism-sizing-02a-dynamic-design`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/445
- Scope summary: Designs additive opt-in dynamic equity-relative sizing for future Main/Karl review and surfaces the exact protected-path regions a later code package would likely touch.
- Authorization basis: Main/Karl accepted `WP-REALISM-SIZING-01c` and authorized the dynamic equity-relative sizing path for this docs-only design and scope-surfacing stage.
- Reasoning model: GPT-5.5 high; docs-only but protected-path-adjacent sizing methodology design.
- Source runway: `WP-RP6688-SIZING-DIAG-01` classified `RP-6688` as sizing/leverage-artifact affected; `WP-REALISM-SIZING-01a` designed the sizing-realism runway; `WP-REALISM-SIZING-01b` mapped runner/spec-side fixed sizing impact; `WP-REALISM-SIZING-01c` implemented runner-side fixed sizing from target leverage and first in-sample open without touching `lib/backtest.py` or `lib/evaluation.py`.
- Created docs:
  - `docs/research_pipeline/2026-06-dynamic_equity_sizing_design.md`
  - `docs/status_entries/WP-REALISM-SIZING-02a.md`
- Modified docs:
  - `docs/project_status.md`
  - `docs/research_pipeline/README.md`
- Dynamic sizing design summary: Defines future additive modes `fixed_order_size` and `dynamic_equity_target_leverage`. Dynamic mode is opt-in only and computes `quantity = target_leverage * sizing_equity / entry_reference_price` at each new entry.
- Default-preservation contract: Future implementation must preserve `fixed_order_size` as the default. Existing callers without explicit sizing mode must produce identical results except for intentionally versioned outputs where the mode changes. Prior result populations remain reproducible and must not be silently reinterpreted.
- Protected-path scope surfaced: The design surfaces likely future `lib/backtest.py` touch regions: `run_backtest()` signature/validation, fixed-size validation, entry quantity calculation, current position quantity state, fee/slippage/funding notional call sites, PnL/unrealized PnL, liquidation/maintenance margin, trade rows, result params, and `BacktestResult` compatibility.
- Evaluation/reporting impact: `lib/evaluation.py` is classified as not required for the core 02b dynamic sizing implementation if `BacktestResult`, equity curves, aggregate costs, and trade-row notionals remain semantically valid. Future sizing-specific reporting metrics would be a separate package.
- Pipeline-versioning posture: `sizing_mode`, `target_leverage`, equity basis, entry reference price basis, max leverage cap, and any future rounding/constraint behavior are identity-bearing for dynamic-sizing outputs. `RP-2134`, `RP-4492`, and `RP-6688` remain valid under their recorded fixed-sizing model and are not migrated or reinterpreted.
- Future code-package split: Proposes, without authorizing, future 02b core `lib/backtest.py` implementation with focused tests, future 02c runner exposure/integration, future 02d sizing metadata schema/validator, and a separately Karl-gated canonical rerun package.
- Validation summary:
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `git diff --check`: pass.
  - `python tools/dev/diff_scope_summary.py`: pass; expected docs-only scope and no forbidden-path matches.
  - Mandatory read-only proof: no diff/status for `lib/backtest.py`, `lib/evaluation.py`, `tools/research_runner/run_offline_sweep.py`, `research/result_populations`, `research/schemas`, `tools/registry`, or `tests`.
  - Full pytest: not run; not required for this T1 docs-only package.
- Authority/finality audit: Changed-file and PR-body audit completed. Hits are design-scope language, future-not-authorized implementation split, protected-path scope surfacing, default-preservation contract, non-authority caveats, forbidden-scope statements, validation command/result references, source artifact/status identifiers, limitations, or existing historical README/project-status text outside this package's new lines. No wording creates 02b authorization, strategy ranking, readiness, promotion, profitability, candidate status, paper/live/runtime authority, or trading authority.
- Boundary summary: Docs-only. No code, schema, validator, tests, Strategy Specs, variant manifests, sweep plans, result populations, data, candidate registry, dashboard implementation, runtime, paper/live, OMS/risk, broker/exchange, or protected paths are changed.
- Merge status: PR #445 is open as a ready-for-review, non-draft PR. Final local rebase and GitHub mergeability gate are recorded in the package report-back.
- Next authority: WP-REALISM-SIZING-02b is not authorized by this package. Any `lib/backtest.py` or `lib/evaluation.py` implementation requires Main+Karl review of this surfaced scope before drafting.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 8 | `C:\GitHub\crypto-perp-wedge-realism-sizing-02a` on `docs/realism-sizing-02a-dynamic-design` | satisfied |
| Verify PR #444 / 01c merged and source artifacts exist | WP section 7 | PR #444 merged at `3ac7a48`; required 01c docs and `RP-6688` exist | satisfied |
| Create dynamic sizing design doc | WP sections 10-24 | `docs/research_pipeline/2026-06-dynamic_equity_sizing_design.md` | satisfied |
| Create status fragment | WP section 25 | this file | satisfied |
| Update project status compactly | WP section 26 | `docs/project_status.md` | satisfied |
| Update research pipeline README index | WP section 27 | `docs/research_pipeline/README.md` | satisfied |
| Run required validation and read-only proof | WP sections 28-29 | validation summary | satisfied |
| Complete authority/finality audit | WP section 30 | authority/finality audit | satisfied |
| Push and open PR with required title | WP section 32 | PR field and merge status | satisfied |
| Complete final rebase and mergeability gate | WP section 33 | merge status | satisfied in final report-back |
