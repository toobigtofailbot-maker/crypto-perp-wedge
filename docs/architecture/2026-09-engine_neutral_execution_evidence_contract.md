# Engine-Neutral Execution/Evidence Contract

## Status and purpose

CPW-CANON-01 defines CPW-owned, framework-neutral content contracts for an exact
scientific execution request and its normalized scientific result. It creates no
execution, approval, persistence, canonical crossing, candidate, runtime,
paper/live, or capital authority.

## Ownership boundary

CPW owns the scientific request, denominator, normalized result meaning, and
their forward content identities. Engines and adapters supply results and retain
auditable provenance, but engine, adapter, orchestration, retry, worker, local
path, environment, dependency, and repository-commit facts do not define the
scientific identities.

## Deterministic serialization

`cpw_engine_neutral_json_v1` accepts JSON-compatible values only, requires
string object keys, rejects non-finite floats and opaque objects, sorts keys,
uses compact separators and UTF-8 with `ensure_ascii=False`, and emits no
trailing newline. Content hashes are lowercase `sha256:<hex>` over exactly
those bytes.

## Request identity scope

`cpw_run_request_v1` hashes exactly its schema version, the Strategy Spec,
Variant Manifest, and Sweep Plan IDs and content hashes, ordered declared
variant IDs, committed denominator, data catalog/slice/timeframe/stream
identity, deterministic seed, backtest assumptions, sizing metadata, and data-
availability claim. It excludes its own hash and the fixed non-authority flags.

## Evidence identity scope

`cpw_result_envelope_v1` hashes exactly its schema version, request content
hash, and scientific result. The scientific result contains the committed full
denominator, exactly reconciled outcome counts, and ordered scientific rows.
Each row receives a new CANON-01 content hash over variant ID, assignment hash,
outcome, attempted state, metrics, non-success/error classification, data
coverage, and scientific lineage. Legacy row IDs and row hashes are excluded.

Execution provenance, compatibility evidence, and non-authority flags are
retained in the envelope but excluded from `evidence_content_sha256`. Thus
identical normalized science for the same request has one identity across
engines while provenance remains queryable.

## Legacy Result Population compatibility

The read-only RP v1 adapter projects existing Result Populations through the
existing replay-normalization API. It preserves complete denominator and row
content, recomputes only the new CANON-01 request/row/evidence identities, and
copies the exact legacy `input_identity_hash` and
`result_population_identity_hash` objects into compatibility evidence. The
replay contract version and normalized stable hash remain labeled as replay
compatibility facts.

Legacy hashes retain their original meaning because historical evidence is not
rewritten or relabeled as the new identity namespace. This is one forward
contract with a historical readability seam, not dual canonical authority.
The legacy adapter may remain only while that narrow readability/translation
seam is required; it is neither another writer nor an authority owner.

## Later consumers and non-authority

The historical CPW adapter may feed this contract. N1 may later build a
Nautilus adapter to the same contract, without changing the contract around
Nautilus-specific objects. CANON-02, CANON-03, and CANON-04 remain separately
authorized packages. This record defines no future engine field mapping and no
writer, approval-binding, receipt, or crossing algorithm.
