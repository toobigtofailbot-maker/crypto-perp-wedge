# WP-V2-AUTONOMY-KERNEL-01

Branch-state T3 implementation; required acceptance complete under the
Karl-approved validation-only continuation dated 2026-10-08. Not merged or
activated; hold for Side 22 exact-head review. No self-merge.
Branch: `codex/wp-v2-autonomy-kernel-01`.
Exact base: `9d9f8a94405ded76bbef0163488b9a8e0596371a`.
Semantic implementation head: `51a05391a7703691a6adf2bee3588cddbdcda832`.
Complete passing full-release head: `d98bf03376f8e1fc4b3450ff77186fc0f2091c6c`.
Final head is the documentation-only evidence tail; its exact SHA and the PR
identity are recorded in the publication report. Independent exact-head review
has not occurred. Publication is authorized after final documentation checks.

## Repo truth

Refreshed `origin/main` matched the exact base before validation and again
before the evidence tail. No open/competing PR or remote package branch existed.
D2-026 remains LOCKED and unsuperseded. Consumers are the governed pilot and
focused tests; no factory/production successor consumer was found. Existing
psycopg/Optuna/Prefect and jsonschema/Pydantic dependencies suffice.
All 22 non-documentation files are byte-identical to the semantic head. The
semantic-to-final diff is restricted to the three permitted documentation files.

## Exact closure

Create exactly 21 files:

- `tools/research_autonomy/__init__.py`
- `tools/research_autonomy/models.py`
- `tools/research_autonomy/envelope.py`
- `tools/research_autonomy/migrations.py`
- `tools/research_autonomy/migrations/0001_research_authority.sql`
- `tools/research_autonomy/research_authority_writer_role.sql`
- `tools/research_autonomy/store.py`
- `tools/research_autonomy/contract_builder.py`
- `tools/research_autonomy/handoff.py`
- `tools/registry/validate_bounded_research_envelopes.py`
- `research/schemas/bounded_research_envelope.schema.json`
- `research/schemas/bounded_research_envelope_control.schema.json`
- `tests/fixtures/research_autonomy/bounded_research_envelope.fixture.json`
- `tests/fixtures/research_autonomy/bounded_research_envelope_control.fixture.json`
- `tests/test_research_autonomy_models.py`
- `tests/test_research_autonomy_postgres.py`
- `tests/test_research_autonomy_contract_builder.py`
- `tests/test_research_autonomy_handoff.py`
- `tests/test_validate_bounded_research_envelopes.py`
- `docs/architecture/2026-10-v2_autonomy_kernel_implementation.md`
- `docs/status_entries/WP-V2-AUTONOMY-KERNEL-01.md`

Modify exactly four files:

- `tools/research_search/contract.py`
- `tools/research_search/run_governed_optuna_pilot.py`
- `tests/research_search/test_search_governor.py`
- `docs/project_status.md`

No other tracked change is authorized. Details and D2-026 implementation mapping
are in `docs/architecture/2026-10-v2_autonomy_kernel_implementation.md`.

## Acceptance evidence

Physical Cases A-K ran at the semantic head. Their evidence remains valid:
no implementation, SQL, schema, fixture or test changed in the continuation.

| Case | Result | Evidence |
| --- | --- | --- |
| A Envelope/control | PASS | Both closed schemas/fixtures; malformed/hash/repo/approval/control inputs rejected; no production envelope |
| B DB/migration/role | PASS | 13 tables, 102 constraints, 91 columns and exact triggers; repeat/checksum/immutability/privilege proofs |
| C Initial campaign | PASS | Registered exact envelope, zero prior history, atomic 6-proposal/4-trial reservation, frozen lineage binding |
| D Wave/accounting | PASS | Exact Governor identities/counts; one audit advance; original idempotent outcomes; numeric-type tamper rejected; retries retain trial ID |
| E Successor | PASS | Finalized parent, inherited DB totals, bounded reservation and current lineage |
| F Concurrency | PASS | One of two conflicting successors wins; cumulative used/reserved remain within ceilings |
| G Holdout/contamination | PASS | Isolated attempt stays unconsumed; informative escape persists; restoration/new-domain/new-ID bypass rejected |
| H Memory independence | PASS | Unchanged Memory rebuild/bootstrap in separate DB and complete synthetic .cpw deletion preserve authority |
| I Active handoff/replay | PASS | Contained/gitignored exact wave replay; rehashed numeric-type and lineage/contract/proposal tampering rejected |
| J Governor/Optuna | PASS | Existing legality/pilot regressions; explicit synthetic bindings; no autonomy .successor authority call |
| K Zero activation | PASS | Exact 25-file diff; no integration/activation/protected mutation; no factory execution; historical regression exception separately recorded |

- Focused: **46 passed**, 24 expected Optuna experimental warnings.
- Adjacent: **60 passed**.
- Live PostgreSQL: **13 passed, zero skips** (authority and existing Memory suites).
- Envelope validator: **PASS**, default zero files and two fixture files.
- Exact 21-created / 4-modified closure and base-to-head diff checks: **PASS**.
- Complete full-release at the committed validation head: **PASS**, **4,000
  passed tests**, **23 accounted existing skips**. All **48 shards PASS** and
  complete; **zero timeouts**. All **196 discovered tracked test files** were
  assigned exactly once, with no missing, duplicate or untracked assignments.
- All **eight required non-shard commands PASS**, including exact schema-path
  authorization, forbidden-path check, Result Population validator and query views.
