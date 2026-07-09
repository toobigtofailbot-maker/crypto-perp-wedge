from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tests.test_agent_formalizer_runner_bridge import _run_product
from tools.lab_pipeline.adapter_contract import RUNNER_ADAPTER_PACKAGE_ID, build_adapter_registry
from tools.lab_pipeline import runner_adapter
from tools.lab_pipeline.runner_adapter import (
    FALSE_AUTHORITY_FLAGS,
    RUNNER_ADAPTER_STAGE_IDENTITY,
    RunnerAdapterError,
    approval_template,
    run_product_runner_adapter,
)
from tools.lab_pipeline.state import file_sha256, read_json, write_json


def _configure_temp_repo(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    output_root = tmp_path / "scratch" / runner_adapter.WP_ID / "outputs"
    monkeypatch.setattr(runner_adapter, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(runner_adapter, "DEFAULT_OUTPUT_ROOT", output_root)
    return output_root


def _prepared_bridge_packet(tmp_path: Path) -> tuple[dict, dict]:
    result, _sink = _run_product(tmp_path)
    review = read_json(tmp_path / result["artifact_paths"]["human_review_packet"])
    return result, review


def _write_execute_approval(
    tmp_path: Path,
    output_root: Path,
    bridge_result: dict,
    bridge_review: dict,
    max_variant_count: int | None = None,
    **overrides: object,
) -> Path:
    metadata = bridge_review["product_bridge_preparation_metadata"]
    payload = approval_template(
        prepared_strategy_spec_path=bridge_result["artifact_paths"]["strategy_spec"],
        prepared_variant_manifest_path=bridge_result["artifact_paths"]["variant_manifest"],
        prepared_sweep_plan_path=bridge_result["artifact_paths"]["sweep_plan"],
        bridge_preparation_run_id=bridge_result["run_id"],
        product_pipeline_run_id=metadata["product_pipeline_run_id"],
        output_root=output_root,
        max_variant_count=max_variant_count,
    )
    payload.update(overrides)
    return Path(write_json(output_root / "karl_runner_execute_approval.json", payload))


def _run_valid_adapter(
    tmp_path: Path,
    output_root: Path,
    bridge_result: dict,
    bridge_review: dict,
    approval_path: Path,
):
    return run_product_runner_adapter(
        prepared_strategy_spec_path=bridge_result["artifact_paths"]["strategy_spec"],
        prepared_variant_manifest_path=bridge_result["artifact_paths"]["variant_manifest"],
        prepared_sweep_plan_path=bridge_result["artifact_paths"]["sweep_plan"],
        bridge_preparation_run_id=bridge_result["run_id"],
        product_pipeline_run_id=bridge_review["product_bridge_preparation_metadata"][
            "product_pipeline_run_id"
        ],
        execute_approval_path=approval_path,
        output_root=output_root,
    )


def _rewrite_prepared_denominator(tmp_path: Path, bridge_result: dict, count: int) -> list[str]:
    variant_ids = [f"VAR-{index:06d}" for index in range(1, count + 1)]
    manifest_path = tmp_path / bridge_result["artifact_paths"]["variant_manifest"]
    sweep_path = tmp_path / bridge_result["artifact_paths"]["sweep_plan"]
    manifest = read_json(manifest_path)
    sweep = read_json(sweep_path)
    template = copy.deepcopy(manifest["variant_assignments"][0])
    assignments = []
    for index, variant_id in enumerate(variant_ids, start=1):
        row = copy.deepcopy(template)
        row["variant_id"] = variant_id
        row["parameter_values"] = {"synthetic_index": index}
        row["lineage"] = {"generated_by_rule": "synthetic-scale-fixture", "generation_order": index}
        assignments.append(row)
    manifest["variant_assignments"] = assignments
    manifest["population_governance"]["population_cap"]["max_variants"] = count
    declared = manifest["population_governance"]["declared_population"]
    declared["committed_population_count"] = count
    declared["declared_variant_count"] = count
    declared["included_variant_count"] = count
    declared["excluded_variant_count"] = 0
    declared["invalid_variant_count"] = 0
    declared["not_attempted_variant_count"] = 0
    trial_budget = manifest["population_governance"]["trial_budget"]
    trial_budget["planned_trial_count"] = count
    trial_budget["trial_budget_denominator"] = count
    trial_budget["denominator_count"] = count
    sweep["parent_variant_manifest"]["manifest_population_count"] = count
    sweep["parent_variant_manifest"]["manifest_committed_population_count"] = count
    sweep["parent_variant_manifest"]["manifest_population_cap"] = count
    sweep["test_selection"]["selection_mode"] = "all_manifest_variants"
    sweep["test_selection"]["selected_variant_ids"] = variant_ids
    sweep["test_selection"]["excluded_variant_ids"] = []
    accounting = sweep["trial_accounting"]
    accounting["committed_population_count"] = count
    accounting["selected_variant_count"] = count
    accounting["executed_variant_count"] = 0
    accounting["successful_variant_count"] = 0
    accounting["failed_variant_count"] = 0
    accounting["errored_variant_count"] = 0
    accounting["aborted_variant_count"] = 0
    accounting["filtered_variant_count"] = 0
    accounting["data_unavailable_variant_count"] = 0
    accounting["excluded_variant_count"] = 0
    accounting["not_attempted_variant_count"] = count
    accounting["multiple_testing_denominator"] = count
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sweep_path.write_text(json.dumps(sweep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return variant_ids


def _fake_runner_result(output_dir: Path, rows: list[dict]) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "result_population_id": "RP-TEST",
        "variant_result_rows": rows,
    }
    path = output_dir / "RP-TEST.result_population.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["outcome_category"]] = counts.get(row["outcome_category"], 0) + 1
    return {
        "ok": True,
        "output_path": str(path),
        "result_population": copy.deepcopy(payload),
        "outcome_category_counts": counts,
    }


def test_runner_adapter_registry_is_implemented_only_for_runner_package() -> None:
    old_registry = {record.stage: record for record in build_adapter_registry("WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02")}
    new_registry = {record.stage: record for record in build_adapter_registry(RUNNER_ADAPTER_PACKAGE_ID)}

    assert old_registry["noncanonical_offline_runner_execution"].implementation_status == "blocked"
    assert new_registry["noncanonical_offline_runner_execution"].implementation_status == "implemented"
    assert new_registry["noncanonical_offline_runner_execution"].blocker_reason is None


def test_valid_execute_approval_invokes_existing_runner_and_reconciles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_root = _configure_temp_repo(monkeypatch, tmp_path)
    bridge_result, bridge_review = _prepared_bridge_packet(tmp_path)
    approval_path = _write_execute_approval(
        tmp_path, output_root, bridge_result, bridge_review
    )

    result = _run_valid_adapter(
        tmp_path, output_root, bridge_result, bridge_review, approval_path
    )

    summary = read_json(tmp_path / result.artifact_paths["runner_adapter_result"])
    adapter_path = tmp_path / result.artifact_paths["adapter_result_population"]
    direct_path = tmp_path / result.artifact_paths["direct_result_population"]
    assert result.adapter_status == "completed"
    assert adapter_path.is_file()
    assert direct_path.is_file()
    assert file_sha256(adapter_path) == file_sha256(direct_path)
    assert result.reconciliation["verdict"] == "passed"
    assert result.reconciliation["raw_byte_hash_match"] is True
    assert summary["runner_code_ref"] == runner_adapter.RUNNER_CODE_REF
    assert summary["runner_reimplemented"] is False
    assert summary["noncanonical_status"] == "noncanonical_product_scratch_only"
    assert summary["approved_sweep_budget"]["schema_version"] == "product_runner_approved_sweep_budget_v1"
    assert summary["approved_sweep_budget"]["committed_population_count"] == 8
    assert summary["approved_sweep_budget"]["max_variant_count"] == 8
    assert summary["largest_tested_denominator"] == 8
    assert summary["budget_exceeded"] is False
    assert summary["full_denominator_preserved"] is True
    assert summary["winner_narrowing"] is False
    assert str(adapter_path).startswith(str(output_root))
    assert not (tmp_path / "research" / "result_populations").exists()
    assert result.audit_records[0]["action_type"] == "noncanonical_offline_sweep_run"
    assert result.audit_records[0]["decision"] == "allowed"


@pytest.mark.parametrize(
    ("approval_overrides", "expected_error"),
    [
        ({"approved_by": "operator"}, "execute_approval_mismatch:approved_by"),
        ({"approval_scope": "noncanonical_offline_research_execution_only"}, "approval_scope"),
        ({"approval_statement": "Approve broad prereg packet."}, "approval_statement"),
        ({"approval_timestamp_utc": "not-a-time"}, "timestamp"),
        ({"prepared_strategy_spec_sha256": "sha256:" + "0" * 64}, "prepared_strategy_spec_sha256"),
        ({"prepared_variant_manifest_sha256": "sha256:" + "0" * 64}, "prepared_variant_manifest_sha256"),
        ({"prepared_sweep_plan_sha256": "sha256:" + "0" * 64}, "prepared_sweep_plan_sha256"),
        ({"bridge_preparation_run_id": "other-bridge-run"}, "bridge_preparation_run_id"),
        ({"product_pipeline_run_id": "other-pipeline-run"}, "product_pipeline_run_id"),
        ({"runner_adapter_stage_identity": "candidate_review"}, "runner_adapter_stage_identity"),
        ({"product_output_root": "scratch/other/outputs"}, "product_output_root"),
        ({"approved_sweep_budget": None}, "approved_sweep_budget"),
        ({"authorizes_runner_execution": False}, "authorizes_runner_execution"),
    ],
)
def test_invalid_execute_approval_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    approval_overrides: dict[str, object],
    expected_error: str,
) -> None:
    output_root = _configure_temp_repo(monkeypatch, tmp_path)
    bridge_result, bridge_review = _prepared_bridge_packet(tmp_path)
    approval_path = _write_execute_approval(
        tmp_path,
        output_root,
        bridge_result,
        bridge_review,
        **approval_overrides,
    )

    with pytest.raises(RunnerAdapterError, match=expected_error):
        _run_valid_adapter(tmp_path, output_root, bridge_result, bridge_review, approval_path)
    assert not list(output_root.rglob("*.result_population.json"))


@pytest.mark.parametrize("flag", FALSE_AUTHORITY_FLAGS)
def test_any_unauthorized_execute_authority_flag_true_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, flag: str
) -> None:
    output_root = _configure_temp_repo(monkeypatch, tmp_path)
    bridge_result, bridge_review = _prepared_bridge_packet(tmp_path)
    approval_path = _write_execute_approval(
        tmp_path,
        output_root,
        bridge_result,
        bridge_review,
        **{flag: True},
    )

    with pytest.raises(RunnerAdapterError, match=flag):
        _run_valid_adapter(tmp_path, output_root, bridge_result, bridge_review, approval_path)
    assert not list(output_root.rglob("*.result_population.json"))


def test_prepare_approval_and_broad_prereg_approval_are_not_execute_approval(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_root = _configure_temp_repo(monkeypatch, tmp_path)
    bridge_result, bridge_review = _prepared_bridge_packet(tmp_path)
    prepare_approval = Path(
        bridge_review["product_bridge_preparation_metadata"]["approval_marker_path"]
    )
    broad_prereg = Path(
        write_json(
            output_root / "pipeline_prereg_approval.json",
            {
                "schema_version": "lab_pipeline_prereg_approval_v1",
                "approved_by": "Karl",
                "approval_scope": "noncanonical_offline_research_execution_only",
                "approval_statement": "Authorizes broad prereg packet.",
                "approval_timestamp_utc": "2026-07-08T00:00:00Z",
            },
        )
    )

    with pytest.raises(RunnerAdapterError, match="schema_version"):
        _run_valid_adapter(tmp_path, output_root, bridge_result, bridge_review, prepare_approval)
    with pytest.raises(RunnerAdapterError, match="schema_version"):
        _run_valid_adapter(tmp_path, output_root, bridge_result, bridge_review, broad_prereg)


def test_denominator_status_mapping_preserves_all_runner_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_root = _configure_temp_repo(monkeypatch, tmp_path)
    bridge_result, bridge_review = _prepared_bridge_packet(tmp_path)
    _rewrite_prepared_denominator(tmp_path, bridge_result, count=5)
    approval_path = _write_execute_approval(
        tmp_path, output_root, bridge_result, bridge_review
    )

    rows = [
        {"variant_id": "VAR-000001", "outcome_category": "successful"},
        {"variant_id": "VAR-000002", "outcome_category": "failed"},
        {"variant_id": "VAR-000003", "outcome_category": "invalid"},
        {"variant_id": "VAR-000004", "outcome_category": "excluded"},
        {"variant_id": "VAR-000005", "outcome_category": "data_unavailable"},
    ]
    payload = {
        "result_population_id": "RP-TEST",
        "variant_result_rows": rows,
    }

    def fake_runner(*_args: object, output_dir: Path, **_kwargs: object) -> dict:
        return _fake_runner_result(output_dir, rows)

    monkeypatch.setattr(runner_adapter, "run_offline_sweep", fake_runner)

    result = _run_valid_adapter(
        tmp_path, output_root, bridge_result, bridge_review, approval_path
    )

    assert result.denominator_counts == {
        "completed": 1,
        "failed": 1,
        "invalid": 1,
        "blocked": 1,
        "pruned": 1,
    }
    summary = read_json(tmp_path / result.artifact_paths["runner_adapter_result"])
    assert summary["denominator_counts"] == result.denominator_counts
    assert summary["winner_narrowing"] is False


def test_large_bounded_synthetic_sweep_preserves_full_denominator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_root = _configure_temp_repo(monkeypatch, tmp_path)
    bridge_result, bridge_review = _prepared_bridge_packet(tmp_path)
    variant_ids = _rewrite_prepared_denominator(tmp_path, bridge_result, count=1000)
    approval_path = _write_execute_approval(
        tmp_path,
        output_root,
        bridge_result,
        bridge_review,
        max_variant_count=1000,
    )
    outcomes = ("successful", "failed", "invalid", "excluded", "not_attempted")
    rows = [
        {"variant_id": variant_id, "outcome_category": outcomes[index % len(outcomes)]}
        for index, variant_id in enumerate(variant_ids)
    ]

    def fake_runner(*_args: object, output_dir: Path, **_kwargs: object) -> dict:
        return _fake_runner_result(output_dir, rows)

    monkeypatch.setattr(runner_adapter, "run_offline_sweep", fake_runner)

    result = _run_valid_adapter(
        tmp_path, output_root, bridge_result, bridge_review, approval_path
    )

    summary = read_json(tmp_path / result.artifact_paths["runner_adapter_result"])
    assert result.denominator_counts == {
        "completed": 200,
        "failed": 200,
        "invalid": 200,
        "blocked": 200,
        "pruned": 200,
    }
    assert summary["approved_sweep_budget"]["committed_population_count"] == 1000
    assert summary["approved_sweep_budget"]["within_approved_budget"] is True
    assert summary["largest_tested_denominator"] == 1000
    assert summary["full_denominator_preserved"] is True
    assert summary["winner_narrowing"] is False
    assert summary["budget_exceeded"] is False


def test_budget_exceeded_fails_closed_before_runner_invocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_root = _configure_temp_repo(monkeypatch, tmp_path)
    bridge_result, bridge_review = _prepared_bridge_packet(tmp_path)
    _rewrite_prepared_denominator(tmp_path, bridge_result, count=9)
    approval_path = _write_execute_approval(
        tmp_path,
        output_root,
        bridge_result,
        bridge_review,
        max_variant_count=9,
    )
    approval = read_json(approval_path)
    approval["approved_sweep_budget"]["max_variant_count"] = 8
    write_json(approval_path, approval)

    def fail_runner(*_args: object, **_kwargs: object) -> dict:
        raise AssertionError("runner must not be invoked when budget is exceeded")

    monkeypatch.setattr(runner_adapter, "run_offline_sweep", fail_runner)

    with pytest.raises(RunnerAdapterError, match="sweep budget exceeded"):
        _run_valid_adapter(tmp_path, output_root, bridge_result, bridge_review, approval_path)
    assert not list(output_root.rglob("*.result_population.json"))


def test_runner_row_shrinkage_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_root = _configure_temp_repo(monkeypatch, tmp_path)
    bridge_result, bridge_review = _prepared_bridge_packet(tmp_path)
    variant_ids = _rewrite_prepared_denominator(tmp_path, bridge_result, count=6)
    approval_path = _write_execute_approval(
        tmp_path, output_root, bridge_result, bridge_review
    )
    rows = [
        {"variant_id": variant_id, "outcome_category": "successful"}
        for variant_id in variant_ids[:-1]
    ]

    def fake_runner(*_args: object, output_dir: Path, **_kwargs: object) -> dict:
        return _fake_runner_result(output_dir, rows)

    monkeypatch.setattr(runner_adapter, "run_offline_sweep", fake_runner)

    with pytest.raises(RunnerAdapterError, match="row count"):
        _run_valid_adapter(tmp_path, output_root, bridge_result, bridge_review, approval_path)


def test_output_root_must_be_product_runner_scratch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _configure_temp_repo(monkeypatch, tmp_path)
    bridge_result, bridge_review = _prepared_bridge_packet(tmp_path)
    bad_root = tmp_path / "scratch" / "OTHER" / "outputs"

    with pytest.raises(RunnerAdapterError, match="product runner output_root"):
        approval_template(
            prepared_strategy_spec_path=bridge_result["artifact_paths"]["strategy_spec"],
            prepared_variant_manifest_path=bridge_result["artifact_paths"]["variant_manifest"],
            prepared_sweep_plan_path=bridge_result["artifact_paths"]["sweep_plan"],
            bridge_preparation_run_id=bridge_result["run_id"],
            product_pipeline_run_id=bridge_review["product_bridge_preparation_metadata"][
                "product_pipeline_run_id"
            ],
            output_root=bad_root,
        )


def test_execute_approval_template_binds_runner_stage_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_root = _configure_temp_repo(monkeypatch, tmp_path)
    bridge_result, bridge_review = _prepared_bridge_packet(tmp_path)
    payload = approval_template(
        prepared_strategy_spec_path=bridge_result["artifact_paths"]["strategy_spec"],
        prepared_variant_manifest_path=bridge_result["artifact_paths"]["variant_manifest"],
        prepared_sweep_plan_path=bridge_result["artifact_paths"]["sweep_plan"],
        bridge_preparation_run_id=bridge_result["run_id"],
        product_pipeline_run_id=bridge_review["product_bridge_preparation_metadata"][
            "product_pipeline_run_id"
        ],
        output_root=output_root,
    )

    assert payload["runner_adapter_stage_identity"] == RUNNER_ADAPTER_STAGE_IDENTITY
    assert payload["authorizes_runner_execution"] is True
    assert all(payload[field] is False for field in FALSE_AUTHORITY_FLAGS)
