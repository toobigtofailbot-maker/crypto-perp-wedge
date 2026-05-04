import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_outcome_ledger import (
    OUTCOME_LEDGER_SCHEMA_PATH,
    validate_outcome_ledgers,
)


def _load_schema(path: Path = OUTCOME_LEDGER_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_registry(path: Path, candidate_id: str = "H-901") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"candidate_id": candidate_id}) + "\n", encoding="utf-8")


def _write_report(path: Path, report_id: str = "REP-9001", candidate_id: str = "H-901") -> None:
    _write_json(path, {"report_id": report_id, "candidate_id": candidate_id, "plan_id": "EXP-9001"})


def _base_outcome(outcome_id: str = "OL-9001") -> dict:
    return {
        "schema_version": "v1",
        "outcome_id": outcome_id,
        "candidate_id": "H-901",
        "lifecycle_state_during_window": "in_research",
        "evaluation_window_start": None,
        "evaluation_window_end": None,
        "outcome_kind": "research_oos",
        "metrics": {
            "source_field": "metrics.out_of_sample",
            "window_convention": "pytest fixture convention",
            "sharpe": 0.1,
            "max_drawdown": 0.2,
            "n_obs": 100,
            "trades": 10,
            "hit_rate": 0.4,
            "profit_factor": 1.1,
            "final_equity": 10010.0,
            "total_pnl": 10.0,
            "gross_pnl": 20.0,
            "fees_paid": 5.0,
            "slippage_paid": 3.0,
            "funding_paid": 2.0,
            "cost_drag_fraction": 0.5,
            "dsr": 0.6,
            "walk_forward_efficiency": 0.7,
            "gates_passed": 3,
            "gates_total": 8,
        },
        "data_provenance": {
            "source_data_refs": ["pytest_dataset"],
            "source_data_window_start": None,
            "source_data_window_end": None,
        },
        "derivation_record": {
            "derivation_method": "from_rep_artifact",
            "source_artifact_id": "REP-9001",
            "source_artifact_path": "research/experiments/REP-9001.report.json",
            "derivation_timestamp": "2026-04-30T12:00:00Z",
        },
        "pipeline_version": "post_wp_5b",
        "linked_artifacts": ["REP-9001"],
        "retrospective_flag": True,
        "retrospective_disclosure": "Pytest retrospective fixture.",
        "linked_advisory_artifacts": [],
    }


def _valid_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo_root = tmp_path
    outcome_ledgers_dir = repo_root / "research" / "outcome_ledgers"
    registry_path = repo_root / "research" / "candidate_registry.jsonl"
    experiments_dir = repo_root / "research" / "experiments"
    _write_registry(registry_path)
    _write_report(experiments_dir / "REP-9001.report.json")
    return repo_root, outcome_ledgers_dir, registry_path


def _validate(tmp_path: Path, payload: dict, filename: str = "OL-9001.outcome_ledger.json") -> list[str]:
    repo_root, outcome_ledgers_dir, registry_path = _valid_fixture(tmp_path)
    _write_json(outcome_ledgers_dir / filename, payload)
    return validate_outcome_ledgers(
        outcome_ledgers_dir=outcome_ledgers_dir,
        registry_path=registry_path,
        experiments_dir=repo_root / "research" / "experiments",
        lifecycle_changes_dir=repo_root / "research" / "lifecycle_changes",
        decision_changes_dir=repo_root / "research" / "decision_changes",
        release_notes_dir=repo_root / "research" / "release_notes",
        agent_outputs_dir=repo_root / "research" / "agent_outputs",
        macro_window_agent_outputs_dir=repo_root / "research" / "macro_window_agent_outputs",
        bucket_mappings_dir=repo_root / "research" / "bucket_mappings",
        pre_gate_advisory_snapshots_dir=repo_root / "research" / "pre_gate_advisory_snapshots",
        overlay_shadow_logs_dir=repo_root / "research" / "overlay_shadow_logs",
        shadow_signal_summaries_dir=repo_root / "research" / "shadow_signal_summaries",
        shadow_signal_summaries_v2_dir=repo_root / "research" / "shadow_signal_summaries_v2",
        repo_root=repo_root,
    )


def test_outcome_ledger_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_outcome_ledger_validator_noops_when_directory_missing(tmp_path):
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    _write_registry(registry_path)

    errors = validate_outcome_ledgers(
        outcome_ledgers_dir=tmp_path / "research" / "outcome_ledgers",
        registry_path=registry_path,
    )

    assert errors == []


