import copy
import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_shadow_signal_summaries import (
    DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR,
    SHADOW_SIGNAL_SUMMARY_SCHEMA_PATH,
    derive_shadow_signal_summary_payload,
    validate_shadow_signal_summaries,
)


def _load_schema(path: Path = SHADOW_SIGNAL_SUMMARY_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_schema_payload(payload: dict) -> list[str]:
    schema = _load_schema()
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _valid_shadow_signal_summary_payload() -> dict:
    return derive_shadow_signal_summary_payload(shadow_signal_summary_id="SSS-9999")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_shadow_signal_summary_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_shadow_signal_summary_payload_passes_schema():
    errors = _validate_schema_payload(_valid_shadow_signal_summary_payload())

    assert errors == []


def test_schema_rejects_missing_segment_key_field():
    payload = _valid_shadow_signal_summary_payload()
    del payload["segments"][0]["fixture_identity"]

    errors = _validate_schema_payload(payload)

    assert errors


def test_shadow_signal_summary_validator_noops_when_directory_empty(tmp_path):
    empty_dir = tmp_path / "research" / "shadow_signal_summaries"
    empty_dir.mkdir(parents=True)

    errors = validate_shadow_signal_summaries(shadow_signal_summaries_dir=empty_dir)

    assert errors == []


def test_shadow_signal_summary_validator_rejects_bad_counts(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries"
    payload = _valid_shadow_signal_summary_payload()
    payload["shadow_signal_summary_id"] = "SSS-9001"
    payload["segments"][0]["observation_count"] = 99
    _write_json(summaries_dir / "SSS-9001.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summaries(shadow_signal_summaries_dir=summaries_dir)

    assert any("observation_count should be" in error for error in errors)


def test_shadow_signal_summary_validator_rejects_bad_denominator(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries"
    payload = _valid_shadow_signal_summary_payload()
    payload["shadow_signal_summary_id"] = "SSS-9002"
    payload["segments"][0]["rate_denominator"] = 99
    _write_json(summaries_dir / "SSS-9002.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summaries(shadow_signal_summaries_dir=summaries_dir)

    assert any("rate_denominator should be" in error for error in errors)


def test_shadow_signal_summary_validator_rejects_insufficient_rule_violation(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries"
    payload = _valid_shadow_signal_summary_payload()
    payload["shadow_signal_summary_id"] = "SSS-9003"
    payload["segments"][0]["insufficient_evidence"] = False
    payload["segments"][0]["signal_outcome"] = "AGREEMENT_SIGNAL"
    payload["segments"][0]["agreement_rate"] = 1.0
    payload["segments"][0]["disagreement_rate"] = 0.0
    _write_json(summaries_dir / "SSS-9003.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summaries(shadow_signal_summaries_dir=summaries_dir)

    assert any("insufficient_evidence should be True" in error for error in errors)
    assert any("signal_outcome should be INSUFFICIENT_EVIDENCE" in error for error in errors)


def test_shadow_signal_summary_validator_accepts_majority_tie_classification_at_floor(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries"
    payload = _valid_shadow_signal_summary_payload()
    payload["shadow_signal_summary_id"] = "SSS-9004"
    segment = payload["segments"][0]
    segment["match_count"] = 5
    segment["mismatch_count"] = 5
    segment["abstention_count"] = 0
    segment["observation_count"] = 10
    segment["rate_denominator"] = 10
    segment["insufficient_evidence"] = False
    segment["signal_outcome"] = "MIXED_SIGNAL"
    segment["agreement_rate"] = 0.5
    segment["disagreement_rate"] = 0.5
    _write_json(summaries_dir / "SSS-9004.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summaries(shadow_signal_summaries_dir=summaries_dir)

    assert any("payload does not match deterministic derivation" in error for error in errors)
    assert not any("signal_outcome should be" in error for error in errors)


def test_current_shadow_signal_summary_file_passes():
    errors = validate_shadow_signal_summaries(
        shadow_signal_summaries_dir=DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR
    )

    assert errors == []


def test_current_shadow_signal_summary_file_matches_deterministic_derivation():
    expected = json.dumps(
        derive_shadow_signal_summary_payload(shadow_signal_summary_id="SSS-0001"),
        indent=2,
    ) + "\n"
    actual = (
        DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR / "SSS-0001.shadow_signal_summary.json"
    ).read_text(encoding="utf-8")

    assert actual == expected


def test_shadow_signal_summary_validator_detects_drifted_payload(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries"
    payload = copy.deepcopy(_valid_shadow_signal_summary_payload())
    payload["shadow_signal_summary_id"] = "SSS-9005"
    payload["segments"][0]["match_count"] = 1
    payload["segments"][0]["mismatch_count"] = 0
    payload["segments"][0]["rate_denominator"] = 1
    _write_json(summaries_dir / "SSS-9005.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summaries(shadow_signal_summaries_dir=summaries_dir)

    assert any("payload does not match deterministic derivation" in error for error in errors)