- Assignment manifest:
  `sha256:58844f89d411d5626e06c4755d73f9b3d1be3dbc648c67c8439209c0c46c99c8`.
- Slowest shard: 41, **703.672 seconds**, below the profile's 1,800-second limit.
- Shards 5, 6 and 33 now PASS; the corpus-backed N1 test executed its two
  existing deterministic backtests inside the unmodified full-release suite.
- Required authority/Memory PostgreSQL tests also executed in the full suite.

| Shard | Result | Shard | Result | Shard | Result |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | 16 | PASS | 32 | PASS |
| 1 | PASS | 17 | PASS | 33 | PASS |
| 2 | PASS | 18 | PASS | 34 | PASS |
| 3 | PASS | 19 | PASS | 35 | PASS |
| 4 | PASS | 20 | PASS | 36 | PASS |
| 5 | PASS | 21 | PASS | 37 | PASS |
| 6 | PASS | 22 | PASS | 38 | PASS |
| 7 | PASS | 23 | PASS | 39 | PASS |
| 8 | PASS | 24 | PASS | 40 | PASS |
| 9 | PASS | 25 | PASS | 41 | PASS |
| 10 | PASS | 26 | PASS | 42 | PASS |
| 11 | PASS | 27 | PASS | 43 | PASS |
| 12 | PASS | 28 | PASS | 44 | PASS |
| 13 | PASS | 29 | PASS | 45 | PASS |
| 14 | PASS | 30 | PASS | 46 | PASS |
| 15 | PASS | 31 | PASS | 47 | PASS |

### Existing skip accounting

No test was changed, mocked, weakened, deselected, marked xfail or newly skipped.
The 23 skips follow unchanged test conditions:

| Shard | Count | Existing prerequisite |
| --- | --- | --- |
| 6 | 2 | One unavailable symlink; unset FUNDING_PROVENANCE_DATA_ROOT opt-in |
| 10 | 1 | Unavailable symlink |
| 14 | 3 | One unrelated absent 4h Parquet; two unavailable storage symlinks |
| 21 | 5 | Unavailable canonical-intake symlinks |
| 29 | 1 | Unavailable Prefect intake symlink |
| 31 | 1 | Unavailable dispatch-authorization symlink |
| 32 | 4 | Unavailable dispatch reservation symlink/junction fixtures |
| 33 | 2 | Explicit full-history and accepted-May-2023 opt-in proofs |
| 41 | 3 | Unavailable execution-event directory redirect fixtures |
| 43 | 1 | Explicit feature-table full-history opt-in proof |

### Exact full-release command

Run with the retained CPW full-release Python 3.12 environment and process-only
isolated test database variables; no connection strings are recorded here.

```text
python tools/dev/verify.py --validation-preset full-release --full-pytest-sharded --pytest-shard-profile full-release-balanced-v1 --authorized-path research/schemas/bounded_research_envelope.schema.json --authorized-path research/schemas/bounded_research_envelope_control.schema.json --authorized-scope research-schema --authorized-package WP-V2-AUTONOMY-KERNEL-01 --base-ref 9d9f8a94405ded76bbef0163488b9a8e0596371a --head-ref d98bf03376f8e1fc4b3450ff77186fc0f2091c6c --json
```

Raw command/results, all shard outcomes, skip accounting, provenance and semantic
blob comparison are retained outside the repo in the package validation directory.
The final documentation-only tail receives docs-only verification and diff checks.

## Prior STOP and approved resolution

The previous full-release failed solely on the absent ignored D4 normalized
CSV in shards 5, 6 and 33. Its failure and STOP were not accepted as a pass.
The user explicitly authorized Karl's 2026-10-08 validation-only continuation,
superseding only WP section 40's product/backtest regression prohibition for
existing mandatory full-release tests. All other boundaries remain intact.

The existing primary-checkout regular-file D4 copy was verified against the
committed 15m D4 catalog before copying: SHA-256
`c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`,
**220,128 data rows**. Source and destination ancestors were checked for
symlink/reparse redirects; no web download, regeneration or substitute data.
The destination was absent, was copied to the exact ignored D4 path, and was
verified byte-identical. After the full-release PASS, only that continuation-
created ignored copy was removed; the original source was retained. No D4 file
was committed. Cleanup left the tracked worktree clean.

The earlier H-004 `h004-clean` context retains its two verified ignored inputs;
no execution stream was hydrated. Known missing legacy execution-stream and
Strategy-Spec hash context remains disclosed, without canonical mutation.
The continuation created no manual experiment or production research run.

## Database environment

PostgreSQL 16.15 from a retained image, dedicated isolated loopback cluster on a
non-default port, no repository/service mounts, no production connection.
Authority and Research Memory use separate logical test databases. Actual
logical separation and bounded writer-role physical proof PASS; required
PostgreSQL proof is 13 passed / zero skips. No credentials or connection strings
are retained in this evidence.

## Authority and next dependency

Implementation authority only: immutable envelope/control binding, separate
durable scientific lineage/accounting/holdout primitives and exact proposal
handoff recovery. The historical full-suite backtest exception creates no
ongoing runner authority. No Stage 5B, autonomous activation, WFO/OOS,
robustness/Monte Carlo, real final-holdout access, canonical Result Population,
candidate/promotion, protected runtime/risk/OMS/reconciliation/overlay/safe-mode,
paper/live/exchange/order or capital authority.

Next dependency: `V2-RESEARCH-FACTORY-LOOP-01`, separately authorized after
accepted merge and refreshed Side truth. Hold for Side 22 exact-head review;
no self-merge and no independent review claimed.
