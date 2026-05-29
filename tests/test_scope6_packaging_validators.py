import json
import subprocess
import sys
from pathlib import Path

from tools.registry.validate_scope6_packaging import validate_scope6_packaging


def _artifact_ref(label: str = "REP-9000") -> dict:
    return {
        "artifact_id_or_label": label,
        "artifact_path": f"research/fixtures/{label}.json",
    }


def _r2s_payload(approval_record_id: str = "R2S-AR-0001", candidate_id: str = "H-001") -> dict:
    return {
        "schema_version": "v1",
        "record_type": "research_to_shadow_approval_record",
        "approval_record_id": approval_record_id,
        "candidate_id": candidate_id,
        "strategy_or_candidate_family": "momentum",
        "evidence_snapshot_references": [_artifact_ref("REP-0001")],
        "d2_006_gate_pass_evidence_reference_or_attestation": _artifact_ref("D2-006-attestation"),
        "rec5_exact_segment_evidence": {
            "candidate_id": candidate_id,
            "outcome_kind": "research_oos",
            "pipeline_version": "pre_wp_5b",
            "expectation_source_type": "d2_006_gates",
            "evidence_references": [_artifact_ref("REC-0001")],
            "no_pooled_or_cross_segment_inference_below_floor": True,
        },
        "no_cross_segment_inference_below_rec5_floor": True,
        "approver_identity": "human-reviewer",
        "approval_timestamp_utc": "2026-05-29T12:00:00Z",
        "decision_outcome": "approved",
        "preservation_confirmation": {
            "permanent_human_gates_preserved": True,
            "d2_006_preserved": True,
            "d2_007_preserved": True,
            "rec5_preserved": True,
            "phase9_preserved": True,
        },
        "transition_machinery_statement": (
            "This record is required before any future research-to-shadow transition, but it does not "
            "implement transition machinery or authorize transition execution."
        ),
        "authority_flags": {
            "candidate_readiness_authority": False,
            "transition_authority": False,
            "promotion_authority": False,
            "gate_execution_authority": False,
            "runtime_authority": False,
            "tier4_authority": False,
        },
    }


def _shadow_evidence_payload(shadow_evidence_id: str = "SER-0001", candidate_id: str = "H-001") -> dict:
    return {
        "schema_version": "v1",
        "record_type": "shadow_evidence_retention",
        "shadow_evidence_id": shadow_evidence_id,
        "candidate_id": candidate_id,
        "shadow_window": {
            "start_utc": "2026-05-01T00:00:00Z",
            "end_utc": "2026-05-15T00:00:00Z",
            "calendar_days_observed": 14,
        },
        "d2_007_thresholds": {
            "minimum_shadow_window_calendar_days": 14,
            "pnl_deviation_max": 0.1,
            "trade_count_deviation_max": 0.05,
        },
        "parity_result": {
            "observed_pnl_deviation": 0.03,
            "observed_trade_count_deviation": 0.02,
            "parity_result_evidence_reference_or_attestation": _artifact_ref("parity-attestation"),
        },
        "shadow_observation_lineage": [_artifact_ref("shadow-lineage")],
        "disclosure": {
            "interruptions": [],
            "invalid_observations": [],
            "missing_data": [],
            "observation_resets": [],
        },
        "evidence_retention_reference": _artifact_ref("retained-evidence"),
        "mismatch_diagnostics": {
            "decision_support_only": True,
            "ranking_authority": False,
            "scoring_authority": False,
            "recommendation_authority": False,
            "transition_logic_authority": False,
            "diagnostic_references": [],
        },
        "authority_flags": {
            "candidate_readiness_authority": False,
            "transition_authority": False,
            "ranking_authority": False,
            "scoring_authority": False,
            "recommendation_authority": False,
            "gate_execution_authority": False,
            "runtime_authority": False,
            "tier4_authority": False,
        },
    }


