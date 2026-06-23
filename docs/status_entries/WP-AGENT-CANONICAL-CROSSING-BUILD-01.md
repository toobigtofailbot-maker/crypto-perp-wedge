# WP-AGENT-CANONICAL-CROSSING-BUILD-01 Branch State

## Scope Summary

Builds a fixture-only canonical crossing mechanism for candidate-review packets
and proves it against fake/test registry copies.

## Karl Authorization

Karl authorized building the canonical crossing mechanism and proving it
end-to-end against fake/test fixtures only.

## Fixture-Only Boundary

The builder accepts only fixture/test inputs from `tests/fixtures/` or the
active WP scratch prefix and writes only under
`scratch/WP-AGENT-CANONICAL-CROSSING-BUILD-01/outputs/<run_id>/`.

## First Real Crossing Boundary

No real crossing is implemented or executed. `WP-AGENT-FIRST-REAL-CROSSING-01`
remains separately Karl-gated.

## Repo-Truth Discovery

Discovery is recorded in
`scratch/WP-AGENT-CANONICAL-CROSSING-BUILD-01/repo_truth_discovery.md`.

Key findings:

- PR #549 requires explicit content-before-lock approval, source hash
  preflight, denominator/caveat preservation, append-only write semantics,
  ToolContext routing, and audit output.
- PR #551 resolved the schema target through
  `candidate_review_packet_crossed` events with `crossing_evidence`.
- The current committed scratch candidate-review packet family has a
  robustness diagnostics hash mismatch, so positive tests use controlled
  fixtures with matching byte hashes.
- No real candidate lifecycle registry artifact exists under `research/`.

## Crossing Mechanism

Added `tools/candidate_lifecycle/canonical_crossing_build.py`.

The builder:

- loads a candidate-review packet, crossing approval artifact, and fake
  registry copy;
- routes crossing action, reads, and writes through ToolContext;
- validates approval, content review, source hashes, denominator/row
  disposition, skipped diagnostics, data/funding posture, and non-authority
  flags;
- constructs one `candidate_review_packet_crossed` event;
- appends it only to a fake registry output under scratch;
- runs the existing candidate registry validator on the fake output; and
- writes required audit artifacts.

## Approval Artifact Contract

The fixture approval contract requires all package-listed fields, including
`content_reviewed_hash`, all source path/hash bindings, `fixture_only=true`,
`canonical_crossing_allowed=true`, `append_only=true`, `no_promotion=true`,
`no_readiness=true`, and operator acknowledgments for missing diagnostics,
data warnings, and funding mode.

## Content-Before-Lock Check

The builder blocks unless `content_reviewed=true` and
`content_reviewed_hash` equals the loaded candidate-review packet byte hash.

## Source / Lineage Hash Preflight

The builder verifies that approval path/hash values match packet lineage and
then recomputes actual source file hashes for formalizer, bridge, robustness,
and denominator ledger sources.

## Denominator / Row-Disposition Preflight

The builder requires all five denominator counts, a declared trial count equal
to the row-disposition length, `all_source_rows_preserved=true`, and row
status counts matching the denominator counts.

## Data Availability and Funding Caveat Preservation

The builder requires data warning/blocker lists and funding mode/stress status
to remain present, then maps them into `crossing_evidence.data_availability`
and `crossing_evidence.funding`.

## Non-Authority Flag Validation

The builder requires packet non-authority flags for no evidence, candidate
authority, promotion authority, ranking authority, paper/live readiness,
trading signal, and human review required. The crossing event writes schema
non-authority declarations and crossing non-authority flags as true.

## Append-Only Fake Write

The builder appends one new event to a fake registry copy, refuses event ID
collisions, refuses existing lifecycle events for the target fake candidate,
and does not mutate the input fake registry file.

## Post-Write Validation

The builder invokes existing candidate lifecycle registry validation on the
scratch output directory after writing the fake output registry.

## ToolContext Integration

Added a narrow ToolContext role/action:

```text
role: canonical_crossing_builder_fixture
action: build_fixture_canonical_crossing
```

The action is closed to active WP scratch outputs and inherits hard blocks for
canonical/protected paths, production lifecycle actions, runtime/paper/live,
OMS/risk/reconciliation/capital, credentials, private endpoints, network, and
provider API calls.

## Audit Outputs

The builder writes:

- `crossing_input_manifest.json`
- `crossing_approval_validation.json`
- `crossing_preflight_report.json`
- `fake_registry_before_hash.json`
- `fake_registry_after_hash.json`
- `post_write_validation_report.json`
- `crossing_audit_log.json`
- `crossing_result_packet.json`

The result packet states fixture-only posture, no real canonical evidence
written, and the separate Karl gate for first real crossing.

## Adversarial Boundary Tests

Added `tests/test_agent_canonical_crossing_build.py` with positive fixture
crossing coverage and blocked/audited cases for missing/false fixture
approval, missing content review, packet/source hash mismatches, denominator
and row-disposition hiding, skipped diagnostic hiding, data/funding hiding,
non-authority flag removal, promotion/readiness implications, overwrite/event
collision, real research registry output targets, canonical RP/Strategy
Spec/Variant/Sweep/trial-log targets, protected runtime/OMS/risk/reconciliation
targets, credentials, private endpoint, network/provider API, and ToolContext
bypass-style production actions.

## Validation Status

Validation performed on this branch:

- Ambient `python -m pytest tests/test_agent_candidate_review_packet.py ...`:
  failed during collection because ambient Python lacks `pandas`; not passing
  evidence.
- Repo-root venv
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_validate_candidate_registry.py tests/test_agent_candidate_review_packet.py tests/test_agent_toolcontext_sandbox.py -q`:
  PASS, 132 passed.
- Repo-root venv
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_agent_canonical_crossing_build.py tests/test_validate_candidate_registry.py tests/test_agent_candidate_review_packet.py tests/test_agent_toolcontext_sandbox.py -q`:
  PASS, 166 passed.
- Repo-root venv
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_validate_result_populations.py tests/test_validate_data_feature_availability.py -q`:
  PASS, 69 passed.
- Repo-root venv `python -m tools.registry.validate_candidate_registry`:
  PASS.
- Repo-root venv `python -m tools.registry.validate_result_populations`:
  PASS.
- Repo-root venv
  `python -m tools.registry.validate_data_feature_availability`: PASS.
- Repo-root venv `python -m tools.research_query.run --list-views`: PASS,
  124 views listed.
- Repo-root venv `python tools/dev/diff_scope_summary.py`: PASS, no
  forbidden-path matches.
- `git diff --check`: PASS.
- Full pytest with repo-root venv: timed out at 10 minutes with no emitted
  failure details; not passing evidence.

## Boundary Summary

No real canonical candidate registry instance was written. No real crossing
was executed. No promotion, freeze, registration, readiness, paper/live,
runtime, OMS, risk, reconciliation, capital, broker/exchange, private
endpoint, provider/API, network, LangGraph dependency, canonical Result
Population, Strategy Spec, Variant Manifest, Sweep Plan, or trial-log path is
touched.

## Non-Authority Statement

This package creates only fixture/test crossing mechanics and audit outputs.
It creates no evidence authority, candidate authority, ranking authority,
promotion authority, paper/live readiness, runtime authority, trading signal,
capital authority, broker/exchange authority, OMS/reconciliation/risk
authority, approval authority, or downstream execution authority.

## Future WP-AGENT-FIRST-REAL-CROSSING-01 Gate

A first real crossing still requires a separate Karl-gated package, a real
candidate-review packet selected by humans, full source content surfaced before
approval, a real approval artifact, explicit real storage authorization, and
fresh validation over current repo truth.
