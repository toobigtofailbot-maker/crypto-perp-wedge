SELECT *
FROM (
    VALUES
        (
            'supported_descriptive',
            'floor-crossed exact-segment inventory',
            'Supported only for H-004 / research_oos / post_wp_5b / d2_006_gates from Q01.'
        ),
        (
            'supported_descriptive',
            'per-observation review',
            'Supported for REC-0022, REC-0023, and REC-0024 from Q02 and Q03.'
        ),
        (
            'supported_descriptive',
            'within-segment cross-observation summary',
            'Supported inside the crossed exact segment; no INSUFFICIENT_EVIDENCE marker is required for within-segment patterns.'
        ),
        (
            'supported_descriptive',
            'per-metric comparison pattern review',
            'Supported for compared metrics exposed by Q04 only.'
        ),
        (
            'supported_descriptive',
            'comparison-surface gap review',
            'Supported for extracted-only and skipped-comparison rows exposed by Q05 only.'
        ),
        (
            'supported_descriptive',
            'consumer-brief methodology example',
            'Supported as an example for later floor-crossed-segment consumer briefs without authorizing those later briefs.'
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
            'Forbidden by WP-10z PFC-2 and outside this brief scope.'
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
            'H-004 post-WP-5b D2 versus exp_success_criteria comparison',
            'Forbidden; expectation sources remain separate.'
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
            'Path B, cohort, new candidate, or protected-path work',
            'Forbidden; no such direction is authorized by this brief.'
        ),
        (
            'post_brief_stop_rule',
            'no automatic further Stage 2 work',
            'WP-10z PFC-3 remains active; another explicit chat-level direction-setting decision is required after WP-11a.'
        )
) AS boundary_claims(claim_class, claim, basis)
ORDER BY claim_class, claim
