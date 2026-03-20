# Open Questions (Phase 2)

## Strategy

* Which 2–3 strategy families should we test first (non-HFT, 1h–4h disciplined)?
* What is the minimal feature set per candidate (avoid feature sprawl)?
* How do we define confidence/ranking outputs without overfitting?

## Evaluation / promotion

* What are paper promotion gates (DD, turnover, stability, parity checks)?
* What time windows/regimes must be covered before any promotion?

## Data / context

* Do we upgrade to 15m canonical base later, or stay 1h/4h for v1?
* Which context features are allowed to influence trade permission beyond the current macro windows?

## Agents / tools

* Where do Claude Skills / OpenClaw add real ROI?
* Which parts remain advisory only vs gated influence?

## Operational

* When do we introduce monitoring (Prometheus/Grafana) vs minimal alerts?
* What is the staged-live plan (small size, incident playbook, rollback)?
