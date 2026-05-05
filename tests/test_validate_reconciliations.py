import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_reconciliations import (
    RECONCILIATION_SCHEMA_PATH,
    validate_reconciliations,
)


def _load_schema(path: Path = RECONCILIATION_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_registry(path: Path, candidate_id: str = "H-901") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"candidate_id": candidate_id}) + "\n", encoding="utf-8")


def _base_metrics() -> dict:
    return {
        "source_field": "metrics.out_of_sample",
        "window_convention": "pytest fixture convention",
        "sharpe": 0.1,
        "max_drawdown": 0.2,
        "n_obs": 100,
        "trades": 10,
        "hit_rate": 0.4,
        "profit_factor": 1.1,
        "final_equity": 10010.0,
        "total_pnl": 10.0,
        "gross_pnl": 20.0,
        "fees_paid": 5.0,
        "slippage_paid": 3.0,
        "funding_paid": 2.0,
        "cost_drag_fraction": 0.5,
        "dsr": 0.6,
        "walk_forward_efficiency": 0.7,
        "gates_passed": 3,
        "gates_total": 8,
    }


def _write_outcome(path: Path, candidate_id: str = "H-901", pipeline_version: str = "post_wp_5b") -> None:
    _write_json(
        path,
        {
            "schema_version": "v1",
            "outcome_id": "OL-9001",
            "candidate_id": candidate_id,
            "outcome_kind": "research_oos",
            "pipeline_version": pipeline_version,
            "metrics": _base_metrics(),
        },
    )


def _write_plan(path: Path, candidate_id: str = "H-901", plan_id: str = "EXP-9001") -> None:
    _write_json(
        path,
        {
            "plan_id": plan_id,
            "candidate_id": candidate_id,
            "success_criteria": {
                "gates": ["D2-006"],
                "additional_criteria": ["pytest fixture criterion"],
            },
        },
    )


def _base_rec(reconciliation_id: str = "REC-9001") -> dict:
    return {
        "schema_version": "v1",
        "reconciliation_id": reconciliation_id,
        "candidate_id": "H-901",
        "outcome_id": "OL-9001",
        "outcome_kind": "research_oos",
        "pipeline_version": "post_wp_5b",
        "expectation_source_type": "exp_success_criteria",
        "expectation_source_artifact_id": "EXP-9001",
        "expectation_source_artifact_path": "research/experiments/EXP-9001.plan.json",
        "expectation_extracted": {
            "source_type": "exp_success_criteria",
            "source_artifact_id": "EXP-9001",
            "source_artifact_path": "research/experiments/EXP-9001.plan.json",
            "extraction_method": "pytest fixture",
            "extracted_at": "2026-05-04T12:00:00Z",
            "metric_expectations": [
                {
                    "metric_name": "sharpe",
                    "expected_operator": "gte",
                    "expected_value": 1.0,
                    "expected_unit": None,
                    "source_field_path": "success_criteria.gates",
                    "source_text": "Fixture expectation",
                }
            ],
        },
        "realized_metrics": _base_metrics(),
        "comparison": {
            "metric_comparisons": [
                {
                    "metric_name": "sharpe",
                    "expected_value": 1.0,
                    "realized_value": 0.1,
                    "delta_absolute": -0.9,
                    "delta_relative": -0.9,
                    "comparison_verdict": "not_met",
                    "comparison_notes": "Fixture comparison.",
                }
            ]
        },
        "overall_verdict": "none_met",
        "interpretation": "Pytest fixture REC.",
        "derivation_record": {
            "derivation_method": "pytest fixture",
            "source_artifact_id": "OL-9001",
            "source_artifact_path": "research/outcome_ledgers/OL-9001.outcome_ledger.json",
            "derivation_timestamp": "2026-05-04T12:00:00Z",
            "source_outcome_id": "OL-9001",
            "expectation_source_type": "exp_success_criteria",
        },
        "retrospective_flag": True,
        "retrospective_disclosure": "Pytest retrospective fixture.",
        "linked_advisory_artifacts": [],
        "linked_lifecycle_artifacts": [],
    }


