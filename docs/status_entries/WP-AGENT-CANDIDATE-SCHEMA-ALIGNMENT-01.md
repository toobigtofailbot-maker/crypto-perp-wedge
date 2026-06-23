# WP-AGENT-CANDIDATE-SCHEMA-ALIGNMENT-01 Branch State

## Scope Summary

Additive schema-alignment package for preserving scratch candidate-review
packet evidence inside the canonical candidate lifecycle registry schema.

Changed scope is limited to:

- `research/schemas/candidate_lifecycle_registry.schema.json`
- `tests/fixtures/candidate_lifecycle_registry/valid_candidate_review_packet_crossing.candidate_lifecycle_registry.json`
- `tests/test_validate_candidate_registry.py`
- `docs/architecture/2026-06-candidate_schema_alignment_for_agent_crossing.md`
- `docs/status_entries/WP-AGENT-CANDIDATE-SCHEMA-ALIGNMENT-01.md`
- `scratch/WP-AGENT-CANDIDATE-SCHEMA-ALIGNMENT-01/repo_truth_discovery.md`

## Main Authorization

Main authorized the schema-alignment decision after the canonical crossing
design surfaced a mismatch between scratch candidate-review packet output and
the canonical candidate lifecycle registry schema. This package resolves the
schema decision before any canonical crossing build.

## Repo-Truth Discovery

Discovery inspected the merged canonical crossing design/status/discovery
artifacts, candidate-review packet agent/tests/output, robustness diagnostician
agent/tests/output, formalizer-runner bridge agent/tests/output, candidate
lifecycle helper/schema/fixture/validator/tests, registry/query surfaces, and
the local override files for schema/validator/query directories.

Key repo-truth facts:

- Scratch candidate-review packets preserve denominator counts, row
  dispositions, skipped diagnostics, missing diagnostic states, data
  warnings/blockers, funding mode, source paths/hashes, and non-authority
  flags.
- The prior candidate lifecycle registry schema had no first-class home for
  those fields.
- `tools/registry/AGENTS.override.md` prohibits modifying validator behavior
  in this package.
- No real candidate lifecycle registry artifact exists under `research/`.

## Needs-Schema-Decision Items

Resolved through first-class event evidence:

- denominator counts and row dispositions;
- source lineage paths/hashes;
- completed/skipped robustness diagnostics;
- missing per-trade, OOS/fold, and funding-stress states;
- data availability warnings, blockers, and caveat classes;
- funding cost mode and funding stress status;
- non-authority flags; and
- append-only/no-overwrite/correction semantics.

Runner metric summaries remain source-hash-bound to the candidate-review
packet and bridge artifacts rather than becoming parallel canonical metric
truth.

## Schema / Vocabulary Alignment

Added `event_type=candidate_review_packet_crossed` to audit events.

Added `crossing_evidence`, required only for that event type, with:

- `source_lineage`
- `denominator_snapshot`
- `diagnostics_summary`
- `data_availability`
- `funding`
- `non_authority_flags`
- `append_only_semantics`

Added artifact reference enum values for candidate-review packet, formalizer,
bridge packet, denominator ledger, robustness diagnostics/review packet,
operator approval, and crossing approval.

Crossing events are constrained to `from_status=null` and
`to_status=proposed`, so the event does not imply validation, paper candidacy,
paper running, live promotion, or readiness.

## Field-Level Mapping

Detailed mapping is documented in
`docs/architecture/2026-06-candidate_schema_alignment_for_agent_crossing.md`.

Summary:

- packet/source paths and hashes map to `source_lineage`;
- five denominator counts, ledger path/hash, declared count, row dispositions,
  and all-source-rows-preserved flag map to `denominator_snapshot`;
- completed, skipped, unsupported, and missing diagnostics map to
  `diagnostics_summary`;
- warnings/blockers/coverage/constraint/caveat classes map to
  `data_availability`;
- funding mode and stress status map to `funding`;
- packet non-authority language maps to required true crossing
  `non_authority_flags`; and
- append-only/no-overwrite/correction rules map to `append_only_semantics`.

## Append-Only / Event Semantics

The schema decision supports append-only/event-shaped crossing:

- new event only;
- no overwrite;
- no deletion;
- corrections require explicit correction/supersession event in a future
  package;
