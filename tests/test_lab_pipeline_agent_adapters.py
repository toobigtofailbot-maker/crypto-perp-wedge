from __future__ import annotations

from pathlib import Path

import pytest

from tools.lab_pipeline.adapter_contract import (
    ADAPTER_STAGE_STATUSES,
    NON_AUTHORITY_ASSERTIONS,
    build_adapter_registry,
)
from tools.lab_pipeline.adapters import run_adapter_flow
from tools.lab_pipeline.orchestrator import approval_template_for, run_pipeline
from tools.lab_pipeline.state import read_json, write_json


PACKAGE_ID = "WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02"


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


def _approved_pipeline(tmp_path: Path):
    pending = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "pipeline")
    approval = _approval_for(
        Path(pending.artifact_paths["preregistration_packet"]),
        tmp_path / "approval.json",
    )
    return pending, approval


def _fake_formalizer(*_args: object, **_kwargs: object):
    return (
        {
            "schema_version": "agent_formalized_idea_v1",
            "run_id": "FAKE-FORMALIZER",
            "status": "accepted",
            "rejection_reasons": [],
            "non_authority": {"scratch_only": True},
        },
        [
            "scratch/WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02/outputs/FAKE-FORMALIZER/formalized_idea.json",
            "scratch/WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02/outputs/FAKE-FORMALIZER/human_review_packet.json",
        ],
        [
            {
                "action_type": "write_scratch",
                "decision": "allowed",
                "target_path": "scratch/wp-labprod-pipeline-agent-adapters-02/outputs/fake-formalizer/formalized_idea.json",
            }
        ],
    )


def test_adapter_registry_is_closed_and_deterministic() -> None:
    first = [record.to_dict() for record in build_adapter_registry(PACKAGE_ID)]
    second = [record.to_dict() for record in build_adapter_registry(PACKAGE_ID)]

    assert first == second
    assert [record["stage"] for record in first] == [
        "idea_formalization",
        "availability_readiness_classification",
        "bridge_spec_variant_sweep_preparation",
        "noncanonical_offline_runner_execution",
        "wfo_oos_gate_review",
        "robustness_diagnostics",
        "candidate_review_packet_preparation",
    ]
    assert {record["implementation_status"] for record in first} == {"implemented", "blocked"}
    for record in first:
        flags = record["authority_flags"]
        assert flags["writes_canonical_evidence"] is False
        assert flags["writes_candidate_lifecycle"] is False
        assert flags["contacts_paper_live_runtime"] is False
        assert flags["uses_provider_api_or_credentials"] is False


def test_adapter_flow_blocks_before_prereg_approval_without_invoking_modules(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pending = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "pipeline")

    def fail_if_called(*_args: object, **_kwargs: object):
        raise AssertionError("adapter module should not run before approval")

    monkeypatch.setattr("tools.lab_pipeline.adapters._run_idea_formalizer", fail_if_called)
    result = run_adapter_flow(
        request=read_json(Path(pending.artifact_paths["pipeline_request"])),
        pipeline_run_id=pending.pipeline_run_id,
        preregistration_packet_path=Path(pending.artifact_paths["preregistration_packet"]),
        approval_path=None,
        output_root=tmp_path / "adapters",
    )

    state = read_json(Path(result.artifact_paths["pipeline_adapter_state"]))
    trace = read_json(Path(result.artifact_paths["adapter_trace"]))
    assert state["adapter_status"] == "awaiting_prereg_approval"
    assert result.gap_count == 0
    assert all(event["status"] == "awaiting_prereg_approval" for event in trace["events"])


def test_invalid_broad_approval_stays_blocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pending = run_pipeline(request_path=_request(tmp_path), output_root=tmp_path / "pipeline")
    approval = _approval_for(
        Path(pending.artifact_paths["preregistration_packet"]),
        tmp_path / "broad_approval.json",
        authorizes_canonical_write=True,
    )
    monkeypatch.setattr("tools.lab_pipeline.adapters._run_idea_formalizer", _fake_formalizer)

    result = run_adapter_flow(
        request=read_json(Path(pending.artifact_paths["pipeline_request"])),
        pipeline_run_id=pending.pipeline_run_id,
        preregistration_packet_path=Path(pending.artifact_paths["preregistration_packet"]),
        approval_path=approval,
        output_root=tmp_path / "adapters",
    )

    state = read_json(Path(result.artifact_paths["pipeline_adapter_state"]))
    assert state["adapter_status"] == "awaiting_prereg_approval"
    assert "approval_too_broad:authorizes_canonical_write" in state["approval_errors"]
    assert result.invoked_real_modules == ()


