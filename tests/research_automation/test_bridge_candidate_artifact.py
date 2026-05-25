from dataclasses import replace
from pathlib import Path

import pytest

from tools.research_automation.bridge import (
    BridgeCandidateArtifactError,
    BridgeRunContext,
    BridgeSourceRef,
    BridgeValidationIssue,
    BridgeValidationResult,
    create_candidate_artifact_draft,
    create_intake_record,
    normalize_bridge_payload,
    sha256_bytes,
    sha256_draft_payload,
    validate_normalized_record,
)
from tools.research_automation.bridge.intake import (
    LOCAL_ONLY_STATE_MARKER,
    POST_BRIDGE_ELIGIBILITY_MARKER,
)


def _valid_intake_record():
    source = BridgeSourceRef(
        source_id="local:auto-bridge:run-0004/output.json",
        source_kind="auto_local_json",
        bridge_era=POST_BRIDGE_ELIGIBILITY_MARKER,
        local_state=LOCAL_ONLY_STATE_MARKER,
        content_sha256=sha256_bytes(b"post-bridge-candidate-artifact-source"),
        metadata={"source_package": "WP-12db / WP-S2c-60+61"},
    )
    run_context = BridgeRunContext(
        run_id="AUTO-BRIDGE-RUN-0004",
        run_timestamp="2026-05-25T00:00:00Z",
        tool_name="local_auto_bridge_candidate_artifact",
        tool_version="wp_12de_v1",
        commit_id="a41007939bb9f86d4d0c0a4c78c6bedf4706920e",
        parameters={"fixture": "in_memory"},
        metadata={"invocation": "unit_test"},
    )
    return create_intake_record(source, run_context)


def _valid_normalized_record():
    return normalize_bridge_payload(
        _valid_intake_record(),
        {
            "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
            "metrics": {"trades": 12, "net_return": 0.42},
        },
        metadata={"validation_fixture": "wp_12de"},
    )


def _valid_validation_result(record=None):
    return validate_normalized_record(record or _valid_normalized_record())


def _valid_draft_payload():
    return {
        "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
        "summary": {"metric_count": 2, "status": "draft_only"},
    }


def test_creates_candidate_artifact_draft_from_valid_record_and_validation_result():
    record = _valid_normalized_record()
    validation = validate_normalized_record(record)

    draft = create_candidate_artifact_draft(
        record,
        validation,
        draft_type="local_summary_draft",
        target_label="bridge_local_review",
        draft_payload=_valid_draft_payload(),
    )

    assert draft.source_record is record
    assert draft.validation_result is validation
    assert draft.bridge_stage == "candidate_artifact_draft"
    assert draft.draft_type == "local_summary_draft"
    assert draft.target_label == "bridge_local_review"
    assert draft.validation_issue_summary == ()
    assert draft.draft_payload["summary"]["metric_count"] == 2


def test_preserves_intake_and_transformation_provenance():
    record = _valid_normalized_record()
    draft = create_candidate_artifact_draft(
        record,
        validate_normalized_record(record),
        draft_type="local_summary_draft",
        target_label="bridge_local_review",
        draft_payload=_valid_draft_payload(),
    )

    assert draft.provenance_summary["source_id"] == record.intake_record.source.source_id
    assert draft.provenance_summary["source_kind"] == "auto_local_json"
    assert draft.provenance_summary["run_id"] == "AUTO-BRIDGE-RUN-0004"
    assert draft.provenance_summary["tool_version"] == "wp_12de_v1"
    assert draft.provenance_summary["normalized_payload_sha256"] == record.payload_sha256
    assert draft.provenance_summary["bridge_stage"] == record.bridge_stage


def test_returns_local_only_non_canonical_unbound_uncommitted_draft():
    record = _valid_normalized_record()
    draft = create_candidate_artifact_draft(
        record,
        validate_normalized_record(record),
        draft_type="local_summary_draft",
        target_label="bridge_local_review",
        draft_payload=_valid_draft_payload(),
    )

    assert draft.local_only is True
    assert draft.non_canonical is True
    assert draft.candidate_bound is False
    assert draft.creates_canonical_artifact is False
    assert draft.creates_committed_evidence is False


def test_produces_deterministic_draft_digest_without_mutating_payload():
    record = _valid_normalized_record()
    validation = validate_normalized_record(record)
    payload = _valid_draft_payload()
    original = dict(payload)

    first = create_candidate_artifact_draft(
        record,
        validation,
        draft_type="local_summary_draft",
        target_label="bridge_local_review",
        draft_payload=payload,
    )
    second = create_candidate_artifact_draft(
        record,
        validation,
        draft_type="local_summary_draft",
        target_label="bridge_local_review",
        draft_payload={
            "summary": {"status": "draft_only", "metric_count": 2},
            "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
        },
    )

    assert first.draft_sha256 == second.draft_sha256
    assert len(first.draft_sha256) == 64
    assert payload == original


def test_sha256_draft_payload_is_deterministic():
    assert sha256_draft_payload({"b": 2, "a": {"value": True}}) == sha256_draft_payload(
        {"a": {"value": True}, "b": 2}
    )


def test_rejects_non_normalized_record_input():
    with pytest.raises(BridgeCandidateArtifactError, match="BridgeNormalizedRecord"):
        create_candidate_artifact_draft(
            object(),
            _valid_validation_result(),
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=_valid_draft_payload(),
        )


