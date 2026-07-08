# Repo-truth discovery — WP-LABPROD-COCKPIT-PIPELINE-STATE-02

Base commit inspected: `origin/main` at `a57af3f` (merge of PR #613).

## Dependencies confirmed merged on main

- PR #612 / `WP-LABPROD-PIPELINE-ORCHESTRATOR-01` — `tools/lab_pipeline/**` present
  (`model.py`, `orchestrator.py`, `run.py`, `state.py`).
- PR #613 / `WP-LABPROD-COCKPIT-STATIC-01` — `tools/lab_cockpit/**` present
  (`model.py`, `render.py`, `run.py`, `__init__.py`) with `tests/test_lab_cockpit.py`.

## Key finding: no committed pipeline run packets

The orchestrator writes run packets under
`scratch/WP-LABPROD-PIPELINE-ORCHESTRATOR-01/outputs/<pipeline_run_id>/`, which is
**not committed** on main (only discovery/contract scratch artifacts are committed
there). So there is no committed pipeline run for the cockpit to project.

Decision: this package generates a small, honest, package-local fixture set of
run packets using the *real* orchestrator (`run_pipeline`), then commits them
under `scratch/WP-LABPROD-COCKPIT-PIPELINE-STATE-02/pipeline_runs/`. See
`generate_pipeline_run_fixtures.py`. The objective explicitly authorizes
"existing committed or package-local pipeline output packets" as the data source.

## Pipeline output shape (from `tools/lab_pipeline`, verified by running it)

Per run directory `<pipeline_run_id>/`:

- `pipeline_state.json` — `pipeline_status` in {`complete`, `awaiting_prereg_approval`,
  `blocked`}; `current_stage`; `stage_statuses[]` (13 stages, each with
  `status` in {`not_started`, `complete`, `awaiting_approval`, `blocked`});
  `blocked_reasons[]`; `source_idea`, `symbol`, `timeframe`, `requested_by`,
  `request_id`; `non_authority_flags`.
- `pipeline_trace.json` — ordered `events[]`.
- `approval_requirement.json` — `preregistration_packet_sha256`,
  `required_fields.approval_scope`. Present once the prereg packet is prepared.
- `noncanonical_execution_summary.json` — only on approved runs;
  `runner_invoked=false`, `execution_kind=deterministic_spine_proof`.
- `operator_review_packet.md`, `non_authority_assertions.json`,
  `artifact_index.json` (basename→sha256), `preregistration_packet.json`,
  `pipeline_request.json`.

## Path-safety caveat found

The orchestrator embeds **absolute machine paths** in `artifact_refs` /
`artifact_index` / operator review packet. Two mitigations:

1. Committed fixtures are path-sanitized to repo-relative and their
   `artifact_index` hashes recomputed (honest for committed bytes).
2. The cockpit projection never surfaces embedded paths — it reconstructs
   repo-relative artifact paths from the run directory and looks up sha256 by
   basename. So even raw (unsanitized) orchestrator output projects cleanly
   (verified by a contract test against a temp-dir orchestrator run).

## Referenced-path status

All required-read paths under `docs/research/*` and `docs/status_entries/*` exist
as named on main; no renames encountered. No open PR touches `tools/lab_cockpit/**`,
`tests/test_lab_cockpit*`, cockpit docs/scratch, or `tools/lab_pipeline/**`
implementation files.
