import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.agents.regime_scoring_stub import (
    DEFAULT_FIXTURE_PATH,
    build_agent_output,
    compute_regime_score,
    load_fixture,
)
from tools.registry.validate_agent_outputs import (
    AGENT_OUTPUT_SCHEMA_PATH,
    DEFAULT_AGENT_OUTPUTS_DIR,
    REPO_ROOT,
    validate_agent_outputs,
)


def _load_schema(path: Path = AGENT_OUTPUT_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(payload: dict) -> list[str]:
    schema = _load_schema()
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _fixture_sha256() -> str:
    return hashlib.sha256(DEFAULT_FIXTURE_PATH.read_bytes()).hexdigest()


def _valid_agent_output() -> dict:
    return {
        "agent_output_id": "AOUT-9999",
        "agent_type": "REGIME_SCORING",
        "generated_at": "2026-04-19T18:00:00Z",
        "input_data_refs": [
            {
                "path": "tests/fixtures/regime_scoring_market_fixture.json",
                "sha256": _fixture_sha256(),
                "role": "fixture_market_snapshot",
            }
        ],
        "as_of_timestamp": "2026-04-19T17:00:00Z",
        "setup_score": 72.95,
        "confidence": 0.891,
        "scoring_method": {
            "method_id": "fixture_regime_scoring_v1",
            "realized_volatility": 0.001720816252602692,
            "vol_component": 0.3441632505205384,
            "funding_component": 0.16,
            "spread_component": 0.16,
            "stress_score": 0.27049795031232304,
        },
        "rationale_summary": "Fixture-backed deterministic advisory output.",
        "deterministic": True,
        "notes": "Advisory-only fixture output with no execution influence.",
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_agent_output_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_minimum_agent_output_passes():
    errors = _validate(_valid_agent_output())

    assert errors == []


def test_missing_required_field_fails():
    payload = _valid_agent_output()
    del payload["rationale_summary"]

    errors = _validate(payload)

    assert any("'rationale_summary' is a required property" in error for error in errors)


def test_invalid_agent_type_fails():
    payload = _valid_agent_output()
    payload["agent_type"] = "MACRO_NARRATIVE"

    errors = _validate(payload)

    assert any("'MACRO_NARRATIVE' is not one of" in error for error in errors)


def test_invalid_setup_score_bounds_fail():
    payload = _valid_agent_output()
    payload["setup_score"] = 100.01

    errors = _validate(payload)

    assert any("is greater than the maximum of 100" in error for error in errors)


def test_invalid_confidence_bounds_fail():
    payload = _valid_agent_output()
    payload["confidence"] = -0.01

    errors = _validate(payload)

    assert any("is less than the minimum of 0" in error for error in errors)


def test_agent_output_validator_noops_when_directory_absent(tmp_path):
    missing_dir = tmp_path / "research" / "agent_outputs"

    errors = validate_agent_outputs(agent_outputs_dir=missing_dir)

    assert errors == []


def test_current_agent_output_file_passes():
    errors = validate_agent_outputs(agent_outputs_dir=DEFAULT_AGENT_OUTPUTS_DIR)

    assert errors == []


def test_agent_output_validator_rejects_bad_input_ref_hash(tmp_path):
    agent_outputs_dir = tmp_path / "research" / "agent_outputs"
    payload = _valid_agent_output()
    payload["agent_output_id"] = "AOUT-9001"
    payload["input_data_refs"][0]["sha256"] = "0" * 64
    _write_json(agent_outputs_dir / "AOUT-9001.agent_output.json", payload)

    errors = validate_agent_outputs(agent_outputs_dir=agent_outputs_dir, repo_root=REPO_ROOT)

    assert any("input_data_refs sha256 mismatch" in error for error in errors)


def test_agent_output_validator_rejects_filename_mismatch(tmp_path):
    agent_outputs_dir = tmp_path / "research" / "agent_outputs"
    payload = _valid_agent_output()
    payload["agent_output_id"] = "AOUT-9002"
    _write_json(agent_outputs_dir / "wrong.agent_output.json", payload)

    errors = validate_agent_outputs(agent_outputs_dir=agent_outputs_dir, repo_root=REPO_ROOT)

    assert any("filename must be AOUT-9002.agent_output.json" in error for error in errors)


def test_fixture_backed_stub_expected_score_values():
    fixture = load_fixture(DEFAULT_FIXTURE_PATH)

    result = compute_regime_score(fixture)

    assert result["setup_score"] == 72.95
    assert result["confidence"] == 0.891


def test_stub_builds_schema_valid_payload_from_fixture():
    payload = build_agent_output()

    errors = _validate(copy.deepcopy(payload))

    assert errors == []
    assert payload["agent_output_id"] == "AOUT-0001"
    assert payload["input_data_refs"][0]["path"] == "tests/fixtures/regime_scoring_market_fixture.json"
    assert payload["input_data_refs"][0]["sha256"] == _fixture_sha256()
