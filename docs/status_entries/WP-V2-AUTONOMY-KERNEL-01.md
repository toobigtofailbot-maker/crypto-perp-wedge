# WP-V2-AUTONOMY-KERNEL-01

Branch-state T3 implementation; corrected scientific-lineage invariant and all
required release gates now PASS after Side 22's validation-only triage.
Not merged or activated; hold for Side 22 exact-head re-review. No self-merge.
Branch: `codex/wp-v2-autonomy-kernel-01`.
Exact base: `9d9f8a94405ded76bbef0163488b9a8e0596371a`.
Old reviewed remote head: `322a02028896893d415eae71d48d987fd335406a`.
Corrected semantic and passing full-release head:
`69d686dc1d22d283ff5a5b6490775092a463b80a`.
Final head is a documentation-only evidence tail; its exact SHA and the updated
PR #735 remote identity are recorded in the publication report. No independent
review of the corrected head is claimed. Ready for Side exact-head re-review: YES.

## Repo truth

Refreshed `origin/main` matched the exact base before correction and again
before this evidence tail. PR #735 was the only open PR and its old exact remote
head remained unchanged before publication; no competing PR existed.
D2-026 remains LOCKED and unsuperseded. Consumers are the governed pilot and
focused tests; no factory/production successor consumer was found. Existing
psycopg/Optuna/Prefect and jsonschema/Pydantic dependencies suffice.
The correction changed only store.py, the new/unmerged 0001 migration, and
test_research_autonomy_postgres.py. All 22 non-documentation files remain
byte-identical to the corrected semantic head through the local evidence tail.
The semantic-to-final diff is restricted to the three permitted docs.

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

Physical Cases A-K were revalidated by the focused, adjacent and expanded live
PostgreSQL suites at the corrected semantic head. The mandatory complete
full-release rerun also PASSes at that exact head.

| Case | Result | Evidence |
| --- | --- | --- |
| A Envelope/control | PASS | Both closed schemas/fixtures; malformed/hash/repo/approval/control inputs rejected; no production envelope |
| B DB/migration/role | PASS | 13 tables, 102 constraints, 91 columns and exact triggers; repeat/checksum/immutability/privilege proofs |
| C Initial campaign | PASS | Registered exact envelope, zero prior history, atomic 6-proposal/4-trial reservation, frozen lineage binding |
| D Wave/accounting | PASS | Exact Governor identities/counts; one audit advance; original idempotent outcomes; numeric-type tamper rejected; retries retain trial ID |
| E Successor | PASS | Exact frozen parent identity and fixed campaign fingerprint; rejected relabel/substitution leaves every authority row unchanged; bounded same-hypothesis continuation succeeds |
| F Concurrency | PASS | One of two conflicting successors wins; cumulative used/reserved remain within ceilings |
| G Holdout/contamination | PASS | Isolated attempt stays unconsumed; informative escape persists; restoration/new-domain/new-ID bypass rejected |
| H Memory independence | PASS | Unchanged Memory rebuild/bootstrap in separate DB and complete synthetic .cpw deletion preserve authority |
| I Active handoff/replay | PASS | Contained/gitignored exact wave replay; rehashed numeric-type and lineage/contract/proposal tampering rejected |
| J Governor/Optuna | PASS | Existing legality/pilot regressions; explicit synthetic bindings; no autonomy .successor authority call |
| K Zero activation | PASS | Exact 25-file diff; no integration/activation/protected mutation; no factory execution; historical regression exception separately recorded |

- Focused: **46 passed**, 24 expected Optuna experimental warnings.
- Adjacent: **60 passed**.
- Live PostgreSQL: **20 passed, zero skips** (17 authority cases, including seven new adversarial cases, and three existing Memory cases).
- Envelope validator: **PASS**, default zero files and two fixture files.
- Exact 21-created / 4-modified closure and base-to-head diff checks: **PASS**.
- Complete full-release rerun at the corrected semantic head: **PASS**,
  **4,007 passed tests**, **23 accounted existing skips**. All **48 shards PASS
  and complete**, **zero timeouts**, all **196 tracked files assigned exactly
  once**, no missing/duplicate/untracked assignments.
- All **eight required non-shard commands PASS**, including exact schema-path
  authorization and forbidden-scope checks.
- Assignment manifest:
  `sha256:58844f89d411d5626e06c4755d73f9b3d1be3dbc648c67c8439209c0c46c99c8`.
- Slowest shard: 5, **1,029.86 seconds**, below the unchanged 1,800-second limit.
- The exact shard-40 four-file triage group PASSed: **74 passed**, complete
  untruncated stdout/stderr retained outside the repo. Shard 40 then PASSed
  inside the complete release rerun as well.
- Required authority/Memory PostgreSQL proof is **20 executed / zero skips**.
  Shard 41 PASS (84 passed, three unrelated directory-redirect skips);
  shard 46 PASS (102 passed, zero skips). N1/adapter/taker-flow shards 5/6/33 PASS.
- Full raw stdout/stderr pairs and individual statuses for all 48 shards and
  eight non-shard commands are retained outside the repo, alongside the JSON
  verifier result and exact command. No output was limited to the 4,000-character
  per-command excerpts. Capture-only external observation wrapped the unchanged
  verifier command executor; test commands, concurrency, timeout and pass/fail
  logic were unchanged. No repo helper or test file was modified.

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

