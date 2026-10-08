# WP-V2-AUTONOMY-KERNEL-01

Branch-state T3 implementation; STOP at full-release acceptance; not pushed,
not merged, not activated, no self-merge.
Branch: `codex/wp-v2-autonomy-kernel-01`.
Exact base: `9d9f8a94405ded76bbef0163488b9a8e0596371a`.
Semantic implementation head: `51a05391a7703691a6adf2bee3588cddbdcda832` (tested; full-release not accepted).
Final head: local docs-only branch tip after this factual evidence tail; its
exact SHA is recorded in the final report. No remote head or PR exists.

## Repo truth

Refreshed `origin/main` matched the exact base. No open/competing PR or package
branch existed. D2-026 remained LOCKED and unsuperseded. Consumers were only
the governed pilot and focused tests; no factory/production successor consumer
was found. Existing psycopg/Optuna/Prefect pins and jsonschema/Pydantic suffice.

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

Physical Cases A-K ran at the exact semantic head above. Package acceptance
remains incomplete because the mandatory full-release verifier failed.

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
| K Zero activation | PASS | Exact 25-file diff; no integration/activation/protected mutation; real N1 corpus execution blocked before data load |

At the semantic head:

- Focused: **46 passed**, 24 expected Optuna experimental warnings.
- Adjacent: **60 passed**.
- Live PostgreSQL: **13 passed, zero skips** (authority and existing Memory suites).
- Envelope validator: **PASS**, default zero files and two fixture files.
- Exact scope and base-to-semantic `git diff --check`: **PASS**; worktree clean.
- Full-release: **FAIL**. All 48 named-profile shards completed; 45 passed,
  three failed (indices **5, 6, 33**); zero timeouts. All 196 discovered tracked
  profile files were assigned exactly once. All eight non-shard commands passed,
  including exact schema-path authorization and forbidden-path checks.
- Failures: existing `tests/test_nautilus_n1_acceptance.py`,
  `tests/test_nautilus_research_adapter.py`, and
  `tests/test_takerflow_feature_materialization.py` require the absent ignored
  `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`.
- Validation context: verified H-004 exact local corpus v1, `h004-clean`;
  its two approved ignored inputs were copied byte-for-byte. No execution stream
  was hydrated and no D4 corpus was copied/read.

## Defined STOP / escalation

WP section 40 says to STOP when a product runner/backtest is required, or real
final-holdout data must be opened. The mandatory native N1 acceptance test calls
`research.execute_nautilus_research(inputs)` twice on the real D4 corpus after
`validate_resolved_inputs()`. That adapter loads the real CSV and invokes its
Nautilus backtest executor. Its current failure happens at the missing-file
validation check, before real corpus execution. No test was skipped, changed,
mocked, or weakened to make full-release pass.

The retained root checkout contains a D4 file, but availability and historical
N1 approval do not expand this package's authority. Side 22 must resolve the
full-release requirement versus the explicit product-backtest/holdout boundary
through a revised validation disposition/package. No kernel code defect is
asserted by these missing-input failures.

No push or PR: section 41 forbids pushing before all required acceptance passes.
Ready for Side exact-head acceptance review: **NO**; the local implementation
and this stop evidence are available for scope resolution. No self-merge.

## Database environment

PostgreSQL 16.15 from a retained image, dedicated isolated loopback cluster on a
non-default port, no repository/service mounts, no production connection.
Authority and Research Memory use separate logical databases whose names
contain `test`, with process-scoped test DSN variables. No credentials or DSN
values are retained here. Actual logical DB separation and bounded writer-role
physical proof both passed.

## Authority and next dependency

Implementation authority only: immutable envelope/control binding, separate
durable scientific lineage/accounting/holdout primitives and exact proposal
handoff recovery. No Stage 5B, autonomous activation, runner/WFO/OOS/robustness/
Monte Carlo, real holdout access, canonical Result Population/candidate/
promotion, protected runtime/risk/OMS/reconciliation/overlay/safe-mode,
paper/live/exchange/order or capital authority.

Next dependency: `V2-RESEARCH-FACTORY-LOOP-01`, separately authorized after
accepted merge and refreshed Side truth. Hold for Side 22 exact-head review;
this branch is not called merge-ready.
