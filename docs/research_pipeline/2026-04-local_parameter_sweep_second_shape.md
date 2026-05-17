# Local Parameter Sweep Second Shape (WP-12r / AUTO-17)

## Package metadata

- Package label: WP-12r / AUTO-17.
- Package title: Local Parameter Sweep Second Shape Exercise.
- Package class: Tier 3 local automation exercise.
- Effective base: refreshed `main` after merged WP-12q / AUTO-16.
- Reused helper: `tools/research_automation/local_parameter_sweep.py`.
- Test module: `tests/research_automation/test_local_parameter_sweep_second_shape.py`.

## Purpose

WP-12r exercises the existing WP-12q in-memory local parameter sweep helper
with a second deterministic parameter shape. The exercise confirms that the
helper can enumerate a two-axis scalar grid into four local batch-compatible
points while preserving structural-only, local-only, non-authoritative
boundaries.

WP-12r reuses the existing WP-12q helper and does not add a new helper.

## Scope

WP-12r adds this documentation page, one focused second-shape test module, and
a narrow `docs/project_status.md` branch-state entry. It uses caller-provided
temporary local output roots in tests and commits no generated local outputs.

WP-12r exercises a two-axis scalar grid only. It does not parse, write,
validate, or commit JSON sweep specification files.

## Non-goals

WP-12r does not add a sweep-spec validator, schema, CLI, central query-layer
exposure, config, dependency, committed generated output, dashboard, agent,
scheduler, Monte Carlo, evidence bridge, runtime/paper/live, OMS/risk/safe-mode,
exchange/broker/order behavior, protected-path behavior, policy/scoring/ranking/
recommendation, approval, promotion, readiness, lifecycle, or downstream
authority.

## Dependency on WP-12q

WP-12q introduced `ParameterSweepSpec`, deterministic sweep point enumeration,
local batch fan-out, local registry integration, and one structural sweep
summary file. WP-12r depends on those existing behaviors and changes none of
them.

If the WP-12q helper could not support this second shape, WP-12r would stop and
report the incompatibility instead of modifying the helper. Current repo truth
supports the required exercise without helper changes.

## Second-shape spec

The WP-12r exercise uses an in-memory `ParameterSweepSpec` with:

- `sweep_id`: `SWEEP-WP12R-0001`;
- `candidate_id`: `H-004`;
- `evaluation_purpose`: `AUTO-17 local parameter sweep second-shape fixture`;
- `data_refs`: `("local_fixture:wp12r:auto17:sample",)`;
- `timeframe`: `1h`;
- `evaluation_window`: `2026-04-03T00:00:00Z` through `2026-04-03T01:00:00Z`;
- `base_parameters`: `{"mode": "second_shape", "max_rows": 1}`;
- `sweep_parameters`: `{"zeta": ("low", "high"), "alpha": (1, 2)}`;
- `pipeline_version`: `wp_12r_auto_17_fixture_v1`;
- `static_metadata`: `{"source_package": "WP-12r / AUTO-17"}`.

The sweep axes are intentionally supplied in non-lexicographic insertion order.

## Expected deterministic enumeration

The existing helper enumerates axes by lexicographic parameter name and
preserves caller-provided value order within each axis. The expected axis order
is `alpha`, then `zeta`.

Expected point parameter values are:

```python
(
    {"alpha": 1, "zeta": "low"},
    {"alpha": 1, "zeta": "high"},
    {"alpha": 2, "zeta": "low"},
    {"alpha": 2, "zeta": "high"},
)
```

Point indexes are `1` through `4`, and local output paths are
`sweep-point-0001` through `sweep-point-0004`.

## Batch fan-out behavior

Each sweep point fans out into one `BatchManifestItem` with the sweep point ID
as `source_id`, H-004 candidate context, the WP-12r fixture data reference, the
1h evaluation window, and combined base plus sweep parameters.

The helper calls the existing local batch runner once with four items and
conservative resource limits: `max_item_count=4`, `max_local_jobs=1`,
`max_concurrency=1`, and `failure_threshold=0`.

The helper's current static batch metadata remains the existing WP-12q helper
metadata. WP-12r records that behavior in tests and does not change it.

## Registry behavior

After local batch success, the helper calls the existing local registry builder
with the caller-provided batch output root and caller-provided registry output
root.

WP-12r records only actual registry record IDs returned by the existing local
registry helper and does not fabricate per-point registry IDs.

## Structural summary behavior

On success, the existing helper writes `local_parameter_sweep_summary.json`
under the caller-provided local output root. The summary records structural
counts, point results, output references, batch references, registry references,
actual registry record IDs, and local boundary markers.

The summary has no interpretive authority fields such as best parameter,
winner, rank, score, recommendation, approval, promotion, readiness, lifecycle,
policy action, runtime action, or paper/live readiness.

## Failure behavior

The second-shape tests confirm that `max_point_count=3` blocks the four-point
grid before any downstream local batch or registry call. That failure writes no
files under the caller-provided output roots.

## Test coverage

The WP-12r test module covers:

- successful batch, registry, and summary output for the two-axis shape;
- stable point IDs and point indexes across clean roots;
- lexicographic axis enumeration with caller value order preserved;
- source ID propagation from sweep points to summary point results;
- batch fan-out into four combined-parameter items;
- downstream-call blocking when the point count exceeds `max_point_count`;
- absence of positive interpretive authority fields in summary JSON;
- preservation of local-only, research-only, non-authoritative, and
  no-committed-evidence markers.

## Boundary preservation

WP-12r preserves:

- `local_only=True`;
- `research_only=True`;
- `non_authoritative=True`;
- `creates_committed_evidence=False`;
- no runtime, paper/live, OMS, risk, or safe-mode contact;
- no exchange, broker, order, scheduler, daemon, queue, watcher, or trigger
  contact.

## Known limitations

- The exercise is in-memory only.
- The exercise covers one two-axis scalar grid with four points.
- There is no JSON sweep-spec file.
- There is no new validation artifact, schema, CLI, query exposure, or
  committed generated output.
- Current local registry behavior remains whatever the existing helper returns
  for the local batch output root.

## Open / deferred items

Deferred items remain separately authorized work only: JSON sweep-spec files,
formal schema or validator work, broader parameter value support, larger sweep
limits, query-layer exposure, registry shape changes, and any downstream
evidence bridge.

## WP-12s checkpoint direction, non-binding

WP-12s remains a possible separately drafted checkpoint if requested and
accepted. WP-12r does not authorize WP-12s or any later package.

## Non-claims

WP-12r creates no schema, validator, query-layer exposure, CLI, config,
dependency, data, evidence artifact, committed output, result-store
implementation, dashboard, agent, scheduler, daemon, queue, watcher, trigger,
Monte Carlo, evidence bridge, runtime, paper/live, OMS, risk, safe-mode,
exchange/broker/order behavior, protected-path behavior, optimizer/scoring/
ranking/recommendation, approval, promotion, demotion, readiness, lifecycle,
policy, or downstream authority.