No existing test was modified, mocked, weakened, deselected, marked xfail or
newly skipped. Seven new adversarial cases were added in the authorized test file.
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
python tools/dev/verify.py --validation-preset full-release --full-pytest-sharded --pytest-shard-profile full-release-balanced-v1 --authorized-path research/schemas/bounded_research_envelope.schema.json --authorized-path research/schemas/bounded_research_envelope_control.schema.json --authorized-scope research-schema --authorized-package WP-V2-AUTONOMY-KERNEL-01 --base-ref 9d9f8a94405ded76bbef0163488b9a8e0596371a --head-ref 69d686dc1d22d283ff5a5b6490775092a463b80a --json
```

Raw command/results, all shard outcomes, skip accounting, provenance and semantic
blob comparison are retained outside the repo in the package validation directory.
The final documentation-only tail receives docs-only verification and diff
checks. All non-documentation Git blobs remain identical to the passing
corrected semantic head.

## Side 22 correction, failed-run history and passing triage

Side 22 inspected remote head `322a02028896893d415eae71d48d987fd335406a`
and found that parent-linked successors could substitute another envelope-legal
hypothesis fingerprint and misattribute hypothesis budgets. Prior green tests
did not prove this invariant.

At corrected semantic head `69d686dc1d22d283ff5a5b6490775092a463b80a`:

- Every new search must match the campaign's fixed fingerprint before mutation.
- Successors load and hash-verify the exact finalized same-campaign parent's
  frozen contract and retain its hypothesis_id, family_id and fingerprint.
- The new/unmerged migration rejects mismatched campaign fingerprints on every
  search INSERT and rejects successor parent-identity relabeling independently.
- Seven new physical cases use two otherwise valid, explicitly allowed
  synthetic mechanisms and recomputed envelope/intent hashes. They prove
  application rejection of fingerprint substitution and either identity relabel;
  direct SQL rejection on initial/successor fingerprints and parent identities;
  no change to any authority table; and legal narrowed bounds/changed seed with
  exact durable counts and campaign ceilings. These cases all PASS.

The first corrected-head full-release genuinely FAILed: all 48 completed,
47 PASS / shard 40 FAIL, zero timeouts. Setup failed for:
`tests/test_execution_event.py::test_malformed_or_conflicting_streams_fail_closed[duplicate_variant-variant ID recurs]`.
The captured traceback entered the unchanged dispatch-authorization writer;
the underlying exception was truncated by the verifier's excerpt limit.
One isolated diagnostic PASSed. That diagnostic did not constitute acceptance,
and the correction remained unpublished pending Side 22's disposition.

Side 22 then explicitly authorized validation-only triage: same branch,
worktree and PR, unchanged corrected semantic bytes, exact four-file group
first, then the complete release at that semantic head with raw output retained.
Both the group (74 passed) and all 48 release shards PASSed. The original cause
remains unknown; a transient setup failure is plausible but unproven. No
protected writer, runner or existing test was edited to obtain this result.
No test was mocked, weakened, deselected, marked xfail or newly skipped.

The earlier STOP docs-tail commit `2590b10aeef7e897805877fef13ec6a4121d42c7`
remains retained locally. To test the exact prescribed semantic commit, the same
branch/worktree selected `69d686dc1d22d283ff5a5b6490775092a463b80a` with a
clean `git reset --keep`; only the earlier three-doc tail was set aside.
Its factual failed-run evidence was preserved in this final documentation tail.
An initial capture-wrapper entrypoint error occurred before any release command
ran; it was corrected outside the repo. It is not presented as a test result.

The previous failed release and one passed diagnostic were never accepted as
release success. This new complete passing invocation is the acceptance proof.
Publish the same branch and update only PR #735 after final docs/scope/clean
checks. Hold for Side 22 exact-head re-review; do not merge or claim independent
review/merge readiness.

## Prior STOP and approved resolution

The original full-release failed on missing D4 data. The approved validation
continuation later PASSed at `d98bf03376f8e1fc4b3450ff77186fc0f2091c6c`
(4,000 passed / 23 accounted skips), published as remote head
`322a02028896893d415eae71d48d987fd335406a`.
That historical PASS neither proved the missing lineage invariant nor replaces
the corrected head's invariant proof or its passing complete rerun.
The user explicitly authorized Karl's 2026-10-08 validation-only continuation,
superseding only WP section 40's product/backtest regression prohibition for
existing mandatory full-release tests. All other boundaries remain intact.

The existing primary-checkout regular-file D4 copy was verified against the
committed 15m D4 catalog before copying: SHA-256
`c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`,
**220,128 data rows**. Source and destination ancestors were checked for
symlink/reparse redirects; no web download, regeneration or substitute data.
The destination was absent, was copied to the exact ignored D4 path, and was
verified byte-identical. Both corrected-head attempts reverified the same
retained source against the
committed catalog and used byte-identical ignored copies. Each run-created copy
was removed after its validation, including the final passing triage run; the
original source was retained. No D4 file was committed. Cleanup left the
tracked worktree clean.

The earlier H-004 `h004-clean` context retains its two verified ignored inputs;
no execution stream was hydrated. Known missing legacy execution-stream and
Strategy-Spec hash context remains disclosed, without canonical mutation.
The continuation created no manual experiment or production research run.

## Database environment

PostgreSQL 16.15 from a retained image, dedicated isolated loopback cluster on a
non-default port, no repository/service mounts, no production connection.
Authority and Research Memory use separate logical test databases. Actual
logical separation and bounded writer-role physical proof PASS; required
PostgreSQL proof is 20 passed / zero skips. No credentials or connection strings
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
