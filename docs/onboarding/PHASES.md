# Phases (high-level)

## Phase 0 — Safety + Parity gates (done)

Goal: prove data integrity + accounting sanity + minimal live API lifecycle without leaving risk open.

Exit: gates passed, artifacts committed, traceability/tags exist.

## Phase 1 — Paper runtime foundation (done)

Goal: build a deterministic, restart-safe paper execution loop that can later host real strategy logic.
Includes: scheduling (1h bar close), overlay evaluator, paper broker, deterministic price ref, ledger accounting, structured events, persistence, idempotency, fail-fast on corrupt state.

Exit: paper loop runs offline, produces logs + state, passes tests, bounded overlay behavior, no forbidden path drift.

## Phase 2 — Research machine + strategy selection (active)

Goal: build a small-scale BTC research and decision-support engine that can discover, test, compare, and later promote strategy candidates without weakening the protected deterministic execution core.

**Current V2 runway:** `D2-020` and
`docs/architecture/2026-10-bounded_autonomous_research_v2_architecture.md`
are controlling. V2-00 is the Stage-5A-equivalent architecture lock and
activates no autonomy. After it merges, the next implementation lane is
five-timeframe/data-feature completion, followed by Prefect consumers,
Hermes/Research Memory/Search Governor integration, product integration, Stage
5B envelope enforcement/activation, and VPS always-on acceptance. Non-capital
VPS deployment is not candidate-gated. After always-on acceptance, serialized
Stage 8A+ engineering and Stage 8R continuous research operate in parallel;
economic activation remains candidate- and human-gated.

Sub-tranches:

* Phase 2a — Research machine foundations: candidate registry, evidence conventions, and pipeline foundation work.
* Phase 2b — Bounded research artifacts / interfaces: experiment plans, reports, candidate stages, and bounded research automation surfaces.
* Phase 2c — Multi-candidate evaluation flow: systematic testing, comparison, and ranking across eligible BTC candidates and timeframes.
* Phase 2d — Candidate ranking / later Strategy v1 selection: human-gated promotion decisions, shadow readiness, and eventual Strategy v1 lock only after evidence supports it.

Exit (Phase 2): structured research evidence supports a formal human-gated decision to promote, revise, discard, or pivot. Strategy v1 selection remains an eventual Phase 2 outcome, not the immediate next step.

**Phase 2 baseline is locked.** See `docs/onboarding/PHASE2_BASELINE.md` for the
authoritative baseline and `D2-020` for the current prospective bounded
autonomous research authorization model.

## Phase 3 — Paper hardening + staged live (future)

Goal: OMS/reconciliation live path, monitoring, incident playbooks, staged sizing.
