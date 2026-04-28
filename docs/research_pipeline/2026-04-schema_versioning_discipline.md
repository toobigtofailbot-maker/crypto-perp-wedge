# Schema Versioning Discipline (WP-9c)

## Purpose

This record locks cross-family schema-versioning discipline after WP-9b.

It supports the Phase 9 `Outcome-Ingesting Research Lifecycle Foundation` by
making future schema-version posture explicit before outcome-ledger,
reconciliation, promotion, demotion, or deployment artifact families are added.

WP-9c is documentation-only. It changes no schema, validator, committed
artifact, query-layer file, helper, test, runtime path, policy, deployment
path, OMS, reconciliation, risk, overlay, safe-mode, or live-trading behavior.

## Scope

This discipline applies prospectively to future Phase 9 schemas and classifies
current research schema families by their current version-marker posture.

WP-9c does not retrofit existing families. It does not change validator
behavior and does not invalidate any committed artifact.

The evidence inventory for current families is recorded in:

```text
docs/research_pipeline/2026-04-schema_family_inventory.md
```

## Core Rules

- Every new Phase 9 schema must include a required top-level `schema_version`
  field.
- The initial version for a new Phase 9 schema is `v1`.
- Single-version artifacts should constrain `schema_version` with `const`
  unless repo truth for that family supports another explicit idiom.
- Breaking schema changes require a new major version or a new schema family.
- Additive backward-compatible changes require explicit package scope,
  compatibility analysis, and a validation plan.
- Schema-version changes must not be smuggled into instance, backfill, or
  artifact-production packages.
- Validators for new Phase 9 schemas must explicitly check the version field,
  not only rely on generic schema validation.
- Query-layer relations must expose schema version when the artifact family has
  one.

## Current Family Classifications

Current repo truth has 13 research schema files.

- LCH is `phase9-explicit-v1`: `lifecycle_change.schema.json` has required
  top-level `schema_version` constrained to `v1`.
- SSS v2 is `explicit-versioned-current`: `shadow_signal_summary_v2.schema.json`
  has required top-level `schema_version` constrained to `v2`.
- SSS v1 is `equivalent-marker-locked`: it has no `schema_version`, and remains
  governed by the locked top-level `derivation_method` marker
  `shadow_signal_summary_option_a_floor_10_v1`.
- Candidate registry is a `retrofit-candidate`: it has no explicit top-level
  `schema_version`; `pipeline_stage` is a lifecycle/status marker, not a schema
  version marker.
- DCH and REL are `retrofit-candidate` legacy pipeline-stage / approval
  families. The DCH `pipeline_stage` vocabulary mismatch with Phase 9 lifecycle
  vocabulary remains a known retrofit candidate, not a WP-9c change.
- EXP and REP are `retrofit-candidate` legacy research evidence families.
- Advisory and shadow evidence families without explicit version markers
  (`agent_output`, `macro_window_agent_output`, `bucket_mapping`,
  `pre_gate_advisory_snapshot`, and `overlay_shadow_log`) are
  `retrofit-candidate` because they are active query-layer families that may be
  touched by later advisory or evidence packages.

No family is classified as `ambiguous-needs-follow-up` in the current
inventory. If future repo truth makes a family ambiguous, the next package must
record the ambiguity before changing schema or validator behavior.

## Non-Retrofit Rule

WP-9c does not patch existing schemas.

No existing artifact should be invalidated by this record. No validator should
start requiring new fields for legacy artifacts because of WP-9c. No query-layer
view should reinterpret historical payloads because of WP-9c.

Any retrofit requires a dedicated future package with:

- reason the retrofit is needed now
- backward-compatibility posture
- validator impact
- query-layer impact
- committed artifact impact
- migration or no-migration decision
- protected-path confirmation

## Retrofit Candidate Handling

Future packages should prioritize retrofit candidates as follows:

- High priority: a family is a Phase 9 dependency or an active
  lifecycle/outcome-learning dependency.
- Medium priority: a family is an active query-layer, advisory, or downstream
  evidence dependency.
- Low priority: a stable legacy family has no near-term mutation path.

The candidate registry and the DCH pipeline-stage vocabulary mismatch remain
known retrofit candidates. WP-9c records them only and does not change their
schemas, validators, instances, or query-layer surfaces.

## Versioned Evolution Rules

Create a new major version or a new family when a change removes fields,
renames fields, changes required-field semantics, changes identifier meaning,
changes state vocabularies incompatibly, or alters validator/query-layer
integrity assumptions already consumed downstream.

Additive changes may remain in the current major version only when they are
backward compatible for existing committed artifacts and downstream query
consumers. Such work still requires explicit package scope and validation.

Repo version strings currently use simple `vN` values. WP-9c does not introduce
minor-version syntax.

Multiple schema versions may coexist when a family has committed instances in
more than one version. Validators and query-layer relations must then state
which versions they accept and expose enough version information for consumers
to avoid silent cross-version assumptions.

After a family becomes complete-as-consumed, use the stability-lock pattern
already used by SSS v1 and SSS v2: future evolution belongs in explicit later
versioned work, not silent mutation of the consumed contract.

## Phase 9 Implications

The future outcome-ledger schema must declare required top-level
`schema_version: "v1"`.

The future REC schema must declare required top-level `schema_version: "v1"`.

The future promotion/demotion policy schema must declare required top-level
`schema_version: "v1"`.

The future deployment artifact schema must declare required top-level
`schema_version: "v1"`.

Future LCH v2 or outcome-ledger v2 work must be explicitly versioned and scoped
as schema/validator/query-layer compatible work. It must not be bundled into an
instance backfill, lifecycle transition, outcome ingestion, reconciliation, or
deployment package.

Schema-versioning discipline does not create runtime influence, automated
promotion, policy authority, deployment authority, or live-trading authority.

## Non-Claims

WP-9c creates no:

- schema changes
- validator changes
- instance changes
- query-layer changes
- lifecycle transition
- outcome ingestion
- reconciliation artifact
- promotion/demotion policy
- deployment artifact
- runtime, OMS, risk, overlay, safe-mode, or live-trading behavior

## Required Future Package Discipline

Any package creating a new Phase 9 schema must cite this document.

Any package retrofitting an existing schema family must state:

- why retrofit is needed now
- backward-compatibility posture
- validator impact
- query-layer impact
- committed artifact impact
- migration or no-migration decision
- protected-path confirmation
