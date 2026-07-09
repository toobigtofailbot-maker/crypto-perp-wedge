from __future__ import annotations

from pathlib import Path

import pytest

from tests.test_agent_formalizer_runner_bridge import _run_product
from tests.test_lab_pipeline_runner_adapter import _run_valid_adapter, _write_execute_approval
from tools.lab_pipeline import gates_adapter, runner_adapter
from tools.lab_pipeline.adapter_contract import GATES_ADAPTER_PACKAGE_ID, build_adapter_registry
from tools.lab_pipeline.gates_adapter import run_product_gates_adapters
from tools.lab_pipeline.state import read_json
from tools.research_agents.candidate_review_packet_agent import CandidateReviewPacketConfig
from tools.research_agents.robustness_diagnostician_agent import RobustnessDiagnosticianConfig


def _configure_temp_repo(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    runner_output_root = tmp_path / "scratch" / runner_adapter.WP_ID / "outputs"
    gates_output_root = tmp_path / "scratch" / gates_adapter.WP_ID / "outputs"
    monkeypatch.setattr(runner_adapter, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(runner_adapter, "DEFAULT_OUTPUT_ROOT", runner_output_root)
    monkeypatch.setattr(gates_adapter, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gates_adapter, "DEFAULT_SCRATCH_ROOT", tmp_path / "scratch" / gates_adapter.WP_ID)
    monkeypatch.setattr(gates_adapter, "DEFAULT_OUTPUT_ROOT", gates_output_root)
    return runner_output_root, gates_output_root


def _product_runner_result(tmp_path: Path, runner_output_root: Path):
    bridge_result, _ = _run_product(tmp_path)
    bridge_review = read_json(tmp_path / bridge_result["artifact_paths"]["human_review_packet"])
    approval_path = _write_execute_approval(
        tmp_path,
        runner_output_root,
        bridge_result,
        bridge_review,
    )
    return _run_valid_adapter(
        tmp_path,
        runner_output_root,
        bridge_result,
        bridge_review,
        approval_path,
    )


def test_gates_adapter_registry_is_implemented_only_for_gates_package() -> None:
    old_registry = {
        record.stage: record for record in build_adapter_registry("WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02")
    }
    gates_registry = {
        record.stage: record for record in build_adapter_registry(GATES_ADAPTER_PACKAGE_ID)
    }

    for stage in (
        "wfo_oos_gate_review",
        "robustness_diagnostics",
        "candidate_review_packet_preparation",
    ):
        assert old_registry[stage].implementation_status == "blocked"
        assert gates_registry[stage].implementation_status == "implemented"
        assert gates_registry[stage].blocker_reason is None


def test_product_gates_adapter_invokes_existing_agents_and_writes_advisory_packet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner_output_root, gates_output_root = _configure_temp_repo(monkeypatch, tmp_path)
    runner_result = _product_runner_result(tmp_path, runner_output_root)

    result = run_product_gates_adapters(
        runner_adapter_result_path=runner_result.artifact_paths["runner_adapter_result"],
        output_root=gates_output_root,
        robustness_config=RobustnessDiagnosticianConfig(bootstrap_samples=50),
        candidate_review_config=CandidateReviewPacketConfig(timestamp_utc="2026-07-08T00:00:00Z"),
    )

    advisory = read_json(tmp_path / result.artifact_paths["advisory_review_packet"])
    wfo = read_json(tmp_path / result.artifact_paths["wfo_oos_result"])
    robustness = read_json(tmp_path / result.artifact_paths["robustness_result"])
    candidate = read_json(tmp_path / result.artifact_paths["candidate_review_result"])
    surface = read_json(tmp_path / result.artifact_paths["candidate_surface_decision"])

    assert result.adapter_status == "completed"
    assert str(result.output_dir).startswith(str(gates_output_root))
    assert advisory["posture"] == "advisory_only_noncanonical_product_scratch"
    assert advisory["denominator_counts"] == {
        "blocked": 0,
        "completed": 8,
        "failed": 0,
        "invalid": 0,
        "pruned": 0,
    }
    assert wfo["existing_gate_invoked"] is True
    assert wfo["withheld_statistics"]["fabricated"] is False
    assert wfo["withheld_statistics"]["status"] == "withheld_missing_walkforward_oos_inputs"
    assert wfo["gate_evaluation"]["aggregate"]["canonical_writes"] == 0
    assert robustness["existing_agent_invoked"] is True
    assert robustness["existing_agent_payload"]["review_packet"]["per_trade_status"][
        "fabricated_per_trade_data"
    ] is False
    assert robustness["existing_agent_payload"]["review_packet"]["oos_walkforward_status"][
        "status"
    ] == "missing_fold_inputs"
    assert candidate["existing_agent_invoked"] is True
    assert candidate["existing_agent_packet"]["denominator_snapshot"]["counts"] == advisory[
        "denominator_counts"
    ]
    assert candidate["existing_agent_packet"]["missing_data_limitations"]["per_trade"][
        "fabricated_per_trade_data"
    ] is False
    assert result.direct_agent_reconciliation["verdict"] == "passed"
    assert result.direct_agent_reconciliation["normalization_used"] is False
    assert surface["decision"] == "needs_more_evidence"
    assert surface["writes_candidate_lifecycle"] is False
    assert surface["writes_crossing"] is False
    assert surface["writes_promotion_or_readiness"] is False
    assert advisory["candidate_surface_routing"]["go_auto_admission"] is False
    assert advisory["candidate_surface_routing"]["go_auto_crossing"] is False
    assert advisory["candidate_surface_routing"]["go_auto_promotion"] is False
    assert not (tmp_path / "research" / "result_populations").exists()
    assert not (tmp_path / "research" / "candidate_registry.jsonl").exists()


def test_gates_adapter_output_root_must_be_package_scratch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner_output_root, _gates_output_root = _configure_temp_repo(monkeypatch, tmp_path)
    runner_result = _product_runner_result(tmp_path, runner_output_root)

    with pytest.raises(gates_adapter.GatesAdapterError, match="output_root"):
        run_product_gates_adapters(
            runner_adapter_result_path=runner_result.artifact_paths["runner_adapter_result"],
            output_root=tmp_path / "scratch" / "OTHER-WP" / "outputs",
        )


def test_go_like_surface_status_is_hold_for_review_without_auto_authority() -> None:
    wfo_result = {
        "gate_evaluation": {
            "aggregate": {
                "pass_count": 1,
                "blocked_count": 0,
            }
        }
    }
    candidate_packet = {"blockers": [], "evidence_gaps": []}

    assert gates_adapter._surface_status(wfo_result, candidate_packet) == "hold_for_review"
