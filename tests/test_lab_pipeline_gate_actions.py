from __future__ import annotations

from pathlib import Path

import pytest

from tools.lab_pipeline import model
from tools.lab_pipeline.gate_actions import (
    NON_AUTHORITY_ASSERTIONS,
    GateActionError,
    create_prereg_approval_marker,
    preview_prereg_approval,
    record_candidate_surface_decision,
)
from tools.lab_pipeline.orchestrator import REPO_ROOT, run_pipeline
from tools.lab_pipeline.state import read_json, write_json


def _request(tmp_path: Path, **overrides: object) -> Path:
    payload = {
        "source_idea": "Evaluate a BTCUSDT 15m noncanonical z-score trial packet.",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "requested_by": "operator",
    }
    payload.update(overrides)
    path = tmp_path / "request.json"
    write_json(path, payload)
    return path


def _pending_packet(tmp_path: Path):
    pending = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "pipeline")
    requirement = Path(pending.artifact_paths["approval_requirement"])
    prereg = Path(pending.artifact_paths["preregistration_packet"])
    return pending, requirement, prereg


def _operator_fields(requirement_path: Path, **overrides: object) -> dict[str, object]:
    requirement = read_json(requirement_path)
    fields = {
        **requirement["required_fields"],
        "approval_timestamp_utc": "2026-07-08T00:00:00Z",
        "authorizes_crossing": False,
        "authorizes_promotion_or_readiness": False,
        "authorizes_provider_api_or_credentials": False,
        "authorizes_dependency_config_data_acquisition": False,
        "authorizes_protected_path_touch": False,
    }
    fields.update(overrides)
    return fields


def _assert_non_authority(assertions: dict[str, bool]) -> None:
    assert assertions == NON_AUTHORITY_ASSERTIONS
    assert all(value is False for value in assertions.values())


def test_approval_preview_produces_no_approval_marker(tmp_path: Path) -> None:
    _, requirement, prereg = _pending_packet(tmp_path)
    preview_path = tmp_path / "preview.md"

    result = preview_prereg_approval(
        approval_requirement_path=requirement,
        preregistration_packet_path=prereg,
        output_file=preview_path,
    )

    assert result.output_path == preview_path.resolve()
    assert result.action_kind == "prereg_approval_preview"
    assert preview_path.exists()
    assert not (preview_path.parent / "approval_marker.json").exists()
    text = preview_path.read_text(encoding="utf-8")
    assert "Packet hash:" in text
    assert "Source idea:" in text
    assert "Symbol/timeframe: BTCUSDT / 15m" in text
    assert "Denominator policy:" in text
    assert "Canonical writes." in text
    assert "- canonical_write: false" in text


def test_valid_explicit_prereg_action_creates_exact_approval_marker(tmp_path: Path) -> None:
    _, requirement, prereg = _pending_packet(tmp_path)
    output = tmp_path / "approval_marker.json"

    result = create_prereg_approval_marker(
        approval_requirement_path=requirement,
        preregistration_packet_path=prereg,
        operator_fields=_operator_fields(requirement),
        output_file=output,
    )

    marker = read_json(result.output_path)
    assert marker["schema_version"] == model.APPROVAL_SCHEMA_VERSION
    assert marker["approved_by"] == "Karl"
    assert marker["approval_scope"] == model.APPROVAL_SCOPE
    assert marker["approval_statement"] == model.APPROVAL_STATEMENT
    assert marker["authorizes_noncanonical_offline_research_execution"] is True
    assert marker["authorizes_canonical_write"] is False
    assert marker["authorizes_candidate_lifecycle"] is False
    assert marker["authorizes_paper_live_runtime"] is False
    assert marker["authorizes_scheduler_autonomy"] is False
    assert marker["authorizes_notifications"] is False
    assert marker["preregistration_packet_sha256"] == read_json(prereg)["packet_sha256"]
    _assert_non_authority(marker["non_authority_assertions"])


def test_mismatched_packet_hash_blocks(tmp_path: Path) -> None:
    _, requirement, prereg = _pending_packet(tmp_path)
    fields = _operator_fields(requirement, preregistration_packet_sha256="sha256:" + "0" * 64)

    with pytest.raises(GateActionError) as excinfo:
        create_prereg_approval_marker(
            approval_requirement_path=requirement,
            preregistration_packet_path=prereg,
            operator_fields=fields,
            output_file=tmp_path / "approval_marker.json",
        )

    assert "preregistration_packet_sha256_mismatch" in str(excinfo.value)


def test_wrong_approval_actor_blocks(tmp_path: Path) -> None:
    _, requirement, prereg = _pending_packet(tmp_path)

    with pytest.raises(GateActionError) as excinfo:
        create_prereg_approval_marker(
            approval_requirement_path=requirement,
            preregistration_packet_path=prereg,
            operator_fields=_operator_fields(requirement, approved_by="operator"),
            output_file=tmp_path / "approval_marker.json",
        )

    assert "approved_by_mismatch" in str(excinfo.value)