def test_rejects_invalid_validation_result():
    record = _valid_normalized_record()
    validation = replace(validate_normalized_record(record), valid=False)

    with pytest.raises(BridgeCandidateArtifactError, match="must be valid"):
        create_candidate_artifact_draft(
            record,
            validation,
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=_valid_draft_payload(),
        )


def test_rejects_validation_result_with_issues():
    record = _valid_normalized_record()
    validation = replace(
        validate_normalized_record(record),
        issues=(
            BridgeValidationIssue(
                code="unexpected_issue",
                message="must fail closed",
                location="validation",
            ),
        ),
    )

    with pytest.raises(BridgeCandidateArtifactError, match="must not contain issues"):
        create_candidate_artifact_draft(
            record,
            validation,
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=_valid_draft_payload(),
        )


def test_rejects_validation_result_with_mismatched_stage_or_posture():
    record = _valid_normalized_record()
    validation = replace(validate_normalized_record(record), stage_checked="other")

    with pytest.raises(BridgeCandidateArtifactError, match="stage"):
        create_candidate_artifact_draft(
            record,
            validation,
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=_valid_draft_payload(),
        )

    validation = replace(validate_normalized_record(record), local_only=False)
    with pytest.raises(BridgeCandidateArtifactError, match="local-only"):
        create_candidate_artifact_draft(
            record,
            validation,
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=_valid_draft_payload(),
        )


def test_can_internally_validate_when_validation_result_is_not_supplied():
    record = _valid_normalized_record()

    draft = create_candidate_artifact_draft(
        record,
        draft_type="local_summary_draft",
        target_label="bridge_local_review",
        draft_payload=_valid_draft_payload(),
    )

    assert draft.validation_result.valid is True


@pytest.mark.parametrize(
    "payload",
    [
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "canonical_status": "canonical"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "nested": {"is_canonical": True}},
    ],
)
def test_rejects_canonical_status_metadata(payload):
    record = _valid_normalized_record()

    with pytest.raises(BridgeCandidateArtifactError, match="canonical-status"):
        create_candidate_artifact_draft(
            record,
            validate_normalized_record(record),
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=payload,
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "artifact_commitment": "draft"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "trial_log_row": True},
    ],
)
def test_rejects_artifact_commitment_metadata(payload):
    record = _valid_normalized_record()

    with pytest.raises(BridgeCandidateArtifactError, match="artifact-commitment"):
        create_candidate_artifact_draft(
            record,
            validate_normalized_record(record),
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=payload,
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "candidate_id": "H-005"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "symbol": "BTCUSDT"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "candidate_bound": False},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "nested": {"cohort": "A2C-001"}},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "nested": {"path_b": True}},
    ],
)
def test_rejects_candidate_binding_metadata(payload):
    record = _valid_normalized_record()

    with pytest.raises(BridgeCandidateArtifactError, match="candidate-binding"):
        create_candidate_artifact_draft(
            record,
            validate_normalized_record(record),
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=payload,
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"bridge_era": "pre_bridge", "value": 1},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "retroactive_transformation": True},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "source": {"pre_bridge": True}},
    ],
)
def test_rejects_pre_bridge_or_retroactive_transformation_metadata(payload):
    record = _valid_normalized_record()

    with pytest.raises(BridgeCandidateArtifactError, match="pre-bridge/retroactive"):
        create_candidate_artifact_draft(
            record,
            validate_normalized_record(record),
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=payload,
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "draft_id": "REP-9999"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "draft_id": "OL-9999"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "draft_id": "REC-9999"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "draft_id": "EXP-9999"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "artifact_path": "research/foo.json"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "output_path": "auto/output.json"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "lifecycle": "ready"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "registry": "candidate_registry"},
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "query_view": "v_candidate_overview"},
    ],
)
def test_rejects_canonical_artifact_id_path_and_authority_claims(payload):
    record = _valid_normalized_record()

    with pytest.raises(BridgeCandidateArtifactError):
        create_candidate_artifact_draft(
            record,
            validate_normalized_record(record),
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=payload,
        )


@pytest.mark.parametrize("payload", [{}, ["not", "a", "mapping"]])
def test_rejects_unsupported_or_empty_draft_payload(payload):
    record = _valid_normalized_record()

    with pytest.raises(BridgeCandidateArtifactError, match="mapping|empty"):
        create_candidate_artifact_draft(
            record,
            validate_normalized_record(record),
            draft_type="local_summary_draft",
            target_label="bridge_local_review",
            draft_payload=payload,
        )


def test_rejects_empty_or_claim_bearing_labels():
    record = _valid_normalized_record()

    with pytest.raises(BridgeCandidateArtifactError, match="non-empty"):
        create_candidate_artifact_draft(
            record,
            validate_normalized_record(record),
            draft_type="",
            target_label="bridge_local_review",
            draft_payload=_valid_draft_payload(),
        )

    with pytest.raises(BridgeCandidateArtifactError, match="canonical artifact ID"):
        create_candidate_artifact_draft(
            record,
            validate_normalized_record(record),
            draft_type="REP-9999",
            target_label="bridge_local_review",
            draft_payload=_valid_draft_payload(),
        )


def test_does_not_write_files_or_create_canonical_artifacts(tmp_path):
    record = _valid_normalized_record()
    draft = create_candidate_artifact_draft(
        record,
        validate_normalized_record(record),
        draft_type="local_summary_draft",
        target_label="bridge_local_review",
        draft_payload=_valid_draft_payload(),
    )

    assert list(Path(tmp_path).iterdir()) == []
    assert draft.creates_canonical_artifact is False
    assert draft.creates_committed_evidence is False
