# Claude Pro - Project Start Here

## What This Repo Is

A BTCUSDT Binance USDT-M perpetual futures trading system with a deterministic paper/runtime foundation and a Phase 2 research/workbench layer. Phase 1 built the protected paper-safe foundation; Phase 2 now includes a candidate-agnostic research machine for discovering, testing, comparing, and later promoting strategy candidates across the locked timeframe set: `15m`, `30m`, `1h`, `4h`, `1d`.

## Hard Startup Sequence

1. Read `docs/project_status.md` first. It is the current-state anchor.
2. Read this file for entrypoint rules.
3. Read `docs/runbook.md`.
4. After that, read only the files needed for the task.

Repo truth beats stale chat context. If a brief, chat, or memory conflicts with current repo files, report the mismatch instead of silently improvising.

## Non-Negotiables

Execution-critical truth must remain deterministic and auditable:

- OMS truth / reconciliation truth.
- Kill-switch semantics.
- D-0001 hard risk caps.
- Context overlay bounds: `{ALLOW, ALLOW_REDUCED(0.5), BLOCK}` plus fail-open behavior.
- Paper ledger accounting math.
- No agentic execution or autonomous risk/execution changes.

## Phase 2 Rules

- Phase 2 is research-first, not runtime-refactor-first.
- Current next-step direction is candidate-agnostic research machine foundation work: registry, schemas, pipeline foundations, and bounded research interfaces.
- Strategy v1 is not locked now. Candidate selection and promotion remain future human-gated decisions based on structured evidence.
- No single global primary timeframe is fixed for research candidates.
- Strategy candidates must declare their primary timeframe, and any allowed confirmation timeframes, within the locked set before testing.
- The model should support ongoing strategy discovery, comparison, ranking, and later bounded promotion rather than anchoring on one immediate candidate.
- The paper runtime remains protected until an explicitly scoped shadow/promotion package authorizes additive work.

## If Something Does Not Line Up

Stop and report when a task requires a decision not present in repo truth, conflicts with locked Phase 2 baseline docs, or would require edits outside the allowed package scope.

## References

- Current-state anchor: `docs/project_status.md`
- Runbook: `docs/runbook.md`
- Stage 2c workflow-efficiency lock: `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md` for Main/Side/Codex authority, tiered workflow, project-status overlap, reporting, and standing efficiency authorization; current merged repo truth still wins.
- Codex token-efficiency guidance: `docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md` for Codex/Side context hygiene and prompt/reporting efficiency; it is guidance-only and does not weaken the hard startup sequence, repo truth, validation, or protected boundaries.
- Long-term architecture scope: `docs/architecture/LONG_TERM_SCOPE.md` when clarifying longer-horizon roadmap, automation, agent, dashboard, or self-improvement scope
- Phase map: `docs/onboarding/PHASES.md`
- Phase 2 baseline: `docs/onboarding/PHASE2_BASELINE.md`
- System map: `docs/onboarding/SYSTEM_MAP.md`
- Workflow/roles: `docs/onboarding/WORKFLOW.md`
- Open questions: `docs/onboarding/OPEN_QUESTIONS.md`
