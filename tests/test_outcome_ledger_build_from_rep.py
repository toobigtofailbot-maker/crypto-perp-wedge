import json
from pathlib import Path

import pytest

from tools.outcome_ledger import build_from_rep as helper
from tools.registry.validate_outcome_ledger import validate_outcome_ledgers
from tools.research_query import query_layer


FIXED_TIMESTAMP = "2026-05-04T20:00:00Z"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _base_kwargs(**overrides):
    kwargs = {
        "outcome_id": "OL-9001",
        "rep_id": "REP-0002",
        "rep_path": "research/experiments/REP-0002.report.json",
        "exp_id": "EXP-0002",
        "exp_path": "research/experiments/EXP-0002.plan.json",
        "candidate_id": "H-001",
        "pipeline_version": "pre_wp_5b",
        "derivation_timestamp": FIXED_TIMESTAMP,
    }
    kwargs.update(overrides)
    return kwargs


def _cli_args(**overrides):
    kwargs = _base_kwargs(**overrides)
    return [
        "--outcome-id",
        kwargs["outcome_id"],
        "--rep-id",
        kwargs["rep_id"],
        "--rep-path",
        kwargs["rep_path"],
        "--exp-id",
        kwargs["exp_id"],
        "--exp-path",
        kwargs["exp_path"],
        "--candidate-id",
        kwargs["candidate_id"],
        "--pipeline-version",
        kwargs["pipeline_version"],
        "--derivation-timestamp",
        kwargs["derivation_timestamp"],
    ]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_registry(path: Path, candidate_id: str = "H-901") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"candidate_id": candidate_id}) + "\n", encoding="utf-8")


def _write_temp_rep_exp(tmp_path: Path, *, include_oos: bool = True) -> tuple[Path, Path, Path]:
    repo_root = tmp_path
    registry_path = repo_root / "research" / "candidate_registry.jsonl"
    rep_path = repo_root / "research" / "experiments" / "REP-9001.report.json"
    exp_path = repo_root / "research" / "experiments" / "EXP-9001.plan.json"
    _write_registry(registry_path)
    _write_json(
        exp_path,
        {
            "plan_id": "EXP-9001",
            "candidate_id": "H-901",
            "data_requirements": ["pytest data ref"],
        },
    )
    rep_payload = {
        "report_id": "REP-9001",
        "plan_id": "EXP-9001",
        "candidate_id": "H-901",
        "metrics": {},
    }
    if include_oos:
        rep_payload["metrics"]["out_of_sample"] = {
            "source_field": "metrics.out_of_sample",
            "window_convention": "pytest",
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
    _write_json(rep_path, rep_payload)
    return repo_root, registry_path, rep_path


def test_builds_h001_candidate_matching_committed_key_fields():
    payload = helper.build_outcome_payload(**_base_kwargs())
    committed = _load_json(helper.REPO_ROOT / "research" / "outcome_ledgers" / "OL-0001.outcome_ledger.json")

    assert payload["outcome_id"] == "OL-9001"
    assert payload["candidate_id"] == committed["candidate_id"] == "H-001"
    assert payload["pipeline_version"] == committed["pipeline_version"] == "pre_wp_5b"
    assert payload["evaluation_window_start"] is None
    assert payload["evaluation_window_end"] is None
    assert payload["metrics"] == committed["metrics"]
    assert payload["data_provenance"]["source_data_refs"] == committed["data_provenance"]["source_data_refs"]
    assert payload["linked_artifacts"] == ["EXP-0002", "REP-0002"]
    assert payload["derivation_record"]["source_artifact_id"] == "REP-0002"
    assert payload["derivation_record"]["source_artifact_path"] == "research/experiments/REP-0002.report.json"
    assert payload["derivation_record"]["derivation_timestamp"] == FIXED_TIMESTAMP


def test_builds_h004_post_wp5b_and_preserves_optional_diagnostics():
    payload = helper.build_outcome_payload(
        **_base_kwargs(
            outcome_id="OL-9002",
            rep_id="REP-0011",
            rep_path="research/experiments/REP-0011.report.json",
            exp_id="EXP-0011",
            exp_path="research/experiments/EXP-0011.plan.json",
            candidate_id="H-004",
            pipeline_version="post_wp_5b",
        )
    )
    source_oos = _load_json(helper.REPO_ROOT / "research" / "experiments" / "REP-0011.report.json")["metrics"][
        "out_of_sample"
    ]

    for field in {
        "trial_count_before_append",
        "trial_count_after_append",
        "config_sha256",
        "dataset_sha256",
        "max_drawdown_peak",
        "max_drawdown_trough",
        "skipped_bars",
        "sensitivity_min_ratio",
        "short_side_trades",
        "short_side_net_pnl",
        "long_side_trades",
        "long_side_net_pnl",
    }:
        assert payload["metrics"][field] == source_oos[field]

    assert payload["candidate_id"] == "H-004"
    assert payload["pipeline_version"] == "post_wp_5b"
    assert "H-004 split handling remains explicit" in payload["notes"]


def test_copies_required_metrics_and_source_data_refs_exactly():
    payload = helper.build_outcome_payload(**_base_kwargs())
    rep = _load_json(helper.REPO_ROOT / "research" / "experiments" / "REP-0002.report.json")
    exp = _load_json(helper.REPO_ROOT / "research" / "experiments" / "EXP-0002.plan.json")

    assert payload["metrics"] == rep["metrics"]["out_of_sample"]
    assert payload["data_provenance"]["source_data_refs"] == exp["data_requirements"]


def test_uses_null_windows_and_non_claim_disclosure():
    payload = helper.build_outcome_payload(**_base_kwargs())

    assert payload["evaluation_window_start"] is None
    assert payload["evaluation_window_end"] is None
    assert payload["data_provenance"]["source_data_window_start"] is None
    assert payload["data_provenance"]["source_data_window_end"] is None
    assert payload["retrospective_flag"] is True
    assert "already committed REP-0002 report" in payload["retrospective_disclosure"]
    for phrase in [
        "REP remains the authoritative research record",
        "no promotion",
        "REC/reconciliation",
        "paper/live",
        "runtime",
        "deployment",
        "strategy adjustment",
        "protected-path authority",
    ]:
        assert phrase in payload["retrospective_disclosure"]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("outcome_id", "OL-12", "outcome_id must match OL-NNNN"),
        ("pipeline_version", "future_pipeline", "pipeline_version must be one of"),
        ("candidate_id", "H-999", "candidate_id not found in registry"),
        ("rep_id", "REP-9999", "does not contain report_id REP-9999"),
        ("rep_path", "research/experiments/REP-9999.report.json", "path does not exist"),
        ("exp_id", "EXP-9999", "does not contain plan_id EXP-9999"),
        ("exp_path", "research/experiments/EXP-9999.plan.json", "path does not exist"),
    ],
)
def test_rejects_invalid_inputs(field: str, value: str, message: str):
    with pytest.raises(ValueError, match=message):
        helper.build_outcome_payload(**_base_kwargs(**{field: value}))


