# CPW-PREFECT-01 — P1/P2/P3 Acceptance

- Branch: `codex/cpw-prefect-01-p1-p2-p3-acceptance`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/715
- Package class: T2, mandatory full-release
- Scope: pin Prefect 3.8.6 and prove P1/P2/P3 against the isolated local test backend without cutover.
- Merge status: open and not merged; mandatory full-release is satisfied and the PR is ready for Side exact-head review.

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
| Required T2/full-release | 22.9 | passed at implementation head `9567d127b625a939eb10abd4e4a4aad7a8ef3364` under `h004-clean` | satisfied |
| CPW-PREFECT-02 only becomes eligible | 0, 19 | architecture and project-status records | satisfied |

## Validation summary

Pre-mutation oracles passed: 93, 60, and 9 tests. Dependency compatibility,
clean lock completeness, Prefect 3.8.6 imports, and `pip check` passed in the
isolated proof and bound repo environments. Focused acceptance passed 12 tests;
post-mutation CPW domain/lab, Search Governor, scheduler/research-automation,
and Hermes oracles passed 58, 17, 78, and 9 tests respectively.

The mandatory full-release passed at implementation head
`9567d127b625a939eb10abd4e4a4aad7a8ef3364` under the locked `h004-clean`
context: the exact ignored canonical 1d and funding datasets were present and
the H-004 execution stream was absent. All 48 selected shards passed; all 181
tracked test files were assigned exactly once; 3,942 nodes completed as 3,897
passed and 45 accepted environment skips; and there were zero missing,
duplicate, incomplete, not-run, or timed-out assignments. The accepted skips
were limited to absent optional local data or PostgreSQL DSNs and unavailable
Windows symlink/junction privileges. `overall_status=pass`.

The earlier environment failures and single RP-0007 fractional-timestamp
inference failure are superseded by 5/5 fresh-process passes of
`test_current_integrity_views_empty_under_pre_execution_refinement`, a complete
`tests/test_research_query.py` pass (82 passed), and the successful
full-release exclusive query shard (82 passed). The timestamp failure was not
reproducible on either refreshed `main` or this PR head, so no query code or
test change was justified or made. This PR is ready for Side exact-head review.

## Boundary summary

No lab scheduler, research automation, lab pipeline, Search Governor, domain or
storage semantics, canonical, Hermes, Nautilus, backtester, candidate lifecycle,
runtime, paper/live, OMS, risk, reconciliation, overlay, exchange, order,
credential, or capital path changes are authorized or present.

## Next dependency / runway

Merge makes `CPW-PREFECT-02` eligible for separate drafting only. No subsequent
package or cutover is automatically authorized, and the project remains
serialized under Karl's current instruction.
