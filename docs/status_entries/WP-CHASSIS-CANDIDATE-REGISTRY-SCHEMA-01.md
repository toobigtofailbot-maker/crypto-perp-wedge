# WP-CHASSIS-CANDIDATE-REGISTRY-SCHEMA-01 - Candidate lifecycle registry schema

- Package class: schema / validator / tests / docs, disconnected chassis package.
- Branch: `feature/chassis-candidate-registry-schema-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-CHASSIS-CANDIDATE-REGISTRY-SCHEMA-01`.
- Base: `origin/main` at `b0e9187`.
- Repo-truth discovery: current `research/schemas/candidate_registry.schema.json`
  and `tools/registry/validate_registry.py` already govern the older H-### line
  registry, so this package adds a lifecycle-specific registry schema instead
  of mutating existing registry contracts.
- Changed files:
  - `research/schemas/candidate_lifecycle_registry.schema.json`
  - `tools/registry/validate_candidate_registry.py`
  - `tests/fixtures/candidate_lifecycle_registry/valid_example.candidate_lifecycle_registry.json`
  - `tests/test_validate_candidate_registry.py`
  - `docs/status_entries/WP-CHASSIS-CANDIDATE-REGISTRY-SCHEMA-01.md`
- Schema summary: Defines a real-capable top-level registry with
  `schema_version`, `registry_id`, `registry_status`,
  `non_authority_declaration`, `transition_rules`, `candidates`,
  `append_only_ledger`, and `validation_summary`.
- Real-capable correction: The lifecycle schema now accepts real-shaped
  registry IDs (`CANDIDATE-REGISTRY-0001`), registry statuses
  (`unpopulated`, `candidate_review`, `archived`), candidate IDs
  (`CANDIDATE-0001` and `H-001` style), and lifecycle event IDs
  (`CLE-0001`) while preserving example/fixture identifiers for tests.
- Validation summary correction: `fixture_only` and
  `real_candidate_registered` are schema booleans rather than fixture-only
  constants; paper/live, runtime, lifecycle-engine, and capital authority
  fields remain hard-false.
- Candidate fields: Includes real-capable candidate IDs, lifecycle status,
  strategy family, description, BTCUSDT market/timeframe metadata, source refs,
  evidence links, lifecycle event refs, review metadata, blocking/next-review
  fields, and required non-authority declarations.
- States: Uses the lifecycle-design state set `proposed`,
  `validated_research`, `paper_candidate`, `paper_running`, `promoted_live`,
  `rejected`, `demoted`, and `retired`.
- Transition representation: Includes allowed-edge and forbidden-principle
  representation in the schema and validates concrete append-only event
  histories in the validator.
- Evidence links: Requires structured artifact type, artifact ref,
  relationship, authority boundary, optional artifact ID, optional identity
  hash, and optional notes. Evidence links are review references only.
- Audit events: Defines append-only event shape with event ID, sequence,
  candidate ID, event type, timestamp, actor, gate, from/to status, reason,
  related evidence, exception/blocking refs, and non-authority declaration.
- Validator behavior: Loads the schema, validates candidate lifecycle registry
  JSON files,
  rejects duplicate candidate/event IDs, unknown lifecycle event refs, invalid
  transition order, incoherent event sequence/timestamps, status-history
  mismatches, promotion without paper/live evidence, demotion/rejection without
  evidence, and false non-authority flags. It remains validation-only and does
  not implement a lifecycle engine.
- Example status: The only committed registry instance is a test fixture under
  `tests/fixtures/candidate_lifecycle_registry/` using fake IDs such as
  `CANDIDATE-EXAMPLE-0001`, `STRAT-SPEC-EXAMPLE`, and `RP-EXAMPLE`.
- Candidate-registration status: No real candidate is registered and no real
  candidate lifecycle registry artifact is committed under `research/`.
- Boundary summary: No real candidate is registered; no canonical
  `research/candidate_registry/` artifact is created; no lifecycle transition
  engine is implemented; no Strategy Spec, Variant Manifest, Sweep Plan, result
  population, existing candidate registry schema, existing result-population or
  strategy-spec schema, compiler, runner, query layer, `lib/`, data, dashboard,
  runtime, paper/live, OMS/risk/reconciliation, broker/exchange, credentials,
  or capital path is changed.
- Authority summary: The schema, validator, and fixture create no candidate
  approval, paper/live readiness, runtime authority, promotion authority,
  trading recommendation, broker/exchange authority, or capital authority.
