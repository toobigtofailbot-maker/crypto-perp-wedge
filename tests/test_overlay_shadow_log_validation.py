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


CANONICAL_SNAPSHOT_PATH = "tests/fixtures/context_snapshot_sample.json"
CANONICAL_CONFIG_PATH = "configs/fmp_macro_flags.json"
EXPLICIT_SNAPSHOT_PATH = "tests/fixtures/context_snapshot_sample_02.json"
EXPLICIT_CONFIG_PATH = "configs/fmp_macro_flags_02.json"


def _load_schema(path: Path = OVERLAY_SHADOW_LOG_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(payload: dict) -> list[str]:
    schema = _load_schema()
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _valid_overlay_shadow_log(
    *,
    snapshot_path: str = CANONICAL_SNAPSHOT_PATH,
    config_path: str = CANONICAL_CONFIG_PATH,
) -> dict:
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
            "snapshot_path": snapshot_path,
            "config_path": config_path,
            "evaluation_time_utc": "2026-04-19T17:00:00Z",
            "decision_id": "D-0001",
            "context_missing": False,
            "reason_code": "NO_ACTIVE_WINDOW",
        },
        "notes": "Zero override, no lib changes, no execution influence, no OMS or risk authority.",
    }


def _valid_pgas_overlay_shadow_log() -> dict:
    payload = _valid_overlay_shadow_log()
    payload["overlay_shadow_log_id"] = "OSH-9998"
    payload["advisory_source"] = "PGAS"
    payload["source_pre_gate_advisory_snapshot_id"] = "PGAS-0002"
    payload["observed_at"] = "2026-04-19T18:00:00Z"
    payload["observation_source"]["evaluation_time_utc"] = "2026-04-19T18:00:00Z"
    payload["notes"] = (
        "WP-7i zero-override shadow comparison. The PGAS combined advisory bucket is advisory-only "
        "and records comparison evidence only; no lib changes, no execution influence, no OMS "
        "authority, and no risk authority are created by this artifact."
    )
    return payload


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_overlay_shadow_log_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_minimum_overlay_shadow_log_passes():
    errors = _validate(_valid_overlay_shadow_log())

    assert errors == []


def test_valid_explicit_overlay_input_pair_passes_schema():
    errors = _validate(
        _valid_overlay_shadow_log(
            snapshot_path=EXPLICIT_SNAPSHOT_PATH,
            config_path=EXPLICIT_CONFIG_PATH,
        )
    )

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


def test_invalid_advisory_source_fails():
    payload = _valid_pgas_overlay_shadow_log()
    payload["advisory_source"] = "PGAS_V2"

    errors = _validate(payload)

    assert errors


def test_pgas_missing_source_snapshot_fails_schema():
    payload = _valid_pgas_overlay_shadow_log()
    del payload["source_pre_gate_advisory_snapshot_id"]

    errors = _validate(payload)

    assert errors


def test_schema_rejects_mixed_canonical_snapshot_with_explicit_config():
    errors = _validate(
        _valid_overlay_shadow_log(
            snapshot_path=CANONICAL_SNAPSHOT_PATH,
            config_path=EXPLICIT_CONFIG_PATH,
        )
    )

    assert errors


def test_schema_rejects_explicit_snapshot_with_canonical_config():
    errors = _validate(
        _valid_overlay_shadow_log(
            snapshot_path=EXPLICIT_SNAPSHOT_PATH,
            config_path=CANONICAL_CONFIG_PATH,
        )
    )

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


def test_overlay_shadow_validator_rejects_pgas_combined_bucket_mismatch(tmp_path):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    payload = _valid_pgas_overlay_shadow_log()
    payload["mapped_bucket"] = "ALLOW"
    payload["size_multiplier"] = 1.0
    payload["comparison_result"] = "MATCH"
    _write_json(overlay_shadow_logs_dir / "OSH-9002.overlay_shadow_log.json", payload)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=overlay_shadow_logs_dir)

    assert any("mapped_bucket mismatch with source PGAS-0002.pre_gate_advisory_snapshot.json" in error for error in errors)
    assert any("size_multiplier mismatch with source PGAS-0002.pre_gate_advisory_snapshot.json" in error for error in errors)


def test_overlay_shadow_validator_rejects_pgas_missing_snapshot_reference(tmp_path):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    payload = _valid_pgas_overlay_shadow_log()
    payload["source_pre_gate_advisory_snapshot_id"] = "PGAS-9999"
    _write_json(overlay_shadow_logs_dir / "OSH-9003.overlay_shadow_log.json", payload)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=overlay_shadow_logs_dir)

    assert any("source pre-gate advisory snapshot file does not exist" in error for error in errors)


def test_overlay_shadow_validator_rejects_duplicate_overlay_shadow_log_ids(tmp_path):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    payload = _valid_overlay_shadow_log()
    payload["overlay_shadow_log_id"] = "OSH-9004"
    _write_json(overlay_shadow_logs_dir / "OSH-9004.overlay_shadow_log.json", payload)
    _write_json(overlay_shadow_logs_dir / "duplicates" / "OSH-9004.overlay_shadow_log.json", payload)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=overlay_shadow_logs_dir)

    assert any("duplicate overlay_shadow_log_id OSH-9004" in error for error in errors)


def test_overlay_shadow_validator_accepts_explicit_overlay_input_paths(tmp_path):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    payload = _valid_overlay_shadow_log(
        snapshot_path=EXPLICIT_SNAPSHOT_PATH,
        config_path=EXPLICIT_CONFIG_PATH,
    )
    payload["overlay_shadow_log_id"] = "OSH-9005"
    _write_json(overlay_shadow_logs_dir / "OSH-9005.overlay_shadow_log.json", payload)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=overlay_shadow_logs_dir)

    assert errors == []


