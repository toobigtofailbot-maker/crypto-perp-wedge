# PostgreSQL Research Memory / Index v1

Package: `WP-RESEARCH-MEMORY-DESIGN-AND-BOUNDED-BUILD-01`

## Boundary

PostgreSQL is a mutable memory and exact-match index over repo truth. It is not
canonical scientific evidence. The committed candidate registry, hypotheses,
experiment plans/reports, decisions, Result Populations, and trial log remain
authoritative. The existing in-memory DuckDB research query layer remains the
read-only cross-artifact analysis surface and is neither replaced nor modified.

The bootstrap reads `research/candidate_registry.jsonl`, hypothesis and decision
paths named by registry rows, and candidate-matched `EXP-*.plan.json` and
`REP-*.report.json` artifacts. It stores metadata, deterministic identity, and
content-addressed references only. It does not ingest Result Population rows,
metrics, trial-log rows, or full experiment/decision content.

## Exact schema

The `research_memory` PostgreSQL schema contains:

- `schema_migrations(version, content_sha256, applied_at)`: checksum-locks the
  ordered SQL migrations.
- `hypothesis_items(memory_item_id, fingerprint_version, fingerprint_sha256,
  strategy_family, mechanism, primary_timeframe, instrument_scope,
  required_data_features, free_parameter_count, canonical_definition,
  created_at, updated_at)`: one relational identity per deterministic
  fingerprint.
- `memory_records(memory_record_id, memory_item_id, authority_state,
  source_key, title, status, classification, negative_reason,
  source_created_at, source_updated_at, source_metadata, indexed_at,
  refreshed_at)`: one source-specific attempt/memory record. `authority_state`
  is exactly `REPO_INDEX` or `NON_AUTHORITATIVE`.
- `memory_aliases(memory_alias_id, memory_item_id, authority_state, source_key,
  alias_kind, alias_key)`: deterministic candidate-ID and normalized-name
  aliases. It provides no fuzzy/semantic inference.
- `evidence_references(evidence_reference_id, memory_record_id, artifact_path,
  artifact_id, evidence_role, artifact_content_sha256, source_record_sha256,
  supports_conclusion)`: exact repo-relative evidence references. For JSONL or
  JSON records, `source_record_sha256` preserves canonicalized record identity
  where available; `artifact_content_sha256` always binds the referenced file
  bytes.

The schema uses B-tree indexes for fingerprint, family/timeframe,
classification/status, alias, and artifact lookup; a GIN index supports exact
array containment over required data/features. There is no pgvector, embedding,
graph, similarity, ranking, promotion, candidate, or execution authority.

## Fingerprint v1

`hypothesis-v1` is SHA-256 over canonical UTF-8 JSON containing:

- repo-scoped instrument identity `BTCUSDT_BINANCE_USDTM_PERP`;
- normalized strategy/economic family;
- normalized mechanism statement (registry `differentiation_summary`, falling
  back to the candidate name);
- primary timeframe;
- sorted, deduplicated required data/feature labels;
- free-parameter count.

Normalization is conservative: Unicode NFKC, trim, lowercase, whitespace
collapse, and set ordering for feature labels. Wording and punctuation remain
identity-bearing. Therefore v1 recognizes deterministic structured equivalents,
not semantic near-neighbors. A later similarity system would require a separate
architecture decision; it is neither needed nor authorized here.

## Bootstrap and rebuild

Run clean migrations, then bootstrap:

```powershell
python -m tools.research_memory.run --dsn $env:RESEARCH_MEMORY_DSN migrate
python -m tools.research_memory.run --dsn $env:RESEARCH_MEMORY_DSN bootstrap --repo-root .
```

Bootstrap is transactional and idempotent. It upserts fingerprint identities
and repo-index records, replaces their aliases/evidence refs, removes stale
`REPO_INDEX` records no longer present in the current registry, and removes
orphan identities. It never deletes `NON_AUTHORITATIVE` memory.

`rebuild` transactionally removes only repo-index records/aliases before
repopulating them from repo artifacts. Deleting the PostgreSQL database loses
only index/mutable-memory state; it cannot delete canonical repo truth. Mutable
pre-canonical records are explicitly `NON_AUTHORITATIVE` and never resolve to a
canonical scientific conclusion.

## Lookup and evidence resolution

`lookup`, `lookup-alias`, and `negative` return index hints with
`index_not_truth=true`. A repo-backed classification appears separately as
`resolved_classification` only when every stored artifact path remains an
ordinary repo file with the exact indexed SHA-256 and at least one exact
reference is marked `supports_conclusion`. Missing, unsafe, or hash-mismatched
evidence suppresses the resolved conclusion while preserving the stale index
hint for refresh diagnostics. Repo bytes therefore win over PostgreSQL state.

```powershell
python -m tools.research_memory.run --dsn $env:RESEARCH_MEMORY_DSN lookup-alias `
  --alias H-005 --repo-root .
python -m tools.research_memory.run --dsn $env:RESEARCH_MEMORY_DSN negative `
  --strategy-family momentum --primary-timeframe 1h --repo-root .
```

## Deferred post-M1 seam

After the separately governed post-M1 industrialized loop exists, its research
intake/dedup step may call only the standalone fingerprint and read lookup API,
and its post-canonical-refresh step may invoke the idempotent bootstrap. That
future adapter must continue to resolve repo evidence before using a conclusion.
No scheduler, agent runtime, Prefect, Hermes, continuous-loop callback,
canonical writer, candidate/promotion gate, or live/runtime integration is
implemented by this package.

## Local PostgreSQL validation

PostgreSQL integration tests require an isolated database whose name contains
`test`:

```powershell
$env:RESEARCH_MEMORY_TEST_DSN = 'postgresql://.../research_memory_test'
python -m pytest tests/test_research_memory_fingerprint.py `
  tests/test_research_memory_repo_source.py `
  tests/test_research_memory_postgres.py -q
```

The integration fixture drops only the `research_memory` schema in that
explicit isolated test database, applies the clean migration twice, and drops
the schema after each test.
