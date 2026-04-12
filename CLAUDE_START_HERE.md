# Claude Pro — Project Start Here

## What this repo is

A BTCUSDT USDT-M perpetual futures trading system with a deterministic execution core, paper runtime, and an expanding research/intelligence layer. Phase 1 built the paper-safe foundation; Phase 2 is strategy research + strategy definition.

## Current status

* Phase 1: paper runtime foundation is complete (deterministic scheduling, overlay gating, simulated broker, ledger, structured logs, persistence/idempotency).
* Phase 2: starts next (research program + strategy candidates + evaluation + promotion gates).

## Non-negotiables (do not break)

Execution-critical truth must remain deterministic + auditable:

* OMS truth / reconciliation truth
* Kill-switch semantics
* Hard risk caps (D-0001)
* Context overlay bounds: {ALLOW, ALLOW_REDUCED(0.5), BLOCK} + fail-open
  Anything “agentic” or AI-driven must not directly modify the above.

## Two-layer principle (important)

* Build workflow is repo-first/workspace-first (modular files, PRs, auditability).
* Target system may become a central intelligence/decision-support layer aggregating many signals and producing rankings/scores — but only as inputs to deterministic risk/execution.

## How to run (paper)

See: docs/runbook.md

## Phase map + what to do next

* Phases: docs/onboarding/PHASES.md
* Phase 2 mandate (research program): docs/onboarding/PHASE2_MANDATE.md
* Architecture map: docs/onboarding/SYSTEM_MAP.md
* Workflow/roles: docs/onboarding/WORKFLOW.md
* Open questions: docs/onboarding/OPEN_QUESTIONS.md

## What not to assume

Phase 2 baseline is now locked. See `docs/onboarding/PHASE2_BASELINE.md` for the authoritative Phase 2 reference, including all locked decisions (D2-001 through D2-017), research workflow, tool decisions, and promotion gates.