def _s2p_payload(
    approval_record_id: str = "S2P-AR-0001",
    candidate_id: str = "H-001",
    shadow_evidence_id: str = "SER-0001",
) -> dict:
    return {
        "schema_version": "v1",
        "record_type": "shadow_to_paper_approval_record",
        "approval_record_id": approval_record_id,
        "candidate_id": candidate_id,
        "shadow_window_evidence_reference": {
            "shadow_evidence_id": shadow_evidence_id,
            "artifact_path": f"research/shadow_evidence_retention/{shadow_evidence_id}.shadow_evidence_retention.json",
        },
        "d2_007_parity_result_reference_or_attestation": _artifact_ref("d2-007-attestation"),
        "interruption_or_invalid_observation_disclosure_reference": _artifact_ref("disclosure-attestation"),
        "paper_runtime_protection_confirmation": True,
        "approver_identity": "human-reviewer",
        "approval_timestamp_utc": "2026-05-29T12:00:00Z",
        "decision_outcome": "approved",
        "preservation_confirmation": {
            "permanent_human_gates_preserved": True,
            "d2_007_preserved": True,
            "phase1_paper_runtime_protection_preserved": True,
            "tier4_boundaries_preserved": True,
        },
        "transition_machinery_statement": (
            "This record is required before any future shadow-to-paper transition, but it does not "
            "implement transition machinery, invoke paper runtime, or authorize transition execution."
        ),
        "authority_flags": {
            "candidate_readiness_authority": False,
            "transition_authority": False,
            "promotion_authority": False,
            "gate_execution_authority": False,
            "paper_runtime_authority": False,
            "runtime_authority": False,
            "tier4_authority": False,
        },
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _validate(tmp_path: Path) -> list[str]:
    return validate_scope6_packaging(
        r2s_approval_records_dir=tmp_path / "research" / "r2s_approval_records",
        shadow_evidence_retention_dir=tmp_path / "research" / "shadow_evidence_retention",
        s2p_approval_records_dir=tmp_path / "research" / "s2p_approval_records",
    )


def _write_valid_set(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        _r2s_payload(),
    )
    _write_json(
        tmp_path / "research" / "shadow_evidence_retention" / "SER-0001.shadow_evidence_retention.json",
        _shadow_evidence_payload(),
    )
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "S2P-AR-0001.s2p_approval_record.json",
        _s2p_payload(),
    )


def test_validator_returns_empty_when_target_directories_are_missing(tmp_path):
    assert _validate(tmp_path) == []


def test_validator_returns_empty_when_target_directories_have_no_matching_artifacts(tmp_path):
    (tmp_path / "research" / "r2s_approval_records").mkdir(parents=True)
    (tmp_path / "research" / "shadow_evidence_retention").mkdir(parents=True)
    (tmp_path / "research" / "s2p_approval_records").mkdir(parents=True)
    _write_json(tmp_path / "research" / "r2s_approval_records" / "ignored.json", {"ignored": True})

    assert _validate(tmp_path) == []


def test_valid_minimal_r2s_approval_record_passes(tmp_path):
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        _r2s_payload(),
    )

    assert _validate(tmp_path) == []


def test_valid_minimal_shadow_evidence_retention_record_passes(tmp_path):
    _write_json(
        tmp_path / "research" / "shadow_evidence_retention" / "SER-0001.shadow_evidence_retention.json",
        _shadow_evidence_payload(),
    )

    assert _validate(tmp_path) == []


def test_valid_minimal_s2p_approval_record_passes(tmp_path):
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "S2P-AR-0001.s2p_approval_record.json",
        _s2p_payload(),
    )

    assert _validate(tmp_path) == []


def test_invalid_r2s_authority_flag_fails(tmp_path):
    payload = _r2s_payload()
    payload["authority_flags"]["transition_authority"] = True
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        payload,
    )

    errors = _validate(tmp_path)

    assert any("authority_flags.transition_authority" in error for error in errors)


def test_invalid_shadow_evidence_threshold_or_authority_flag_fails(tmp_path):
    payload = _shadow_evidence_payload()
    payload["d2_007_thresholds"]["minimum_shadow_window_calendar_days"] = 13
    payload["authority_flags"]["recommendation_authority"] = True
    _write_json(
        tmp_path / "research" / "shadow_evidence_retention" / "SER-0001.shadow_evidence_retention.json",
        payload,
    )

    errors = _validate(tmp_path)

    assert any("d2_007_thresholds.minimum_shadow_window_calendar_days" in error for error in errors)
    assert any("authority_flags.recommendation_authority" in error for error in errors)


