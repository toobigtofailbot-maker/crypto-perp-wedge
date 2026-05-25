from pathlib import Path

import pytest

from tools.research_automation.bridge import (
    BridgeIntakeRecord,
    BridgeRunContext,
    BridgeSourceRef,
    BridgeTransformError,
    create_intake_record,
    normalize_bridge_payload,
    sha256_bytes,
    sha256_json_payload,
)
from tools.research_automation.bridge.intake import (
    LOCAL_ONLY_STATE_MARKER,
    POST_BRIDGE_ELIGIBILITY_MARKER,
)
from tools.research_automation.bridge.transform import NORMALIZED_BRIDGE_STAGE


def _valid_intake_record():
    source = BridgeSourceRef(
        source_id="local:auto-bridge:run-0002/output.json",
        source_kind="auto_local_json",
        bridge_era=POST_BRIDGE_ELIGIBILITY_MARKER,
        local_state=LOCAL_ONLY_STATE_MARKER,
        content_sha256=sha256_bytes(b"post-bridge-transform-source"),
        metadata={"source_package": "WP-12db / WP-S2c-60+61"},
    )
    run_context = BridgeRunContext(
        run_id="AUTO-BRIDGE-RUN-0002",
        run_timestamp="2026-05-25T00:00:00Z",
        tool_name="local_auto_bridge_transform",
        tool_version="wp_12dc_v1",
        commit_id="8fe75503a7299fd08f886c03294b10a187d7720b",
        parameters={"fixture": "in_memory"},
        metadata={"invocation": "unit_test"},
    )
    return create_intake_record(source, run_context)


def test_accepts_valid_intake_record_and_in_memory_mapping_payload():
    intake_record = _valid_intake_record()
    payload = {
        "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
        "metrics": {"trades": 12, "net_return": 0.42},
        "notes": ["caller", "provided", "payload"],
    }

    record = normalize_bridge_payload(intake_record, payload)

    assert record.intake_record is intake_record
    assert record.bridge_stage == NORMALIZED_BRIDGE_STAGE
    assert record.local_only is True
    assert record.non_canonical is True
    assert record.creates_canonical_artifact is False
    assert record.creates_committed_evidence is False
    assert record.normalized_payload["metrics"]["trades"] == 12


def test_preserves_intake_provenance():
    intake_record = _valid_intake_record()

    record = normalize_bridge_payload(
        intake_record,
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1},
    )

    assert record.intake_record.source.source_id == intake_record.source.source_id
    assert record.intake_record.source.metadata["source_package"] == (
        "WP-12db / WP-S2c-60+61"
    )
    assert record.intake_record.run_context.run_id == "AUTO-BRIDGE-RUN-0002"


def test_preserves_normalized_payload_values_deterministically():
    intake_record = _valid_intake_record()
    payload = {
        "z": 3,
        "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
        "a": {"nested": [2, 1]},
    }
    original = dict(payload)

    first = normalize_bridge_payload(intake_record, payload)
    second = normalize_bridge_payload(intake_record, dict(reversed(payload.items())))

    assert first.normalized_payload == second.normalized_payload
    assert first.payload_sha256 == second.payload_sha256
    assert payload == original


def test_sha256_json_payload_is_deterministic():
    payload = {"b": 2, "a": {"value": True}}

    assert sha256_json_payload(payload) == sha256_json_payload(
        {"a": {"value": True}, "b": 2}
    )
    assert len(sha256_json_payload(payload)) == 64


def test_rejects_non_bridge_intake_record_input():
    with pytest.raises(BridgeTransformError, match="BridgeIntakeRecord"):
        normalize_bridge_payload(
            object(), {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1}
        )


def test_rejects_non_local_or_canonical_intake_record():
    intake_record = _valid_intake_record()
    canonical_intake = BridgeIntakeRecord(
        source=intake_record.source,
        run_context=intake_record.run_context,
        bridge_era=POST_BRIDGE_ELIGIBILITY_MARKER,
        local_state="canonical",
        local_only=False,
        non_canonical=False,
        creates_canonical_artifact=True,
        creates_committed_evidence=True,
    )

    with pytest.raises(BridgeTransformError, match="local state"):
        normalize_bridge_payload(
            canonical_intake,
            {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1},
        )


def test_rejects_canonical_status_claim_in_payload_metadata():
    with pytest.raises(BridgeTransformError, match="canonical-status"):
        normalize_bridge_payload(
            _valid_intake_record(),
            {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1},
            metadata={"canonical_status": "canonical"},
        )


def test_rejects_artifact_commitment_claim_in_payload_metadata():
    with pytest.raises(BridgeTransformError, match="artifact-commitment"):
        normalize_bridge_payload(
            _valid_intake_record(),
            {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1},
            metadata={"artifact_commitment": "REP-9999"},
        )


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
def test_rejects_candidate_binding_metadata_in_payload_or_nested_metadata(
    payload, metadata
):
    with pytest.raises(BridgeTransformError, match="candidate-binding"):
        normalize_bridge_payload(_valid_intake_record(), payload, metadata=metadata)


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
def test_rejects_pre_bridge_or_retroactive_transformation_claim(payload, metadata):
    with pytest.raises(BridgeTransformError, match="pre-bridge/retroactive"):
        normalize_bridge_payload(_valid_intake_record(), payload, metadata=metadata)


def test_rejects_unsupported_payload_type():
    with pytest.raises(BridgeTransformError, match="mapping"):
        normalize_bridge_payload(_valid_intake_record(), ["not", "a", "mapping"])


def test_does_not_write_files_or_create_canonical_artifacts(tmp_path):
    record = normalize_bridge_payload(
        _valid_intake_record(),
        {"bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER, "value": 1},
    )

    assert list(Path(tmp_path).iterdir()) == []
    assert record.creates_canonical_artifact is False
    assert record.creates_committed_evidence is False
