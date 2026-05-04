WITH exp_links AS (
    SELECT
        o.outcome_id,
        COUNT(DISTINCT CAST(ref_value AS VARCHAR)) AS exp_link_count
    FROM outcome_ledgers AS o,
    UNNEST(o.linked_artifacts) AS refs(ref_value)
    WHERE CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
    GROUP BY o.outcome_id
),
row_lineage AS (
    SELECT
        o.outcome_id,
        CASE
            WHEN CAST(o.derivation_record.source_artifact_id AS VARCHAR) LIKE 'REP-%'
             AND COALESCE(e.exp_link_count, 0) > 0
                THEN 1
            ELSE 0
        END AS has_exp_rep_lineage,
        list_count(o.linked_advisory_artifacts) AS advisory_link_count
    FROM outcome_ledgers AS o
    LEFT JOIN exp_links AS e
      ON o.outcome_id = e.outcome_id
)
SELECT
    COUNT(*) AS ol_row_count,
    SUM(has_exp_rep_lineage) AS rows_with_exp_rep_links,
    SUM(CASE WHEN has_exp_rep_lineage = 0 THEN 1 ELSE 0 END) AS rows_missing_exp_rep_links,
    SUM(advisory_link_count) AS advisory_link_count,
    SUM(CASE WHEN advisory_link_count > 0 THEN 1 ELSE 0 END) AS rows_with_advisory_links,
    CASE
        WHEN SUM(has_exp_rep_lineage) = COUNT(*)
            THEN 'all OL rows have EXP/REP lineage'
        ELSE 'one or more OL rows are missing EXP/REP lineage'
    END AS lineage_status,
    CASE
        WHEN SUM(advisory_link_count) = 0
            THEN 'advisory links are currently empty; forward-compatible field is unexercised'
        ELSE 'one or more advisory links are populated'
    END AS advisory_status
FROM row_lineage