def test_rejects_missing_required_oos_metrics(tmp_path):
    repo_root, registry_path, _ = _write_temp_rep_exp(tmp_path, include_oos=False)

    with pytest.raises(ValueError, match="REP metrics.out_of_sample is required"):
        helper.build_outcome_payload(
            outcome_id="OL-9001",
            rep_id="REP-9001",
            rep_path="research/experiments/REP-9001.report.json",
            exp_id="EXP-9001",
            exp_path="research/experiments/EXP-9001.plan.json",
            candidate_id="H-901",
            pipeline_version="pre_wp_5b",
            derivation_timestamp=FIXED_TIMESTAMP,
            repo_root=repo_root,
            registry_path=registry_path,
        )


def test_rejects_missing_required_oos_metric_field(tmp_path):
    repo_root, registry_path, rep_path = _write_temp_rep_exp(tmp_path)
    rep = _load_json(rep_path)
    del rep["metrics"]["out_of_sample"]["sharpe"]
    _write_json(rep_path, rep)

    with pytest.raises(ValueError, match="missing required fields: sharpe"):
        helper.build_outcome_payload(
            outcome_id="OL-9001",
            rep_id="REP-9001",
            rep_path="research/experiments/REP-9001.report.json",
            exp_id="EXP-9001",
            exp_path="research/experiments/EXP-9001.plan.json",
            candidate_id="H-901",
            pipeline_version="pre_wp_5b",
            derivation_timestamp=FIXED_TIMESTAMP,
            repo_root=repo_root,
            registry_path=registry_path,
        )


def test_validation_against_temp_corpus_passes():
    payload = helper.build_outcome_payload(**_base_kwargs())

    assert helper.validate_candidate_against_corpus(payload) == []


def test_validation_against_temp_validator_passes(tmp_path):
    payload = helper.build_outcome_payload(**_base_kwargs())
    outcome_ledgers_dir = tmp_path / "outcome_ledgers"
    _write_json(outcome_ledgers_dir / "OL-9001.outcome_ledger.json", payload)

    errors = validate_outcome_ledgers(outcome_ledgers_dir=outcome_ledgers_dir)

    assert errors == []


def test_generated_temp_artifact_has_empty_query_integrity_views(monkeypatch, tmp_path):
    payload = helper.build_outcome_payload(**_base_kwargs())
    outcome_ledgers_dir = tmp_path / "outcome_ledgers"
    _write_json(outcome_ledgers_dir / "OL-9001.outcome_ledger.json", payload)
    monkeypatch.setattr(query_layer, "OUTCOME_LEDGERS_DIR", outcome_ledgers_dir)

    connection = query_layer.init_duckdb()
    try:
        for view_name in {
            "v_integrity_outcome_ledger_refs",
            "v_integrity_outcome_ledger_window_bounds",
            "v_integrity_outcome_ledger_derivation",
            "v_integrity_outcome_ledger_scope",
        }:
            assert connection.execute(f'SELECT * FROM "{view_name}"').fetchall() == []
    finally:
        connection.close()


def test_cli_stdout_writes_json_without_creating_file(capsys):
    exit_code = helper.run(_cli_args() + ["--stdout"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["outcome_id"] == "OL-9001"
    assert payload["derivation_record"]["source_artifact_id"] == "REP-0002"
    assert "Validation: PASS" in captured.err


def test_cli_output_writes_file(tmp_path, capsys):
    output_path = tmp_path / "candidate.json"

    exit_code = helper.run(_cli_args() + ["--output", str(output_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8"))["outcome_id"] == "OL-9001"
    assert "Wrote validated outcome ledger candidate" in captured.out


def test_cli_invalid_input_returns_nonzero_and_stable_error(capsys):
    exit_code = helper.run(_cli_args(outcome_id="OL-12") + ["--stdout"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ERROR: outcome_id must match OL-NNNN" in captured.err


def test_cli_refuses_to_overwrite_existing_output_file(tmp_path, capsys):
    output_path = tmp_path / "candidate.json"
    output_path.write_text("already here\n", encoding="utf-8")

    exit_code = helper.run(_cli_args() + ["--output", str(output_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ERROR: refusing to overwrite existing file" in captured.err
    assert output_path.read_text(encoding="utf-8") == "already here\n"

