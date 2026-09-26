# CPW-PREFECT-01 — P1/P2/P3 Acceptance

- Branch: `codex/cpw-prefect-01-p1-p2-p3-acceptance`
- PR: to be opened before final validation
- Package class: T2, mandatory full-release
- Scope: pin Prefect 3.8.6 and prove P1/P2/P3 against the isolated local test backend without cutover.
- Merge status: open implementation package; not merged.

## Changed files

1. `tools/prefect_integration/__init__.py`
2. `tools/prefect_integration/acceptance.py`
3. `tests/test_prefect_acceptance.py`
4. `docs/architecture/2026-09-prefect_p1_p2_p3_acceptance_contract.md`
5. `docs/status_entries/CPW-PREFECT-01.md`
6. `requirements.txt`
7. `requirements.lock.txt`
8. `docs/project_status.md`

## Active-WP Requirement Traceability

| Requirement | WP source section | Evidence location | Status |
| --- | --- | --- | --- |
| Exact Prefect 3.8.6 dependency | 9.1 | dependency files and exact-version test | satisfied |
| Clean constrained dependency compatibility | 7.D | isolated Python 3.11 compatibility probe | satisfied |
| Fresh-lock install and pip check | 9.3 | clean `--no-deps` proof environment | satisfied |
| Local-only Prefect test backend | 18 | acceptance fixture and architecture record | satisfied |
| P1 actual concurrency | 13.2 | `test_p1_concurrency_preserves_frozen_order_denominator_and_repeatability` | satisfied |
| P1 deterministic scientific order | 13.3 | P1 result assertions and CPW validator | satisfied |
| P1 full denominator | 13.3 | P1 result assertions and CPW validator | satisfied |
| P2 actual PAUSED state | 14.4 | backend state polling in gate helper | satisfied |
| P2 exact CPW validation | 14.5 | `validate_prereg_approval` call and valid case | satisfied |
| Invalid approval matrix | 14.6 | six parameterized invalid cases | satisfied |
| P2 no duplicate continuation | 14.7 | second-resume assertion and byte check | satisfied |
| P3A Prefect retry | 15A | runtime `run_count`, attempt files, client record | satisfied |
| P3A one scientific identity/denominator | 15A.3 | one-row CPW-validated ledger | satisfied |
| P3B fresh-flow recovery | 16.2–16.3 | failed flow A and successful distinct flow B | satisfied |
| P3B exact-effect reuse/no rewrite | 16.3 | bytes/hash/mtime and disposition assertions | satisfied |
| Conflict fail-closed | 16.4 | conflicting fresh flow and unchanged-byte assertions | satisfied |
| P3 canonical non-authority/no overclaim | 21 | source and architecture record | satisfied |
| Test harness test-only classification | 18 | architecture record | satisfied |
| Negative semantic-owner proof | 17, 18 | source/AST negative test | satisfied |
| No existing orchestration cutover | 17 | closed diff and architecture record | satisfied |
| No framework authority drift | 3 | owner matrix and source/AST test | satisfied |
| Exact eight-path scope | 8 | committed range proof | satisfied |
| Required T2/full-release | 22.9 | final validation record to be added after run | blocked |
| CPW-PREFECT-02 only becomes eligible | 0, 19 | architecture and project-status records | satisfied |

## Validation summary

Pre-mutation oracles passed: 93, 60, and 9 tests. Dependency compatibility,
clean lock completeness, Prefect 3.8.6 imports, and `pip check` passed in the
isolated proof and bound repo environments. Focused acceptance passed 12 tests.
Final adjacent and full-release evidence will replace this paragraph before the
PR is reported ready.

## Boundary summary

No lab scheduler, research automation, lab pipeline, Search Governor, domain or
storage semantics, canonical, Hermes, Nautilus, backtester, candidate lifecycle,
runtime, paper/live, OMS, risk, reconciliation, overlay, exchange, order,
credential, or capital path changes are authorized or present.

## Next dependency / runway

Merge makes `CPW-PREFECT-02` eligible for separate drafting only. No subsequent
package or cutover is automatically authorized, and the project remains
serialized under Karl's current instruction.
