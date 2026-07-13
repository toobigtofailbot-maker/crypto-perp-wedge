# Full-suite sharded validation summary

- Collection: 2848 nodes; SHA-256 e785f8add24c57f09225779b6c1fc3a605fd30083226c212d82a73f8b553f296.
- Terminal leaf shards: 8; zero timeouts; zero internal errors.
- Aggregate: 2836 passed, 6 failed, 6 skipped, 0 errors.
- Exact node coverage once: True.
- Failure union exactly matches source-hash-bound six-node allowlist: True.
- All 15 affected lab-state nodes passed.

## Exact remaining failures

- tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage
- tests/test_lab_operator_surface.py::test_batch_boundary_reflects_coverage_gap_closure
- tests/test_research_query.py::test_current_integrity_views_empty_under_pre_execution_refinement
- tests/test_research_query.py::test_strategy_spec_integrity_views_empty_under_current_zero_instance_state
- tests/test_research_query.py::test_strategy_spec_relation_first_instance_repo_state
- tests/test_research_query.py::test_strategy_spec_views_expose_first_instance_repo_state

The repository baseline remains red on these six pre-existing unrelated failures. This validation introduces no skip, xfail, suppression, or unrelated repair.

At the current PR head, the coverage CLI observes 2,109 discovered artifacts. The 59 tracked package-evidence files explain the increase from the earlier 2,049 observation. The stable test invariant is that total equals inventory length and exceeds 1,000; exact contract counts remain 123 covered, 119 surface-visible, zero gaps, and zero malformed. The production fix remains byte-identical.

The narrow follow-up reran the complete affected S04 terminal shard: 355 passed, zero failed, zero skipped, and zero errors. Replacing the original 355-pass S04 result leaves the aggregate unchanged at 2,836 passed, 6 failed, 6 skipped, and zero errors, with the failure union still an exact allowlist match.

## Preliminary harness attempts

- S01 attempt 1 used an absent in-repo basetemp parent and was superseded after preserving its evidence.
- S03 attempt 1 used an in-repo basetemp that deliberately triggered path guards and was superseded by the terminal external-temp run.
- Neither preliminary attempt is included in terminal coverage or aggregate totals.
