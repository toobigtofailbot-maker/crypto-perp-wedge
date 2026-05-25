from pathlib import Path

import pytest

from tools.research_automation.bridge import (
    BridgeIntakeError,
    BridgeRunContext,
    BridgeSourceRef,
    create_intake_record,
    sha256_bytes,
)
from tools.research_automation.bridge.intake import (
    LOCAL_ONLY_STATE_MARKER,
    POST_BRIDGE_ELIGIBILITY_MARKER,
)


def _valid_source(**overrides):
    values = {
        "source_id": "local:auto-bridge:run-0001/output.json",
        "source_kind": "auto_local_json",
        "bridge_era": POST_BRIDGE_ELIGIBILITY_MARKER,
        "local_state": LOCAL_ONLY_STATE_MARKER,
        "content_sha256": sha256_bytes(b"post-bridge-local-source"),
        "metadata": {"source_package": "WP-12db / WP-S2c-60+61"},
    }
    values.update(overrides)
    return BridgeSourceRef(**values)


def _valid_run_context(**overrides):
    values = {
        "run_id": "AUTO-BRIDGE-RUN-0001",
        "run_timestamp": "2026-05-25T00:00:00Z",
        "tool_name": "local_auto_bridge_intake",
        "tool_version": "wp_12db_v1",
        "commit_id": "80883d00406cd3107f9f8a2475d179162bb71886",
        "parameters": {"fixture": "in_memory"},
        "metadata": {"invocation": "unit_test"},
    }
    values.update(overrides)
    return BridgeRunContext(**values)


def test_accepts_valid_post_bridge_local_only_source():
    record = create_intake_record(_valid_source(), _valid_run_context())

    assert record.local_only is True
    assert record.non_canonical is True
    assert record.creates_canonical_artifact is False
    assert record.creates_committed_evidence is False
    assert record.bridge_era == POST_BRIDGE_ELIGIBILITY_MARKER
    assert record.local_state == LOCAL_ONLY_STATE_MARKER


def test_rejects_pre_bridge_source_era():
    with pytest.raises(BridgeIntakeError, match="post_bridge"):
        create_intake_record(_valid_source(bridge_era="pre_bridge"), _valid_run_context())


def test_rejects_missing_source_identity():
    with pytest.raises(BridgeIntakeError, match="source identity"):
        create_intake_record(_valid_source(source_id=""), _valid_run_context())


def test_rejects_missing_run_identity():
    with pytest.raises(BridgeIntakeError, match="run identity"):
        create_intake_record(_valid_source(), _valid_run_context(run_id=""))


def test_rejects_missing_local_only_non_canonical_state_marker():
    with pytest.raises(BridgeIntakeError, match="local state"):
        create_intake_record(_valid_source(local_state="canonical"), _valid_run_context())


def test_rejects_canonical_status_claim_in_metadata():
    source = _valid_source(metadata={"canonical_status": "canonical"})

    with pytest.raises(BridgeIntakeError, match="canonical-status"):
        create_intake_record(source, _valid_run_context())


def test_rejects_artifact_commitment_claim_in_metadata():
    run_context = _valid_run_context(metadata={"artifact_commitment": "REP-9999"})

    with pytest.raises(BridgeIntakeError, match="artifact-commitment"):
        create_intake_record(_valid_source(), run_context)


@pytest.mark.parametrize(
    "metadata",
    [
        {"candidate_id": "H-005"},
        {"symbol": "BTCUSDT"},
        {"cohort": "A2C-001"},
        {"path_b": True},
        {"nested": {"candidate_binding": "H-006"}},
    ],
)
def test_rejects_candidate_binding_metadata(metadata):
    with pytest.raises(BridgeIntakeError, match="candidate-binding"):
        create_intake_record(_valid_source(metadata=metadata), _valid_run_context())


def test_preserves_provenance_fields_in_returned_record():
    source = _valid_source(
        source_id="local:auto-bridge:source-42",
        source_kind="auto_local_bundle",
        metadata={"source_package": "WP-12db"},
    )
    run_context = _valid_run_context(
        run_id="RUN-42",
        run_timestamp="2026-05-25T12:34:56Z",
        tool_name="bridge-intake-test",
        tool_version="v1",
        commit_id="abc123",
        parameters={"alpha": 1, "beta": "two"},
        metadata={"operator": "codex"},
    )

    record = create_intake_record(source, run_context)

    assert record.source.source_id == "local:auto-bridge:source-42"
    assert record.source.source_kind == "auto_local_bundle"
    assert record.source.metadata["source_package"] == "WP-12db"
    assert record.run_context.run_id == "RUN-42"
    assert record.run_context.run_timestamp == "2026-05-25T12:34:56Z"
    assert record.run_context.tool_name == "bridge-intake-test"
    assert record.run_context.tool_version == "v1"
    assert record.run_context.commit_id == "abc123"
    assert record.run_context.parameters["alpha"] == 1
    assert record.run_context.metadata["operator"] == "codex"


def test_sha256_bytes_is_deterministic_for_caller_supplied_bytes():
    assert sha256_bytes(b"same source") == sha256_bytes(b"same source")
    assert sha256_bytes(b"same source") != sha256_bytes(b"different source")
    assert len(sha256_bytes(b"same source")) == 64


def test_intake_does_not_write_files_or_create_canonical_artifacts(tmp_path):
    record = create_intake_record(_valid_source(), _valid_run_context())

    assert list(Path(tmp_path).iterdir()) == []
    assert record.creates_canonical_artifact is False
    assert record.creates_committed_evidence is False
