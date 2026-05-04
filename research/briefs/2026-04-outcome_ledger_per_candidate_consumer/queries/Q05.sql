SELECT
    outcome_id,
    candidate_id,
    linked_artifacts,
    len(linked_artifacts) AS linked_artifact_count,
    linked_advisory_artifacts,
    len(linked_advisory_artifacts) AS linked_advisory_artifact_count,
    derivation_record.source_artifact_id AS source_artifact_id,
    derivation_record.source_artifact_path AS source_artifact_path
FROM outcome_ledgers
ORDER BY outcome_id;
