import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_release_notes import (
    RELEASE_NOTES_SCHEMA_PATH,
    validate_release_notes,
)


def _fixture_ids(offset: int = 1) -> dict[str, str]:
    return {
        "candidate_id": f"H-{920 + offset:03d}",
        "decision_change_id": f"DCH-{9200 + offset:04d}",
        "release_notes_id": f"REL-{9200 + offset:04d}",
    }


def _load_schema(path: Path = RELEASE_NOTES_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(payload: dict) -> list[str]:
    schema = _load_schema()
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _valid_release_notes(offset: int = 1) -> dict:
    ids = _fixture_ids(offset)
    return {
        "release_notes_id": ids["release_notes_id"],
        "decision_change_id": ids["decision_change_id"],
        "candidate_id": ids["candidate_id"],
        "released_at": "2026-04-19T13:00:00Z",
        "released_by": "pytest fixture",
        "effective_stage": "shadow_live",
        "monitoring_plan": {
            "metrics_tracked": ["fixture metric"],
            "review_cadence": "fixture cadence",
            "rollback_triggers": ["fixture rollback trigger"],
            "alert_recipients": ["fixture reviewer"],
        },
        "rollback_plan": "Fixture rollback plan.",
    }


def _valid_decision_change(offset: int = 1) -> dict:
    ids = _fixture_ids(offset)
    return {
        "decision_change_id": ids["decision_change_id"],
        "candidate_id": ids["candidate_id"],
        "report_ids": [],
        "decision": "APPROVE_TO_SHADOW",
        "stage_transition": {
            "from_stage": "paper_validated",
            "to_stage": "shadow_live",
        },
        "decided_by": "pytest fixture",
        "decided_at": "2026-04-19T12:00:00Z",
        "rationale": "Fixture rationale.",
        "evidence_summary": "Fixture evidence.",
        "risk_acknowledgment": "Fixture risk acknowledgment.",
        "supersedes_decision_id": None,
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_release_notes_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_minimum_release_notes_passes():
    errors = _validate(_valid_release_notes())

    assert errors == []


def test_missing_required_field_fails():
    payload = _valid_release_notes()
    del payload["rollback_plan"]

    errors = _validate(payload)

    assert any("'rollback_plan' is a required property" in error for error in errors)


def test_invalid_effective_stage_fails():
    payload = _valid_release_notes()
    payload["effective_stage"] = "unknown_stage"

    errors = _validate(payload)

    assert any("'unknown_stage' is not one of" in error for error in errors)


def test_release_notes_validator_noops_when_directory_absent(tmp_path):
    missing_dir = tmp_path / "research" / "release_notes"

    errors = validate_release_notes(release_notes_dir=missing_dir)

    assert errors == []


def test_release_notes_validator_valid_fixture_passes(tmp_path):
    release_notes_dir = tmp_path / "research" / "release_notes"
    decision_changes_dir = tmp_path / "research" / "decision_changes"

    _write_json(decision_changes_dir / "DCH-fixture.decision_change.json", _valid_decision_change())
    _write_json(release_notes_dir / "REL-fixture.release_notes.json", _valid_release_notes())

    errors = validate_release_notes(
        release_notes_dir=release_notes_dir,
        decision_changes_dir=decision_changes_dir,
    )

    assert errors == []


def test_release_notes_validator_unresolved_decision_change_id_fails(tmp_path):
    release_notes_dir = tmp_path / "research" / "release_notes"
    decision_changes_dir = tmp_path / "research" / "decision_changes"

    decision_changes_dir.mkdir(parents=True)
    _write_json(release_notes_dir / "REL-fixture.release_notes.json", _valid_release_notes())

    errors = validate_release_notes(
        release_notes_dir=release_notes_dir,
        decision_changes_dir=decision_changes_dir,
    )

    assert any("decision_change_id not found" in error for error in errors)


def test_release_notes_validator_candidate_id_mismatch_fails(tmp_path):
    release_notes_dir = tmp_path / "research" / "release_notes"
    decision_changes_dir = tmp_path / "research" / "decision_changes"
    payload = _valid_release_notes()
    payload["candidate_id"] = _fixture_ids(2)["candidate_id"]

    _write_json(decision_changes_dir / "DCH-fixture.decision_change.json", _valid_decision_change())
    _write_json(release_notes_dir / "REL-fixture.release_notes.json", payload)

    errors = validate_release_notes(
        release_notes_dir=release_notes_dir,
        decision_changes_dir=decision_changes_dir,
    )

    assert any("does not match decision_change" in error for error in errors)


def test_release_notes_validator_effective_stage_mismatch_fails(tmp_path):
    release_notes_dir = tmp_path / "research" / "release_notes"
    decision_changes_dir = tmp_path / "research" / "decision_changes"
    payload = _valid_release_notes()
    payload["effective_stage"] = "paper_validated"

    _write_json(decision_changes_dir / "DCH-fixture.decision_change.json", _valid_decision_change())
    _write_json(release_notes_dir / "REL-fixture.release_notes.json", payload)

    errors = validate_release_notes(
        release_notes_dir=release_notes_dir,
        decision_changes_dir=decision_changes_dir,
    )

    assert any("effective_stage" in error and "does not match" in error for error in errors)


def test_release_notes_validator_released_before_decided_fails(tmp_path):
    release_notes_dir = tmp_path / "research" / "release_notes"
    decision_changes_dir = tmp_path / "research" / "decision_changes"
    payload = _valid_release_notes()
    payload["released_at"] = "2026-04-19T11:59:59Z"

    _write_json(decision_changes_dir / "DCH-fixture.decision_change.json", _valid_decision_change())
    _write_json(release_notes_dir / "REL-fixture.release_notes.json", payload)

    errors = validate_release_notes(
        release_notes_dir=release_notes_dir,
        decision_changes_dir=decision_changes_dir,
    )

    assert any("released_at" in error and "is before" in error for error in errors)
