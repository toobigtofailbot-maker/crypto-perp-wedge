# WP-AGENT-CANONICAL-CROSSING-DESIGN-01 Branch State

## Scope Summary

Docs-only design for a future human-gated canonical crossing from an approved
scratch candidate-review packet to a canonical candidate lifecycle registry
entry or event.

## Main Authorization

Main authorized `WP-AGENT-CANONICAL-CROSSING-DESIGN-01` after the
non-canonical front-half research-agent loop completed. The package is
design-only and does not authorize implementation or canonical writes.

## Design-Only Boundary

Changed files are limited to:

- `docs/architecture/2026-06-agent_canonical_crossing_design.md`
- `docs/status_entries/WP-AGENT-CANONICAL-CROSSING-DESIGN-01.md`
- `scratch/WP-AGENT-CANONICAL-CROSSING-DESIGN-01/repo_truth_discovery.md`

No code, schema, validator, query-layer behavior, ToolContext permission,
canonical registry data, Result Population, Strategy Spec, Variant Manifest,
Sweep Plan, trial log, data, config, dependency, runtime, paper/live, OMS,
risk, reconciliation, capital, broker/exchange, credential, private endpoint,
or live-trading path is changed.

## Repo-Truth Discovery

Discovery inspected the current candidate-review packet agent and tests,
formalizer/bridge/robustness status entries, ToolContext policy, candidate
lifecycle helper, candidate lifecycle registry schema and validator, current
candidate registry, lifecycle-change schema/validator/artifacts, Result
Population and data availability validators, and query-layer lifecycle and
integrity surfaces.

Key repo-truth adjustments:

- The candidate-review packet is scratch-only and non-authoritative.
- The lifecycle helper is scratch-only and uses a state vocabulary different
  from the candidate lifecycle registry fixture schema.
- A real-capable candidate lifecycle registry schema exists, but no real
  candidate lifecycle registry artifact is committed under `research/`.
- Canonical `research/lifecycle_changes/*.lifecycle_change.json` artifacts
  exist for H-001 through H-010 and use the current `proposed`,
  `in_research`, `research_concluded`, `archived`, and related vocabulary.
- Existing ToolContext hard-blocks canonical writes, lifecycle transitions,
  promotion, readiness, runtime, paper/live, OMS/risk/reconciliation, capital,
  credentials, network, provider memory as truth, and evidence suppression.

## Crossing Contract Summary

The designed future flow is:

```text
scratch candidate-review packet
-> full content surfaced to human
-> explicit human approval artifact
-> validator/integrity preflight
-> append-only canonical candidate lifecycle write
-> post-write validation/query integrity check
-> audit record / report packet
```

The design explicitly prohibits label-only approval, silent canonical creation,
source-summary-only crossing, overwrite of canonical entries, mutation of prior
evidence, candidate promotion without a separate gate, paper/live readiness
implication, provider memory as repo truth, and dropped denominator or skipped
diagnostic information.

## Human Approval Artifact

The approval artifact design requires explicit fields for approval identity,
approver, UTC timestamp, scope, source packet path/hash, formalizer path/hash,
bridge path/hash, robustness path/hash, denominator ledger path/hash, content
review confirmation, canonical crossing permission, canonical write scope,
append-only confirmation, no-promotion and no-readiness confirmations, and
operator acknowledgments for missing diagnostics, data-availability warnings,
and funding mode.

Approval cannot be inferred from file presence, PR merge, label, comment,
status entry, agent recommendation, or prior noncanonical packet approval.

## Content-Before-Lock Rule

The future gate must surface the full packet JSON and Markdown plus linked
source paths/hashes, denominator ledger, robustness skipped diagnostics, data
warnings, funding mode, blockers, and open questions before approval. The
source packet hash must be validated after approval and before write.

## Field-Level Mapping Summary

The design maps strategy family, idea summary, timeframe, source artifact
references, approval references, non-authority flags, questions, blockers, and
next-review information to existing lifecycle registry fields where possible.
It marks denominator counts, row dispositions, detailed runner metrics,
skipped diagnostics, data warnings, funding mode, and missing diagnostic states
as `needs schema decision` where the current schema has no field.

## Validator / Integrity Gate Summary

Pre-write gates include packet contract validation, source hash matching,
approval artifact validation, denominator equality, non-authority flag checks,
missing-diagnostic/data/funding caveat preservation, target schema/storage
decision, ToolContext gate enforcement, and explicit absence of
promotion/readiness/paper/live/runtime fields.

Post-write gates include selected lifecycle registry or lifecycle-change
validation, relevant existing registry validators, Result Population and data
availability validators, query view discovery, integrity views that find the
new event or entry, source hash retention, denominator retention, no
promotion/readiness state, audit record existence, and `git diff --check`.

## Append-Only Rule

Future crossing writes are limited to a new candidate lifecycle entry or new
event only. No overwrite, deletion, silent source replacement, or mutation of
prior evidence is allowed. Corrections require an explicit correction or
supersession event, and all source hashes remain preserved.

## Karl-Gated Build Boundary

Implementation requires a later Karl-gated build package. That package must
separately authorize the target storage path, lifecycle vocabulary, approval
artifact schema/storage, source contract validator, any schema/validator/query
changes, ToolContext action changes, exact tests, and first real-write policy.

## Validation Status

- Ambient Python 3.14 `python -m pytest tests -k "candidate_lifecycle or candidate_review" -q`:
  FAILED during collection because the ambient interpreter lacks repo
  dependencies including `pandas` and `numpy`; not passing evidence.
- Repo-venv `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests -k "candidate_lifecycle or candidate_review" -q`:
  PASS, 49 passed and 2,095 deselected.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.registry.validate_data_feature_availability`: PASS.
- `python -m tools.research_query.run --list-views`: PASS, 124 views listed.
- `python tools/dev/diff_scope_summary.py`: PASS; only the three expected
  untracked files, no forbidden-path matches.
- `git diff --check`: PASS.

## Non-Authority Statement

This package is architecture/design documentation only. It creates no canonical
artifact, candidate registration, lifecycle transition, promotion, readiness,
ranking, recommendation, approval, paper/live, runtime, OMS, risk,
reconciliation, capital, broker/exchange, credential, private endpoint,
provider/API, network, or execution authority.
