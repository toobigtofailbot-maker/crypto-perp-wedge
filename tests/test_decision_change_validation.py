import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_decision_changes import (
    DECISION_CHANGE_SCHEMA_PATH,
    validate_decision_changes,
)


def _fixture_ids(offset: int = 1) -> dict[str, str]:
    return {
        "candidate_id": f"H-{900 + offset:03d}",
        "report_id": f"REP-{9000 + offset:04d}",
        "decision_change_id": f"DCH-{9000 + offset:04d}",
        "supersedes_decision_id": f"DCH-{9100 + offset:04d}",
    }


def _load_schema(path: Path = DECISION_CHANGE_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(payload: dict) -> list[str]:
    schema = _load_schema()
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _valid_decision_change(offset: int = 1) -> dict:
    ids = _fixture_ids(offset)
    return {
        "decision_change_id": ids["decision_change_id"],
        "candidate_id": ids["candidate_id"],
        "report_ids": [],
        "decision": "REJECT_AT_THIS_STAGE",
        "stage_transition": {
            "from_stage": "baseline_tested",
            "to_stage": "archived",
        },
        "decided_by": "pytest fixture",
        "decided_at": "2026-04-19T12:00:00Z",
        "rationale": "Fixture rationale.",
        "evidence_summary": "Fixture evidence summary.",
        "risk_acknowledgment": "Fixture risk acknowledgment.",
        "supersedes_decision_id": None,
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_registry(path: Path, candidate_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"candidate_id": candidate_id}) + "\n", encoding="utf-8")


def _write_report(path: Path, report_id: str) -> None:
    _write_json(path, {"report_id": report_id})


def test_decision_change_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_minimum_decision_change_passes():
    errors = _validate(_valid_decision_change())

    assert errors == []


def test_missing_required_field_fails():
    payload = _valid_decision_change()
    del payload["rationale"]

    errors = _validate(payload)

    assert any("'rationale' is a required property" in error for error in errors)


def test_invalid_decision_enum_fails():
    payload = _valid_decision_change()
    payload["decision"] = "APPROVE"

    errors = _validate(payload)

    assert any("'APPROVE' is not one of" in error for error in errors)


def test_approve_decision_requires_report_ids():
    payload = _valid_decision_change()
    payload["decision"] = "APPROVE_TO_SHADOW"

    errors = _validate(payload)

    assert any("should be non-empty" in error for error in errors)


def test_revert_requires_supersedes_decision_id():
    payload = _valid_decision_change()
    payload["decision"] = "REVERT_PRIOR_APPROVAL"

    errors = _validate(payload)

    assert any("is not of type 'string'" in error for error in errors)


def test_request_revision_requires_conditions():
    payload = _valid_decision_change()
    payload["decision"] = "REQUEST_REVISION"

    errors = _validate(payload)

    assert any("'conditions' is a required property" in error for error in errors)


def test_invalid_stage_enum_fails():
    payload = _valid_decision_change()
    payload["stage_transition"]["from_stage"] = "unknown_stage"

    errors = _validate(payload)

    assert any("'unknown_stage' is not one of" in error for error in errors)


def test_decision_change_validator_noops_when_directory_absent(tmp_path):
    missing_dir = tmp_path / "research" / "decision_changes"

    errors = validate_decision_changes(decision_changes_dir=missing_dir)

    assert errors == []


def test_decision_change_validator_valid_fixture_dir_passes(tmp_path):
    ids = _fixture_ids()
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    experiments_dir = tmp_path / "research" / "experiments"
    decision_changes_dir = tmp_path / "research" / "decision_changes"
    payload = _valid_decision_change()
    payload["decision"] = "APPROVE_TO_SHADOW"
    payload["report_ids"] = [ids["report_id"]]

    _write_registry(registry_path, ids["candidate_id"])
    _write_report(experiments_dir / "REP-fixture.report.json", ids["report_id"])
    _write_json(decision_changes_dir / "DCH-fixture.decision_change.json", payload)

    errors = validate_decision_changes(
        decision_changes_dir=decision_changes_dir,
        registry_path=registry_path,
        experiments_dir=experiments_dir,
    )

    assert errors == []


def test_decision_change_validator_unresolved_candidate_id_fails(tmp_path):
    ids = _fixture_ids()
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    experiments_dir = tmp_path / "research" / "experiments"
    decision_changes_dir = tmp_path / "research" / "decision_changes"
    payload = _valid_decision_change()
    payload["report_ids"] = [ids["report_id"]]
    payload["decision"] = "APPROVE_TO_SHADOW"

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text("", encoding="utf-8")
    _write_report(experiments_dir / "REP-fixture.report.json", ids["report_id"])
    _write_json(decision_changes_dir / "DCH-fixture.decision_change.json", payload)

    errors = validate_decision_changes(
        decision_changes_dir=decision_changes_dir,
        registry_path=registry_path,
        experiments_dir=experiments_dir,
    )

    assert any("candidate_id not found in registry" in error for error in errors)


def test_decision_change_validator_unresolved_report_id_fails(tmp_path):
    ids = _fixture_ids()
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    experiments_dir = tmp_path / "research" / "experiments"
    decision_changes_dir = tmp_path / "research" / "decision_changes"
    payload = _valid_decision_change()
    payload["report_ids"] = [ids["report_id"]]
    payload["decision"] = "APPROVE_TO_SHADOW"

    _write_registry(registry_path, ids["candidate_id"])
    experiments_dir.mkdir(parents=True)
    _write_json(decision_changes_dir / "DCH-fixture.decision_change.json", payload)

    errors = validate_decision_changes(
        decision_changes_dir=decision_changes_dir,
        registry_path=registry_path,
        experiments_dir=experiments_dir,
    )

    assert any("report_id not found in discovered reports" in error for error in errors)
