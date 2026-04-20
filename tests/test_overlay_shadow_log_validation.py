import copy
import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_overlay_shadow_logs import (
    DEFAULT_OVERLAY_SHADOW_LOGS_DIR,
    OVERLAY_SHADOW_LOG_SCHEMA_PATH,
    validate_overlay_shadow_logs,
)
from tools.shadow.overlay_shadow_hook import build_default_overlay_shadow_log


def _load_schema(path: Path = OVERLAY_SHADOW_LOG_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(payload: dict) -> list[str]:
    schema = _load_schema()
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _valid_overlay_shadow_log() -> dict:
    return {
        "overlay_shadow_log_id": "OSH-9999",
        "source_bucket_mapping_id": "BMAP-0001",
        "source_agent_output_id": "AOUT-0001",
        "observed_overlay_bucket": "ALLOW",
        "observed_overlay_size_multiplier": 1.0,
        "mapped_bucket": "ALLOW_REDUCED",
        "size_multiplier": 0.5,
        "comparison_result": "MISMATCH",
        "override_applied": False,
        "fail_open_preserved": True,
        "advisory_only": True,
        "observed_at": "2026-04-19T17:00:00Z",
        "observation_source": {
            "source_type": "committed_macro_context_fixture",
            "snapshot_path": "tests/fixtures/context_snapshot_sample.json",
            "config_path": "configs/fmp_macro_flags.json",
            "evaluation_time_utc": "2026-04-19T17:00:00Z",
            "decision_id": "D-0001",
            "context_missing": False,
            "reason_code": "NO_ACTIVE_WINDOW",
        },
        "notes": "Zero override, no lib changes, no execution influence, no OMS or risk authority.",
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_overlay_shadow_log_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_minimum_overlay_shadow_log_passes():
    errors = _validate(_valid_overlay_shadow_log())

    assert errors == []


def test_invalid_comparison_enum_fails():
    payload = _valid_overlay_shadow_log()
    payload["comparison_result"] = "DIFFERENT"

    errors = _validate(payload)

    assert errors


def test_override_applied_true_fails():
    payload = _valid_overlay_shadow_log()
    payload["override_applied"] = True

    errors = _validate(payload)

    assert errors


def test_fail_open_preserved_false_fails():
    payload = _valid_overlay_shadow_log()
    payload["fail_open_preserved"] = False

    errors = _validate(payload)

    assert errors


def test_overlay_shadow_validator_noops_when_directory_empty(tmp_path):
    empty_dir = tmp_path / "research" / "overlay_shadow_logs"
    empty_dir.mkdir(parents=True)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=empty_dir)

    assert errors == []


def test_overlay_shadow_validator_rejects_source_artifact_mismatch(tmp_path):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    payload = _valid_overlay_shadow_log()
    payload["overlay_shadow_log_id"] = "OSH-9001"
    payload["mapped_bucket"] = "ALLOW"
    payload["size_multiplier"] = 1.0
    payload["comparison_result"] = "MATCH"
    _write_json(overlay_shadow_logs_dir / "OSH-9001.overlay_shadow_log.json", payload)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=overlay_shadow_logs_dir)

    assert any("mapped_bucket mismatch" in error for error in errors)
    assert any("size_multiplier mismatch" in error for error in errors)


def test_hook_builds_current_overlay_shadow_log():
    payload = build_default_overlay_shadow_log()

    assert payload["overlay_shadow_log_id"] == "OSH-0001"
    assert payload["source_bucket_mapping_id"] == "BMAP-0001"
    assert payload["source_agent_output_id"] == "AOUT-0001"
    assert payload["observed_overlay_bucket"] == "ALLOW"
    assert payload["mapped_bucket"] == "ALLOW_REDUCED"
    assert payload["size_multiplier"] == 0.5
    assert payload["comparison_result"] == "MISMATCH"
    assert payload["override_applied"] is False
    assert payload["fail_open_preserved"] is True
    assert payload["advisory_only"] is True


def test_current_overlay_shadow_log_file_passes():
    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=DEFAULT_OVERLAY_SHADOW_LOGS_DIR)

    assert errors == []


def test_hook_payload_is_schema_valid():
    payload = build_default_overlay_shadow_log()

    errors = _validate(copy.deepcopy(payload))

    assert errors == []
