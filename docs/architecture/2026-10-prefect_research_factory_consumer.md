# Manual Prefect Research Factory Consumer

CPW-PREFECT-FACTORY-01 implements a manual consumer with bounded scratch-only
physical crash/recovery acceptance. It activates neither the factory nor Stage 5B.
The frozen factory, kernel, adapter and other Prefect consumers are unchanged.

## Interface and authority

`research_factory_consumer(manifest_path, manifest_sha256, human_invocation=False)`
is one manual Prefect flow, with retries 0 and result persistence disabled.
Its direct seam is `run_manual_factory_request`. Prefect owns operational state
only. CPW owns all proposals, trials, denominators, scientific dispositions,
approval, evidence, retry budgets and successor decisions.

The manifest is a bounded JSON file under `.cpw/active`, pinned by its full
`sha256:` file hash. Its closed `cpw_prefect_factory_request_v1` contract requires:

- `schema_version`, `repo_sha`, `campaign_id`, `search_id`, `contract_hash`,
  `handoff_content_sha256`, and ordered accepted `scientific_trial_ids`;
- `created_at_utc`, `preparation_root` and `output_root`;
- six exact `{path, sha256}` bindings: `handoff`, `ohlcv_input`,
  `d4_catalog_slice`, `d2_import_report`, `fold_manifest`, `execute_approval`.

The handoff uses its existing `.cpw/active/research-autonomy` namespace. Prepared
artifacts stay in scratch; outputs must satisfy the unchanged adapter output
root. Paths reject traversal and Windows reparse/symlink components. Files are
rehash-checked, and HEAD must match the frozen handoff in a clean tracked tree.
Requests contain no executable plans, commands, DSNs or credentials. Input
bindings are restricted to active/scratch research work, data slices, and D4
processed data. Before approval or dispatch, the execution data identity and
OHLCV/catalog/import hashes must match the frozen contract and committed
source provenance; matching caller-supplied hashes alone is insufficient.

An operator prepares the existing deterministic wave without executing it,
freezes its timestamp and fold manifest, and supplies an actual exact human v2
approval through the existing approval path. The wrapper generates no marker
and supplies no approval fields. `human_invocation=True` or a Prefect UI action
alone grants nothing. The existing factory rechecks scientific authority and
the adapter's exact v2 gate before physical dispatch.

## Claim and recovery

The sole additional write is a non-authoritative, immutable safety claim under
`.cpw/active/prefect/research-factory/claims/`. Its name hashes the campaign and
search, excluding the timestamp, output roots, marker and all Prefect IDs.
Atomic exclusive publication permits one wrapper dispatch only. The claim
contains the original manifest reference, accepted trial IDs and a conservative
`may_have_run` state. It is never cleared, overwritten, reset or used as approval.
This deliberately blocks subsequent waves of the same search; it implements
no successor or retry coordinator. Retain claims across worker/server restarts.
Deleting a claim is not an authorized recovery operation.

Changed requests for a claimed search block. Exact duplicate delivery with no
complete durable result blocks for investigation, including a crash before
dispatch, unknown physical completion, and partial terminal commitment. A
post-delegation exception reports an unknown runner count (`null`), not zero,
and creates no scientific failure or retry record.

For complete durable results, the existing `load_trial_result` validates
retained scientific bytes and audit identity. The wrapper resolves the original
mapping and evidence-completed checkpoint, checks their request bindings, and
uses the unchanged manual loop's durable-only early return with zero runner
calls. It never regenerates a wave or reruns D4. Missing, changed or contradictory
retained evidence blocks. No new scientific result store is introduced.

Operational outputs distinguish `completed`, `recovered`, `blocked`, `failed`,
preserve CPW dispositions/withholding reasons, and assert default-OFF and no
authority. Blocked/failed outcomes return a Prefect Failed state, never a silent
Prefect Completed state. Their finite operational JSON is retained in the Failed
state message; placing a map in Failed-state data is incompatible with Prefect's
exception decoder. Operational infrastructure failure is not a scientific
`SOFTWARE_FAILED` classification.

## Deployment and isolation

Registration uses the existing local-source pattern with the exact clean
40-character worktree HEAD, Prefect 3.8.6 and loopback HTTP API only. Deployment
`cpw-research-factory-manual-v1` uses the existing process-pool name, concurrency
limit 1, `build=False`, `push=False`, no schedules and no triggers. Validation
must additionally verify pool/process-worker concurrency 1. No Cloud/API key,
task fan-out, autonomous scheduling or other consumer cutover is permitted.

`CPW_RESEARCH_FACTORY_AUTHORITY_DSN` is process-local only. The connection must
resolve to loopback and the existing least-privilege
`cpw_research_authority_writer` role without superuser or RLS bypass. It is never
a Prefect parameter/result/log field. Scientific authority and Research Memory
remain separate logical databases; Prefect's database stores operational history.

## Acceptance and limits

The parent WP requires focused and adjacent engineering tests, isolated local
PostgreSQL/Prefect operational acceptance, integrity checks, all 48 full-release
shards, and Side 22 review of the exact final local head. Synthetic engineering
fixtures prove code behavior only. Real-science recovery acceptance requires a
fresh exact-source request/fixture/marker and Karl's separate explicit approval;
the historical PR #737 study and marker must not be reused.

The accepted continuation permits one reviewed PR and its required public
`smoke` check after physical acceptance and local validation. Merge remains
Karl-only. Candidate, canonical, runtime,
OMS, reconciliation, risk, safe mode, overlays, paper/live and capital boundaries
remain protected. Current validation and blockers are recorded in
`docs/status_entries/CPW-PREFECT-FACTORY-01.md`.

The accepted physical proof retains its original scientific HEAD
`627e4c0161afd8d90817e07d32727546f3338a9c`, request and two trial IDs. A verified
Windows Prefect child was suspended and hard-killed at the original native
`reconcile_manual_run` call entry, after complete physical evidence and before
terminal commits. Explicit native recovery, idempotent replay and a fresh
Prefect operational-ID duplicate preserved two terminal results with zero
additional adapter, population, fold or backtest calls.

Native result commits and loads rebuild seeded MC diagnostics to verify retained
evidence. Karl's exact acceptance-only budget amendment authorized ten such
verification calls, separate from the single scientific advisory report.
Actual totals were 12 variant backtests, one 10,000-resample scientific report
and ten matching verification recomputations / 100,000 validation resamples,
within 260.375 seconds. The native verifier was unchanged. This exception is
specific to the recorded acceptance; it grants no future execution authority.
The later documentation/review head preserves the old scientific bindings.
