# Repo Truth Discovery

## Facts

- PR #624 is merged to `main`: `WP-LABPROD-PIPELINE-GATES-ADAPTERS-05`, merged 2026-07-09T14:52:09Z.
- Local `main` matched `origin/main` at `129bb28424c825a2d0bb1607366dc09bd9ef01c1` before the package branch was created.
- `gh pr list --state open --limit 100` returned no open PRs.
- Existing product pipeline state artifacts are committed under `scratch/WP-LABPROD-COCKPIT-PIPELINE-STATE-02/pipeline_runs`.
- Product runner adapter status fields exist in `tools/lab_pipeline/runner_adapter.py` via `product_runner_adapter_result_v1`, `adapter_status`, `denominator_counts`, and execute approval binding fields.
- Product gates adapter advisory packet fields exist in `tools/lab_pipeline/gates_adapter.py` via `product_pipeline_advisory_review_packet_v1`, `adapter_status`, `denominator_counts`, `runner_result_reference`, and `candidate_surface_routing`.
- No committed product runner/gates `outputs/` directory is present on current repo truth, so current committed status has zero advisory packets ready.

## Inference

- A read-only queue/status projection can be implemented without invoking runner/gates code by scanning JSON artifacts under the existing product scratch roots.
- A completed spine-only pipeline fixture with no runner adapter output is best surfaced as `awaiting_execute_approval`, because the merged runner adapter requires a separate exact-content execute approval before runner execution.

## Decision

- Implement status visibility in a new lightweight module: `tools/lab_pipeline/queue_status.py`.
- Avoid importing runner/gates execution modules in the status surface to prevent accidental dependency or execution coupling.
- Keep all notification fields as dry-run preview metadata only.

## Open Questions

- None blocking for this package.

## Future Options

- A later package may render this model inside the cockpit or operator surface, but this package does not modify cockpit/dashboard controls.
