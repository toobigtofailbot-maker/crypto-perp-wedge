# H-004 Strategy Spec External Content Readiness Contract

## Decision and scope

Main selects H-C for the H-004 dispatch prerequisite. A later immutable external-content-readiness fact must bind both the exact Strategy Spec file bytes and the full parsed JSON content. This lock is limited to H-004 dispatch prerequisites.

This decision is not a repository-wide Strategy Spec hash migration. It does not reinterpret, replace, repair, or prove the historical `hash_pinning.canonical_spec_hash` values or `strategy_spec_hash_scope_v1`. It creates no dispatch, execution, Result Population, ranking, recommendation, candidate, promotion, readiness beyond content integrity, runtime, paper/live, OMS, risk, reconciliation, scheduler, or notification authority. The production fact, validator, query views, and dispatch-record changes are outside this package.

## Locked two-hash binding

A valid future fact binds one canonical Strategy Spec at one source Git commit with both of these values:

1. `raw_file_sha256`: SHA-256 over the exact UTF-8 file bytes as stored, including all incidental whitespace and any final newline.
2. `full_repo_canonical_json_sha256`: parse the complete UTF-8 JSON document, serialize the complete value with `repo_canonical_json_v1`, and SHA-256 the resulting canonical bytes.

For Strategy Spec full-content lineage, the current reproducible implementation anchor is `tools/registry/validate_variant_sweep_artifacts.py::canonical_json_bytes`. The locked byte algorithm is:

- parse exactly one complete UTF-8 JSON value;
- require an object at the document root;
- sort object keys recursively;
- use compact separators `,` and `:`;
- serialize Unicode directly with `ensure_ascii=false`;
- emit UTF-8 bytes;
- add no incidental whitespace and no trailing newline to the canonical payload.

The current Strategy Specs contain JSON number values. The existing VM-parent lineage helper above accepts those values and reproduces all seven parent hashes. The distinct queue/Gate-Q record helper in `tools/canon_intake/queue_admission.py::repo_canonical_json_v1` rejects in-memory floating-point values and therefore is not the callable helper for a float-bearing full Strategy Spec. This lock does not weaken that queue-record rule or redefine queue records. The future readiness fact itself uses only strings, booleans, and integer byte lengths; it introduces no fractional-number field.

The canonicalization identity stored in the future fact is exactly `repo_canonical_json_v1`. That identity is dispatch-scoped here to the full Strategy Spec content algorithm above. No subset, field projection, deleted-hash-field variant, or third inferred Strategy Spec hash scope is permitted.

## Reproduction proof at the locked base

At source commit `1c22edf602f748ed03d9304c66b4b40cd6f0d601`, STRAT-SPEC-0007 has:

- path: `research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json`;
- Git blob: `ac5a493cb5b7d1a5de3647df07bd3151a8e4a440`;
- raw byte length: `19880`;
- raw file SHA-256: `sha256:b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c`;
- full `repo_canonical_json_v1` SHA-256: `sha256:8b6f7dd7a3e12b934c1038ae113aa25aa79f0b3cc6a336b25bd58164f5cc92db`;
- VM-0007 parent Strategy Spec hash: the same full canonical hash;
- historical internal status: `not_computed`;
- historical internal canonical hash: `null`;
- historical scope version: `strategy_spec_hash_scope_v1`.

The same full-content procedure reproduces the VM parent binding for STRAT-SPEC-0001 through STRAT-SPEC-0007. The package preservation manifest records exact raw hashes for every current Strategy Spec, Variant Manifest, and Sweep Plan.

## Legacy internal hash posture

The embedded `hash_pinning.canonical_spec_hash`, `hash_pinning.hash_status`, and `strategy_spec_hash_scope_v1` values are immutable legacy facts. H-C neither proves nor claims that their historical scope is reproducible. In particular, STRAT-SPEC-0007 remains `hash_status=not_computed`; its embedded hash remains null.

No Strategy Spec, Variant Manifest parent binding, or Sweep Plan is changed. External content readiness is separate from embedded `hash_pinning.hash_status`. A future fact must disclose `legacy_hash_scope_reproducibility=unresolved` and must not contain a field that claims the legacy internal hash was verified.

## Future immutable fact contract

The Draft 7 schema is `research/schemas/strategy_spec_external_content_readiness.schema.json`. A later implementation must create exactly one fact per Strategy Spec with these required fields:

