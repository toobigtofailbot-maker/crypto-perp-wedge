SELECT
    'corpus inventory' AS claim_area,
    'SUPPORTED_DESCRIPTIVE' AS status,
    'Q01 reports current OL rows, candidates, source REP/EXP counts, pipeline versions, strategy families, and advisory link count' AS basis,
    'inventory only; no policy, ranking, or runtime authority' AS boundary
UNION ALL
SELECT
    'per-candidate path',
    'SUPPORTED_DESCRIPTIVE',
    'WP-9p and Q02 show OL coverage by candidate, including H-004 as the only two-entry candidate',
    'single-window factual inspection only below OL-4'
UNION ALL
SELECT
    'pipeline-version distribution',
    'SUPPORTED_DESCRIPTIVE',
    'WP-9q and Q02 show 10 pre_wp_5b rows and 1 post_wp_5b row',
    'pipeline_version is disclosure only; no automatic comparability'
UNION ALL
SELECT
    'strategy-family distribution',
    'SUPPORTED_DESCRIPTIVE',
    'WP-9r and Q02 show 8 represented strategy families with trend_following and momentum as multi-entry families',
    'family grouping does not rank families or lower OL-4'
UNION ALL
SELECT
    'H-004 structural exception',
    'SUPPORTED_DESCRIPTIVE',
    'Q03 shows OL-0005 / REP-0005 / EXP-0005 / pre_wp_5b and OL-0011 / REP-0011 / EXP-0011 / post_wp_5b',
    'structural exception only; no improvement, degradation, comparability, or recommendation claim'
UNION ALL
SELECT
    'source EXP/REP lineage',
    'SUPPORTED_DESCRIPTIVE',
    'Q01 and Q06 show 11 source REP artifacts and 11 source EXP artifacts',
    'lineage completeness only; no REC or advisory conclusion'
UNION ALL
SELECT
    'OL-4 consumer-time floor marking',
    'SUPPORTED_DESCRIPTIVE',
    'Q04 shows all candidate / outcome_kind / pipeline_version segments below n >= 3',
    'all current cross-window inference remains INSUFFICIENT_EVIDENCE'
UNION ALL
SELECT
    'promotion/demotion policy',
    'UNSUPPORTED_FUTURE_DEPENDENT',
    'no promotion or demotion policy artifact is created or modified',
    'requires later explicit policy package'
UNION ALL
SELECT
    'REC/reconciliation',
    'UNSUPPORTED_FUTURE_DEPENDENT',
    'WP-9s reads OL only and creates no REC schema or artifact',
    'requires later REC/reconciliation package'
UNION ALL
SELECT
    'paper/live semantics',
    'UNSUPPORTED_FUTURE_DEPENDENT',
    'OL v1 supports research_oos only',
    'paper/live outcome semantics require later versioned work'
UNION ALL
SELECT
    'evidence-quality scoring',
    'UNSUPPORTED_FUTURE_DEPENDENT',
    'no evidence-quality score field, schema, or artifact is introduced',
    'requires later explicit scoring package'
UNION ALL
SELECT
    'strategy-family ranking',
    'UNSUPPORTED_FUTURE_DEPENDENT',
    'family counts are descriptive and floor-limited',
    'no family superiority, inferiority, robustness, or recommendation claim'
UNION ALL
SELECT
    'pipeline-version performance comparison',
    'UNSUPPORTED_FUTURE_DEPENDENT',
    'pipeline_version is disclosure and H-004 rows are single-window facts',
    'no automatic pre/post comparability below OL-4'
UNION ALL
SELECT
    'cross-window inference',
    'UNSUPPORTED_FUTURE_DEPENDENT',
    'Q04 shows every current segment below n >= 3',
    'all current segments remain INSUFFICIENT_EVIDENCE'
UNION ALL
SELECT
    'runtime/deployment authority',
    'UNSUPPORTED_FUTURE_DEPENDENT',
    'WP-9s changes only research brief/status surfaces',
    'no runtime, deployment, OMS, risk, safe-mode, or live-trading authority'
ORDER BY claim_area