def test_broad_authority_flags_block(tmp_path: Path) -> None:
    _, requirement, prereg = _pending_packet(tmp_path)

    with pytest.raises(GateActionError) as excinfo:
        create_prereg_approval_marker(
            approval_requirement_path=requirement,
            preregistration_packet_path=prereg,
            operator_fields=_operator_fields(
                requirement,
                authorizes_canonical_write=True,
                authorizes_provider_api_or_credentials=True,
            ),
            output_file=tmp_path / "approval_marker.json",
        )

    message = str(excinfo.value)
    assert "authorizes_canonical_write_mismatch" in message
    assert "approval_too_broad:authorizes_provider_api_or_credentials" in message


def test_missing_exact_statement_blocks(tmp_path: Path) -> None:
    _, requirement, prereg = _pending_packet(tmp_path)

    with pytest.raises(GateActionError) as excinfo:
        create_prereg_approval_marker(
            approval_requirement_path=requirement,
            preregistration_packet_path=prereg,
            operator_fields=_operator_fields(requirement, approval_statement="Approve this run."),
            output_file=tmp_path / "approval_marker.json",
        )

    assert "approval_statement_mismatch" in str(excinfo.value)


def test_output_path_escape_blocks(tmp_path: Path) -> None:
    _, requirement, prereg = _pending_packet(tmp_path)
    unsafe_repo_path = REPO_ROOT / "scratch" / "OTHER-WP" / "approval_marker.json"

    with pytest.raises(GateActionError) as excinfo:
        create_prereg_approval_marker(
            approval_requirement_path=requirement,
            preregistration_packet_path=prereg,
            operator_fields=_operator_fields(requirement),
            output_file=unsafe_repo_path,
        )

    assert "must be under" in str(excinfo.value)


def test_generated_approval_marker_is_accepted_by_existing_pipeline_validation(tmp_path: Path) -> None:
    _, requirement, prereg = _pending_packet(tmp_path)
    approval = create_prereg_approval_marker(
        approval_requirement_path=requirement,
        preregistration_packet_path=prereg,
        operator_fields=_operator_fields(requirement),
        output_file=tmp_path / "approval_marker.json",
    )

    accepted = run_pipeline(
        request_path=_request(tmp_path),
        approval_path=approval.output_path,
        output_root=tmp_path / "pipeline",
    )

    assert accepted.pipeline_status == "complete"
    assert accepted.current_stage == "complete"


def test_candidate_surface_scaffold_accepts_only_non_authority_decision_values(
    tmp_path: Path,
) -> None:
    for decision in ("hold_for_review", "needs_more_evidence", "do_not_escalate"):
        result = record_candidate_surface_decision(
            decision=decision,
            decided_by="Karl",
            decision_timestamp_utc="2026-07-08T00:00:00Z",
            output_file=tmp_path / f"{decision}.json",
        )
        payload = read_json(result.output_path)
        assert payload["decision"] == decision
        assert payload["writes_candidate_lifecycle"] is False
        assert payload["writes_crossing"] is False
        assert payload["writes_promotion_or_readiness"] is False


@pytest.mark.parametrize(
    "decision,rationale,expected",
    [
        ("admit_candidate", "", "forbidden"),
        ("cross", "", "forbidden"),
        ("promote", "", "forbidden"),
        ("ready_for_paper", "", "forbidden"),
        ("start_paper", "", "forbidden"),
        ("start_shadow", "", "forbidden"),
        ("start_live", "", "forbidden"),
        ("hold_for_review", "write candidate lifecycle", "candidate_lifecycle_write"),
        ("hold_for_review", "execute crossing", "crossing"),
        ("hold_for_review", "promote this", "promotion"),
        ("hold_for_review", "start paper", "paper_start"),
        ("hold_for_review", "touch live runtime", "runtime"),
        ("hold_for_review", "use scheduler", "scheduler_autonomy"),
        ("hold_for_review", "call provider API credentials", "provider_api_credential"),
    ],
)
def test_candidate_crossing_promotion_paper_live_runtime_scheduler_provider_terms_are_blocked(
    tmp_path: Path, decision: str, rationale: str, expected: str
) -> None:
    with pytest.raises(GateActionError) as excinfo:
        record_candidate_surface_decision(
            decision=decision,
            decided_by="Karl",
            decision_timestamp_utc="2026-07-08T00:00:00Z",
            rationale=rationale,
            output_file=tmp_path / "candidate_surface_decision.json",
        )

    assert expected in str(excinfo.value)


def test_non_authority_flags_are_present_in_every_output(tmp_path: Path) -> None:
    _, requirement, prereg = _pending_packet(tmp_path)
    preview = preview_prereg_approval(
        approval_requirement_path=requirement,
        preregistration_packet_path=prereg,
        output_file=tmp_path / "preview.md",
    )
    approval = create_prereg_approval_marker(
        approval_requirement_path=requirement,
        preregistration_packet_path=prereg,
        operator_fields=_operator_fields(requirement),
        output_file=tmp_path / "approval_marker.json",
    )
    decision = record_candidate_surface_decision(
        decision="hold_for_review",
        decided_by="Karl",
        decision_timestamp_utc="2026-07-08T00:00:00Z",
        output_file=tmp_path / "candidate_surface_decision.json",
    )

    assert "- protected_path_touch: false" in preview.output_path.read_text(encoding="utf-8")
    _assert_non_authority(read_json(approval.output_path)["non_authority_assertions"])
    _assert_non_authority(read_json(decision.output_path)["non_authority_assertions"])
