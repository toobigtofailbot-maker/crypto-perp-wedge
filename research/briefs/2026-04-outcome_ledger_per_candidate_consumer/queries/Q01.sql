WITH corpus AS (
    SELECT
        COUNT(*) AS ol_row_count,
        COUNT(DISTINCT candidate_id) AS candidate_count,
        COUNT(DISTINCT derivation_record.source_artifact_id) AS source_rep_count,
        SUM(CASE WHEN pipeline_version = 'pre_wp_5b' THEN 1 ELSE 0 END) AS pre_wp_5b_count,
        SUM(CASE WHEN pipeline_version = 'post_wp_5b' THEN 1 ELSE 0 END) AS post_wp_5b_count,
        SUM(len(linked_advisory_artifacts)) AS advisory_link_count
    FROM outcome_ledgers
),
exp_sources AS (
    SELECT
        COUNT(DISTINCT CAST(ref_value AS VARCHAR)) AS source_exp_count
    FROM outcome_ledgers,
    UNNEST(linked_artifacts) AS refs(ref_value)
    WHERE CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
)
SELECT
    corpus.ol_row_count,
    corpus.candidate_count,
    corpus.source_rep_count,
    exp_sources.source_exp_count,
    corpus.pre_wp_5b_count,
    corpus.post_wp_5b_count,
    corpus.advisory_link_count
FROM corpus
CROSS JOIN exp_sources;
