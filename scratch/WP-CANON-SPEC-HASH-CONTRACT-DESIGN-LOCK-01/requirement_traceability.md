# Active-WP requirement traceability

| Active-WP requirement | Source | Evidence | Status |
|---|---|---|---|
| H-004-dispatch-scoped H-C, no repo-wide migration or authority | sections 2, 9.1, 13 | architecture `Decision and scope`; schema non-authority constants | satisfied |
| Bind raw bytes and full repo-canonical JSON | sections 9.2, 9.4 | architecture `Locked two-hash binding`; schema `content_binding`; valid fixtures | satisfied |
| Preserve and disclose legacy internal scope as unresolved | sections 9.3, 9.4 | architecture `Legacy internal hash posture`; schema `legacy_internal_hash`; tests | satisfied |
| Future immutable fact shape and create semantics | sections 9.4, 9.5 | schema; architecture `Future immutable fact contract` and `Immutable creation requirements` | satisfied |
| Two separate future query surfaces | section 9.6 | architecture `Locked two-view posture` | satisfied |
| Downstream dispatch binding after PR #665 | section 9.7 | architecture `Downstream dispatch binding after PR #665` | satisfied |
| Valid and invalid non-production fixtures | section 10 | `fixture_matrix.md` and `fixtures/` | satisfied |
| Targeted schema/semantic/preservation tests | section 11 | `tests/test_strategy_spec_external_content_readiness_contract.py` | satisfied |
| No production fact, validator, views, dispatch schema, or canonical artifact mutation | sections 3, 7, 12, 13 | changed-file allowlist; preservation manifest; boundary scan | satisfied |
| Required validation and unchanged integrity baseline | sections 14, 15 | `integrity_baseline.json`; final `validation_summary.json` | satisfied |
| Package status fragment, commit, push, ready PR | sections 7, 17 | status fragment and GitHub PR #666 | satisfied |
