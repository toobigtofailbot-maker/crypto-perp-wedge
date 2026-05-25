from pathlib import Path

import pytest

from tools.research_automation.bridge import (
    BridgeCandidateArtifactError,
    BridgeIntakeError,
    BridgeOrchestrationError,
    BridgeTransformError,
    run_bridge_pipeline,
    sha256_bytes,
)
from tools.research_automation.bridge.intake import POST_BRIDGE_ELIGIBILITY_MARKER


def _valid_kwargs(**overrides):
    values = {
        "source_id": "local:auto-bridge:run-0005/output.json",
        "source_kind": "auto_local_json",
        "source_content": b"post-bridge-orchestrate-source",
        "source_metadata": {"source_package": "WP-12df / WP-S2c-68+69"},
        "run_id": "AUTO-BRIDGE-RUN-0005",
        "run_timestamp": "2026-05-25T00:00:00Z",
        "tool_name": "local_auto_bridge_orchestrate",
        "tool_version": "wp_12df_v1",
        "commit_id": "504e260bece61c600884216f6d9a63f0522c0ea6",
        "run_parameters": {"fixture": "in_memory"},
        "run_metadata": {"invocation": "unit_test"},
        "normalized_payload": {
            "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
            "metrics": {"trades": 12, "net_return": 0.42},
        },
        "normalized_metadata": {"normalization_fixture": "wp_12df"},
        "draft_type": "local_summary_draft",
        "target_label": "bridge_local_review",
        "draft_payload": {
            "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
            "summary": {"metric_count": 2, "status": "draft_only"},
        },
    }
    values.update(overrides)
    return values


def test_complete_in_memory_bridge_pipeline_succeeds():
    result = run_bridge_pipeline(**_valid_kwargs())

    assert result.intake_record.source.source_id == (
        "local:auto-bridge:run-0005/output.json"
    )
    assert result.normalized_record.normalized_payload["metrics"]["trades"] == 12
    assert result.validation_result.valid is True
    assert result.candidate_artifact_draft.draft_type == "local_summary_draft"
    assert result.bridge_stage_summary == (
        "intake",
        "normalized",
        "validation",
        "candidate_artifact_draft",
    )


def test_result_is_local_only_non_canonical_unbound_and_uncommitted():
    result = run_bridge_pipeline(**_valid_kwargs())

    assert result.local_only is True
    assert result.non_canonical is True
    assert result.creates_canonical_artifact is False
    assert result.creates_committed_evidence is False
    assert result.intake_record.creates_canonical_artifact is False
    assert result.normalized_record.creates_committed_evidence is False
    assert result.validation_result.creates_canonical_artifact is False
    assert result.candidate_artifact_draft.candidate_bound is False
    assert result.candidate_artifact_draft.creates_committed_evidence is False


def test_provenance_is_preserved_from_intake_through_draft():
    result = run_bridge_pipeline(**_valid_kwargs())

    expected_digest = sha256_bytes(b"post-bridge-orchestrate-source")
    draft_provenance = result.candidate_artifact_draft.provenance_summary

    assert result.intake_record.source.content_sha256 == expected_digest
    assert result.normalized_record.intake_record is result.intake_record
    assert result.candidate_artifact_draft.source_record is result.normalized_record
    assert draft_provenance["source_id"] == result.intake_record.source.source_id
    assert draft_provenance["source_content_sha256"] == expected_digest
    assert draft_provenance["run_id"] == result.intake_record.run_context.run_id
    assert draft_provenance["normalized_payload_sha256"] == (
        result.normalized_record.payload_sha256
    )


