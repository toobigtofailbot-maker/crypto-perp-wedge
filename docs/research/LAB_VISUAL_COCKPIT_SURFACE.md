# Lab Visual Cockpit Surface

The lab visual cockpit is a separate static read-only layer beside the audit dashboard. The audit dashboard remains the deterministic source-of-truth compliance/provenance surface.

## Boundary

- Static HTML/CSS output only.
- Consumes committed repo artifacts and generated package-local evidence.
- Does not fetch network data.
- Does not expose forms or command controls.
- Does not create candidate, crossing, promotion, paper/live, runtime, OMS, risk, or reconciliation authority.
- Missing equity, drawdown, returns, and MC/robustness distributions are rendered as unavailable or withheld rather than fabricated.

## Reproducible output

`python -m tools.lab_visual_cockpit.run --out-dir build/lab_visual_cockpit`

Generated files:

- `build/lab_visual_cockpit/index.html`
- `build/lab_visual_cockpit/cockpit_data.json`
- `build/lab_visual_cockpit/cockpit.md`

## Panels

- Lab overview
- Capability completion
- Strategy / research-job explorer
- Backtest visualization with unavailable curve states
- MC / robustness with withheld/unavailable states
- Factory / activity timeline
- Candidate / review funnel
- Operator reports
