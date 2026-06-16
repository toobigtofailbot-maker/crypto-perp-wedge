import copy
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_paper_state import (
    DEFAULT_PAPER_STATE_FIXTURE_DIR,
    PAPER_STATE_SCHEMA_PATH,
    REPO_ROOT,
    validate_paper_states,
)


VALID_FIXTURE_PATH = DEFAULT_PAPER_STATE_FIXTURE_DIR / "valid_example.paper_state.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_schema(path: Path = PAPER_STATE_SCHEMA_PATH) -> dict:
    return _load_json(path)


def _valid_paper_state() -> dict:
    return copy.deepcopy(_load_json(VALID_FIXTURE_PATH))


def _write_paper_state(paper_state_dir: Path, payload: dict, name: str = "fixture.paper_state.json") -> Path:
    paper_state_dir.mkdir(parents=True, exist_ok=True)
    path = paper_state_dir / name
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _drift_evidence_ref() -> dict:
    return {
        "artifact_type": "test_fixture",
        "artifact_id": "DRIFT-EVIDENCE-FIXTURE",
        "artifact_path": "tests/fixtures/paper_state/valid_example.paper_state.json",
        "relationship": "drift_evidence",
        "authority_boundary": "fixture_only",
        "identity_hash": None,
        "notes": "Pytest drift evidence fixture.",
    }


def test_paper_state_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_fake_fixture_passes():
    errors = validate_paper_states()

    assert errors == []


def test_real_shaped_non_authoritative_temp_payload_passes(tmp_path):
    payload = _valid_paper_state()
    payload["paper_state_id"] = "PAPER-STATE-0001"
    payload["mode"] = "paper_simulated"
    payload["candidate_ref"] = {
        "artifact_type": "candidate",
        "artifact_id": "CANDIDATE-0001",
        "artifact_path": None,
        "relationship": "non_authoritative_context",
        "authority_boundary": "review_reference_only",
        "identity_hash": None,
        "notes": "Temp validator payload only; not committed as paper-running.",
    }
    payload["validation_summary"]["fixture_only"] = False
    payload["validation_summary"]["notes"] = "Temp real-shaped payload for validator coverage only."
    paper_state_dir = tmp_path / "paper_state"
    _write_paper_state(paper_state_dir, payload)

    errors = validate_paper_states(paper_state_dir=paper_state_dir)

    assert errors == []


def test_false_non_authority_flag_fails(tmp_path):
    payload = _valid_paper_state()
    payload["non_authority_declaration"]["not_live_authority"] = False
    paper_state_dir = tmp_path / "paper_state"
    _write_paper_state(paper_state_dir, payload)

    errors = validate_paper_states(paper_state_dir=paper_state_dir)

    assert any("True was expected" in error for error in errors)


def test_fill_references_unknown_order_fails(tmp_path):
    payload = _valid_paper_state()
    payload["fills"][0]["order_id"] = "ORDER-EXAMPLE-MISSING"
    paper_state_dir = tmp_path / "paper_state"
    _write_paper_state(paper_state_dir, payload)

    errors = validate_paper_states(paper_state_dir=paper_state_dir)

    assert any("references unknown order_id ORDER-EXAMPLE-MISSING" in error for error in errors)


def test_duplicate_order_id_fails(tmp_path):
    payload = _valid_paper_state()
    payload["orders"].append(copy.deepcopy(payload["orders"][0]))
    payload["orders"][1]["client_order_id"] = "CLIENT-ORDER-EXAMPLE-0002"
    paper_state_dir = tmp_path / "paper_state"
    _write_paper_state(paper_state_dir, payload)

    errors = validate_paper_states(paper_state_dir=paper_state_dir)

    assert any("duplicate order_id: ORDER-EXAMPLE-0001" in error for error in errors)


def test_duplicate_fill_id_fails(tmp_path):
    payload = _valid_paper_state()
    payload["fills"].append(copy.deepcopy(payload["fills"][0]))
    paper_state_dir = tmp_path / "paper_state"
    _write_paper_state(paper_state_dir, payload)

    errors = validate_paper_states(paper_state_dir=paper_state_dir)

    assert any("duplicate fill_id: FILL-EXAMPLE-0001" in error for error in errors)


def test_non_none_drift_without_reason_or_evidence_fails(tmp_path):
    payload = _valid_paper_state()
    payload["drift"]["classification"] = "equity_mismatch"
    payload["drift"]["severity"] = "warning"
    payload["drift"]["reason"] = ""
    payload["drift"]["evidence_refs"] = []
    paper_state_dir = tmp_path / "paper_state"
    _write_paper_state(paper_state_dir, payload)

    errors = validate_paper_states(paper_state_dir=paper_state_dir)

    assert any("non-none drift requires a reason" in error for error in errors)
    assert any("non-none drift requires evidence_refs" in error for error in errors)


def test_halt_required_drift_without_safe_mode_policy_fails(tmp_path):
    payload = _valid_paper_state()
    payload["drift"]["classification"] = "open_order_mismatch"
    payload["drift"]["severity"] = "halt_required"
    payload["drift"]["reason"] = "Pytest severe drift."
    payload["drift"]["evidence_refs"] = [_drift_evidence_ref()]
    payload["risk_state"]["safe_mode_state"] = "normal"
    payload["risk_state"]["no_new_intent"] = False
    payload["risk_state"]["operator_halt"] = False
    paper_state_dir = tmp_path / "paper_state"
    _write_paper_state(paper_state_dir, payload)

    errors = validate_paper_states(paper_state_dir=paper_state_dir)

    assert any("halt_required drift requires safe_mode_state" in error for error in errors)
    assert any("halt_required drift requires no_new_intent true" in error for error in errors)
    assert any("halt_required drift requires operator_halt true" in error for error in errors)


def test_halt_required_drift_with_safe_mode_policy_passes(tmp_path):
    payload = _valid_paper_state()
    payload["drift"]["classification"] = "open_order_mismatch"
    payload["drift"]["severity"] = "halt_required"
    payload["drift"]["reason"] = "Pytest severe drift."
    payload["drift"]["evidence_refs"] = [_drift_evidence_ref()]
    payload["risk_state"]["safe_mode_state"] = "safe_mode"
    payload["risk_state"]["no_new_intent"] = True
    payload["risk_state"]["operator_halt"] = True
    paper_state_dir = tmp_path / "paper_state"
    _write_paper_state(paper_state_dir, payload)

    errors = validate_paper_states(paper_state_dir=paper_state_dir)

    assert errors == []


def test_invalid_enum_state_fails(tmp_path):
    payload = _valid_paper_state()
    payload["risk_state"]["safe_mode_state"] = "trade_anyway"
    paper_state_dir = tmp_path / "paper_state"
    _write_paper_state(paper_state_dir, payload)

    errors = validate_paper_states(paper_state_dir=paper_state_dir)

    assert any("'trade_anyway' is not one of" in error for error in errors)


def test_cli_module_invocation_works(tmp_path):
    paper_state_dir = tmp_path / "paper_state"
    _write_paper_state(paper_state_dir, _valid_paper_state())

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.registry.validate_paper_state",
            "--paper-state-dir",
            str(paper_state_dir),
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK: paper-state fixtures" in result.stdout


def test_no_real_research_paper_state_artifact_committed():
    research_paper_state_dir = REPO_ROOT / "research" / "paper_state"
    committed_research_paper_state_artifacts = sorted(
        path
        for path in (REPO_ROOT / "research").rglob("*.paper_state.json")
        if "schemas" not in path.parts
    )

    assert not research_paper_state_dir.exists()
    assert committed_research_paper_state_artifacts == []