def test_deterministic_digest_behavior_is_preserved():
    first = run_bridge_pipeline(**_valid_kwargs())
    second = run_bridge_pipeline(
        **_valid_kwargs(
            normalized_payload={
                "metrics": {"net_return": 0.42, "trades": 12},
                "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
            },
            draft_payload={
                "summary": {"status": "draft_only", "metric_count": 2},
                "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
            },
        )
    )

    assert first.intake_record.source.content_sha256 == (
        second.intake_record.source.content_sha256
    )
    assert first.normalized_record.payload_sha256 == (
        second.normalized_record.payload_sha256
    )
    assert first.candidate_artifact_draft.draft_sha256 == (
        second.candidate_artifact_draft.draft_sha256
    )


def test_accepts_caller_provided_matching_source_digest():
    digest = sha256_bytes(b"post-bridge-orchestrate-source")

    result = run_bridge_pipeline(**_valid_kwargs(source_content_sha256=digest))

    assert result.intake_record.source.content_sha256 == digest


def test_rejects_mismatched_caller_provided_source_digest():
    with pytest.raises(BridgeOrchestrationError, match="must match"):
        run_bridge_pipeline(**_valid_kwargs(source_content_sha256="a" * 64))


def test_pre_bridge_source_era_fails_closed():
    with pytest.raises(BridgeIntakeError, match="post_bridge"):
        run_bridge_pipeline(**_valid_kwargs(source_bridge_era="pre_bridge"))


def test_missing_source_or_run_identity_fails_closed():
    with pytest.raises(BridgeIntakeError, match="source identity"):
        run_bridge_pipeline(**_valid_kwargs(source_id=""))

    with pytest.raises(BridgeIntakeError, match="run identity"):
        run_bridge_pipeline(**_valid_kwargs(run_id=""))


def test_canonical_status_claim_fails_closed():
    with pytest.raises(BridgeTransformError, match="canonical-status"):
        run_bridge_pipeline(
            **_valid_kwargs(
                normalized_payload={
                    "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
                    "canonical_status": "canonical",
                }
            )
        )


def test_artifact_commitment_claim_fails_closed():
    with pytest.raises(BridgeCandidateArtifactError, match="artifact-commitment"):
        run_bridge_pipeline(
            **_valid_kwargs(
                draft_payload={
                    "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
                    "trial_log_row": True,
                }
            )
        )


def test_candidate_binding_metadata_fails_closed():
    with pytest.raises(BridgeIntakeError, match="candidate-binding"):
        run_bridge_pipeline(**_valid_kwargs(source_metadata={"candidate_id": "H-005"}))


@pytest.mark.parametrize(
    "draft_payload",
    [
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "draft_id": "REP-9999"},
        {
            "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
            "artifact_path": "research/foo.json",
        },
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "trial_log_row": True},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "registry": "candidate_registry"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "query_view": "v_auto_bridge"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "lifecycle": "ready"},
    ],
)
def test_canonical_artifact_path_trial_log_registry_query_lifecycle_claims_fail_closed(
    draft_payload,
):
    with pytest.raises(BridgeCandidateArtifactError):
        run_bridge_pipeline(**_valid_kwargs(draft_payload=draft_payload))


@pytest.mark.parametrize(
    "overrides,expected_error",
    [
        ({"normalized_payload": {}}, BridgeTransformError),
        ({"normalized_payload": ["not", "a", "mapping"]}, BridgeTransformError),
        ({"draft_payload": {}}, BridgeCandidateArtifactError),
        ({"draft_payload": ["not", "a", "mapping"]}, BridgeCandidateArtifactError),
    ],
)
def test_unsupported_or_empty_payload_fails_closed(overrides, expected_error):
    with pytest.raises(expected_error):
        run_bridge_pipeline(**_valid_kwargs(**overrides))


def test_no_file_reads_writes_or_canonical_artifact_creation_occur(tmp_path):
    result = run_bridge_pipeline(**_valid_kwargs())

    assert list(Path(tmp_path).iterdir()) == []
    assert result.creates_canonical_artifact is False
    assert result.creates_committed_evidence is False
    assert result.candidate_artifact_draft.creates_canonical_artifact is False
