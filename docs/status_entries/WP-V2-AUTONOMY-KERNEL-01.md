# WP-V2-AUTONOMY-KERNEL-01

Branch-state T3 implementation; not merged, not activated, no self-merge.
Branch: `codex/wp-v2-autonomy-kernel-01`.
Exact base: `9d9f8a94405ded76bbef0163488b9a8e0596371a`.
Semantic head: pending committed final implementation.
Final head: reported by the final branch/PR exact-head evidence after any docs tail.

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

Final committed-head acceptance is pending. Development test passes are not
final semantic-head evidence.

| Case | Final result | Evidence |
| --- | --- | --- |
| A Envelope/control | NOT RUN | Final committed head pending |
| B DB/migration/role | NOT RUN | Final committed head pending |
| C Initial campaign | NOT RUN | Final committed head pending |
| D Wave/accounting | NOT RUN | Final committed head pending |
| E Successor | NOT RUN | Final committed head pending |
| F Concurrency | NOT RUN | Final committed head pending |
| G Holdout/contamination | NOT RUN | Final committed head pending |
| H Memory independence | NOT RUN | Final committed head pending |
| I Active handoff/replay | NOT RUN | Final committed head pending |
| J Governor/Optuna | NOT RUN | Final committed head pending |
| K Zero activation | NOT RUN | Final diff inspection pending |

Focused/adjacent/live PostgreSQL/validator/full-release/shard finality and
`git diff --check`: final evidence pending.

## Database environment

PostgreSQL 16.15 from a retained image, dedicated isolated loopback cluster on a
non-default port, no repository/service mounts, no production connection.
Authority and Research Memory use separate logical databases whose names
contain `test`, with process-scoped test DSN variables. No credentials or DSN
values are retained here. Writer-role physical proof is mandatory.

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
