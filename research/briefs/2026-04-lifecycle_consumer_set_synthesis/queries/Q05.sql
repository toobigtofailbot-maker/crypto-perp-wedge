SELECT *
FROM (
    VALUES
        (
            'current LCH corpus inventory',
            'supported_descriptive',
            'current central lifecycle query surfaces expose row, candidate, transition, evidence, and boundary counts',
            null,
            false
        ),
        (
            'per-candidate retrospective path view',
            'supported_descriptive',
            'WP-9f and current LCH rows show one ordered retrospective path across H-001 through H-010',
            null,
            false
        ),
        (
            'per-transition-edge aggregate view',
            'supported_descriptive',
            'WP-9g and current transition rows show three edges with all ten candidates on each edge',
            null,
            false
        ),
        (
            'evidence-artifact-type lineage view',
            'supported_descriptive',
            'WP-9h and current evidence refs classify HYPOTHESIS path, REP, DEC path, DCH, and REL refs with zero unknown refs',
            null,
            false
        ),
        (
            'H-005 evidence exception identification',
            'supported_descriptive',
            'current archival transition evidence makes H-005 the only DCH/REL cross-family exception',
            null,
            false
        ),
        (
            'lifecycle integrity and boundary validation',
            'supported_descriptive',
            'current lifecycle integrity views and all discovered integrity views return no rows',
            null,
            false
        ),
        (
            'future candidate forward-flow behavior',
            'requires_future_artifacts',
            'current LCH corpus is retrospective for H-001 through H-010 only',
            'future non-retrospective LCH artifacts and an approved forward-flow package',
            false
        ),
        (
            'paper/live lifecycle behavior',
            'unsupported_current_corpus',
            'current lifecycle states and transitions do not include paper or live behavior',
            'approved lifecycle extension and committed paper/live lifecycle artifacts',
            false
        ),
        (
            'fast-track versus standard-track comparison',
            'unsupported_current_corpus',
            'current fast_track_flag count is zero',
            'future fast-track and standard-track LCH examples plus approved comparison scope',
            false
        ),
        (
            'halted/recovery behavior',
            'unsupported_current_corpus',
            'current path contains no halted or recovery states',
            'approved halted/recovery lifecycle semantics and committed artifacts',
            false
        ),
        (
            'outcome-learning linkage',
            'requires_future_artifacts',
            'current lifecycle corpus has no outcome-learning ledger or outcome linkage',
            'approved outcome-learning architecture and committed outcome artifacts',
            false
        ),
        (
            'REC/reconciliation linkage',
            'requires_future_artifacts',
            'current lifecycle corpus has no REC or reconciliation linkage',
            'approved REC/reconciliation architecture and committed artifacts',
            false
        ),
        (
            'promotion/demotion threshold',
            'requires_future_artifacts',
            'current lifecycle consumers are descriptive and do not encode thresholds',
            'approved promotion policy architecture and threshold artifacts',
            false
        ),
        (
            'evidence-quality scoring',
            'requires_future_artifacts',
            'current evidence lineage classifies artifact types only and does not score evidence quality',
            'approved scoring semantics and evidence-quality artifacts',
            false
        ),
        (
            'runtime/deployment authority',
            'unsupported_current_corpus',
            'research briefs and LCH artifacts have no execution authority',
            'explicit later package opening protected runtime/deployment scope',
            false
        )
) AS t(
    capability,
    status,
    reason,
    required_future_dependency,
    policy_authority
)
ORDER BY
    CASE status
        WHEN 'supported_descriptive' THEN 1
        WHEN 'unsupported_current_corpus' THEN 2
        WHEN 'requires_future_artifacts' THEN 3
        ELSE 99
    END,
    capability;
