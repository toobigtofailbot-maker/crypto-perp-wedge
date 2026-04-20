import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.agents.macro_narrative_stub import (
    DEFAULT_FIXTURE_PATH,
    build_macro_window_agent_output,
    derive_macro_window_flag,
    load_fixture,
)
from tools.registry.validate_macro_window_agent_outputs import (
    DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR,
    MACRO_WINDOW_AGENT_OUTPUT_SCHEMA_PATH,
    REPO_ROOT,
    validate_macro_window_agent_outputs,
)


def _load_schema(path: Path = MACRO_WINDOW_AGENT_OUTPUT_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(payload: dict) -> list[str]:
    schema = _load_schema()
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _fixture_sha256() -> str:
    return hashlib.sha256(DEFAULT_FIXTURE_PATH.read_bytes()).hexdigest()


def _valid_macro_window_agent_output() -> dict:
    return {
        "macro_window_agent_output_id": "MOUT-9999",
        "generated_at": "2026-04-19T19:00:00Z",
        "as_of_timestamp": "2026-04-19T18:00:00Z",
        "source_fixture_path": "tests/fixtures/macro_narrative_input_fixture.json",
        "source_fixture_sha256": _fixture_sha256(),
        "macro_window_flag": True,
        "event_class": "SYNTHETIC_MACRO_EVENT",
        "event_name": "Synthetic macro risk window fixture",
        "deterministic": True,
        "advisory_only": True,
        "notes": "Fixture-backed advisory-only macro-window output with no execution influence.",
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_macro_window_agent_output_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_minimum_macro_window_agent_output_passes():
    errors = _validate(_valid_macro_window_agent_output())

    assert errors == []


def test_invalid_macro_window_agent_output_id_pattern_fails():
    payload = _valid_macro_window_agent_output()
    payload["macro_window_agent_output_id"] = "AOUT-9999"

    errors = _validate(payload)

    assert any("does not match '^MOUT-[0-9]{4}$'" in error for error in errors)


def test_macro_window_agent_output_validator_noops_when_directory_absent(tmp_path):
    missing_dir = tmp_path / "research" / "macro_window_agent_outputs"

    errors = validate_macro_window_agent_outputs(macro_window_agent_outputs_dir=missing_dir)

    assert errors == []


def test_macro_window_agent_output_validator_rejects_missing_fixture(tmp_path):
    outputs_dir = tmp_path / "research" / "macro_window_agent_outputs"
    payload = _valid_macro_window_agent_output()
    payload["macro_window_agent_output_id"] = "MOUT-9001"
    payload["source_fixture_path"] = "tests/fixtures/missing_macro_narrative_fixture.json"
    _write_json(outputs_dir / "MOUT-9001.macro_window_agent_output.json", payload)

    errors = validate_macro_window_agent_outputs(
        macro_window_agent_outputs_dir=outputs_dir,
        repo_root=REPO_ROOT,
    )

    assert any("source_fixture_path does not exist" in error for error in errors)


def test_macro_window_agent_output_validator_rejects_hash_mismatch(tmp_path):
    outputs_dir = tmp_path / "research" / "macro_window_agent_outputs"
    payload = _valid_macro_window_agent_output()
    payload["macro_window_agent_output_id"] = "MOUT-9002"
    payload["source_fixture_sha256"] = "0" * 64
    _write_json(outputs_dir / "MOUT-9002.macro_window_agent_output.json", payload)

    errors = validate_macro_window_agent_outputs(
        macro_window_agent_outputs_dir=outputs_dir,
        repo_root=REPO_ROOT,
    )

    assert any("source_fixture_sha256 mismatch" in error for error in errors)


def test_macro_window_agent_output_validator_rejects_inconsistent_flag(tmp_path):
    outputs_dir = tmp_path / "research" / "macro_window_agent_outputs"
    payload = _valid_macro_window_agent_output()
    payload["macro_window_agent_output_id"] = "MOUT-9003"
    payload["macro_window_flag"] = False
    _write_json(outputs_dir / "MOUT-9003.macro_window_agent_output.json", payload)

    errors = validate_macro_window_agent_outputs(
        macro_window_agent_outputs_dir=outputs_dir,
        repo_root=REPO_ROOT,
    )

    assert any("macro_window_flag should be True" in error for error in errors)


def test_current_macro_window_agent_output_file_passes():
    errors = validate_macro_window_agent_outputs(
        macro_window_agent_outputs_dir=DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR
    )

    assert errors == []


def test_fixture_backed_stub_expected_flag():
    fixture = load_fixture(DEFAULT_FIXTURE_PATH)

    result = derive_macro_window_flag(fixture)

    assert result is True


def test_stub_builds_schema_valid_payload_from_fixture():
    payload = build_macro_window_agent_output()

    errors = _validate(copy.deepcopy(payload))

    assert errors == []
    assert payload["macro_window_agent_output_id"] == "MOUT-0001"
    assert payload["source_fixture_path"] == "tests/fixtures/macro_narrative_input_fixture.json"
    assert payload["source_fixture_sha256"] == _fixture_sha256()
    assert payload["macro_window_flag"] is True