def test_valid_approval_runs_safe_adapters_and_gap_registers_unsafe_stages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pending, approval = _approved_pipeline(tmp_path)
    monkeypatch.setattr("tools.lab_pipeline.adapters._run_idea_formalizer", _fake_formalizer)

    result = run_adapter_flow(
        request=read_json(Path(pending.artifact_paths["pipeline_request"])),
        pipeline_run_id=pending.pipeline_run_id,
        preregistration_packet_path=Path(pending.artifact_paths["preregistration_packet"]),
        approval_path=approval,
        output_root=tmp_path / "adapters",
    )

    state = read_json(Path(result.artifact_paths["pipeline_adapter_state"]))
    gaps = read_json(Path(result.artifact_paths["adapter_gap_register"]))
    trace = read_json(Path(result.artifact_paths["adapter_trace"]))
    assertions = read_json(Path(result.artifact_paths["non_authority_assertions"]))
    assert state["adapter_status"] == "complete_with_gaps"
    assert state["adapter_status"] != "complete"
    assert gaps["gap_count"] == 5
    assert {gap["stage"] for gap in gaps["gaps"]} == {
        "bridge_spec_variant_sweep_preparation",
        "noncanonical_offline_runner_execution",
        "wfo_oos_gate_review",
        "robustness_diagnostics",
        "candidate_review_packet_preparation",
    }
    assert all(event["status"] in ADAPTER_STAGE_STATUSES for event in trace["events"])
    assert not any(event["status"] == "complete" for event in trace["events"])
    for key, value in NON_AUTHORITY_ASSERTIONS.items():
        assert assertions[key] is value


def test_run_pipeline_with_adapters_links_package_local_packet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pending, approval = _approved_pipeline(tmp_path)
    monkeypatch.setattr("tools.lab_pipeline.adapters._run_idea_formalizer", _fake_formalizer)

    result = run_pipeline(
        request_path=_request(tmp_path),
        approval_path=approval,
        output_root=tmp_path / "pipeline",
        run_adapters=True,
        adapter_output_root=tmp_path / "adapters",
    )

    assert result.pipeline_status == "complete"
    assert "pipeline_adapter_state" in result.artifact_paths
    state = read_json(Path(result.artifact_paths["pipeline_adapter_state"]))
    assert state["pipeline_run_id"] == pending.pipeline_run_id
    assert state["adapter_status"] == "complete_with_gaps"


def test_repo_resident_adapter_output_root_must_stay_in_package_scratch(
    tmp_path: Path,
) -> None:
    pending, approval = _approved_pipeline(tmp_path)

    with pytest.raises(Exception, match="adapter output_root inside repo must be under"):
        run_adapter_flow(
            request=read_json(Path(pending.artifact_paths["pipeline_request"])),
            pipeline_run_id=pending.pipeline_run_id,
            preregistration_packet_path=Path(pending.artifact_paths["preregistration_packet"]),
            approval_path=approval,
            output_root=Path("scratch") / "not-this-adapter-package",
        )


@pytest.mark.parametrize(
    ("requested_authority", "expected"),
    [
        (["canonical Result Population write"], "canonical_result_population_write"),
        (["candidate admission"], "candidate_admission_or_lifecycle_write"),
        (["paper/live runtime handoff"], "paper_live_runtime_contact"),
        (["scheduler autonomous dispatch"], "scheduler_or_autonomous_dispatch"),
        (["provider API credential use"], "provider_api_or_credential_use"),
        (["fire notification"], "notification_firing"),
    ],
)
def test_pipeline_rejects_authority_requests_before_adapter_flow(
    tmp_path: Path, requested_authority: list[str], expected: str
) -> None:
    result = run_pipeline(
        request_path=_request(tmp_path, requested_authority=requested_authority),
        output_root=tmp_path / "pipeline",
        run_adapters=True,
        adapter_output_root=tmp_path / "adapters",
    )

    assert result.pipeline_status == "blocked"
    assert any(expected in reason for reason in result.blocked_reasons)
    assert "pipeline_adapter_state" not in result.artifact_paths
