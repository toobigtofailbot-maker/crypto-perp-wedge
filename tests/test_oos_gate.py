from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from tools.candidate_lifecycle.lifecycle_engine import REQUIRED_NON_AUTHORITY_FLAGS, build_lifecycle_report
from tools.oos_gate.evaluate import evaluate_candidate_review_gate, validate_oos_gate_artifact


FIXTURES = Path(__file__).parent / "fixtures"


def _candidate_input() -> dict:
    return json.loads(
        (FIXTURES / "candidate_lifecycle_engine" / "valid_candidate_inputs.json").read_text(
            encoding="utf-8"
        )
    )


def _gate_artifact(decision: str = "pass") -> dict:
    return {
        "schema_version": "oos_gate_contract.v1",
        "gate_id": "OOS-GATE-FIXTURE-0001",
        "created_at_utc": "2026-06-24T00:00:00Z",
        "source_result_population": {
            "result_population_id": "RP-FIXTURE-0001",
            "result_population_ref": "research/result_populations/RP-FIXTURE-0001.result_population.json",
            "input_identity_hash": "sha256:fixture-input",
            "result_population_identity_hash": "sha256:fixture-result",
        },
        "source_walkforward_run": {
            "run_id": "WF-RUN-0123456789ABCDEF",
            "report_ref": "scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_run_report.json",
        },
        "split": {
            "method": "purged_embargoed_explicit_walkforward",
            "in_sample_period": {
                "start_utc": "2022-01-01T00:00:00Z",
                "end_utc": "2023-01-01T00:00:00Z",
            },
            "out_of_sample_period": {
                "start_utc": "2023-01-01T00:00:00Z",
                "end_utc": "2023-02-01T00:00:00Z",
            },
            "purge": {"mode": "bars", "bars": 96},
            "embargo": {"mode": "bars", "bars": 32},
            "window_count": 1,
            "minimum_required_windows": 1,
        },
        "oos_metrics": {
            "mean_oos_sharpe": 1.2,
            "minimum_oos_sharpe": 1.1,
            "maximum_oos_drawdown": 0.12,
        },
        "row_variant_mapping": {
            "mapping_basis": "walkforward_run_report.variant_results",
            "declared_variant_count": 1,
            "per_window_variant_rows": 1,
            "denominator_preserved": True,
        },
        "gate_decision": decision,
        "reason_codes": ["oos_gate_passed"] if decision == "pass" else [f"oos_gate_{decision}"],
        "canonical_status": "non_canonical",
        "non_authority_declaration": {
            "not_candidate_approval": True,
            "not_promotion_authority": True,
            "not_readiness_authority": True,
            "not_ranking_authority": True,
            "not_recommendation_authority": True,
            "not_runtime_authority": True,
            "not_paper_live_authority": True,
            "not_result_population_write_authority": True,
            "not_candidate_lifecycle_write_authority": True,
        },
    }


def test_oos_gate_artifact_validates() -> None:
    assert validate_oos_gate_artifact(_gate_artifact()) == []


def test_missing_oos_evidence_blocks_candidate_gate() -> None:
    result = evaluate_candidate_review_gate(_candidate_input(), _gate_artifact())

    candidate = result["candidate_results"][0]
    assert candidate["candidate_review_gate_status"] == "blocked"
    assert "missing_oos_gate_ref" in candidate["blockers"]
    assert result["aggregate"]["candidate_lifecycle_writes"] == 0


def test_failed_oos_gate_blocks_candidate_review_pass() -> None:
    candidate_input = _candidate_input()
    candidate_input["candidates"][0]["evidence_refs"]["oos_gate_ref"] = (
        "scratch/WP-LAB-WALKFORWARD-OOS-GATE-01/oos_gate_contract.json"
    )
    result = evaluate_candidate_review_gate(candidate_input, _gate_artifact("fail"))

    candidate = result["candidate_results"][0]
    assert candidate["candidate_review_gate_status"] == "blocked"
    assert "oos_gate_decision_fail" in candidate["blockers"]
    assert result["aggregate"]["pass_count"] == 0


def test_purge_embargo_settings_are_recorded_and_validated() -> None:
    artifact = _gate_artifact()
    assert artifact["split"]["purge"] == {"mode": "bars", "bars": 96}
    assert artifact["split"]["embargo"] == {"mode": "bars", "bars": 32}
    invalid = copy.deepcopy(artifact)
    invalid["split"]["purge"]["bars"] = -1

    errors = validate_oos_gate_artifact(invalid)

    assert "split.purge.bars must be a non-negative integer" in errors


def test_gate_does_not_write_candidate_lifecycle() -> None:
    candidate_input = _candidate_input()
    candidate_input["candidates"][0]["evidence_refs"]["oos_gate_ref"] = (
        "scratch/WP-LAB-WALKFORWARD-OOS-GATE-01/oos_gate_contract.json"
    )
    result = evaluate_candidate_review_gate(candidate_input, _gate_artifact())

    assert result["candidate_results"][0]["candidate_review_gate_status"] == "pass"
    assert result["aggregate"]["canonical_writes"] == 0
    assert result["aggregate"]["candidate_lifecycle_writes"] == 0
    assert result["aggregate"]["runtime_actions"] == 0


def test_existing_candidate_review_behavior_is_preserved() -> None:
    report = build_lifecycle_report(_candidate_input())

    candidate = report["candidate_reports"][0]
    assert candidate["pending_state"] == "human_approval_required"
    assert candidate["blockers"] == []
    assert candidate["non_authority_flags"] == REQUIRED_NON_AUTHORITY_FLAGS


def test_cli_validates_gate_artifact(tmp_path: Path) -> None:
    gate_path = tmp_path / "gate.json"
    gate_path.write_text(json.dumps(_gate_artifact()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "tools.oos_gate.evaluate", "--gate-artifact", str(gate_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK: OOS gate artifact validates" in result.stdout
