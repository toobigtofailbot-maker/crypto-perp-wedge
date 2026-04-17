# Project Status

This file is the current-state anchor. Read it before architecture, execution, implementation, or review work. Update it after meaningful merges that change repo state.

Startup read order:

1. `docs/project_status.md`
2. `CLAUDE_START_HERE.md`
3. `docs/runbook.md`

## Project Identity

- Instrument: BTCUSDT Binance USDT-M perpetual.
- Runtime foundation: deterministic paper/runtime core from Phase 1.
- Current program: Phase 2 research/workbench progression toward strategy evidence and shadow promotion.
- Locked Phase 2 timeframe set: `15m`, `30m`, `1h`, `4h`, `1d`.
- Timeframe rule: no single global primary timeframe is fixed. Each candidate declares its primary timeframe and any allowed confirmation timeframes before testing.

## Current Phase / Repo State

- Phase 1 is closed.
- Phase 2 baseline is locked in `docs/onboarding/PHASE2_BASELINE.md`.
- WP-1a Batch 1, WP-1a Batch 2 corrected, WP-1b, WP-1c, the current-state-anchor package, OPS-02, WP-2b, WP-2c, WP-3b, WP-3c, and WP-4a are merged to `main`; WP-4b1 is in execution.
- Current repo state is research-first: validate or kill BTCUSDT perp strategy hypotheses without weakening protected execution boundaries.

## Key Architecture References

- Long-term roadmap, automation, managed-agent, dashboard, and self-improvement scope is locked in `docs/architecture/LONG_TERM_SCOPE.md`.

## Merged Work Package Ledger

Naming convention: `WP-*` is reserved for Main Architecture research/execution work packages. `OPS-*` is reserved for repo-maintenance, workflow, and entrypoint addenda outside the main research package chain.

| Package | Status | PR / merge ref | Outcome |
|---|---|---|---|
| WP-0 baseline lock | Merged | PR #17 / `b0149b2` | Locked Phase 2 baseline and D2-001 through D2-017 references. |
| WP-1a Batch 1 | Merged | PR #18 / `1282f4f` | Added full BTCUSDT history foundation for locked research timeframes and funding. |
| WP-1a Batch 2 corrected | Merged | PR #19 / `284a7f8` | Added corrected mark/index/premium history and irreparable official-source-gap policy. |
| WP-1b | Merged | PR #20 / `42b450a` | Added research workbench, backtest/evaluation scaffolding, trial log support, and dependencies. |
| WP-1c | Merged | PR #21 / `f51ec44` | Added orchestration scaffold, agent/skill definitions, and research/evaluation prompt artifacts. |
| OPS-01 - current-state anchor | Merged | PR #22 / `77d9ec5` | Added this current-state anchor and entrypoint references. |

## Locked / Do-Not-Touch Boundaries

Protected unless a package explicitly authorizes the change and the locked decision process supports it:

- OMS truth / reconciliation truth.
- Kill-switch semantics.
- D-0001 hard risk caps.
- Overlay output set `{ALLOW, ALLOW_REDUCED=0.5, BLOCK}` and fail-open behavior.
- Paper ledger accounting math.
- Event log schema except explicit additive changes.
- No agentic execution or autonomous risk/execution changes.
- Phase 1 paper runtime remains protected while Phase 2 research proceeds through the workbench and later shadow path.

## Data Status

- Free Binance sources are the authoritative Phase 2 dataset path.
- Current repo documentation covers full BTCUSDT OHLCV, funding, mark price, index price, and premium index history for the locked timeframe set.
- Provenance belongs in `docs/data_catalog.md`; raw and processed data contents are not package-edit targets unless explicitly authorized.
- Known irreparable official-source gaps are tracked by `data/irreparable_gaps.json` and governed by D2-003A plus `docs/irreparable_gaps_policy.md`.
- WP-3b intraday assessment confirms existing 1h and 30m OHLCV data are sufficient for H-005 / H-006 baseline execution; 15m OHLCV is also ready for future OHLCV-only hypotheses.

## Research / Workbench Status

