from __future__ import annotations

from pathlib import Path

import pytest

from tools.lab_pipeline import model
from tools.lab_pipeline.orchestrator import approval_template_for, run_pipeline
from tools.lab_pipeline.state import read_json, write_json


def _request(tmp_path: Path, **overrides: object) -> Path:
    payload = {
        "source_idea": "Test a BTCUSDT 15m SMA/stddev mean-reversion idea.",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "requested_by": "operator",
    }
    payload.update(overrides)
    path = tmp_path / "request.json"
    write_json(path, payload)
    return path


def _approval_for(prereg_path: Path, target: Path, **overrides: object) -> Path:
    payload = approval_template_for(prereg_path)
    payload.update(overrides)
    write_json(target, payload)
    return target


def test_pipeline_creates_deterministic_state_packet_for_valid_request(tmp_path: Path) -> None:
    request = _request(tmp_path)
    first = run_pipeline(request_path=request, output_root=tmp_path / "out")
    second = run_pipeline(request_path=request, output_root=tmp_path / "out")

    assert first.pipeline_run_id == second.pipeline_run_id
    state = read_json(Path(first.artifact_paths["pipeline_state"]))
    assert state["schema_version"] == model.SCHEMA_VERSION
    assert state["pipeline_status"] == "awaiting_prereg_approval"
    assert state["current_stage"] == "awaiting_prereg_approval"
    assert state["non_authority_flags"]["noncanonical_only"] is True


def test_pipeline_halts_at_prereg_approval_without_token(tmp_path: Path) -> None:
    result = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "out")
    assert result.pipeline_status == "awaiting_prereg_approval"
    assert "approval_requirement" in result.artifact_paths
    assert any("missing_prereg_approval" in reason for reason in result.blocked_reasons)


def test_mismatched_approval_token_blocks(tmp_path: Path) -> None:
    first = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "out")
    prereg = Path(first.artifact_paths["preregistration_packet"])
    approval = _approval_for(
        prereg,
        tmp_path / "bad_approval.json",
        preregistration_packet_sha256="sha256:not-the-packet",
    )

    result = run_pipeline(
        request_path=_request(tmp_path),
        approval_path=approval,
        output_root=tmp_path / "out",
    )

    assert result.pipeline_status == "awaiting_prereg_approval"
    assert any("approval_hash_mismatch" in reason for reason in result.blocked_reasons)


def test_exact_content_approval_allows_only_noncanonical_continuation(tmp_path: Path) -> None:
    pending = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "out")
    approval = _approval_for(
        Path(pending.artifact_paths["preregistration_packet"]),
        tmp_path / "approval.json",
    )

    result = run_pipeline(
        request_path=_request(tmp_path),
        approval_path=approval,
        output_root=tmp_path / "out",
    )

    assert result.pipeline_status == "complete"
    state = read_json(Path(result.artifact_paths["pipeline_state"]))
    stages = {item["stage"]: item["status"] for item in state["stage_statuses"]}
    assert stages["approved_for_noncanonical_execution"] == "complete"
    assert stages["complete"] == "complete"
    assertions = read_json(Path(result.artifact_paths["non_authority_assertions"]))
    assert assertions["canonical_files_written"] is False
    assert assertions["paper_live_runtime_contacted"] is False
    assert assertions["scheduler_or_autonomy_used"] is False


@pytest.mark.parametrize(
    "requested_authority, expected",
    [
        (["canonical Result Population write"], "canonical_result_population_write"),
        (["candidate admission"], "candidate_admission_or_lifecycle_write"),
        (["paper/live runtime handoff"], "paper_live_runtime_contact"),
        (["scheduler autonomous dispatch"], "scheduler_or_autonomous_dispatch"),
    ],
)
def test_forbidden_authority_requests_block(
    tmp_path: Path, requested_authority: list[str], expected: str
) -> None:
    result = run_pipeline(
        request_path=_request(tmp_path, requested_authority=requested_authority),
        output_root=tmp_path / "out",
    )

    assert result.pipeline_status == "blocked"
    assert any(expected in reason for reason in result.blocked_reasons)


def test_artifact_index_preserves_generated_artifacts(tmp_path: Path) -> None:
    pending = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "out")
    approval = _approval_for(
        Path(pending.artifact_paths["preregistration_packet"]),
        tmp_path / "approval.json",
    )
    result = run_pipeline(
        request_path=_request(tmp_path),
        approval_path=approval,
        output_root=tmp_path / "out",
    )
    index = read_json(Path(result.artifact_paths["artifact_index"]))
    names = set(index["artifacts"])
    required = {
        "pipeline_request",
        "pipeline_state",
        "pipeline_trace",
        "preregistration_packet",
        "approval_requirement",
        "non_authority_assertions",
        "operator_review_packet",
    }
    assert required.issubset(names)
    assert all(item["sha256"] for item in index["artifacts"].values())


def test_non_authority_flags_present_in_every_emitted_state_and_review_packet(
    tmp_path: Path,
) -> None:
    pending = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "out")
    approval = _approval_for(
        Path(pending.artifact_paths["preregistration_packet"]),
        tmp_path / "approval.json",
    )
    result = run_pipeline(
        request_path=_request(tmp_path),
        approval_path=approval,
        output_root=tmp_path / "out",
    )
    state = read_json(Path(result.artifact_paths["pipeline_state"]))
    assertions = read_json(Path(result.artifact_paths["non_authority_assertions"]))
    review = Path(result.artifact_paths["operator_review_packet"]).read_text(encoding="utf-8")
    assert state["non_authority_flags"]["scratch_only"] is True
    assert assertions["non_authority_flags"]["offline_only"] is True
    assert "noncanonical_only: true" in review


def test_no_provider_api_network_action_is_attempted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_network(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network should not be attempted")

    import socket

    monkeypatch.setattr(socket, "create_connection", fail_network)
    result = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "out")
    assertions = read_json(Path(result.artifact_paths["non_authority_assertions"]))
    assert assertions["provider_api_network_attempted"] is False


def test_no_canonical_files_are_written(tmp_path: Path) -> None:
    result = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "out")
    written = "\n".join(result.artifact_paths.values())
    assert "research/result_populations" not in written
    assert "research/candidate_registry" not in written
    assert "src/" not in written
    assert "configs/" not in written


def test_no_dashboard_or_cockpit_files_are_touched(tmp_path: Path) -> None:
    result = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "out")
    generated_names = "\n".join(path.name for path in map(Path, result.artifact_paths.values()))
    generated_keys = "\n".join(result.artifact_paths)
    assert "dashboard" not in generated_names.lower()
    assert "dashboard" not in generated_keys.lower()
    assert "cockpit" not in generated_names.lower()
    assert "cockpit" not in generated_keys.lower()
