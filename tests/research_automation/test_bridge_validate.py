from dataclasses import replace
from pathlib import Path

import pytest

from tools.research_automation.bridge import (
    BridgeIntakeRecord,
    BridgeNormalizedRecord,
    BridgeRunContext,
    BridgeSourceRef,
    BridgeValidationError,
    assert_valid_normalized_record,
    create_intake_record,
    normalize_bridge_payload,
    sha256_bytes,
    validate_normalized_record,
)
from tools.research_automation.bridge.intake import (
    LOCAL_ONLY_STATE_MARKER,
    POST_BRIDGE_ELIGIBILITY_MARKER,
)
from tools.research_automation.bridge.transform import NORMALIZED_BRIDGE_STAGE


def _valid_intake_record():
    source = BridgeSourceRef(
        source_id="local:auto-bridge:run-0003/output.json",
        source_kind="auto_local_json",
        bridge_era=POST_BRIDGE_ELIGIBILITY_MARKER,
        local_state=LOCAL_ONLY_STATE_MARKER,
        content_sha256=sha256_bytes(b"post-bridge-validate-source"),
        metadata={"source_package": "WP-12db / WP-S2c-60+61"},
    )
    run_context = BridgeRunContext(
        run_id="AUTO-BRIDGE-RUN-0003",
        run_timestamp="2026-05-25T00:00:00Z",
        tool_name="local_auto_bridge_validate",
        tool_version="wp_12dd_v1",
        commit_id="51d2ae6f3a4871c83d8cbadbd25ba05d19d391a3",
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
        metadata={"validation_fixture": "wp_12dd"},
    )


def _issue_codes(result):
    return {issue.code for issue in result.issues}


def test_validates_correct_normalized_record():
    result = validate_normalized_record(_valid_normalized_record())

    assert result.valid is True
    assert result.issues == ()
    assert result.stage_checked == NORMALIZED_BRIDGE_STAGE
    assert result.local_only is True
    assert result.non_canonical is True
    assert result.creates_canonical_artifact is False
    assert result.creates_committed_evidence is False


def test_assert_valid_normalized_record_succeeds_for_correct_record():
    result = assert_valid_normalized_record(_valid_normalized_record())

    assert result.valid is True


def test_rejects_non_bridge_normalized_record_input():
    result = validate_normalized_record(object())

    assert result.valid is False
    assert _issue_codes(result) == {"not_normalized_record"}

    with pytest.raises(BridgeValidationError, match="not_normalized_record"):
        assert_valid_normalized_record(object())


def test_rejects_non_local_or_canonical_normalized_record():
    record = replace(
        _valid_normalized_record(),
        local_only=False,
        non_canonical=False,
        creates_canonical_artifact=True,
        creates_committed_evidence=True,
    )

    result = validate_normalized_record(record)

    assert result.valid is False
    assert {
        "not_local_only_non_canonical",
        "canonical_artifact_claim",
        "committed_evidence_claim",
    }.issubset(_issue_codes(result))
    assert result.creates_canonical_artifact is False
    assert result.creates_committed_evidence is False


def test_rejects_wrong_bridge_stage():
    result = validate_normalized_record(
        replace(_valid_normalized_record(), bridge_stage="candidate_artifact")
    )

    assert result.valid is False
    assert "unsupported_bridge_stage" in _issue_codes(result)


@pytest.mark.parametrize("digest", [None, "", "not-a-digest", "a" * 63, "g" * 64])
def test_rejects_missing_or_malformed_payload_digest(digest):
    result = validate_normalized_record(
        replace(_valid_normalized_record(), payload_sha256=digest)
    )

    assert result.valid is False
    assert "malformed_payload_digest" in _issue_codes(result)


def test_rejects_empty_normalized_payload():
    result = validate_normalized_record(
        replace(_valid_normalized_record(), normalized_payload={})
    )

    assert result.valid is False
    assert "empty_normalized_payload" in _issue_codes(result)


