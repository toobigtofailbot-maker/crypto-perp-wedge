# Fixture matrix

All fixtures are non-production and live under this package scratch directory. The valid STRAT-SPEC-0007 fixture reproduces current canonical source bytes. The generic fixture is materialized by tests at its declared logical `research/strategy_specs/STRAT-SPEC-9000.strategy_spec.json` path. STRAT-SPEC-9000 tests schema and content-binding mechanics only; it grants no production fact authority and is not an in-scope H-004 Strategy Spec.

| Fixture | Expected result | Contract point |
|---|---|---|
| `valid/STRAT-SPEC-0007.external_content_readiness.json` | pass | H-C binding over the current H-004 Strategy Spec |
| `valid/STRAT-SPEC-9000.external_content_readiness.json` | pass | non-production-only generic schema/content mechanics |
| `invalid/wrong_raw_hash.case.json` | fail | exact raw hash |
| `invalid/wrong_canonical_hash.case.json` | fail | exact full canonical hash |
| `invalid/wrong_canonicalization.case.json` | fail | closed canonicalization |
| `invalid/wrong_spec_id_path.case.json` | fail | derived ID/path binding |
| `invalid/missing_byte_length.case.json` | fail | required byte length |
| `invalid/legacy_falsely_verified.case.json` | fail | no legacy verification claim |
| `invalid/repo_wide_authority_claim.case.json` | fail | no repo-wide migration |
| `invalid/strategy_spec_mutation_claim.case.json` | fail | no source mutation |
| `invalid/missing_unresolved_disclosure.case.json` | fail | mandatory unresolved disclosure |
| `invalid/duplicate_superseding_behavior.case.json` | fail | no duplicate/superseding behavior |
| `invalid/dispatch_runtime_ranking_authority.case.json` | fail | no dispatch/runtime/ranking authority |
