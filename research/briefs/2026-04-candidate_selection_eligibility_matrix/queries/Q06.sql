SELECT
    'forbidden_output_field' AS posture_kind,
    forbidden_field AS posture_value,
    'excluded_from_wp10k_outputs' AS wp10k_posture
FROM (
    VALUES
        ('rank'),
        ('score'),
        ('recommendation'),
        ('promotion_status'),
        ('paper_live_readiness'),
        ('policy_action'),
        ('runtime_action')
) AS forbidden_fields(forbidden_field)
UNION ALL
SELECT
    'supported_next_package_class' AS posture_kind,
    package_class AS posture_value,
    'supported_as_future_bounded_planning_or_consumer_work' AS wp10k_posture
FROM (
    VALUES
        ('candidate-selection eligibility matrix / rule application'),
        ('evidence-generation architecture detail')
) AS supported_classes(package_class)
UNION ALL
SELECT
    'forbidden_next_package_class' AS posture_kind,
    package_class AS posture_value,
    'requires_later_explicit_main_3_0_authorization_or_remains_out_of_scope'
        AS wp10k_posture
FROM (
    VALUES
        ('EXP planning without Main 3.0 approval'),
        ('policy/scoring/ranking/paper-live/runtime')
) AS forbidden_classes(package_class)
ORDER BY posture_kind, posture_value
