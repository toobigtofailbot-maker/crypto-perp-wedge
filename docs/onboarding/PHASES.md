# Phases (high-level)

## Phase 0 — Safety + Parity gates (done)

Goal: prove data integrity + accounting sanity + minimal live API lifecycle without leaving risk open.

Exit: gates passed, artifacts committed, traceability/tags exist.

## Phase 1 — Paper runtime foundation (done)

Goal: build a deterministic, restart-safe paper execution loop that can later host real strategy logic.
Includes: scheduling (1h bar close), overlay evaluator, paper broker, deterministic price ref, ledger accounting, structured events, persistence, idempotency, fail-fast on corrupt state.

Exit: paper loop runs offline, produces logs + state, passes tests, bounded overlay behavior, no forbidden path drift.

## Phase 2 — Strategy research + strategy definition (starts next)

Goal: build an “Aladdin-like” small-scale research and decision-support engine:

* explore 2–3 serious candidate wedges (not a toy A/B)
* build evaluation discipline (segmentation, robustness, evidence)
* define Strategy v1 spec + parameters + promotion gates (paper → staged live)

Exit (Phase 2): Strategy v1 is locked + implemented + paper-evaluated with a formal promotion gate decision (promote / revise / discard).

**Phase 2 baseline is locked.** See `docs/onboarding/PHASE2_BASELINE.md` for the authoritative reference containing all locked decisions (D2-001 through D2-017).

## Phase 3 — Paper hardening + staged live (future)

Goal: OMS/reconciliation live path, monitoring, incident playbooks, staged sizing.
