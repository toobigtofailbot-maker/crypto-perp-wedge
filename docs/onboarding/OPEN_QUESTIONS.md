# Open Questions (Phase 2)

## Strategy

**RESOLVED:** Strategy families and feature sets are addressed by D2-001 (research-first), D2-002 (lightweight backtester), D2-006 (≤5 free parameters gate). See `docs/onboarding/PHASE2_BASELINE.md`.

* Which 2–3 strategy families should we test first (non-HFT, 1h–4h disciplined)?
* What is the minimal feature set per candidate (avoid feature sprawl)?
* How do we define confidence/ranking outputs without overfitting?

## Evaluation / promotion

**RESOLVED:** Promotion gates and time windows are locked in D2-006 and D2-007. See `docs/onboarding/PHASE2_BASELINE.md`.

* What are paper promotion gates (DD, turnover, stability, parity checks)?
* What time windows/regimes must be covered before any promotion?

## Data / context

**RESOLVED:** Data sourcing and timeframes are locked in D2-003 and D2-013. See `docs/onboarding/PHASE2_BASELINE.md`.

* Do we upgrade to 15m canonical base later, or stay 1h/4h for v1?
* Which context features are allowed to influence trade permission beyond the current macro windows?

## Agents / tools

**RESOLVED:** Tool adoption/rejection and agent roster are locked in D2-010, D2-011, and D2-012. See `docs/onboarding/PHASE2_BASELINE.md`.

* Where do Claude Skills / OpenClaw add real ROI?
* Which parts remain advisory only vs gated influence?

## Operational

* When do we introduce monitoring (Prometheus/Grafana) vs minimal alerts?
* What is the staged-live plan (small size, incident playbook, rollback)?
