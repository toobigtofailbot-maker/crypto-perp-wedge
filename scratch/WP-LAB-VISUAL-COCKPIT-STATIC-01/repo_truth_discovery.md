# WP-LAB-VISUAL-COCKPIT-STATIC-01 repo truth discovery

- base commit: `257abf5d19ee7ac99044cc4fea0dcfe62d8502c8`
- PR #596 evidence observed: merged at current `origin/main` merge commit `257abf5d19ee7ac99044cc4fea0dcfe62d8502c8`.
- existing audit dashboard outputs observed: `tools/lab_dashboard/run.py`, `tools/lab_dashboard/data_model.py`, `tools/lab_dashboard/render.py`; left unchanged.
- visual data sources selected: lab completion map, event-tape contract/summary/tape, Side 12 readiness audit, queue replay, notify/report replay, agent/dashboard replay, audit dashboard projection, and committed result populations.
- chart/rendering route selected: dependency-free static HTML/CSS with inline SVG/CSS charts; no script, no forms, no network
- dependency route selected: stdlib Python only; no npm/pip/frontend dependency changes
- files intentionally left unchanged: `tools/lab_dashboard/**`, `tools/lab_reporting/**`, `tools/lab_state/**`, `tools/research_query/**`, `tools/registry/**`, `research/candidate_registry.jsonl`, `research/result_populations/**`, `lib/**`, `configs/**`, `data/**`.
- cockpit read-only/non-authoritative statement: the cockpit is a static artifact viewer only; it performs no server/backend work, live fetch, candidate admission, crossing, promotion, paper/live/runtime action, OMS/risk/reconciliation action, or metric fabrication.
