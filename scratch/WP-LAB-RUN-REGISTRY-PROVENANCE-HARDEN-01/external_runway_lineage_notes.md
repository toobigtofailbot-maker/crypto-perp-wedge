# External Runway Lineage Notes

This package uses the saved external adoption runway only as read-only lineage context where committed repo artifacts already exist.

- Analytics metrics: existing advisory report `scratch/EXT-INTEG-ANALYTICS-METRICS-01/advisory_analytics_report.json` is attached by the existing lab registry builder where lineage matches. No metrics dependency is added.
- Workflow-gen: existing generated sidecar artifacts under `scratch/EXT-INTEG-WORKFLOW-GEN-01/` remain sidecar lineage only. No new artifacts are generated.
- Robustness MC: existing advisory report `scratch/EXT-INTEG-ROBUSTNESS-MC-01/seeded_advisory_mc_report.json` is display-only lineage where attached. No MC is computed here.
- Vectorbt: existing `scratch/EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01/vectorbt_triage_report.json` remains a non-canonical triage sidecar. No import/install is performed.
- CCXT: not used.
- Nautilus: not used.

No external runway item creates ranking, recommendation, gate, candidate, crossing, paper/live, runtime, broker, exchange, order, or execution authority.
