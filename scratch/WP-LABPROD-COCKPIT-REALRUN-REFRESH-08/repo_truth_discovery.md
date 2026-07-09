# Repo Truth Discovery — WP-LABPROD-COCKPIT-REALRUN-REFRESH-08

## Hard-dependency verification

- **PR #624 merged on `main`.** `git log` shows merge commit `129bb28`
  ("Merge pull request #624 …/wp-labprod-pipeline-gates-adapters-05") as HEAD and
  present on `origin/main`. Dependency satisfied.
- **Product pipeline produces advisory review packets.** The gates adapter
  `tools/lab_pipeline/gates_adapter.py::run_product_gates_adapters` writes
  `advisory_review_packet.json` (schema `product_pipeline_advisory_review_packet_v1`)
  over one product runner adapter output. Confirmed by running
  `tests/test_lab_pipeline_gates_adapter.py` (4 passed).
- **Runner + gates output schemas discoverable.**
  - Runner adapter: `tools/lab_pipeline/runner_adapter.py` →
    `product_runner_adapter_result_v1` (denominator_counts,
    direct_runner_reconciliation, runner_outputs).
  - Gates adapter advisory packet: denominator_counts, wfo_oos_result
    (`adapter_status`, withheld_statistics), robustness_result
    (existing_agent_payload.review_packet with diagnostics_completed /
    diagnostics_skipped), candidate_review_result
    (existing_agent_result.status, existing_agent_packet.evidence_gaps /
    blockers), candidate_surface_routing (surface_status, go_auto_* = false,
    candidate_lifecycle_written = false), non_promotion_posture.
- **Existing cockpit tests / build commands known.**
  - Tests: `tests/test_lab_cockpit.py`, `tests/test_lab_cockpit_pipeline_state.py`,
    `tests/test_lab_visual_cockpit_static.py`.
  - Build: `python -m tools.lab_cockpit.run --data-json | --html | --markdown |
    --out-dir <dir>`.
- **No open PR edits cockpit/dashboard/state/query files.** This package only
  touches `tools/lab_cockpit/*`, a new test file, and its own scratch/docs.

## Real-run artifact discoverability

No product runs are committed on `origin/main`: the bridge, runner adapter, and
gates adapter all write to gitignored package `outputs/` roots (e.g.
`scratch/WP-LABPROD-PIPELINE-GATES-ADAPTERS-05/outputs`). This mirrors the prior
`WP-LABPROD-COCKPIT-PIPELINE-STATE-02` situation, which committed a fixture set
produced by the *real* orchestrator.

**Decision (precedented, in-scope):** generate a small committed fixture by
driving the *real* product chain (product bridge prepare → product runner adapter
→ product gates adapters) once into a throwaway temp repo and copying the honest
terminal artifacts into `scratch/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08/product_runs/`.
Every number the cockpit shows is read from a real advisory packet; nothing is
hand-authored. See `generate_product_run_fixtures.py`.

## Product chain entry points reused (no new authority)

- Bridge prepare: `tests/test_agent_formalizer_runner_bridge.py::_run_product`
  (drives `FormalizerRunnerBridge` in product prepare mode).
- Runner adapter: `tools/lab_pipeline/runner_adapter.py::run_product_runner_adapter`.
- Gates adapters: `tools/lab_pipeline/gates_adapter.py::run_product_gates_adapters`.

All three are existing merged code. The cockpit itself invokes none of them; it
reads their committed output read-only.
