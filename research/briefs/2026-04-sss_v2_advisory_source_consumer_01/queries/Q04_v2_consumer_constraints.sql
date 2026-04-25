SELECT
    'first_v2_consumer_over_sss_0002' AS constraint_key,
    'This bundle is the first bounded downstream consumer over the committed SSS v2 instance SSS-0002.' AS constraint_statement,
    'Repo truth contains WP-8a plus SSS-0002 and no prior v2 consumer brief.' AS supported_by_current_repo_truth

UNION ALL

SELECT
    'no_runtime_or_policy_authority' AS constraint_key,
    'The brief is descriptive only and grants no runtime, policy, override, OMS, risk, or execution authority.' AS constraint_statement,
    'SSS-0002 notes advisory-only semantics and the package scope forbids protected-path changes.' AS supported_by_current_repo_truth

UNION ALL

SELECT
    'no_schema_or_validator_modification' AS constraint_key,
    'The consumer reads the committed v2 instance without modifying any schema or validator.' AS constraint_statement,
    'The package uses existing SSS v1 and v2 schema and validator files unchanged.' AS supported_by_current_repo_truth

UNION ALL

SELECT
    'below_floor_limits_claims' AS constraint_key,
    'Below-floor evidence still limits the consumer to insufficiency statements rather than usable source-level rates.' AS constraint_statement,
    'Both SSS-0002 source segments have observation_count = 5, floor_required = 10, and null usable rates.' AS supported_by_current_repo_truth

UNION ALL

SELECT
    'v2_solves_shape_not_sufficiency' AS constraint_key,
    'SSS v2 solves the first-class source-only instance shape while leaving evidence sufficiency dependent on corpus size.' AS constraint_statement,
    'SSS-0002 uses segmentation_axes = [\"advisory_source\"], but both realized sources remain below the locked floor.' AS supported_by_current_repo_truth

ORDER BY constraint_key;