def test_outcome_ledger_validator_noops_when_directory_empty(tmp_path):
    outcome_ledgers_dir = tmp_path / "research" / "outcome_ledgers"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    outcome_ledgers_dir.mkdir(parents=True)
    _write_registry(registry_path)

    errors = validate_outcome_ledgers(
        outcome_ledgers_dir=outcome_ledgers_dir,
        registry_path=registry_path,
    )

    assert errors == []


def test_valid_temp_outcome_ledger_passes(tmp_path):
    errors = _validate(tmp_path, _base_outcome())

    assert errors == []


def test_duplicate_outcome_id_fails(tmp_path):
    repo_root, outcome_ledgers_dir, registry_path = _valid_fixture(tmp_path)
    _write_json(outcome_ledgers_dir / "a" / "OL-9001.outcome_ledger.json", _base_outcome())
    _write_json(outcome_ledgers_dir / "b" / "OL-9001.outcome_ledger.json", _base_outcome())

    errors = validate_outcome_ledgers(
        outcome_ledgers_dir=outcome_ledgers_dir,
        registry_path=registry_path,
        experiments_dir=repo_root / "research" / "experiments",
        repo_root=repo_root,
    )

    assert any("duplicate outcome_id OL-9001" in error for error in errors)


def test_filename_outcome_id_mismatch_fails(tmp_path):
    errors = _validate(tmp_path, _base_outcome(), filename="OL-9999.outcome_ledger.json")

    assert any("filename must be OL-9001.outcome_ledger.json" in error for error in errors)


def test_unknown_candidate_fails(tmp_path):
    payload = _base_outcome()
    payload["candidate_id"] = "H-999"

    errors = _validate(tmp_path, payload)

    assert any("candidate_id not found in registry: H-999" in error for error in errors)


def test_unknown_rep_source_artifact_fails(tmp_path):
    payload = _base_outcome()
    payload["derivation_record"]["source_artifact_id"] = "REP-9999"
    payload["derivation_record"]["source_artifact_path"] = "research/experiments/REP-9999.report.json"
    payload["linked_artifacts"] = []

    errors = _validate(tmp_path, payload)

    assert any("source_artifact_id not found in discovered reports: REP-9999" in error for error in errors)


def test_source_artifact_id_path_mismatch_fails(tmp_path):
    repo_root, outcome_ledgers_dir, registry_path = _valid_fixture(tmp_path)
    _write_report(repo_root / "research" / "experiments" / "REP-0001.report.json", report_id="REP-0001")
    payload = _base_outcome()
    payload["derivation_record"]["source_artifact_path"] = "research/experiments/REP-0001.report.json"
    _write_json(outcome_ledgers_dir / "OL-9001.outcome_ledger.json", payload)

    errors = validate_outcome_ledgers(
        outcome_ledgers_dir=outcome_ledgers_dir,
        registry_path=registry_path,
        experiments_dir=repo_root / "research" / "experiments",
        repo_root=repo_root,
    )

    assert any("source_artifact_path research/experiments/REP-0001.report.json does not match" in error for error in errors)


def test_one_sided_evaluation_window_null_fails(tmp_path):
    payload = _base_outcome()
    payload["evaluation_window_start"] = "2026-01-01"

    errors = _validate(tmp_path, payload)

    assert any("evaluation window must have both start and end or both null" in error for error in errors)


def test_evaluation_window_end_before_start_fails(tmp_path):
    payload = _base_outcome()
    payload["evaluation_window_start"] = "2026-02-01"
    payload["evaluation_window_end"] = "2026-01-01"

    errors = _validate(tmp_path, payload)

    assert any("evaluation window end is before start" in error for error in errors)


def test_one_sided_source_data_window_null_fails(tmp_path):
    payload = _base_outcome()
    payload["data_provenance"]["source_data_window_start"] = "2026-01-01"

    errors = _validate(tmp_path, payload)

    assert any("source_data window must have both start and end or both null" in error for error in errors)


def test_source_data_window_end_before_start_fails(tmp_path):
    payload = _base_outcome()
    payload["data_provenance"]["source_data_window_start"] = "2026-02-01"
    payload["data_provenance"]["source_data_window_end"] = "2026-01-01"

    errors = _validate(tmp_path, payload)

    assert any("source_data window end is before start" in error for error in errors)


def test_retrospective_flag_true_without_disclosure_fails(tmp_path):
    payload = _base_outcome()
    del payload["retrospective_disclosure"]

    errors = _validate(tmp_path, payload)

    assert any("'retrospective_disclosure' is a required property" in error for error in errors)


def test_forbidden_extra_top_level_property_fails(tmp_path):
    payload = _base_outcome()
    payload["evidence_quality_score"] = 1.0

    errors = _validate(tmp_path, payload)

    assert any("Additional properties are not allowed" in error for error in errors)