- schema version and deterministic fact ID;
- deterministic fact path;
- exact scope `h004_dispatch_external_content_readiness`;
- Strategy Spec ID and canonical repo-relative path;
- raw byte length and exact raw file SHA-256;
- canonicalization identity `repo_canonical_json_v1` and full canonical JSON SHA-256;
- source Git commit and source Git blob SHA;
- computation tool identity, repo-relative path, SHA-256, and version;
- computed timestamp;
- exact readiness state `external_content_ready`;
- observed embedded legacy hash status, scope version, and nullable legacy hash;
- mandatory `legacy_hash_scope_reproducibility=unresolved`;
- no-mutation proof;
- immutable-create declarations;
- dispatch-prerequisite-only declaration;
- closed non-authority declarations.

ID and path derivation are exact:

- fact ID: `SS-ECR-<strategy_spec_id>`, for example `SS-ECR-STRAT-SPEC-0007`;
- fact path: `research/strategy_spec_external_content_readiness/<fact_id>.external_content_readiness.json`.

The later writer and validator must deterministically enforce the ID/path relation, the Strategy Spec ID/path relation, exact content hashes, source commit/blob binding, and tool binding.

## Immutable creation requirements for the later package

The later implementation must:

- use exclusive create for both identifier and target path;
- confine source and target paths to their exact repo roots;
- reject a symlink at the source, target, or any path component;
- reject duplicate fact IDs, duplicate target paths, and more than one fact for a Strategy Spec;
- re-read and revalidate the exact source bytes immediately before the exclusive write;
- reject stale commit, blob, byte length, raw hash, canonical hash, tool, or legacy-observation bindings;
- forbid overwrite, delete/recreate, in-place repair, superseding, and automatic migration;
- validate deterministically and fail closed.

No production fact directory or fact is created by this design package.

## Locked two-view posture for the later query package

The later query package must implement two separate, stable integrity surfaces. They are not implemented here.

### `v_integrity_strategy_spec_external_content_readiness`

This violation view reports whether each in-scope H-004 Strategy Spec is reproducibly bound by exactly one valid external fact. It must be empty for an in-scope spec only when the fact exists and all ID, path, uniqueness, source commit/blob, raw byte length, raw hash, full canonical hash, canonicalization, tool, readiness-state, legacy-disclosure, immutability, and non-authority checks pass. Missing, duplicate, stale, mismatched, malformed, or unauthorized facts produce rows and fail the external-content prerequisite.

After a later valid production fact exists, H-004 may pass this external-content prerequisite when this surface is empty. This surface does not make H-004 otherwise ready and grants no dispatch authority by itself.

### `v_integrity_strategy_spec_legacy_hash_scope_reproducibility`

This disclosure view reports the unresolved reproducibility of historical `strategy_spec_hash_scope_v1`. Under H-C it remains nonempty for STRAT-SPEC-0007 with `legacy_hash_scope_reproducibility=unresolved`, even when the external-content surface passes. Surface A must not mask, delete, coerce, or reinterpret this row.

The unresolved legacy disclosure does not block the H-004 dispatch-scoped external-content prerequisite after Surface A passes, unless Main later changes policy. It remains visible as an integrity finding. The existing `v_integrity_strategy_spec_hash_readiness` STRAT-SPEC-0007 `not_computed` row remains unchanged until the later query package explicitly reconciles view topology without losing the finding.

## Downstream dispatch binding after PR #665

After the dispatch control-plane package in PR #665 merges, a separate approved schema/fixture package must update the dispatch record to bind all of:

- external readiness fact ID;
- external readiness fact path;
- exact raw SHA-256 of the fact file;
- Strategy Spec raw file SHA-256;
- Strategy Spec full `repo_canonical_json_v1` SHA-256;
- canonicalization identity;
- disclosed legacy internal status and unresolved scope reproducibility.

This is a downstream schema follow-up only. This package does not modify PR #665, any dispatch schema, queue/Gate-Q admission, runner, validator, query layer, or canonical artifact.

## Current integrity baseline and non-readiness conclusion

The merged-base query layer exposes 58 `v_integrity_*` views. Exactly one row is nonempty: `v_integrity_strategy_spec_hash_readiness` reports STRAT-SPEC-0007 with source field `hash_pinning.hash_status`, expected `computed when intended_for_variant_manifest=true`, and actual `not_computed`.

This design lock intentionally leaves that row unchanged. No external-readiness row exists because neither a production fact nor a query view exists. H-004 is not dispatch-ready as a result of this package.