- source hashes preserved;
- denominator snapshot preserved;
- caveats preserved; and
- missing diagnostics preserved.

No crossing implementation is included here.

## Validator / Integrity Gate Changes

No `tools/registry` validator behavior changed. Existing
`tools.registry.validate_candidate_registry` continues to load the schema and
run existing semantic checks.

Added regression tests prove schema behavior for valid and invalid crossing
event evidence. Query-layer behavior is unchanged because no real
`research/candidate_lifecycle_registry/` artifact exists and this package is
not authorized to write one.

## Fake Fixture Coverage

Added a fake/test-only candidate lifecycle registry fixture:

```text
tests/fixtures/candidate_lifecycle_registry/valid_candidate_review_packet_crossing.candidate_lifecycle_registry.json
```

It preserves:

- all five denominator counts;
- all eight row dispositions;
- packet/formalizer/bridge/robustness/ledger paths and hashes;
- skipped diagnostics and skipped reasons;
- missing per-trade, OOS/fold, and funding-stress states;
- data warnings, blockers, coverage classes, constraint classes, and caveats;
- `funding_cost_mode=off` with funding stress not run;
- non-authority flags; and
- append-only semantics.

## Candidate Lifecycle Helper Alignment

The scratch lifecycle helper remains unchanged. It uses a different lifecycle
state vocabulary from the candidate lifecycle registry schema and is not a
canonical write path. Future crossing work must resolve helper/vocabulary
alignment before implementation if it needs helper output changes.

## LangGraph Dependency Note

LangGraph dependency cleanup is a separate housekeeping decision or should be
folded into a future infra/dependency cleanup WP. This schema-alignment WP
does not touch LangGraph dependencies.

## Stop Conditions

No stop condition fired during this package.

Future crossing must stop if source hashes mismatch, denominator counts or row
dispositions are incomplete, skipped diagnostics or data/funding caveats are
hidden, non-authority flags are missing, a crossing would overwrite prior
canonical evidence, or a crossing would imply promotion/readiness/paper/live
authority.

## Validation Status

- Ambient Python 3.14
  `python -m pytest tests -k "candidate_lifecycle or candidate_review or candidate_schema" -q`:
  FAILED during collection because the ambient interpreter lacks repo
  dependencies including `pandas` and `numpy`; not passing evidence.
- Repo-venv
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests -k "candidate_lifecycle or candidate_review or candidate_schema" -q`:
  PASS, 50 passed and 2,131 deselected.
- Repo-venv `python -m pytest tests/test_validate_candidate_registry.py -q`:
  PASS, 19 passed.
- Repo-venv `python -m tools.registry.validate_candidate_registry`: PASS.
- Repo-venv `python -m tools.registry.validate_result_populations`: PASS.
- Repo-venv `python -m tools.registry.validate_data_feature_availability`: PASS.
- Repo-venv `python -m tools.research_query.run --list-views`: PASS, 124
  views listed.
- Repo-venv `python tools/dev/diff_scope_summary.py`: PASS/advisory; it
  reports the authorized schema path under a generic `research/` forbidden-path
  pattern and no runtime/protected-path match.
- `git diff --check`: PASS.
- Full pytest: not run; package validation used the scoped selector and
  required validators above.

## Boundary Summary

No real canonical candidate registry instance was written. No canonical
crossing was implemented. No registration, freeze, promotion, paper/live
readiness, ranking, recommendation, Result Population, Strategy Spec, Variant
Manifest, Sweep Plan, trial log, runtime, paper/live, OMS, risk,
reconciliation, capital, private endpoint, provider/API/network, dependency,
or LangGraph cleanup path was touched.

## Non-Authority Statement

This package creates schema, documentation, tests, and fake fixture coverage
only. It creates no evidence authority, candidate authority, ranking authority,
promotion authority, paper/live readiness, runtime authority, trading signal,
capital authority, broker/exchange authority, OMS/reconciliation/risk
authority, approval authority, or downstream execution authority.

## Karl-Gated Crossing Build Boundary

The first actual agent-touched canonical write remains Karl-gated and is not
authorized here. A later build must separately authorize the real storage
target, approval artifact schema/storage, source contract validator, hash
preflight, ToolContext permission changes, query/integrity exposure, exact
post-write validation, and first real crossing policy.
