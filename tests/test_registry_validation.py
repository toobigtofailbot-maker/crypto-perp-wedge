import copy
import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_experiment_artifacts import validate_experiment_artifacts
from tools.registry.validate_registry import REPO_ROOT, validate_registry


REGISTRY_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "candidate_registry.schema.json"
PLAN_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "experiment_plan.schema.json"
REPORT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "experiment_report.schema.json"


def _load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(schema_path: Path, payload: dict) -> list[str]:
    schema = _load_schema(schema_path)
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _valid_registry_row() -> dict:
    return {
        "candidate_id": "H-999",
        "name": "Fixture Candidate",
        "status": "CONCLUDED",
        "overall_verdict": "NO-GO",
        "strategy_family": "fixture",
        "timeframe": "1h",
        "information_inputs": ["ohlcv_1h"],
        "free_parameter_count": 1,
        "hypothesis_md_path": "research/hypotheses/H-001/HYPOTHESIS.md",
        "decision_record_path": "research/decisions/DEC-0001.md",
        "trial_ids": ["ea334eac-fd82-4d65-9457-09d3a4141fc6"],
        "pipeline_stage": "baseline_tested",
        "created_at": "2026-04-14",
        "updated_at": "2026-04-15",
    }


def _reserved_slot_row() -> dict:
    return {
        "candidate_id": "H-011",
        "name": "BTC/Gold relative-strength regime signal (reserved)",
        "status": "DRAFT",
        "overall_verdict": "PENDING",
        "strategy_family": "cross_asset_regime",
        "timeframe": "weekly",
        "information_inputs": [],
        "free_parameter_count": None,
        "hypothesis_md_path": None,
        "decision_record_path": None,
        "trial_ids": [],
        "pipeline_stage": "reserved",
        "created_at": "2026-04-18",
        "updated_at": "2026-04-18",
    }


def test_valid_backfill_like_row_passes():
    errors = _validate(REGISTRY_SCHEMA_PATH, _valid_registry_row())
    assert errors == []


def test_invalid_candidate_id_fails():
    row = _valid_registry_row()
    row["candidate_id"] = "BAD-1"

    errors = _validate(REGISTRY_SCHEMA_PATH, row)

    assert any("'BAD-1' does not match" in error for error in errors)


def test_missing_required_field_fails():
    row = _valid_registry_row()
    del row["name"]

    errors = _validate(REGISTRY_SCHEMA_PATH, row)

    assert any("'name' is a required property" in error for error in errors)


def test_conflicting_status_and_verdict_fails():
    row = _valid_registry_row()
    row["status"] = "DRAFT"
    row["overall_verdict"] = "NO-GO"

    errors = _validate(REGISTRY_SCHEMA_PATH, row)

    assert any("'DRAFT' is not one of" in error for error in errors)


def test_reserved_h011_shape_passes():
    row = _reserved_slot_row()

    errors = _validate(REGISTRY_SCHEMA_PATH, row)

    assert errors == []


def test_reserved_slot_rejects_decision_record_path():
    row = _reserved_slot_row()
    row["decision_record_path"] = "research/decisions/DEC-0001.md"

    errors = _validate(REGISTRY_SCHEMA_PATH, row)

    assert any("is not of type 'null'" in error for error in errors)


def test_reserved_slot_rejects_trial_ids():
    row = _reserved_slot_row()
    row["trial_ids"] = ["ea334eac-fd82-4d65-9457-09d3a4141fc6"]

    errors = _validate(REGISTRY_SCHEMA_PATH, row)

    assert any("is expected to be empty" in error for error in errors)


def test_reserved_slot_rejects_hypothesis_md_path():
    row = _reserved_slot_row()
    row["hypothesis_md_path"] = "research/hypotheses/H-001/HYPOTHESIS.md"

    errors = _validate(REGISTRY_SCHEMA_PATH, row)

    assert any("is not of type 'null'" in error for error in errors)


def test_current_registry_passes():
    errors = validate_registry()
    assert errors == []


def test_experiment_plan_schema_basic():
    plan = {
        "plan_id": "EXP-0001",
        "candidate_id": "H-001",
        "plan_type": "baseline",
        "rationale": "Test the registered baseline.",
        "hypothesis_to_test": "The baseline clears the shared promotion gates.",
        "success_criteria": {
            "gates": ["D2-006"],
            "additional_criteria": ["No unhandled data gaps"],
        },
        "evaluation_window": {
            "in_sample": {"start": None, "end": None},
            "out_of_sample": {"start": None, "end": None},
        },
        "parameters": {"lookback": 6},
        "data_requirements": ["binance_um_perp_BTCUSDT_4h"],
        "pre_registration_date": "2026-04-18",
        "author": "pytest",
        "human_approval_required": False,
    }

    errors = _validate(PLAN_SCHEMA_PATH, plan)

    assert errors == []


def test_experiment_report_schema_basic():
    report = {
        "report_id": "REP-0001",
        "plan_id": "EXP-0001",
        "candidate_id": "H-001",
        "execution_date": "2026-04-18",
        "trial_ids": ["ea334eac-fd82-4d65-9457-09d3a4141fc6"],
        "metrics": {
            "in_sample": {"sharpe": -0.3898},
            "out_of_sample": {"sharpe": -0.3898},
        },
        "gate_results": [
            {
                "gate_id": "D2-006-G1",
                "threshold": 1.0,
                "observed": -0.3898,
                "pass": False,
            },
            {
                "gate_id": "D2-006-G2",
                "threshold": "dsr_val > 0.95 vs evaluator SR benchmark",
                "observed": "current evaluator output",
                "pass": False,
            },
        ],
        "overall_verdict": "NO-GO",
        "observations": "Fixture report validates textual and numeric gate values.",
        "next_step_recommendation": "archive",
        "diagnostic_findings": ["Fixture diagnostic"],
    }

    errors = _validate(REPORT_SCHEMA_PATH, report)

    assert errors == []


def test_experiment_artifact_validator_noops_when_directory_absent(tmp_path):
    missing_experiments_dir = tmp_path / "research" / "experiments"
    errors = validate_experiment_artifacts(experiments_dir=missing_experiments_dir)

    assert errors == []


def test_experiment_artifact_validator_rejects_plan_yaml(tmp_path):
    experiments_dir = tmp_path / "research" / "experiments"
    experiments_dir.mkdir(parents=True)
    (experiments_dir / "EXP-0001.plan.yaml").write_text("plan_id: EXP-0001\n", encoding="utf-8")

    errors = validate_experiment_artifacts(experiments_dir=experiments_dir)

    assert len(errors) == 1
    assert "YAML experiment artifacts are unsupported in WP-6a" in errors[0]
    assert "*.plan.json or *.report.json" in errors[0]


def test_experiment_artifact_validator_rejects_report_yaml(tmp_path):
    experiments_dir = tmp_path / "research" / "experiments"
    experiments_dir.mkdir(parents=True)
    (experiments_dir / "REP-0001.report.yaml").write_text(
        "report_id: REP-0001\n",
        encoding="utf-8",
    )

    errors = validate_experiment_artifacts(experiments_dir=experiments_dir)

    assert len(errors) == 1
    assert "YAML experiment artifacts are unsupported in WP-6a" in errors[0]
    assert "*.plan.json or *.report.json" in errors[0]


def test_concluded_requires_trial_id():
    row = copy.deepcopy(_valid_registry_row())
    row["trial_ids"] = []

    errors = _validate(REGISTRY_SCHEMA_PATH, row)

    assert any("should be non-empty" in error for error in errors)