def test_overlay_shadow_validator_rejects_missing_explicit_snapshot_path(tmp_path):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    payload = _valid_overlay_shadow_log(
        snapshot_path="tests/fixtures/context_snapshot_sample_missing.json",
        config_path=EXPLICIT_CONFIG_PATH,
    )
    payload["overlay_shadow_log_id"] = "OSH-9006"
    _write_json(overlay_shadow_logs_dir / "OSH-9006.overlay_shadow_log.json", payload)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=overlay_shadow_logs_dir)

    assert any("observation_source.snapshot_path does not exist" in error for error in errors)


def test_overlay_shadow_validator_rejects_missing_explicit_config_path(tmp_path):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    payload = _valid_overlay_shadow_log(
        snapshot_path=EXPLICIT_SNAPSHOT_PATH,
        config_path="configs/fmp_macro_flags_missing.json",
    )
    payload["overlay_shadow_log_id"] = "OSH-9007"
    _write_json(overlay_shadow_logs_dir / "OSH-9007.overlay_shadow_log.json", payload)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=overlay_shadow_logs_dir)

    assert any("observation_source.config_path does not exist" in error for error in errors)


def test_overlay_shadow_validator_rejects_canonical_snapshot_with_explicit_config(tmp_path):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    payload = _valid_overlay_shadow_log(
        snapshot_path=CANONICAL_SNAPSHOT_PATH,
        config_path=EXPLICIT_CONFIG_PATH,
    )
    payload["overlay_shadow_log_id"] = "OSH-9008"
    _write_json(overlay_shadow_logs_dir / "OSH-9008.overlay_shadow_log.json", payload)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=overlay_shadow_logs_dir)

    assert any(
        "must both use the canonical pair or both use an explicit noncanonical pair" in error
        for error in errors
    )


def test_overlay_shadow_validator_rejects_explicit_snapshot_with_canonical_config(tmp_path):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    payload = _valid_overlay_shadow_log(
        snapshot_path=EXPLICIT_SNAPSHOT_PATH,
        config_path=CANONICAL_CONFIG_PATH,
    )
    payload["overlay_shadow_log_id"] = "OSH-9009"
    _write_json(overlay_shadow_logs_dir / "OSH-9009.overlay_shadow_log.json", payload)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=overlay_shadow_logs_dir)

    assert any(
        "must both use the canonical pair or both use an explicit noncanonical pair" in error
        for error in errors
    )


def test_overlay_shadow_validator_accepts_mixed_corpus_with_canonical_and_explicit_entries(tmp_path):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"

    canonical_payload = _valid_overlay_shadow_log()
    canonical_payload["overlay_shadow_log_id"] = "OSH-9010"
    _write_json(overlay_shadow_logs_dir / "OSH-9010.overlay_shadow_log.json", canonical_payload)

    explicit_payload = _valid_pgas_overlay_shadow_log()
    explicit_payload["overlay_shadow_log_id"] = "OSH-9011"
    explicit_payload["observation_source"]["snapshot_path"] = EXPLICIT_SNAPSHOT_PATH
    explicit_payload["observation_source"]["config_path"] = EXPLICIT_CONFIG_PATH
    _write_json(overlay_shadow_logs_dir / "OSH-9011.overlay_shadow_log.json", explicit_payload)

    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=overlay_shadow_logs_dir)

    assert errors == []


def test_hook_builds_current_overlay_shadow_log():
    payload = build_default_overlay_shadow_log()

    assert payload["overlay_shadow_log_id"] == "OSH-0001"
    assert "advisory_source" not in payload
    assert payload["source_bucket_mapping_id"] == "BMAP-0001"
    assert payload["source_agent_output_id"] == "AOUT-0001"
    assert payload["observed_overlay_bucket"] == "ALLOW"
    assert payload["mapped_bucket"] == "ALLOW_REDUCED"
    assert payload["size_multiplier"] == 0.5
    assert payload["comparison_result"] == "MISMATCH"
    assert payload["override_applied"] is False
    assert payload["fail_open_preserved"] is True
    assert payload["advisory_only"] is True


def test_hook_builds_pgas_overlay_shadow_log():
    payload = build_default_overlay_shadow_log(advisory_source="PGAS")

    assert payload["overlay_shadow_log_id"] == "OSH-0002"
    assert payload["advisory_source"] == "PGAS"
    assert payload["source_pre_gate_advisory_snapshot_id"] == "PGAS-0002"
    assert payload["source_bucket_mapping_id"] == "BMAP-0001"
    assert payload["source_agent_output_id"] == "AOUT-0001"
    assert payload["observed_overlay_bucket"] == "ALLOW"
    assert payload["observed_at"] == "2026-04-19T18:00:00Z"
    assert payload["mapped_bucket"] == "ALLOW_REDUCED"
    assert payload["size_multiplier"] == 0.5
    assert payload["comparison_result"] == "MISMATCH"
    assert payload["override_applied"] is False
    assert payload["fail_open_preserved"] is True
    assert payload["advisory_only"] is True


def test_current_overlay_shadow_log_file_passes():
    errors = validate_overlay_shadow_logs(overlay_shadow_logs_dir=DEFAULT_OVERLAY_SHADOW_LOGS_DIR)

    assert errors == []


def test_current_overlay_shadow_log_file_matches_historical_builder_output():
    payload = build_default_overlay_shadow_log()
    expected = json.dumps(payload, indent=2) + "\n"
    actual = (DEFAULT_OVERLAY_SHADOW_LOGS_DIR / "OSH-0001.overlay_shadow_log.json").read_text(encoding="utf-8")

    assert actual == expected


def test_hook_payload_is_schema_valid():
    payload = build_default_overlay_shadow_log()

    errors = _validate(copy.deepcopy(payload))

    assert errors == []
