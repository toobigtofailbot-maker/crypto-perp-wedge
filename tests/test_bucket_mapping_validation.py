import copy
import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.mappers.score_bucket_mapper import (
    DEFAULT_AGENT_OUTPUT_PATH,
    build_bucket_mapping,
    load_agent_output,
    map_score_to_bucket,
)
from tools.registry.validate_bucket_mappings import (
    BUCKET_MAPPING_SCHEMA_PATH,
    DEFAULT_AGENT_OUTPUTS_DIR,
    DEFAULT_BUCKET_MAPPINGS_DIR,
    validate_bucket_mappings,
)


def _load_schema(path: Path = BUCKET_MAPPING_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(payload: dict) -> list[str]:
    schema = _load_schema()
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _valid_bucket_mapping() -> dict:
    return {
        "bucket_mapping_id": "BMAP-9999",
        "source_agent_output_id": "AOUT-0001",
        "agent_type": "REGIME_SCORING",
        "generated_at": "2026-04-19T18:00:00Z",
        "as_of_timestamp": "2026-04-19T17:00:00Z",
        "source_setup_score": 72.95,
        "source_confidence": 0.891,
        "mapping_method": "score_thresholds_with_confidence_floor_v1",
        "confidence_floor": 0.6,
        "confidence_floor_triggered": False,
        "mapped_bucket": "ALLOW_REDUCED",
        "size_multiplier": 0.5,
        "deterministic": True,
        "advisory_only": True,
        "notes": "Advisory-only mapping with no overlay contact and no execution influence.",
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_bucket_mapping_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_minimum_bucket_mapping_passes():
    errors = _validate(_valid_bucket_mapping())

    assert errors == []


def test_invalid_bucket_enum_fails():
    payload = _valid_bucket_mapping()
    payload["mapped_bucket"] = "PAUSE"

    errors = _validate(payload)

    assert any("'PAUSE' is not one of" in error for error in errors)


def test_invalid_multiplier_pairing_fails():
    payload = _valid_bucket_mapping()
    payload["size_multiplier"] = 1.0

    errors = _validate(payload)

    assert any("0.5 was expected" in error for error in errors)


def test_invalid_confidence_floor_triggered_state_fails():
    payload = _valid_bucket_mapping()
    payload["source_confidence"] = 0.55
    payload["confidence_floor_triggered"] = False

    errors = _validate(payload)

    assert any("0.6" in error for error in errors)


def test_bucket_mapping_validator_noops_when_directory_absent(tmp_path):
    missing_dir = tmp_path / "research" / "bucket_mappings"

    errors = validate_bucket_mappings(bucket_mappings_dir=missing_dir)

    assert errors == []


def test_bucket_mapping_validator_rejects_source_artifact_mismatch(tmp_path):
    bucket_mappings_dir = tmp_path / "research" / "bucket_mappings"
    payload = _valid_bucket_mapping()
    payload["bucket_mapping_id"] = "BMAP-9001"
    payload["source_setup_score"] = 80.0
    _write_json(bucket_mappings_dir / "BMAP-9001.bucket_mapping.json", payload)

    errors = validate_bucket_mappings(
        bucket_mappings_dir=bucket_mappings_dir,
        agent_outputs_dir=DEFAULT_AGENT_OUTPUTS_DIR,
    )

    assert any("source_setup_score mismatch" in error for error in errors)


def test_current_bucket_mapping_file_passes():
    errors = validate_bucket_mappings(bucket_mappings_dir=DEFAULT_BUCKET_MAPPINGS_DIR)

    assert errors == []


def test_mapper_expected_threshold_outcome():
    agent_output = load_agent_output(DEFAULT_AGENT_OUTPUT_PATH)

    payload = build_bucket_mapping(copy.deepcopy(agent_output))

    assert payload["bucket_mapping_id"] == "BMAP-0001"
    assert payload["source_agent_output_id"] == "AOUT-0001"
    assert payload["source_setup_score"] == 72.95
    assert payload["source_confidence"] == 0.891
    assert payload["mapped_bucket"] == "ALLOW_REDUCED"
    assert payload["size_multiplier"] == 0.5
    assert payload["confidence_floor_triggered"] is False


def test_mapper_confidence_floor_blocks_first():
    result = map_score_to_bucket(setup_score=95.0, confidence=0.59)

    assert result == {
        "mapped_bucket": "BLOCK",
        "size_multiplier": 0.0,
        "confidence_floor_triggered": True,
    }