def test_invalid_s2p_paper_runtime_protection_or_authority_flag_fails(tmp_path):
    payload = _s2p_payload()
    payload["paper_runtime_protection_confirmation"] = False
    payload["authority_flags"]["paper_runtime_authority"] = True
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "S2P-AR-0001.s2p_approval_record.json",
        payload,
    )

    errors = _validate(tmp_path)

    assert any("paper_runtime_protection_confirmation" in error for error in errors)
    assert any("authority_flags.paper_runtime_authority" in error for error in errors)


def test_wrong_filename_for_valid_payloads_fails(tmp_path):
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "wrong.r2s_approval_record.json",
        _r2s_payload(),
    )
    _write_json(
        tmp_path / "research" / "shadow_evidence_retention" / "wrong.shadow_evidence_retention.json",
        _shadow_evidence_payload(),
    )
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "wrong.s2p_approval_record.json",
        _s2p_payload(),
    )

    errors = _validate(tmp_path)

    assert any("filename must be R2S-AR-0001.r2s_approval_record.json" in error for error in errors)
    assert any("filename must be SER-0001.shadow_evidence_retention.json" in error for error in errors)
    assert any("filename must be S2P-AR-0001.s2p_approval_record.json" in error for error in errors)


def test_duplicate_ids_in_one_family_fail(tmp_path):
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        _r2s_payload(),
    )
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "nested" / "R2S-AR-0001.r2s_approval_record.json",
        _r2s_payload(),
    )

    errors = _validate(tmp_path)

    assert any("duplicate approval_record_id R2S-AR-0001" in error for error in errors)


def test_r2s_nested_rec5_candidate_mismatch_fails(tmp_path):
    payload = _r2s_payload(candidate_id="H-001")
    payload["rec5_exact_segment_evidence"]["candidate_id"] = "H-002"
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        payload,
    )

    errors = _validate(tmp_path)

    assert any("rec5_exact_segment_evidence.candidate_id must match candidate_id H-001" in error for error in errors)


def test_s2p_reference_to_existing_shadow_evidence_with_different_candidate_id_fails(tmp_path):
    _write_json(
        tmp_path / "research" / "shadow_evidence_retention" / "SER-0001.shadow_evidence_retention.json",
        _shadow_evidence_payload(candidate_id="H-002"),
    )
    _write_json(
        tmp_path / "research" / "s2p_approval_records" / "S2P-AR-0001.s2p_approval_record.json",
        _s2p_payload(candidate_id="H-001", shadow_evidence_id="SER-0001"),
    )

    errors = _validate(tmp_path)

    assert any("candidate_id H-002 does not match S2P candidate_id H-001" in error for error in errors)


def test_cli_returns_zero_for_valid_temp_fixture_set(tmp_path):
    _write_valid_set(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.registry.validate_scope6_packaging",
            "--r2s-approval-records-dir",
            str(tmp_path / "research" / "r2s_approval_records"),
            "--shadow-evidence-retention-dir",
            str(tmp_path / "research" / "shadow_evidence_retention"),
            "--s2p-approval-records-dir",
            str(tmp_path / "research" / "s2p_approval_records"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "OK: Scope 6 packaging artifacts validate" in result.stdout


def test_cli_returns_one_for_invalid_temp_fixture_set(tmp_path):
    payload = _r2s_payload()
    payload["authority_flags"]["transition_authority"] = True
    _write_json(
        tmp_path / "research" / "r2s_approval_records" / "R2S-AR-0001.r2s_approval_record.json",
        payload,
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.registry.validate_scope6_packaging",
            "--r2s-approval-records-dir",
            str(tmp_path / "research" / "r2s_approval_records"),
            "--shadow-evidence-retention-dir",
            str(tmp_path / "research" / "shadow_evidence_retention"),
            "--s2p-approval-records-dir",
            str(tmp_path / "research" / "s2p_approval_records"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "ERROR:" in result.stdout
