# Local Sweep Usability Consumer Brief

## Package Metadata

- Package label: WP-12z / AUTO-25.
- Package title: Local Sweep Usability Consumer Brief.
- Package class: Tier 1 documentation-only / decision-support consumer brief.
- Effective base: refreshed `main` after merged WP-12y / AUTO-24.
- Committed files: this document and `docs/project_status.md` only.
- No implementation files.
- No test files.
- No committed JSON spec instance files.
- No committed generated output files.
- No committed sidecar index files.

## Purpose

WP-12z reads the merged WP-12t through WP-12y material descriptively to
evaluate local sweep usability after successful JSON-driven end-to-end
composition.

This brief surfaces findings, visible gaps, and open questions only. It does
not select future implementation direction, pre-commit a post-checkpoint
architecture decision, or make local sweep material canonical.

## Source Material Read

Source documents reviewed:

- `docs/research_pipeline/2026-04-json_sweep_spec_materialization_design.md`
  (WP-12t design).
- `docs/research_pipeline/2026-04-json_sweep_spec_loader_vertical_slice.md`
  (WP-12u loader slice).
- `docs/research_pipeline/2026-04-local_sweep_result_index_design.md`
  (WP-12v result-index design).
- `docs/research_pipeline/2026-04-local_sweep_result_index_vertical_slice.md`
  (WP-12w result-index slice).
- `docs/research_pipeline/2026-04-local_parameter_sweep_usability_checkpoint.md`
  (WP-12x checkpoint).
- `docs/research_pipeline/2026-04-json_sweep_end_to_end_exercise.md`
  (WP-12y exercise).

Helper files reviewed:

- `tools/research_automation/local_json_sweep_spec_loader.py`.
- `tools/research_automation/local_parameter_sweep.py`.
- `tools/research_automation/local_sweep_result_index.py`.

## What The Local Sweep Usability Path Now Enables

Repo truth now supports these local-only capabilities:

- WP-12t designed local JSON sweep-spec materialization around a single-spec
  wrapper object.
- WP-12u implemented a local loader that converts one caller-provided local
  JSON spec file into the existing in-memory `ParameterSweepSpec`.
- `run_local_json_parameter_sweep(...)` delegates to the existing local sweep
  helper only after successful JSON load.
- `run_local_parameter_sweep(...)` runs a bounded deterministic local sweep
  from an explicit `ParameterSweepSpec`, fans out local batch-compatible work,
  builds the existing local run registry, and writes a structural local sweep
  summary only after batch and registry success.
- WP-12v designed local sweep result organization through a structural sidecar
  posture.
- WP-12w implemented `write_local_sweep_result_index(...)`, which indexes an
  already-completed local sweep result without running sweeps, registries, or
  JSON loaders.
- WP-12y verified load -> sweep -> sidecar composition using existing helpers
  only and without helper modification.
- Registry record IDs used by the sweep summary and sidecar are actual
  returned IDs only.
- Generated JSON spec material, sweep outputs, local registry outputs, and
  sidecar outputs remain caller-local and uncommitted.

## Structural Shapes Now Visible

The JSON spec wrapper shape is visible at a high level: a local JSON object
with `spec_version`, `materialization_kind`, `locality`, `boundary_markers`,
and a `parameter_sweep_spec` body that maps to `ParameterSweepSpec`.

The local sweep shape is visible at a high level: a loaded spec becomes a
finite deterministic point set, the points become local batch-run-compatible
items, the batch output root is indexed by the local run registry, and a
`local_parameter_sweep_summary.json` links sweep identity, point results,
batch summary references, registry file reference, actual registry record IDs,
boundary markers, and non-authority flags.

The sidecar index shape is visible at a high level:
`local_sweep_result_index.json` records structural links to the sweep summary,
batch output root, batch summaries, registry file, actual registry record IDs,
point refs, and boundary flags.

WP-12y linked these pieces structurally by using a caller-local JSON spec,
loading it through the WP-12u loader, running the existing local sweep helper,
and writing the WP-12w sidecar for the completed sweep output. This does not
make any JSON spec, sweep output, registry output, or sidecar output canonical.

## What Remains Not Enabled

The merged material still does not enable:

- committed JSON spec instances;
- committed generated sweep outputs;
- committed local registry outputs;
- committed sidecar outputs;
- schema authority;
- `tools.registry` validator authority;
- query-layer exposure;
- CLI or retrieval tooling;
- canonical `research/` artifact placement;
- evidence bridge;
- dashboard, agent, scheduler, daemon, queue, watcher, or trigger behavior;
- Monte Carlo or robustness execution;
- runtime, paper/live, OMS, risk, safe-mode, exchange, broker, or order
  behavior;
- protected-path behavior;
- ranking, scoring, recommendation, approval, promotion, demotion, readiness,
  lifecycle, policy, or downstream authority.

## Usability Gaps Surfaced By The Merged Material

Visible usability gaps from the merged material are:

- Local spec naming and location conventions remain caller-local and not
  standardized.
- Multiple-sweep discoverability remains limited without retrieval tooling.
- The sidecar index exists per completed sweep, but no cross-sweep local index
  exists.
- No CLI exists for loading, running, or inspecting local sweep material.
- No schema or central validator exists for JSON specs or sidecars.
- No query-layer visibility exists by design.
- Generated outputs remain intentionally local and uncommitted.
- Consumer interpretation remains manual and non-authoritative.

These are findings and open gaps only. They are not recommendations.

## Questions For The Later Post-Checkpoint Direction Decision

Later WP-12ab / Main re-engagement may need to address:

- Should local usability stop at documentation and helper-level composition, or
  add local retrieval ergonomics?
- Should JSON spec and sidecar material remain purely caller-local, or is a
  separate local convention needed?
- Is a CLI worth considering, despite the current no-CLI boundary?
- Should schema, validator, and query exposure remain forbidden, or is a later
  architecture decision needed?
- Should the AUTO track pause after checkpoint, move to another local usability
  gap, or re-engage a broader roadmap question?

WP-12z does not select among these questions.

## Boundary And Non-Authority Posture

This brief reads source documents and helper files only. It does not re-run the
WP-12y exercise and does not import generated WP-12y local material.

This brief does not make local material canonical and does not create
implementation, tests, schemas, validators, query exposure, CLI, generated
outputs, evidence bridge, dashboard, agent, scheduler, Monte Carlo behavior,
runtime behavior, or downstream authority.

## Open / Deferred Items

Deferred items remain:

- WP-12aa checkpoint / stability lock.
- WP-12ab post-checkpoint direction decision requiring Main re-engagement.
- Any local retrieval ergonomics.
- Any CLI.
- Any schema, validator, or query exposure.
- Evidence bridge.
- Dashboard, agent, or scheduler behavior.
- Monte Carlo or robustness execution.
- Runtime, paper, or live integration.

## Non-Claims

WP-12z does not create implementation, tests, helper changes, integration
layers, JSON spec instances, generated outputs, local registry outputs,
sidecar result-index outputs, schemas, validators, query-layer exposure, CLI,
configs, dependencies, data changes, evidence artifacts, evidence bridges,
dashboards, agents, schedulers, daemons, queues, watchers, triggers, Monte
Carlo behavior, runtime, paper/live, OMS, risk, safe-mode, exchange, broker,
order behavior, protected-path behavior, or downstream authority.

WP-12z does not claim best parameters, ranking, scoring, recommendation,
approval, readiness, promotion, demotion, lifecycle transition, policy action,
runtime action, evidence value, query authority, schema authority, validator
authority, canonical artifact status, or downstream authority.
