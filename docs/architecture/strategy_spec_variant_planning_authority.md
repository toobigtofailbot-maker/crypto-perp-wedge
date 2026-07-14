# Strategy Spec Variant-Planning Authority

## Decision and boundary

An immutable canonical Strategy Spec whose embedded status is `review_requested` may support exactly one bounded Variant Manifest only through a separate Karl-approved, append-only variant-planning approval. Gate C remains authority for one exact canonical write only. Variant-planning approval is not Gate Q, queue admission, dispatch, research execution, evidence, candidate, ranking, recommendation, readiness, runtime, paper/live, OMS, risk, or reconciliation authority.

Existing canonical parents whose embedded status is `approved_for_variant_planning` retain the current pathway. Existing Specs, VMs, Sweeps, results, and queue evidence require no migration and remain byte-identical.

## Open governance naming and placement decision

Merged repo truth does not select a governance name for this separate authority. Karl/Main must choose exactly one presentation before any implementation package begins:

1. standalone **Gate C-VP**; or
2. a documented **variant-planning sub-gate under Gate C**.

Both choices use the identical artifact, protected-writer, audit, single-use, contract-core, validator, Gate-Q/queue-lineage, backward-compatibility, and no-downstream-authority semantics locked below. Neither choice expands Gate C's existing exact canonical-write scope. The neutral term `variant-planning approval` in this document describes the common contract and is not a silent governance-name selection. This design must merge, and Karl/Main must close this naming/placement decision, before implementation starts.

## Current contradiction

`research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json` has `status="review_requested"`, null reviewer and review time, and `approval_scope="none"`. Its exact Gate-C approval authorizes only `one_append_only_canonical_strategy_spec_write`. The Agent Inbox event is annotation-only. In contrast, `research/schemas/variant_manifest.schema.json` permits only `approved_for_variant_planning` in `parent_strategy_spec.strategy_spec_review_status`. The current semantic validator proves the parent identity and hash but does not compare this declared status with the canonical parent or independent approval evidence.

In-place mutation is prohibited: it would change the approved content hash, invalidate the crossing record's binding, bypass exclusive creation, and damage historical replay. Gate C cannot be reinterpreted as downstream approval. Allowing an unsupported `review_requested` parent would remove the human gate. The external approval pathway is therefore the only locked direction.

## Authoritative approval contract

The future schema is `strategy_spec_variant_planning_approval_v1`. Approval IDs match `^VPAPP-[0-9]{8}-[A-Z0-9]{8}$`. The sole authoritative directory and derived path are:

`research/strategy_spec_variant_planning_approvals/<approval_id>.variant_planning_approval.json`

The artifact contains:

- identity: schema version, ID, target path, `approved_by="Karl"`, timezone-aware `approved_at`, `approval_scope="one_bounded_variant_manifest_preparation"`, exact-content review, append-only and single-use facts;
- canonical parent: Spec ID, canonical path, exact whole-file SHA-256, observed embedded status, and the exact Gate-C audit path, 1-based line, raw-line SHA-256 including newline, Gate-C approval ID, Spec ID, and canonical target;
- `variant_manifest_contract_core`: exact parent identity/hash, VM ID/path, search-family ID, ordered axes and values, population cap/count, denominator basis, adaptive-search false, post-hoc mutation forbidden, and all non-authority facts;
- `contract_core_sha256`, scope `variant_planning_contract_core_v1`, and canonicalization `repo_canonical_json_v1`;
- amendment/revocation policy `supersede_with_new_approval_before_manifest_creation`; after use, no amendment or revocation mutates history;
- all authority flags specified below, exact approval-file hashing by references, reuse rejection, and overwrite prohibition.

The approval file cannot contain its own full-file hash. Consumers compute the exact whole-file SHA-256 and store it in their references and audit records. This removes self-hash recursion while preserving exact-byte evidence.

For H-004-R2 the core binds `VM-0007`, its canonical VM path, `SF-H004-R2-EMA-PULLBACK-CONTINUATION-1D-0001`, ordered axes `pullback_ema_bars`, `trend_fast_ema_bars`, `atr_multiplier`, `max_holding_bars`, their specified three-value sets, cap/count 81, denominator `committed_pre_registered_population_count`, adaptive search false, and post-hoc mutation forbidden.

## Contract-core canonicalization

Use the already locked `repo_canonical_json_v1`: recursively reject floats; allow only string-keyed objects, arrays, strings, integers, booleans, and null; serialize UTF-8 with keys sorted lexicographically by Python/Unicode code-point order, compact `,` and `:` separators, `ensure_ascii=false`, deterministic JSON escaping, and no insignificant whitespace. This is repo-local and makes no RFC 8785/JCS claim.

`contract_core_sha256` is SHA-256 of exactly the canonical bytes of the complete `variant_manifest_contract_core` object, prefixed `sha256:`. Decimal parameter values must be represented as scaled integers plus units in the approval core: H-004-R2 uses `atr_multiplier_milli=[2000,2500,3000]`. The VM validator converts exact schema numbers to these scaled integers, rejects non-exact or out-of-scale values, derives the complete core, and compares hashes and values. This avoids float canonicalization ambiguity.

The final VM contains `variant_planning_approval` with approval ID, derived authoritative path, exact approval-file SHA-256, contract-core SHA-256, and `evidence_mode="external_append_only_approval"`. Gate Q later binds the exact final VM bytes. No circular hash remains.

