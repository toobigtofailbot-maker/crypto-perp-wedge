SELECT *
FROM (
    VALUES
        (
            'supported_descriptive',
            'floor-crossed exact-segment inventory',
            'Supported only for H-004 / research_oos / post_wp_5b / exp_success_criteria from Q01.'
        ),
        (
            'supported_descriptive',
            'per-observation review',
            'Supported for REC-0011, REC-0025, and REC-0026 from Q02 and Q03.'
        ),
        (
            'supported_descriptive',
            'within-segment cross-observation summary',
            'Supported inside the crossed exact segment; no INSUFFICIENT_EVIDENCE marker is required for within-segment patterns.'
        ),
        (
            'supported_descriptive',
            'EXP-success comparison-surface review',
            'Supported for EXP-success comparison rows exposed by Q04 only.'
        ),
        (
            'supported_descriptive',
            'comparison-surface availability review',
            'Supported for unavailable, skipped, null, or insufficient-evidence comparison posture exposed by Q05 only.'
        ),
        (
            'supported_descriptive',
            'consumer-brief methodology example',
            'Supported as an example for later floor-crossed expectation-source segment briefs without authorizing those later briefs.'
        ),
        (
            'supported_descriptive',
            'gap review for brief coverage',
            'Supported as a descriptive coverage-gap review only.'
        ),
        (
            'marker_rule',
            'INSUFFICIENT_EVIDENCE not required within crossed exact segment',
            'Within-segment cross-observation patterns for the selected exact segment may be stated descriptively.'
        ),
        (
            'marker_rule',
            'INSUFFICIENT_EVIDENCE required for cross-boundary claims',
            'Claims outside the selected exact segment require INSUFFICIENT_EVIDENCE or explicit forbidden-boundary language.'
        ),
        (
            'forbidden_claim',
            'cross-segment inference',
            'Forbidden by PFC-2-style boundaries and outside this brief scope.'
        ),
        (
            'forbidden_claim',
            'D2 versus EXP-success comparison',
            'Forbidden; sibling d2_006_gates co-existence may be disclosed as structural inventory only.'
        ),
        (
            'forbidden_claim',
            'H-004 general inference',
            'Forbidden; this brief is exact-segment only.'
        ),
        (
            'forbidden_claim',
            'H-004 pre/post comparison',
            'Forbidden; pre-WP-5b and post-WP-5b rows remain structurally separate.'
        ),
        (
            'forbidden_claim',
            'aggregate-corpus or cohort-level inference',
            'Forbidden; this brief does not combine segment, corpus, or cohort evidence.'
        ),
        (
            'forbidden_claim',
            'predictive inference',
            'Forbidden; current observations do not project future observations.'
        ),
        (
            'forbidden_claim',
            'policy, scoring, ranking, recommendation, paper-live, runtime, lifecycle, promotion, or demotion authority',
            'Forbidden; the brief is descriptive only and carries no protected-path or operational authority.'
        ),
        (
            'forbidden_claim',
            'Path B, cohort implementation, paired-source reuse, H-001 runway work, H-005 or H-006 work, new candidate, or protected-path work',
            'Forbidden; no such direction is authorized by this brief.'
        ),
        (
            'post_brief_stop_rule',
            'no automatic further work from WP-S2c-7',
            'WP-S2c-7 authorizes no successor package and does not start or modify the A2C-001 H-001 runway.'
        )
) AS boundary_claims(claim_class, claim, basis)
ORDER BY claim_class, claim
