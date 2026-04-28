import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_lifecycle_changes import (
    LIFECYCLE_CHANGE_SCHEMA_PATH,
    validate_lifecycle_changes,
)


def _load_schema(path: Path = LIFECYCLE_CHANGE_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_registry(path: Path, candidate_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"candidate_id": candidate_id}) + "\n", encoding="utf-8")


def _base_lifecycle_change(lifecycle_change_id: str = "LCH-9001") -> dict:
    return {
        "lifecycle_change_id": lifecycle_change_id,
        "schema_version": "v1",
        "candidate_id": "H-901",
        "from_state": "proposed",
        "to_state": "in_research",
        "transition_edge": "proposed->in_research",
        "decided_by": "pytest fixture",
        "decided_at": "2026-04-23T12:00:00Z",
        "evidence_summary": "Fixture lifecycle evidence summary.",
        "risk_acknowledgment": "Fixture risk acknowledgment.",
        "evidence_artifact_refs": [],
        "supersedes_lch_id": None,
    }


def test_lifecycle_change_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_lifecycle_change_validator_noops_when_directory_missing(tmp_path):
    missing_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    _write_registry(registry_path, "H-901")

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=missing_dir,
        registry_path=registry_path,
    )

    assert errors == []


def test_lifecycle_change_validator_noops_when_directory_empty(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    lifecycle_changes_dir.mkdir(parents=True)
    _write_registry(registry_path, "H-901")

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert errors == []


def test_valid_synthetic_lifecycle_change_passes(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    _write_registry(registry_path, "H-901")
    _write_json(
        lifecycle_changes_dir / "LCH-9001.lifecycle_change.json",
        _base_lifecycle_change(),
    )

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert errors == []


def test_invalid_schema_shape_fails(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    payload = _base_lifecycle_change()
    del payload["decided_by"]
    _write_registry(registry_path, "H-901")
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert any("'decided_by' is a required property" in error for error in errors)


def test_filename_lifecycle_change_id_mismatch_fails(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    _write_registry(registry_path, "H-901")
    _write_json(
        lifecycle_changes_dir / "LCH-9999.lifecycle_change.json",
        _base_lifecycle_change("LCH-9001"),
    )

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert any("filename must be LCH-9001.lifecycle_change.json" in error for error in errors)


def test_duplicate_lifecycle_change_id_fails(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    _write_registry(registry_path, "H-901")
    _write_json(lifecycle_changes_dir / "a" / "LCH-9001.lifecycle_change.json", _base_lifecycle_change())
    _write_json(lifecycle_changes_dir / "b" / "LCH-9001.lifecycle_change.json", _base_lifecycle_change())

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert any("duplicate lifecycle_change_id LCH-9001" in error for error in errors)


def test_unknown_candidate_fails(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text("", encoding="utf-8")
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", _base_lifecycle_change())

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert any("candidate_id not found in registry: H-901" in error for error in errors)


def test_unknown_supersedes_lch_fails(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    payload = _base_lifecycle_change()
    payload["supersedes_lch_id"] = "LCH-9999"
    _write_registry(registry_path, "H-901")
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert any("supersedes_lch_id not found" in error for error in errors)


def test_transition_edge_from_to_mismatch_fails(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    payload = _base_lifecycle_change()
    payload["to_state"] = "paper_active"
    payload["evidence_artifact_refs"] = ["REP-0001"]
    _write_registry(registry_path, "H-901")
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert any("transition_edge proposed->in_research does not match" in error for error in errors)


def test_operational_transition_with_empty_evidence_fails(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    payload = _base_lifecycle_change()
    payload["from_state"] = "paper_eligible"
    payload["to_state"] = "paper_active"
    payload["transition_edge"] = "paper_eligible->paper_active"
    _write_registry(registry_path, "H-901")
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert any("requires evidence_artifact_refs" in error for error in errors)


def test_retrospective_flag_without_disclosure_fails(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    payload = _base_lifecycle_change()
    payload["retrospective_flag"] = True
    _write_registry(registry_path, "H-901")
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert any("retrospective_flag=true requires retrospective_disclosure" in error for error in errors)


def test_fast_track_without_strong_candidate_criteria_fails(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    payload = _base_lifecycle_change()
    payload["from_state"] = "paper_concluded"
    payload["to_state"] = "live_eligible"
    payload["transition_edge"] = "paper_concluded->live_eligible"
    payload["evidence_artifact_refs"] = ["REP-0001"]
    payload["fast_track_flag"] = True
    _write_registry(registry_path, "H-901")
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
    )

    assert any("fast_track_flag=true requires strong_candidate_criteria_refs" in error for error in errors)


def test_unknown_known_pattern_evidence_ref_fails(tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    experiments_dir = tmp_path / "research" / "experiments"
    payload = _base_lifecycle_change()
    payload["from_state"] = "paper_concluded"
    payload["to_state"] = "live_eligible"
    payload["transition_edge"] = "paper_concluded->live_eligible"
    payload["evidence_artifact_refs"] = ["REP-9999"]
    _write_registry(registry_path, "H-901")
    experiments_dir.mkdir(parents=True)
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=lifecycle_changes_dir,
        registry_path=registry_path,
        experiments_dir=experiments_dir,
    )

    assert any("evidence_artifact_refs unresolved REP reference: REP-9999" in error for error in errors)
