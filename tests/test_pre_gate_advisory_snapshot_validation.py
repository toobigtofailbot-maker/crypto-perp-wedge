import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_pre_gate_advisory_snapshots import (
    DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR,
    PRE_GATE_ADVISORY_SNAPSHOT_SCHEMA_PATH,
    REPO_ROOT,
    validate_pre_gate_advisory_snapshots,
)
from tools.support.build_pre_gate_advisory_snapshot import (
    DEFAULT_AGENT_OUTPUT_PATH,
    DEFAULT_BUCKET_MAPPING_PATH,
    DEFAULT_MACRO_WINDOW_AGENT_OUTPUT_PATH,
    build_pre_gate_advisory_snapshot,
    load_json,
)


def _load_schema(path: Path = PRE_GATE_ADVISORY_SNAPSHOT_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(payload: dict) -> list[str]:
    schema = _load_schema()
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _valid_pre_gate_advisory_snapshot() -> dict:
    return {
        "pre_gate_advisory_snapshot_id": "PGAS-9999",
        "generated_at": "2026-04-19T19:00:00Z",
        "as_of_timestamp": "2026-04-19T18:00:00Z",
        "source_agent_output_id": "AOUT-0001",
        "source_bucket_mapping_id": "BMAP-0001",
        "source_macro_window_agent_output_id": "MOUT-0001",
        "setup_score": 72.95,
        "confidence": 0.891,
        "mapped_bucket": "ALLOW_REDUCED",
        "size_multiplier": 0.5,
        "macro_window_flag": True,
        "deterministic": True,
        "advisory_only": True,
        "combination_rule_applied": "NONE_BUNDLE_ONLY",
        "notes": (
            "Bundle-only snapshot with no final gate decision, no runtime influence, "
            "no execution authority, and no overlay, OMS, risk, or policy authority."
        ),
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_pre_gate_advisory_snapshot_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_minimum_pre_gate_advisory_snapshot_passes():
    errors = _validate(_valid_pre_gate_advisory_snapshot())

    assert errors == []


def test_invalid_pre_gate_advisory_snapshot_id_pattern_fails():
    payload = _valid_pre_gate_advisory_snapshot()
    payload["pre_gate_advisory_snapshot_id"] = "PGA-9999"

    errors = _validate(payload)

    assert any("does not match '^PGAS-[0-9]{4}$'" in error for error in errors)


def test_pre_gate_advisory_snapshot_validator_rejects_missing_source_artifact(tmp_path):
    snapshots_dir = tmp_path / "research" / "pre_gate_advisory_snapshots"
    payload = _valid_pre_gate_advisory_snapshot()
    payload["pre_gate_advisory_snapshot_id"] = "PGAS-9001"
    payload["source_bucket_mapping_id"] = "BMAP-9998"
    _write_json(snapshots_dir / "PGAS-9001.pre_gate_advisory_snapshot.json", payload)

    errors = validate_pre_gate_advisory_snapshots(
        pre_gate_advisory_snapshots_dir=snapshots_dir,
    )

    assert any("source bucket mapping file does not exist" in error for error in errors)


def test_pre_gate_advisory_snapshot_validator_rejects_copied_value_mismatch(tmp_path):
    snapshots_dir = tmp_path / "research" / "pre_gate_advisory_snapshots"
    payload = _valid_pre_gate_advisory_snapshot()
    payload["pre_gate_advisory_snapshot_id"] = "PGAS-9002"
    payload["macro_window_flag"] = False
    _write_json(snapshots_dir / "PGAS-9002.pre_gate_advisory_snapshot.json", payload)

    errors = validate_pre_gate_advisory_snapshots(
        pre_gate_advisory_snapshots_dir=snapshots_dir,
    )

    assert any("macro_window_flag mismatch" in error for error in errors)


def test_pre_gate_advisory_snapshot_validator_rejects_invalid_combination_rule(tmp_path):
    snapshots_dir = tmp_path / "research" / "pre_gate_advisory_snapshots"
    payload = _valid_pre_gate_advisory_snapshot()
    payload["pre_gate_advisory_snapshot_id"] = "PGAS-9003"
    payload["combination_rule_applied"] = "FUSED_RULE_V1"
    _write_json(snapshots_dir / "PGAS-9003.pre_gate_advisory_snapshot.json", payload)

    errors = validate_pre_gate_advisory_snapshots(
        pre_gate_advisory_snapshots_dir=snapshots_dir,
    )

    assert any("combination_rule_applied should be one of" in error for error in errors)


def test_pre_gate_advisory_snapshot_schema_rejects_bundle_only_combined_bucket():
    payload = _valid_pre_gate_advisory_snapshot()
    payload["combined_bucket"] = "ALLOW_REDUCED"

    errors = _validate(payload)

    assert errors


def test_pre_gate_advisory_snapshot_schema_rejects_missing_non_none_combined_bucket():
    payload = _valid_pre_gate_advisory_snapshot()
    payload["combination_rule_applied"] = "MACRO_AWARE_FLOOR"

    errors = _validate(payload)

    assert any("'combined_bucket' is a required property" in error for error in errors)


def test_pre_gate_advisory_snapshot_validator_rejects_wrong_combined_bucket(tmp_path):
    snapshots_dir = tmp_path / "research" / "pre_gate_advisory_snapshots"
    payload = _valid_pre_gate_advisory_snapshot()
    payload["pre_gate_advisory_snapshot_id"] = "PGAS-9004"
    payload["combination_rule_applied"] = "MACRO_AWARE_FLOOR"
    payload["combined_bucket"] = "ALLOW"
    _write_json(snapshots_dir / "PGAS-9004.pre_gate_advisory_snapshot.json", payload)

    errors = validate_pre_gate_advisory_snapshots(
        pre_gate_advisory_snapshots_dir=snapshots_dir,
    )

    assert any("combined_bucket should be ALLOW_REDUCED" in error for error in errors)


def test_pre_gate_advisory_snapshot_validator_rejects_duplicate_ids(tmp_path):
    snapshots_dir = tmp_path / "research" / "pre_gate_advisory_snapshots"
    payload = _valid_pre_gate_advisory_snapshot()
    payload["pre_gate_advisory_snapshot_id"] = "PGAS-9005"
    _write_json(snapshots_dir / "PGAS-9005.pre_gate_advisory_snapshot.json", payload)
    _write_json(snapshots_dir / "duplicates" / "PGAS-9005.pre_gate_advisory_snapshot.json", payload)

    errors = validate_pre_gate_advisory_snapshots(
        pre_gate_advisory_snapshots_dir=snapshots_dir,
    )

    assert any("duplicate pre_gate_advisory_snapshot_id PGAS-9005" in error for error in errors)


def test_pre_gate_advisory_snapshot_validator_noops_when_directory_absent(tmp_path):
    missing_dir = tmp_path / "research" / "pre_gate_advisory_snapshots"

    errors = validate_pre_gate_advisory_snapshots(pre_gate_advisory_snapshots_dir=missing_dir)

    assert errors == []


def test_current_pre_gate_advisory_snapshot_file_passes():
    errors = validate_pre_gate_advisory_snapshots(
        pre_gate_advisory_snapshots_dir=DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR,
    )

    assert errors == []


def test_builder_builds_current_snapshot_from_repo_truth():
    payload = build_pre_gate_advisory_snapshot(
        agent_output=load_json(DEFAULT_AGENT_OUTPUT_PATH),
        bucket_mapping=load_json(DEFAULT_BUCKET_MAPPING_PATH),
        macro_window_agent_output=load_json(DEFAULT_MACRO_WINDOW_AGENT_OUTPUT_PATH),
    )

    assert payload == {
        "pre_gate_advisory_snapshot_id": "PGAS-0001",
        "generated_at": "2026-04-19T19:00:00Z",
        "as_of_timestamp": "2026-04-19T18:00:00Z",
        "source_agent_output_id": "AOUT-0001",
        "source_bucket_mapping_id": "BMAP-0001",
        "source_macro_window_agent_output_id": "MOUT-0001",
        "setup_score": 72.95,
        "confidence": 0.891,
        "mapped_bucket": "ALLOW_REDUCED",
        "size_multiplier": 0.5,
        "macro_window_flag": True,
        "deterministic": True,
        "advisory_only": True,
        "combination_rule_applied": "NONE_BUNDLE_ONLY",
        "notes": (
            "WP-7g bundle-only pre-gate advisory snapshot over committed advisory artifacts. "
            "It encodes no final gate decision, no runtime influence, no execution authority, "
            "and no overlay, OMS, risk, or policy authority."
        ),
    }


def test_builder_builds_macro_aware_floor_snapshot_from_repo_truth():
    payload = build_pre_gate_advisory_snapshot(
        agent_output=load_json(DEFAULT_AGENT_OUTPUT_PATH),
        bucket_mapping=load_json(DEFAULT_BUCKET_MAPPING_PATH),
        macro_window_agent_output=load_json(DEFAULT_MACRO_WINDOW_AGENT_OUTPUT_PATH),
        pre_gate_advisory_snapshot_id="PGAS-0002",
        combination_rule_applied="MACRO_AWARE_FLOOR",
    )

    assert payload == {
        "pre_gate_advisory_snapshot_id": "PGAS-0002",
        "generated_at": "2026-04-19T19:00:00Z",
        "as_of_timestamp": "2026-04-19T18:00:00Z",
        "source_agent_output_id": "AOUT-0001",
        "source_bucket_mapping_id": "BMAP-0001",
        "source_macro_window_agent_output_id": "MOUT-0001",
        "setup_score": 72.95,
        "confidence": 0.891,
        "mapped_bucket": "ALLOW_REDUCED",
        "size_multiplier": 0.5,
        "macro_window_flag": True,
        "deterministic": True,
        "advisory_only": True,
        "combination_rule_applied": "MACRO_AWARE_FLOOR",
        "combined_bucket": "ALLOW_REDUCED",
        "notes": (
            "WP-7h deterministic pre-gate advisory snapshot over committed advisory artifacts. "
            "It applies the first non-bundle-only MACRO_AWARE_FLOOR rule, remains advisory-only, "
            "has no runtime influence, no execution authority, and has no overlay, OMS, risk, "
            "or policy authority."
        ),
    }