- Phase 2 uses the lightweight research backtester/evaluation path for hypothesis testing.
- Promotion gates, DSR/trial-log discipline, and pre-registration remain the overfitting firewall.
- Final Strategy v1 is not locked.
- Long-term research direction targets a multi-strategy, multi-timeframe portfolio rather than concentration in a single strategy or timeframe.
- H-001 and H-002 are CONCLUDED / NO-GO after 4h baseline execution.
- H-003 and H-004 are CONCLUDED / NO-GO after 1d baseline execution; 1d is in Cold Storage.
- H-005 is CONCLUDED / NO-GO after 1h baseline execution.
- H-006 is CONCLUDED / NO-GO after 30m baseline execution.
- WP-3b created DEC-0003 and DEC-0004 and grew `research/trial_log.jsonl` from 2 to 4 rows.
- WP-3c created DEC-0005 and DEC-0006 and grew `research/trial_log.jsonl` from 4 to 6 rows.
- WP-4a created the H-001 through H-006 failure analysis, documented alternative families, and registered H-007 through H-010 without new backtests or trial-log entries.
- WP-4b1 executed H-007 and H-010 4h cross-stream baselines, created DEC-0007 and DEC-0010, and grew `research/trial_log.jsonl` from 6 to 8 rows.
- H-007 is CONCLUDED / NO-GO after 4h funding + momentum baseline execution.
- H-010 is CONCLUDED / NO-GO after 4h basis / premium mean-reversion baseline execution.
- Hypothesis status count: 8 CONCLUDED / NO-GO; 2 DRAFT / pending (H-008 and H-009).
- 4h is back in Cold Storage after H-007 and H-010 also failed D2-006 promotion gates.
- Brief phase note: WP-4b1 executed; WP-4b2 pending.
- H-008 replaced the initially considered volatility-scaling concept because current backtester signal handling does not support true fractional exposure without code changes.
- Current candidate map: H-008 1h premium-confirmed momentum continuation and H-009 30m multi-timeframe trend alignment remain pending for WP-4b2. 4h and 1d are in Cold Storage; 15m remains in-scope and data-ready, but current intraday evidence argues for caution before faster expansion.

## Orchestration / Skills / Prompts Status

- `.claude/` contains bounded agent operating guidance and role/skill scaffolding from WP-1c.
- `prompts/` contains execution, report-back, review, hypothesis, and evaluation templates.
- Orchestration is a thin repo-first workflow layer. It does not own runtime state or execution decisions.
- Default execution flow is Main Architecture -> Claude Code / Codex direct execution brief. Separate Karl Architecture handoff/review is optional and used only when explicitly requested.

## Deferred But Intentional Items

- Final candidate selection and promotion decisions.
- Shadow adapter and research-to-paper parity package.
- Phase 3 live-path hardening and monitoring.
- Platform migration or deeper execution refactors unless later justified by locked architecture.
- Sub-15m and paid/tick-level data work for Phase 2.

## Current Open Risks / Architecture Questions

- Whether any future active intraday candidate can pass baseline gates after H-005/H-006 failed on 1h / 30m, following H-001/H-002/H-007/H-010 failures on 4h and H-003/H-004 failures on 1d.
- How to expand 15m candidate registration without weakening cost-drag, overfitting, or promotion-gate discipline, given negative 1h / 30m intraday evidence.
- How candidates that survive research gates will be wrapped for shadow mode.
- How to keep trial-log discipline tight while allowing useful exploratory EDA.
- How to enforce downstream handling of irreparable official-source gaps without silent interpolation.

## Next Expected Package / Immediate Architecture Need

WP-4b1 executed H-007 and H-010. The likely next architecture need is WP-4b2 execution of H-008 and H-009, unless Main Architecture pauses after the renewed 4h Cold Storage result.

- WP-5a pipeline audit completed; see `docs/audits/2026-04-pipeline_audit.md`
- Audit verdict: MINOR ISSUES (no liquidation model; cost-drag edge cases; all NO-GO verdicts remain valid)
- Next step: WP-5b bounded fix package recommended before executing H-008/H-009

## Update Discipline

- Read this file first.
- Follow the startup read order above before drafting or executing a package.
- Prefer current repo truth over stale chat context.
- If this file conflicts with locked baseline docs, report the mismatch and follow the locked baseline until corrected.
- Update this file after meaningful merges that change current state, boundaries, data status, workbench status, orchestration status, or immediate next architecture needs.