def _fixture_repo(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo_root = tmp_path
    reconciliations_dir = repo_root / "research" / "reconciliations"
    registry_path = repo_root / "research" / "candidate_registry.jsonl"
    _write_registry(registry_path)
    _write_outcome(repo_root / "research" / "outcome_ledgers" / "OL-9001.outcome_ledger.json")
    _write_plan(repo_root / "research" / "experiments" / "EXP-9001.plan.json")
    (repo_root / "docs" / "onboarding").mkdir(parents=True)
    (repo_root / "docs" / "onboarding" / "PHASE2_BASELINE.md").write_text("D2-006\n", encoding="utf-8")
    return repo_root, reconciliations_dir, registry_path


def _validate(tmp_path: Path, payload: dict, filename: str = "REC-9001.reconciliation.json") -> list[str]:
    repo_root, reconciliations_dir, registry_path = _fixture_repo(tmp_path)
    _write_json(reconciliations_dir / filename, payload)
    return validate_reconciliations(
        reconciliations_dir=reconciliations_dir,
        registry_path=registry_path,
        outcome_ledgers_dir=repo_root / "research" / "outcome_ledgers",
        experiments_dir=repo_root / "research" / "experiments",
        lifecycle_changes_dir=repo_root / "research" / "lifecycle_changes",
        agent_outputs_dir=repo_root / "research" / "agent_outputs",
        macro_window_agent_outputs_dir=repo_root / "research" / "macro_window_agent_outputs",
        bucket_mappings_dir=repo_root / "research" / "bucket_mappings",
        pre_gate_advisory_snapshots_dir=repo_root / "research" / "pre_gate_advisory_snapshots",
        overlay_shadow_logs_dir=repo_root / "research" / "overlay_shadow_logs",
        shadow_signal_summaries_dir=repo_root / "research" / "shadow_signal_summaries",
        shadow_signal_summaries_v2_dir=repo_root / "research" / "shadow_signal_summaries_v2",
        repo_root=repo_root,
    )


def test_reconciliation_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_reconciliation_validator_noops_when_directory_missing(tmp_path):
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    _write_registry(registry_path)

    errors = validate_reconciliations(
        reconciliations_dir=tmp_path / "research" / "reconciliations",
        registry_path=registry_path,
    )

    assert errors == []


def test_reconciliation_validator_noops_when_directory_empty(tmp_path):
    reconciliations_dir = tmp_path / "research" / "reconciliations"
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    reconciliations_dir.mkdir(parents=True)
    _write_registry(registry_path)

    errors = validate_reconciliations(
        reconciliations_dir=reconciliations_dir,
        registry_path=registry_path,
    )

    assert errors == []


def test_valid_temp_reconciliation_passes(tmp_path):
    assert _validate(tmp_path, _base_rec()) == []


def test_invalid_schema_shape_fails(tmp_path):
    payload = _base_rec()
    del payload["interpretation"]

    errors = _validate(tmp_path, payload)

    assert any("'interpretation' is a required property" in error for error in errors)


def test_filename_reconciliation_id_mismatch_fails(tmp_path):
    errors = _validate(tmp_path, _base_rec(), filename="REC-9999.reconciliation.json")

    assert any("filename must be REC-9001.reconciliation.json" in error for error in errors)


def test_duplicate_reconciliation_id_fails(tmp_path):
    repo_root, reconciliations_dir, registry_path = _fixture_repo(tmp_path)
    _write_json(reconciliations_dir / "a" / "REC-9001.reconciliation.json", _base_rec())
    _write_json(reconciliations_dir / "b" / "REC-9001.reconciliation.json", _base_rec())

    errors = validate_reconciliations(
        reconciliations_dir=reconciliations_dir,
        registry_path=registry_path,
        outcome_ledgers_dir=repo_root / "research" / "outcome_ledgers",
        experiments_dir=repo_root / "research" / "experiments",
        repo_root=repo_root,
    )

    assert any("duplicate reconciliation_id REC-9001" in error for error in errors)


def test_wrong_rec_suffix_fails(tmp_path):
    repo_root, reconciliations_dir, registry_path = _fixture_repo(tmp_path)
    _write_json(reconciliations_dir / "REC-9001.json", _base_rec())

    errors = validate_reconciliations(
        reconciliations_dir=reconciliations_dir,
        registry_path=registry_path,
        outcome_ledgers_dir=repo_root / "research" / "outcome_ledgers",
        experiments_dir=repo_root / "research" / "experiments",
        repo_root=repo_root,
    )

    assert any("REC artifact filename must use REC-NNNN.reconciliation.json suffix" in error for error in errors)


def test_unresolved_outcome_fails(tmp_path):
    payload = _base_rec()
    payload["outcome_id"] = "OL-9999"
    payload["derivation_record"]["source_outcome_id"] = "OL-9999"

    errors = _validate(tmp_path, payload)

    assert any("outcome_id not found in discovered outcome ledgers: OL-9999" in error for error in errors)


def test_outcome_candidate_mismatch_fails(tmp_path):
    repo_root, reconciliations_dir, registry_path = _fixture_repo(tmp_path)
    _write_registry(registry_path, "H-902")
    payload = _base_rec()
    payload["candidate_id"] = "H-902"
    _write_json(reconciliations_dir / "REC-9001.reconciliation.json", payload)

    errors = validate_reconciliations(
        reconciliations_dir=reconciliations_dir,
        registry_path=registry_path,
        outcome_ledgers_dir=repo_root / "research" / "outcome_ledgers",
        experiments_dir=repo_root / "research" / "experiments",
        repo_root=repo_root,
    )

    assert any("candidate_id H-902 does not match referenced OL" in error for error in errors)


def test_outcome_pipeline_mismatch_fails(tmp_path):
    payload = _base_rec()
    payload["pipeline_version"] = "pre_wp_5b"

    errors = _validate(tmp_path, payload)

    assert any("pipeline_version pre_wp_5b does not match referenced OL" in error for error in errors)


def test_invalid_expectation_source_fails(tmp_path):
    payload = _base_rec()
    payload["expectation_source_type"] = "bad_source"
    payload["expectation_extracted"]["source_type"] = "bad_source"

    errors = _validate(tmp_path, payload)

    assert any("'bad_source' is not one of" in error for error in errors)


def test_exp_expectation_source_path_mismatch_fails(tmp_path):
    repo_root, reconciliations_dir, registry_path = _fixture_repo(tmp_path)
    _write_plan(
        repo_root / "research" / "experiments" / "EXP-9999.plan.json",
        plan_id="EXP-9999",
    )
    payload = _base_rec()
    payload["expectation_source_artifact_id"] = "EXP-9999"
    payload["expectation_extracted"]["source_artifact_id"] = "EXP-9999"
    _write_json(reconciliations_dir / "REC-9001.reconciliation.json", payload)

    errors = validate_reconciliations(
        reconciliations_dir=reconciliations_dir,
        registry_path=registry_path,
        outcome_ledgers_dir=repo_root / "research" / "outcome_ledgers",
        experiments_dir=repo_root / "research" / "experiments",
        repo_root=repo_root,
    )

    assert any("expectation_source_artifact_path" in error and "does not match" in error for error in errors)


def test_d2_006_source_path_id_mismatch_fails(tmp_path):
    payload = _base_rec()
    payload["expectation_source_type"] = "d2_006_gates"
    payload["expectation_source_artifact_id"] = "BAD-D2"
    payload["expectation_source_artifact_path"] = "docs/onboarding/BAD.md"
    payload["expectation_extracted"]["source_type"] = "d2_006_gates"
    payload["expectation_extracted"]["source_artifact_id"] = "BAD-D2"
    payload["expectation_extracted"]["source_artifact_path"] = "docs/onboarding/BAD.md"
    payload["derivation_record"]["expectation_source_type"] = "d2_006_gates"

    errors = _validate(tmp_path, payload)

    assert any("d2_006_gates requires expectation_source_artifact_id D2-006" in error for error in errors)
    assert any("d2_006_gates requires expectation_source_artifact_path" in error for error in errors)


def test_retrospective_flag_true_without_disclosure_fails(tmp_path):
    payload = _base_rec()
    del payload["retrospective_disclosure"]

    errors = _validate(tmp_path, payload)

    assert any("'retrospective_disclosure' is a required property" in error for error in errors)


def test_realized_metric_mismatch_fails(tmp_path):
    payload = _base_rec()
    payload["realized_metrics"]["sharpe"] = 9.9

    errors = _validate(tmp_path, payload)

    assert any("realized_metrics.sharpe" in error and "does not match" in error for error in errors)


def test_linked_ref_checks_fail_for_unresolved_known_refs(tmp_path):
    payload = _base_rec()
    payload["linked_advisory_artifacts"] = ["PGAS-9999"]
    payload["linked_lifecycle_artifacts"] = ["LCH-9999"]

    errors = _validate(tmp_path, payload)

    assert any("linked_advisory_artifacts unresolved PGAS reference: PGAS-9999" in error for error in errors)
    assert any("linked_lifecycle_artifacts unresolved LCH reference: LCH-9999" in error for error in errors)


def test_clear_overall_verdict_mismatch_fails(tmp_path):
    payload = _base_rec()
    payload["overall_verdict"] = "all_met"

    errors = _validate(tmp_path, payload)

    assert any("overall_verdict all_met does not match" in error for error in errors)