## Protected writer and audit

The future writer is `tools/canon_intake/variant_planning_approval.py`. Its sole audit is `research/strategy_spec_variant_planning_audit/variant_planning_approvals.jsonl`, using records with schema `strategy_spec_variant_planning_approval_audit_v1` and IDs `VPAUDIT-<approval_id>`.

Before and again inside an exclusive repository-local lock, the writer must validate the exact schema, Karl identity, timezone, flags, ID-derived non-symlinked path, parent ID/path/hash/status, unique Gate-C raw line and approval ID, unused approval/VM/path/search-family identifiers, exact contract core/hash, and absence of traversal, symlink components, floats, collisions, and targets. Search-family IDs are globally single-use across authoritative approvals, VMs, and audit history.

It exclusively creates the approval file, fsyncs according to current protected-writer conventions, appends one `repo_canonical_json_v1` audit line plus LF, and fsyncs. It rolls back partial creation/append. Rollback or post-commit lock-cleanup failure is integrity-critical, forbids automatic retry, and requires operator investigation. Exact duplicate submissions reject; they are not idempotent success. The audit permanently reserves approval ID, VM ID/path, and search-family ID even if files are later removed.

The audit records approval ID/path/file hash, parent ID/path/hash, Gate-C reference, VM ID/path, search-family ID, core hash, population, approval time, writer version, passed-before-write outcome, and every no-downstream-authority fact. Every historical line is schema- and semantics-replayed before a new crossing. Unrelated later appends do not alter a line reference.

The writer never creates or mutates a Spec, VM, Sweep, Gate Q, queue item, run, result, or candidate.

## VM schema and validator pathway

The implementation package must add an optional `variant_planning_approval` object to VM schema `v1`; no new VM schema version is needed because the addition is backward-compatible and conditional semantics are enforced by the validator. Existing VMs without the object remain valid only when the canonical parent's embedded status is `approved_for_variant_planning`.

For an embedded `review_requested` parent, the object is mandatory. The effective VM field remains `strategy_spec_review_status="approved_for_variant_planning"`, but the validator accepts it only after independently validating the authoritative approval schema/path/hash, exact parent and Gate-C lineage, unused/single-use audit evidence, exact VM ID/path and search family, and derived contract-core equality. It rejects missing/wrong approval evidence, unsupported literals, changed axes/order/values, population/denominator mismatch, malformed history, broad authority, and path/symlink failures.

VM schema additions are exactly the optional top-level object and its five required, additional-properties-forbidden fields: `approval_id`, `path`, `sha256`, `contract_core_sha256`, and `evidence_mode`. Semantic conditionality, authoritative-directory confinement, cross-file evidence, and reuse require validator logic rather than JSON Schema alone.

Tests must retain all six current Spec/VM/Sweep pairs, test the embedded-approved legacy path, the external path, and every rejection above. The Sweep contract continues to bind the final VM hash and needs no planning-approval field.

## Gate-Q and queue lineage

For the external pathway, Gate-Q `artifact_refs`, the queue item's `lineage`, and the admission audit must additionally bind variant-planning approval ID/path/full-file hash and contract-core hash. Gate-Q and queue schemas require this evidence conditionally when the VM uses external evidence. Queue admission independently reruns the VM/external-approval validation, validates the variant-planning audit record and permanent reuse facts, and historical replay repeats the same checks.

Legacy embedded-approved bundles remain valid without this lineage. Gate Q cannot substitute for missing planning approval or retroactively authorize a VM. Gate Q authorizes one inert admission; admission does not dispatch; dispatch/execution requires separate later authority.

## Authority flags

Only `authorizes_variant_manifest_preparation` and `authorizes_one_manifest_only` are true. These are false: `authorizes_strategy_spec_mutation`, `authorizes_gate_c`, `authorizes_gate_q`, `authorizes_queue_admission`, `authorizes_dispatch`, `authorizes_research_execution`, `authorizes_result_population`, `authorizes_candidate_lifecycle`, `authorizes_ranking`, `authorizes_recommendation`, `authorizes_promotion_readiness`, `authorizes_scheduler_autonomy`, `authorizes_notifications`, `authorizes_runtime`, `authorizes_paper_live`, and `authorizes_oms_risk_reconciliation`.

## State sequence

1. Gate C creates the immutable canonical Spec, which may remain review requested.
2. Exact planning-approval bytes are prepared; Karl reviews them.
3. The protected writer creates one approval and one audit line.
4. One VM is generated against and references the approval; validation proves equality.
5. A Sweep and dataset/VM/Sweep readiness evidence are prepared.
6. Exact Gate-Q content is prepared and separately approved by Karl.
7. Admission creates one inert `admitted_non_dispatched` item.
8. Dispatch and execution remain separately unauthorized.

## Implementation sequence

This sequence is a future option only after the design merges and Karl/Main closes the naming/placement decision above.

1. Approval schema, protected writer, audit schema, and tests.
2. VM schema/validator plus conditional Gate-Q, queue-item, admission-audit lineage and replay.
3. First exact H-004-R2 planning approval.
4. Resume the data/VM/Sweep prerequisite package.
5. Exact Gate-Q preparation and Karl approval.
6. Inert queue admission.
7. Separately authorized dispatch, if ever approved.

This document is a design lock only and creates none of those artifacts or authorities.