@pytest.mark.parametrize(
    "payload,metadata",
    [
        ({"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "canonical_status": "yes"}, {}),
        ({"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1}, {"is_canonical": True}),
    ],
)
def test_rejects_canonical_status_metadata(payload, metadata):
    record = replace(
        _valid_normalized_record(),
        normalized_payload=payload,
        normalized_metadata=metadata,
    )

    result = validate_normalized_record(record)

    assert result.valid is False
    assert "canonical_status_metadata" in _issue_codes(result)


@pytest.mark.parametrize(
    "payload,metadata",
    [
        (
            {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "artifact_commitment": "REP-9999"},
            {},
        ),
        (
            {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1},
            {"trial_log_row": True},
        ),
    ],
)
def test_rejects_artifact_commitment_metadata(payload, metadata):
    record = replace(
        _valid_normalized_record(),
        normalized_payload=payload,
        normalized_metadata=metadata,
    )

    result = validate_normalized_record(record)

    assert result.valid is False
    assert "artifact_commitment_metadata" in _issue_codes(result)


@pytest.mark.parametrize(
    "payload,metadata",
    [
        ({"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "candidate_id": "H-005"}, {}),
        ({"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1}, {"symbol": "BTCUSDT"}),
        (
            {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "nested": {"cohort": "A2C-001"}},
            {},
        ),
        (
            {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1},
            {"nested": {"path_b": True}},
        ),
    ],
)
def test_rejects_candidate_binding_metadata(payload, metadata):
    record = replace(
        _valid_normalized_record(),
        normalized_payload=payload,
        normalized_metadata=metadata,
    )

    result = validate_normalized_record(record)

    assert result.valid is False
    assert "candidate_binding_metadata" in _issue_codes(result)


@pytest.mark.parametrize(
    "payload,metadata",
    [
        ({"bridge_era": "pre_bridge", "value": 1}, {}),
        (
            {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1},
            {"retroactive_transformation": True},
        ),
        (
            {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "source": {"pre_bridge": True}},
            {},
        ),
    ],
)
def test_rejects_pre_bridge_or_retroactive_transformation_metadata(payload, metadata):
    record = replace(
        _valid_normalized_record(),
        normalized_payload=payload,
        normalized_metadata=metadata,
    )

    result = validate_normalized_record(record)

    assert result.valid is False
    assert "pre_bridge_retroactive_metadata" in _issue_codes(result)


@pytest.mark.parametrize(
    "intake_record,expected_code",
    [
        (None, "missing_intake_record"),
        (
            BridgeIntakeRecord(
                source=BridgeSourceRef(
                    source_id="",
                    source_kind="auto_local_json",
                    bridge_era=POST_BRIDGE_ELIGIBILITY_MARKER,
                    local_state=LOCAL_ONLY_STATE_MARKER,
                ),
                run_context=BridgeRunContext(
                    run_id="AUTO-BRIDGE-RUN-0003",
                    run_timestamp="2026-05-25T00:00:00Z",
                ),
                bridge_era=POST_BRIDGE_ELIGIBILITY_MARKER,
                local_state=LOCAL_ONLY_STATE_MARKER,
                local_only=True,
                non_canonical=True,
                creates_canonical_artifact=False,
                creates_committed_evidence=False,
            ),
            "missing_source_identity",
        ),
        (
            BridgeIntakeRecord(
                source=BridgeSourceRef(
                    source_id="local:auto-bridge:source",
                    source_kind="auto_local_json",
                    bridge_era=POST_BRIDGE_ELIGIBILITY_MARKER,
                    local_state=LOCAL_ONLY_STATE_MARKER,
                ),
                run_context=BridgeRunContext(run_id="", run_timestamp="2026-05-25T00:00:00Z"),
                bridge_era=POST_BRIDGE_ELIGIBILITY_MARKER,
                local_state=LOCAL_ONLY_STATE_MARKER,
                local_only=True,
                non_canonical=True,
                creates_canonical_artifact=False,
                creates_committed_evidence=False,
            ),
            "missing_run_identity",
        ),
        (
            replace(_valid_intake_record(), bridge_era="pre_bridge"),
            "invalid_intake_bridge_era",
        ),
    ],
)
def test_rejects_invalid_or_missing_intake_provenance(intake_record, expected_code):
    result = validate_normalized_record(
        replace(_valid_normalized_record(), intake_record=intake_record)
    )

    assert result.valid is False
    assert expected_code in _issue_codes(result)


def test_does_not_write_files_or_create_canonical_artifacts(tmp_path):
    result = validate_normalized_record(_valid_normalized_record())

    assert list(Path(tmp_path).iterdir()) == []
    assert result.creates_canonical_artifact is False
    assert result.creates_committed_evidence is False
