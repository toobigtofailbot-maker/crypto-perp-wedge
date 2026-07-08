# Pipeline-state cockpit projection contract

Read-only contract between `tools/lab_pipeline` run packets and the cockpit
pipeline-state panel (`tools/lab_cockpit`). The cockpit is a pure projection; it
reads packets and renders. It never writes packets, invokes the runner, mutates
approval markers, or exposes any control.

## Data source

Default: `scratch/WP-LABPROD-COCKPIT-PIPELINE-STATE-02/pipeline_runs/<run_id>/`
(constant `PIPELINE_RUNS_ROOT`). `build_pipeline_state(repo_root, runs_root)`
accepts an override so tests can point at any orchestrator output root.

A run directory is considered only if it contains at least one known pipeline
artifact file. Runs are ordered deterministically by run id.

## Per-run status mapping

| pipeline_status (raw)        | + condition                     | display_status            | label                     |
| ---------------------------- | ------------------------------- | ------------------------- | ------------------------- |
| `complete`                   | `runner_invoked == false`       | `complete_spine_only`     | COMPLETE · SPINE ONLY     |
| `complete`                   | `runner_invoked == true`        | `complete`                | COMPLETE                  |
| `awaiting_prereg_approval`   | —                               | `awaiting_prereg_approval`| AWAITING PREREG APPROVAL  |
| `blocked`                    | —                               | `blocked_or_invalid`      | BLOCKED                   |
| anything else / unknown      | —                               | `blocked_or_invalid`      | UNKNOWN / INVALID         |
| `pipeline_state.json` missing/malformed | —                    | `blocked_or_invalid`      | MALFORMED / UNAVAILABLE   |

`runner_invoked` is read from `noncanonical_execution_summary.json` when present;
otherwise `null`. `complete_real` is expected to be 0 until
`WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02` wires real adapters.

## Fail-closed rules

- Runs directory absent or empty → panel `available=false`, `status=unavailable`.
- Run present but `pipeline_state.json` missing/malformed → invalid run card,
  `display_status=blocked_or_invalid`, no fabricated state.

## Honest labeling

While no run invoked a real runner, the panel is `spine_only=true` and shows:

> State spine / prereg approval contract only; real agent/runner adapter flow not
> yet complete.

The approved run is a deterministic spine proof and is never presented as a real
completed hypothesis run.

## Path & hash handling

- Artifact paths surfaced are repo-relative, reconstructed as
  `{runs_root}/{run_id}/{filename}`; embedded absolute paths are never surfaced.
- sha256 values are read from the run's own `artifact_index.json` by basename
  (display only; the cockpit does not re-verify hashes).

## Adapter-gap posture

`adapter_gap_register` is not emitted by PR #612 packets; the panel surfaces the
gap honestly via the spine-only label. A structured per-run adapter-gap row can
be added read-only when a later package emits an adapter gap register.

## No-control guarantee

Rendered HTML contains no `<script>`, `<button>`, `<form>`, `<input>`, `onclick`,
`fetch(`, `setInterval`, `setTimeout`, meta refresh, or external network
reference. Output is byte-deterministic for the same checkout and fixtures.
