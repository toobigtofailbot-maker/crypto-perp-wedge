# Local Sweep Result Index Vertical Slice

## Package Metadata

- Package label: WP-12w / AUTO-22.
- Package title: Local Sweep Result Index Sidecar Vertical Slice.
- Package class: Tier 3 local automation implementation slice.
- Effective base: refreshed `main` after merged WP-12v / AUTO-21.
- Implementation module: `tools/research_automation/local_sweep_result_index.py`.
- Test module: `tests/research_automation/test_local_sweep_result_index.py`.
- Dependency: merged WP-12v local sweep result index design.

## Purpose

WP-12w implements the first local-only structural sidecar writer for completed
local parameter sweep results. The writer indexes already-completed local sweep
results only. It does not run sweeps, run registries, run JSON loaders, or
interpret sweep outcomes.

## Implementation Summary

The implementation adds `write_local_sweep_result_index(...)`, which accepts an
existing sweep result object and a caller-provided local output root. When the
sweep result has an existing `local_parameter_sweep_summary.json` and protected
boundaries are preserved, it writes exactly one sidecar file:

```text
local_sweep_result_index.json
```

The writer is tolerant of the existing `LocalParameterSweepResult` shape by
using structural attributes instead of requiring exact type identity. It does
not modify existing sweep, JSON-loader, batch, or registry helpers.

## Sidecar Writer Behavior

The writer:

- writes only under caller-provided local output roots;
- requires `output_root` to already exist and never creates directories;
- requires `sweep_result.summary` to be present;
- requires `sweep_result.summary_file` to exist;
- requires local-only, research-only, non-authoritative,
  no-committed-evidence, and protected-boundary flags;
- records only actual `registry_record_ids` already present on the sweep
  summary;
- preserves structural point references from `summary.point_results`;
- writes deterministic JSON with sorted keys, two-space indentation, and a
  trailing newline;
- writes no generated committed outputs.

On failure it writes no files, returns `index=None`, `index_file=None`,
`written_files={}`, non-empty failure reasons, and
`protected_boundary_preserved=False`.

## Sidecar File Shape

The sidecar records structural fields only:

- index version, kind, implementation ID, and package label;
- sweep ID;
- inert `spec_source` and `loader_source` strings;
- sweep summary, batch summary, batch summary validation, and registry file
  references;
- caller-provided batch output root reference;
- actual registry record IDs;
- point count;
- point references containing point ID, point index, output path, batch item
  ID, dry-run run ID, and status;
- boundary markers and boundary flags.

It does not include policy, scoring, ranking, recommendation, approval,
promotion, demotion, readiness, lifecycle, runtime action, or downstream
authority fields.

## Tests Added

`tests/research_automation/test_local_sweep_result_index.py` covers:

- successful sidecar write after an existing local sweep summary;
- missing output root with no directory creation;
- missing summary and missing summary-file failures;
- protected-boundary and required boundary-flag failures;
- inert source string recording;
- actual registry record IDs only;
- no fabricated per-point registry IDs;
- no authority fields in JSON or result dataclasses;
- no public execution wrapper or direct imports of sweep, JSON sweep, or
  registry execution helpers.

All generated test material is created under `tmp_path`.

## Known Limitations

- There is no formal schema.
- There is no `tools.registry` validator.
- There is no query-layer exposure.
- There is no CLI.
- There is no separate index validation helper.
- The writer does not canonicalize paths into `research/`.
- The writer does not create JSON sweep-spec instances.
- Per-point registry IDs remain unsupported unless actual future repo truth
  provides them through separate authorization.

## Open / Deferred Items

Deferred items require separate authorization:

- formal schema or validator;
- `tools.registry` validator;
- query-layer exposure;
- CLI or retrieval tooling;
- richer local path conventions;
- evidence bridge;
- dashboard, agent, scheduler, or Monte Carlo behavior;
- runtime, paper-live, OMS, risk, safe-mode, exchange, broker, or order
  behavior;
- downstream authority.

## Boundary And Non-Authority Posture

WP-12w creates no schema, creates no `tools.registry` validator, creates no
query-layer exposure, creates no CLI, changes no configs, dependencies, or
data, creates no JSON spec instances, creates no evidence bridge, and creates
no dashboard, agent, scheduler, or Monte Carlo behavior.

It touches no runtime, paper-live, OMS, risk, safe-mode, exchange, broker,
order, protected-path, or live-trading behavior.

It creates no policy, scoring, ranking, recommendation, approval, promotion,
demotion, readiness, lifecycle, runtime action, paper-live action, or
downstream authority.
