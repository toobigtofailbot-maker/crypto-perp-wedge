import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

from tests.test_validate_strategy_specs import _base_strategy_spec as _strategy_spec_fixture
from tests.test_validate_variant_sweep_artifacts import (
    _base_sweep_plan as _sweep_plan_fixture,
    _base_variant_manifest as _variant_manifest_fixture,
    _base_strategy_spec_for_variant,
)
from tools.registry.validate_result_populations import (
    DEFAULT_RESULT_POPULATION_SCHEMA_PATH,
    DEFAULT_STRATEGY_SPEC_SCHEMA_PATH,
    DEFAULT_SWEEP_PLAN_SCHEMA_PATH,
    DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH,
    OUTCOME_CATEGORIES,
    _hash_scope_payload,
    main,
    sha256_prefixed,
    validate_result_populations,
)


def _load_schema(path: Path = DEFAULT_RESULT_POPULATION_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _sha256_prefixed(value: object) -> str:
    return sha256_prefixed(value)


def _canonical_hash(payload: dict, scope: list[str]) -> str:
    scoped = _hash_scope_payload(payload, scope)
    assert scoped is not None
    return _sha256_prefixed(scoped)


def _refresh_identity_hashes(payload: dict) -> None:
    payload["input_identity_hash"]["hash"] = _canonical_hash(
        payload,
        payload["input_identity_hash"]["hash_scope"],
    )
    payload["lineage"]["parent_hash_chain"]["input_identity_hash"] = payload["input_identity_hash"]["hash"]
    payload["result_population_identity_hash"]["hash"] = _canonical_hash(
        payload,
        payload["result_population_identity_hash"]["hash_scope"],
    )


def _add_sizing_metadata(payload: dict, sizing_metadata: dict) -> None:
    payload["sizing_metadata"] = sizing_metadata
    for identity_key in ("input_identity_hash", "result_population_identity_hash"):
        scope = payload[identity_key]["hash_scope"]
        if "sizing_metadata" not in scope:
            scope.insert(scope.index("backtest_assumption_summary"), "sizing_metadata")
    _refresh_identity_hashes(payload)


def _base_strategy_spec(strategy_spec_id: str = "STRAT-SPEC-9001") -> dict:
    return _base_strategy_spec_for_variant(strategy_spec_id)


def _base_variant_manifest(parent_hash: str) -> dict:
    return _variant_manifest_fixture(parent_hash)


def _base_sweep_plan(manifest: dict) -> dict:
    return _sweep_plan_fixture(manifest)


def _true_flags(*names: str) -> dict:
    return {name: True for name in names}


def _row(
    row_number: int,
    variant_id: str,
    outcome_category: str = "successful",
) -> dict:
    successful = outcome_category == "successful"
    row = {
        "variant_id": variant_id,
        "row_id": f"RP-0001-ROW-{row_number:06d}",
        "row_identity_hash": None,
        "assignment_hash": None,
        "assignment_ref": None,
        "outcome_category": outcome_category,
        "attempted": successful,
        "metrics": {
            "pnl": 1.0 if successful else None,
            "return_pct": 0.01 if successful else None,
            "drawdown": 0.02 if successful else None,
            "trade_count": 1 if successful else None,
            "win_rate": 1.0 if successful else None,
            "sharpe": 0.5 if successful else None,
            "fees": 0.1 if successful else None,
            "funding": 0.0 if successful else None,
            "slippage": 0.0 if successful else None,
            "exposure": 1.0 if successful else None,
        },
        "non_success": {
            "reason": None if successful else "fixture non-success",
            "rule_ref": None,
            "declared_before_results": None if successful else True,
            "counts_in_denominator": True,
        },
        "error": {
            "error_category": None,
            "error_message_class": None,
            "is_infrastructure_error": None,
            "is_strategy_underperformance": None,
            "counts_in_denominator": True,
        },
        "data_coverage": {
            "data_catalog_ref": "docs/data_catalog.md",
            "data_slice_identity": "pytest-slice",
            "timeframe": "1h",
            "data_stream": "ohlcv",
            "missing_data_policy": "block_if_missing",
            "irreparable_gap": False,
            "counts_in_denominator": True,
        },
        "backtest_assumption_ref": None,
        "lineage": {
            "parent_variant_id": variant_id,
            "parent_variant_assignment_hash": None,
            "parent_variant_assignment_ref": None,
            "parent_sweep_plan_id": "SWEEP-PLAN-0001",
            "parent_manifest_id": "VM-0001",
        },
        "row_mutation_policy": _true_flags(
            "scientific_row_identity_immutable_after_commit",
            "corrections_require_append_only_event",
            "post_commit_in_place_mutation_forbidden",
            "post_hoc_cleanup_forbidden",
        ),
    }
    return row


def _base_result_population(
    strategy_hash: str,
    manifest: dict,
    sweep_plan: dict,
    status: str = "generated",
) -> dict:
    manifest_hash = manifest["manifest_hash_pinning"]["manifest_hash"]
    sweep_hash = _sha256_prefixed(sweep_plan)
    rows = [_row(1, "VAR-000001", "successful"), _row(2, "VAR-000002", "failed")]
    counts = {category: 0 for category in OUTCOME_CATEGORIES}
    counts["successful"] = 1
    counts["failed"] = 1
    counts["counts_sum"] = 2
    counts["counts_sum_equals_committed_denominator"] = True
    payload = {
        "schema_version": "v1",
        "result_population_id": "RP-0001",
        "status": status,
        "non_authority_declaration": {
            **_true_flags(
                "not_executable",
                "not_runner_authority",
                "not_sweep_authority",
                "not_result_authority",
                "not_candidate_approval",
                "not_exp_approval",
                "not_ranking_authority",
                "not_recommendation_authority",
                "not_readiness_authority",
                "not_transition_authority",
                "not_runtime_authority",
                "not_paper_live_authority",
                "not_gate_authority",
                "not_canonical_evidence_replacement",
                "not_trial_log_replacement",
                "not_outcome_ledger_replacement",
                "not_reconciliation_authority",
                "not_decision_authority",
                "not_exp_replacement",
                "not_rep_replacement",
                "not_ol_replacement",
                "not_rec_replacement",
                "not_dec_replacement",
            ),
            "canonical_evidence_relationship": "reference_only",
        },
        "parent_strategy_spec": {
            "strategy_spec_id": "STRAT-SPEC-9001",
            "strategy_spec_schema_version": "v1",
            "strategy_spec_hash": strategy_hash,
            "hash_algorithm": "sha256",
            "hash_scope_version": "strategy_spec_hash_scope_v1",
            "strategy_spec_ref": None,
            "mismatch_policy": "block",
            "missing_parent_policy": "block",
        },
        "parent_variant_manifest": {
            "variant_manifest_id": "VM-0001",
            "variant_manifest_schema_version": "v1",
            "manifest_hash": manifest_hash,
            "hash_algorithm": "sha256",
            "hash_scope_version": "variant_manifest_hash_scope_v1",
            "manifest_ref": None,
            "manifest_pre_registration_status": "frozen_for_sweep_planning",
            "committed_population_count": 2,
            "mismatch_policy": "block",
            "missing_manifest_policy": "block",
        },
        "parent_sweep_plan": {
            "sweep_plan_id": "SWEEP-PLAN-0001",
            "sweep_plan_schema_version": "v1",
            "sweep_plan_identity_hash": sweep_hash,
            "hash_algorithm": "sha256",
            "hash_scope_version": "sweep_plan_identity_hash_scope_v1",
            "sweep_plan_ref": None,
            "manifest_id": "VM-0001",
            "manifest_hash": manifest_hash,
            "committed_population_count": 2,
            "selected_variant_count": 2,
            "mismatch_policy": "block",
            "missing_sweep_plan_policy": "block",
        },
        "execution_context": {
            "runner_id": None,
            "runner_version": None,
            "runner_code_ref": "future-offline-runner",
            "repo_commit": "pytest",
            "environment_summary": [],
            "dependency_summary": [],
            "determinism_seed": 7,
            "execution_mode": "offline_research",
            "offline_only": True,
            "no_runtime_contact": True,
            "no_paper_live_contact": True,
            "no_broker_exchange_order_contact": True,
            "no_protected_path_contact": True,
        },
        "input_identity_hash": {
            "hash": None,
            "hash_algorithm": "sha256",
            "canonicalization": "json_canonical_v1",
            "hash_scope_version": "input_identity_hash_scope_v1",
            "hash_scope": [
                "parent_strategy_spec.strategy_spec_hash",
                "parent_variant_manifest.manifest_hash",
                "parent_sweep_plan.sweep_plan_identity_hash",
                "parent_variant_manifest.committed_population_count",
                "parent_sweep_plan.committed_population_count",
                "execution_context.runner_code_ref",
                "execution_context.repo_commit",
                "data_coverage_summary.data_catalog_ref",
                "data_coverage_summary.data_slice_identity",
                "backtest_assumption_summary",
            ],
            "audit_envelope_excluded": True,
            "audit_envelope_exclusion_reason": (
                "administrative_audit_metadata_is_excluded_from_scientific_identity"
            ),
        },
        "result_population_identity_hash": {
            "hash": None,
            "hash_algorithm": "sha256",
            "canonicalization": "json_canonical_v1",
            "hash_scope_version": "result_population_identity_hash_scope_v1",
            "hash_scope": [
                "parent_strategy_spec.strategy_spec_hash",
                "parent_variant_manifest.manifest_hash",
                "parent_sweep_plan.sweep_plan_identity_hash",
                "parent_variant_manifest.committed_population_count",
                "parent_sweep_plan.committed_population_count",
                "execution_context.runner_code_ref",
                "execution_context.repo_commit",
                "data_coverage_summary.data_catalog_ref",
                "data_coverage_summary.data_slice_identity",
                "backtest_assumption_summary",
                "committed_denominator_snapshot",
                "variant_result_rows",
                "outcome_category_counts",
                "append_only_ledger.creation_event_ref",
                "validation_summary.validator_identity",
            ],
            "audit_envelope_excluded": True,
            "audit_envelope_exclusion_reason": (
                "administrative_audit_metadata_is_excluded_from_scientific_identity"
            ),
        },
        "audit_envelope": {
            "excluded_from_input_identity_hash": True,
            "excluded_from_result_population_identity_hash": True,
            "may_contain_scientific_content": False,
            "administrative_only": True,
            "created_at": "2026-06-01T00:00:00Z",
            "created_by": "pytest",
            "review_notes": [],
            "operator_notes": [],
            "validation_run_logs": [],
            "administrative_lineage": [],
        },
        "committed_denominator_snapshot": {
            "denominator_basis": "committed_pre_registered_population_count",
            "parent_manifest_committed_population_count": 2,
            "parent_sweep_plan_committed_population_count": 2,
            "selected_variant_count": 2,
            "result_row_count": 2,
            "outcome_counts_sum": 2,
            "committed_denominator": 2,
            **_true_flags(
                "denominator_equals_parent_manifest_committed_population_count",
                "denominator_equals_parent_sweep_plan_committed_population_count",
                "outcome_counts_sum_equals_committed_denominator",
                "result_row_count_equals_committed_denominator",
                "executed_only_denominator_forbidden",
                "successful_only_denominator_forbidden",
                "winner_only_retention_forbidden",
                "post_hoc_cleanup_forbidden",
                "failed_variants_remain_in_denominator",
                "invalid_variants_remain_in_denominator",
                "excluded_variants_remain_in_denominator",
                "errored_variants_remain_in_denominator",
                "aborted_variants_remain_in_denominator",
                "filtered_variants_remain_in_denominator",
                "data_unavailable_variants_remain_in_denominator",
                "not_attempted_variants_remain_in_denominator",
            ),
        },
        "variant_result_rows": rows,
        "outcome_category_counts": counts,
        "append_only_ledger": {
            **_true_flags(
                "ledger_required",
                "append_only",
                "post_commit_in_place_mutation_forbidden",
                "scientific_identity_mutation_forbidden_after_finalization",
                "corrections_require_append_only_event",
                "supersession_preserves_prior_result_population",
            ),
            "creation_event_ref": "RP-0001-EVENT-001",
            "events": [
                {
                    "event_id": "RP-0001-EVENT-001",
                    "event_type": "created",
                    "event_timestamp": "2026-06-01T00:00:00Z",
                    "actor_or_tool": "pytest",
                    "related_artifact_refs": [],
                    "notes": [],
                }
            ],
        },
        "validation_summary": {
            "schema_validation_status": "passed",
            "validator_status": "passed",
            "validator_version": "pytest",
            "validator_identity": "pytest-validator",
            "validation_timestamp": "2026-06-01T00:00:00Z",
            "blocking_errors": [],
            "non_blocking_warnings": [],
            "validator_authority_boundary": "evidence_only_no_approval_no_execution",
            "validator_does_not_approve": True,
            "validator_does_not_recommend": True,
            "validator_does_not_rank": True,
            "validator_does_not_execute": True,
            "validator_does_not_contact_runtime": True,
        },
        "error_summary": {
            "failed": 1,
            "errored": 0,
            "aborted": 0,
            "filtered": 0,
            "data_unavailable": 0,
            "not_attempted": 0,
            "invalid": 0,
            "excluded": 0,
            "all_error_categories_counted_in_denominator": True,
            "error_rows_preserved": True,
        },
        "data_coverage_summary": {
            "data_catalog_ref": "docs/data_catalog.md",
            "data_slice_identity": "pytest-slice",
            "timeframe": "1h",
            "data_stream": "ohlcv",
            "missing_data_policy": "block_if_missing",
            "irreparable_gap_count": 0,
            "data_unavailable_count": 0,
            "data_coverage_notes": [],
        },
        "backtest_assumption_summary": {
            "fee_side_assumption": None,
            "exchange_constraint_disclosure": None,
            "funding_notional": "unspecified",
            "slippage_model": "unspecified",
            "fill_mode": "unspecified",
            "order_size_assumption": None,
            "liquidity_capacity_assumption": None,
            "liquidation_mode": "unspecified",
            "maintenance_margin_assumption": None,
            "mark_price_source": "unspecified",
            "bar_path_assumption": "unspecified",
            "records_assumptions_only": True,
        },
        "lineage": {
            "strategy_spec_id": "STRAT-SPEC-9001",
            "variant_manifest_id": "VM-0001",
            "sweep_plan_id": "SWEEP-PLAN-0001",
            "result_population_id": "RP-0001",
            "parent_hash_chain": {
                "strategy_spec_hash": strategy_hash,
                "variant_manifest_hash": manifest_hash,
                "sweep_plan_identity_hash": sweep_hash,
                "input_identity_hash": None,
            },
            "created_from_validated_inputs": True,
            "complete_population_lineage_preserved": True,
        },
        "review": {
            "review_status": "not_reviewed",
            "review_scope": "none",
            "review_notes": [],
            "non_authority_acknowledgement": _true_flags(
                "not_approval",
                "not_recommendation",
                "not_readiness",
                "not_transition",
                "not_gate_satisfaction",
                "not_runtime_authority",
                "not_paper_live_authority",
            ),
        },
    }
    payload["input_identity_hash"]["hash"] = _canonical_hash(
        payload,
        payload["input_identity_hash"]["hash_scope"],
    )
    payload["lineage"]["parent_hash_chain"]["input_identity_hash"] = payload["input_identity_hash"]["hash"]
    payload["result_population_identity_hash"]["hash"] = _canonical_hash(
        payload,
        payload["result_population_identity_hash"]["hash_scope"],
    )
    return payload


def _fixture_paths(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    root = tmp_path / "research"
    return (
        root / "strategy_specs",
        root / "variant_manifests",
        root / "sweep_plans",
        root / "result_populations",
    )


def _write_valid_fixture(tmp_path: Path) -> tuple[dict, dict, dict, dict, Path, Path, Path, Path]:
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir, result_populations_dir = _fixture_paths(tmp_path)
    strategy_spec = _base_strategy_spec()
    strategy_hash = _sha256_prefixed(strategy_spec)
    manifest = _base_variant_manifest(strategy_hash)
    sweep_plan = _base_sweep_plan(manifest)
    result_population = _base_result_population(strategy_hash, manifest, sweep_plan)
    _write_json(strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json", strategy_spec)
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep_plan)
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)
    return (
        strategy_spec,
        manifest,
        sweep_plan,
        result_population,
        strategy_specs_dir,
        variant_manifests_dir,
        sweep_plans_dir,
        result_populations_dir,
    )


def _validate(tmp_path: Path) -> list[str]:
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir, result_populations_dir = _fixture_paths(tmp_path)
    return validate_result_populations(
        result_populations_dir=result_populations_dir,
        strategy_specs_dir=strategy_specs_dir,
        variant_manifests_dir=variant_manifests_dir,
        sweep_plans_dir=sweep_plans_dir,
    )


def _replace_first_data_ref_field(value: object, feature_name: str) -> bool:
    if isinstance(value, dict):
        if value.get("operand_type") == "data_ref":
            value["ref"] = feature_name
            value["field"] = feature_name
            return True
        return any(_replace_first_data_ref_field(child, feature_name) for child in value.values())
    if isinstance(value, list):
        return any(_replace_first_data_ref_field(child, feature_name) for child in value)
    return False


def _write_full_history_claim_fixture(
    tmp_path: Path,
    feature_name: str,
    source_class: str,
    *,
    condition_assertions: list[str] | None = None,
    override: dict | None = None,
    host_data_ref_only: bool = False,
) -> None:
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir, result_populations_dir = _fixture_paths(
        tmp_path
    )
    strategy_spec = _base_strategy_spec()
    if host_data_ref_only:
        host_ref = strategy_spec["timeframe_and_data"]["host_data_refs"][0]
        host_ref["stream"] = "funding"
        host_ref["field"] = feature_name
    else:
        assert _replace_first_data_ref_field(strategy_spec, feature_name)
    strategy_hash = _sha256_prefixed(strategy_spec)
    manifest = _base_variant_manifest(strategy_hash)
    sweep_plan = _base_sweep_plan(manifest)
    result_population = _base_result_population(strategy_hash, manifest, sweep_plan)
    result_population["data_availability_claim"] = {
        "coverage_claim": "FULL_HISTORY",
        "feature_sources": [
            {
                "feature_name": feature_name,
                "source_class": source_class,
                "condition_assertions": condition_assertions or [],
            }
        ],
        "historical_dataset_overrides": [] if override is None else [override],
        "claim_notes": [],
    }
    for identity_key in ("input_identity_hash", "result_population_identity_hash"):
        scope = result_population[identity_key]["hash_scope"]
        scope.insert(scope.index("backtest_assumption_summary"), "data_availability_claim")
    _refresh_identity_hashes(result_population)
    _write_json(strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json", strategy_spec)
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep_plan)
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)


def test_result_population_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema(DEFAULT_RESULT_POPULATION_SCHEMA_PATH))
    Draft7Validator.check_schema(_load_schema(DEFAULT_STRATEGY_SPEC_SCHEMA_PATH))
    Draft7Validator.check_schema(_load_schema(DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH))
    Draft7Validator.check_schema(_load_schema(DEFAULT_SWEEP_PLAN_SCHEMA_PATH))


def test_validator_noops_when_result_population_directory_missing(tmp_path):
    errors = validate_result_populations(result_populations_dir=tmp_path / "missing")

    assert errors == []


def test_validator_noops_when_result_population_directory_empty(tmp_path):
    result_populations_dir = tmp_path / "research" / "result_populations"
    result_populations_dir.mkdir(parents=True)

    errors = validate_result_populations(result_populations_dir=result_populations_dir)

    assert errors == []


def test_valid_temp_parent_artifacts_and_result_population_pass(tmp_path):
    _write_valid_fixture(tmp_path)

    assert _validate(tmp_path) == []


def test_committed_result_populations_remain_valid():
    committed_paths = [
        Path("research/result_populations/RP-2134.result_population.json"),
        Path("research/result_populations/RP-4492.result_population.json"),
        Path("research/result_populations/RP-6688.result_population.json"),
    ]

    for committed_path in committed_paths:
        assert committed_path.exists()

    assert validate_result_populations() == []


def test_open_interest_full_history_claim_requires_historical_override(tmp_path):
    _write_full_history_claim_fixture(
        tmp_path,
        "open_interest",
        "PUBLIC_REST_CURRENT_OPEN_INTEREST",
    )
    assert any("cannot support FULL_HISTORY" in error for error in _validate(tmp_path))


def test_declared_host_data_ref_is_included_in_full_history_guard(tmp_path):
    _write_full_history_claim_fixture(
        tmp_path,
        "open_interest",
        "PUBLIC_REST_CURRENT_OPEN_INTEREST",
        host_data_ref_only=True,
    )
    assert any("cannot support FULL_HISTORY" in error for error in _validate(tmp_path))


def test_long_short_ratio_full_history_claim_requires_historical_override(tmp_path):
    _write_full_history_claim_fixture(
        tmp_path,
        "global_long_short_account_ratio",
        "PUBLIC_REST_GLOBAL_ACCOUNT_RATIO",
    )
    assert any("cannot support FULL_HISTORY" in error for error in _validate(tmp_path))


def test_vendor_only_feature_requires_vendor_or_captured_provenance(tmp_path):
    _write_full_history_claim_fixture(
        tmp_path,
        "liquidation_volume",
        "VENDOR_HISTORICAL_DATASET",
        override={
            "feature_name": "liquidation_volume",
            "override_type": "EXPLICIT_ALIGNED_HISTORICAL_DATASET",
            "dataset_ref": "fixture-liquidations",
            "provenance_ref": "fixture-provenance",
            "alignment_assertion": True,
            "full_history_coverage_assertion": True,
        },
    )
    assert any("requires a vendor or captured" in error for error in _validate(tmp_path))


def test_open_interest_full_history_claim_accepts_explicit_vendor_override(tmp_path):
    _write_full_history_claim_fixture(
        tmp_path,
        "open_interest",
        "PUBLIC_REST_CURRENT_OPEN_INTEREST",
        override={
            "feature_name": "open_interest",
            "override_type": "VENDOR_HISTORICAL_DATASET",
            "dataset_ref": "vendor://fixture/open-interest",
            "provenance_ref": "docs/fixture-open-interest-provenance.md",
            "alignment_assertion": True,
            "full_history_coverage_assertion": True,
        },
    )
    assert _validate(tmp_path) == []


def test_taker_flow_d4_source_may_claim_conditional_full_history(tmp_path):
    _write_full_history_claim_fixture(
        tmp_path,
        "taker_buy_volume",
        "CANONICAL_D4_KLINE_DERIVATION",
        condition_assertions=[
            "Canonical D4 bars cover the claimed evidence window.",
            "Buy volume is deterministically derived from the exact bound D4 parent.",
            "Feature values are available only at completed-bar close.",
        ],
    )
    assert _validate(tmp_path) == []


def test_taker_flow_generic_canonical_source_may_claim_conditional_full_history(tmp_path):
    _write_full_history_claim_fixture(
        tmp_path,
        "taker_sell_volume",
        "CANONICAL_KLINE_TAKERFLOW_DERIVATION",
        condition_assertions=[
            "The exact canonical D2-021 base covers the claimed evidence window.",
            "The feature is derived row-locally from that exact bound canonical base.",
            "Feature values are available only at completed-bar close.",
            "Feature parent identity equals execution-base identity.",
        ],
    )
    assert _validate(tmp_path) == []


def test_taker_ratio_rest_source_remains_recent_only(tmp_path):
    _write_full_history_claim_fixture(
        tmp_path,
        "taker_buy_sell_ratio",
        "PUBLIC_REST_TAKER_RATIO",
    )
    assert any("RECENT_ONLY_PUBLIC_REST" in error for error in _validate(tmp_path))


def test_unknown_data_ref_feature_fails_closed(tmp_path):
    _write_full_history_claim_fixture(
        tmp_path,
        "unknown_perp_feature",
        "UNKNOWN_SOURCE",
    )
    errors = _validate(tmp_path)
    assert any("unknown" in error.lower() for error in errors)


def test_old_shape_without_sizing_metadata_remains_valid(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)

    assert "sizing_metadata" not in result_population
    assert "sizing_metadata" not in result_population["input_identity_hash"]["hash_scope"]
    assert "sizing_metadata" not in result_population["result_population_identity_hash"]["hash_scope"]
    assert _validate(tmp_path) == []


def test_dynamic_sizing_metadata_is_accepted(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    _add_sizing_metadata(
        result_population,
        {
            "sizing_mode": "dynamic_equity_target_leverage",
            "target_leverage": 1.0,
            "sizing_equity_basis": "realized_available_equity_at_entry",
            "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
        },
    )
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert _validate(tmp_path) == []


def test_fixed_sizing_metadata_is_accepted_without_target_leverage(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    _add_sizing_metadata(
        result_population,
        {
            "sizing_mode": "fixed_order_size",
            "sizing_equity_basis": "not_applicable_fixed_order_size",
            "entry_reference_price_basis": "not_applicable_fixed_order_size",
        },
    )
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert _validate(tmp_path) == []


def test_invalid_sizing_mode_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    _add_sizing_metadata(
        result_population,
        {
            "sizing_mode": "unknown_mode",
            "target_leverage": 1.0,
            "sizing_equity_basis": "realized_available_equity_at_entry",
            "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
        },
    )
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("sizing_mode" in error for error in _validate(tmp_path))


def test_invalid_target_leverage_fails(tmp_path):
    invalid_values = [0, -1, float("nan"), float("inf"), "1.0"]

    for index, target_leverage in enumerate(invalid_values):
        case_path = tmp_path / f"case-{index}"
        *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(case_path)
        _add_sizing_metadata(
            result_population,
            {
                "sizing_mode": "dynamic_equity_target_leverage",
                "target_leverage": target_leverage,
                "sizing_equity_basis": "realized_available_equity_at_entry",
                "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
            },
        )
        _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

        assert any("target_leverage" in error for error in _validate(case_path))


def test_missing_dynamic_sizing_fields_fail(tmp_path):
    for missing_field in (
        "target_leverage",
        "sizing_equity_basis",
        "entry_reference_price_basis",
    ):
        case_path = tmp_path / missing_field
        *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(case_path)
        sizing_metadata = {
            "sizing_mode": "dynamic_equity_target_leverage",
            "target_leverage": 1.0,
            "sizing_equity_basis": "realized_available_equity_at_entry",
            "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
        }
        del sizing_metadata[missing_field]
        _add_sizing_metadata(result_population, sizing_metadata)
        _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

        assert any(missing_field in error for error in _validate(case_path))


def test_invalid_sizing_basis_fields_fail(tmp_path):
    for field_name in ("sizing_equity_basis", "entry_reference_price_basis"):
        case_path = tmp_path / field_name
        *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(case_path)
        sizing_metadata = {
            "sizing_mode": "dynamic_equity_target_leverage",
            "target_leverage": 1.0,
            "sizing_equity_basis": "realized_available_equity_at_entry",
            "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
        }
        sizing_metadata[field_name] = "unsupported_basis"
        _add_sizing_metadata(result_population, sizing_metadata)
        _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

        assert any(field_name in error for error in _validate(case_path))


def test_optional_max_leverage_cap_validation(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path / "valid")
    _add_sizing_metadata(
        result_population,
        {
            "sizing_mode": "dynamic_equity_target_leverage",
            "target_leverage": 1.0,
            "sizing_equity_basis": "realized_available_equity_at_entry",
            "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
            "max_leverage_cap": 2.0,
        },
    )
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)
    assert _validate(tmp_path / "valid") == []

    for index, max_leverage_cap in enumerate([0, -1, float("nan"), float("inf"), "2.0"]):
        case_path = tmp_path / f"invalid-{index}"
        *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(case_path)
        _add_sizing_metadata(
            result_population,
            {
                "sizing_mode": "dynamic_equity_target_leverage",
                "target_leverage": 1.0,
                "sizing_equity_basis": "realized_available_equity_at_entry",
                "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
                "max_leverage_cap": max_leverage_cap,
            },
        )
        _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

        assert any("max_leverage_cap" in error for error in _validate(case_path))


def test_sizing_metadata_must_be_identity_scoped(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["sizing_metadata"] = {
        "sizing_mode": "dynamic_equity_target_leverage",
        "target_leverage": 1.0,
        "sizing_equity_basis": "realized_available_equity_at_entry",
        "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
    }
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    errors = _validate(tmp_path)

    assert any("input_identity_hash.hash_scope must include sizing_metadata" in error for error in errors)
    assert any(
        "result_population_identity_hash.hash_scope must include sizing_metadata" in error
        for error in errors
    )


def test_sizing_metadata_changes_identity_hashes(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    _add_sizing_metadata(
        result_population,
        {
            "sizing_mode": "dynamic_equity_target_leverage",
            "target_leverage": 1.0,
            "sizing_equity_basis": "realized_available_equity_at_entry",
            "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
        },
    )
    initial_input_hash = result_population["input_identity_hash"]["hash"]
    initial_result_hash = result_population["result_population_identity_hash"]["hash"]

    result_population["sizing_metadata"]["target_leverage"] = 2.0
    _refresh_identity_hashes(result_population)
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert result_population["input_identity_hash"]["hash"] != initial_input_hash
    assert result_population["result_population_identity_hash"]["hash"] != initial_result_hash
    assert _validate(tmp_path) == []


def test_invalid_result_population_json_fails(tmp_path):
    _write_valid_fixture(tmp_path)
    *_, result_populations_dir = _fixture_paths(tmp_path)
    (result_populations_dir / "RP-0001.result_population.json").write_text("{", encoding="utf-8")

    assert any("invalid JSON" in error for error in _validate(tmp_path))


def test_missing_required_schema_field_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    del result_population["review"]
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("'review' is a required property" in error for error in _validate(tmp_path))


def test_filename_result_population_id_mismatch_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    (result_populations_dir / "RP-0001.result_population.json").unlink()
    _write_json(result_populations_dir / "RP-9999.result_population.json", result_population)

    assert any("filename must be RP-0001.result_population.json" in error for error in _validate(tmp_path))


def test_duplicate_result_population_ids_fail(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    _write_json(result_populations_dir / "nested" / "RP-0001.result_population.json", result_population)

    assert any("duplicate result_population_id RP-0001" in error for error in _validate(tmp_path))


def test_schema_invalid_nested_payload_returns_errors_without_raising(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    del result_population["committed_denominator_snapshot"]["committed_denominator"]
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    errors = _validate(tmp_path)

    assert errors
    assert any("committed_denominator" in error for error in errors)


def test_open_unknown_outcome_category_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["variant_result_rows"][0]["outcome_category"] = "winner"
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("winner" in error for error in _validate(tmp_path))


def test_outcome_counts_extra_custom_category_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["outcome_category_counts"]["custom"] = 1
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("Additional properties are not allowed" in error for error in _validate(tmp_path))


def test_audit_envelope_in_input_identity_hash_scope_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["input_identity_hash"]["hash_scope"] = ["audit_envelope"]
    result_population["input_identity_hash"]["hash"] = None
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("audit_envelope" in error for error in _validate(tmp_path))


def test_audit_envelope_in_result_population_identity_hash_scope_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["result_population_identity_hash"]["hash_scope"] = ["audit_envelope"]
    result_population["result_population_identity_hash"]["hash"] = None
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("audit_envelope" in error for error in _validate(tmp_path))


def test_audit_envelope_admin_only_flags_false_fail(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["audit_envelope"]["administrative_only"] = False
    result_population["audit_envelope"]["may_contain_scientific_content"] = True
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    errors = _validate(tmp_path)
    assert any("administrative_only" in error for error in errors)
    assert any("may_contain_scientific_content" in error for error in errors)


def test_parent_strategy_spec_hash_mismatch_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["parent_strategy_spec"]["strategy_spec_hash"] = "sha256:" + "0" * 64
    result_population["lineage"]["parent_hash_chain"]["strategy_spec_hash"] = "sha256:" + "0" * 64
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("parent_strategy_spec.strategy_spec_hash mismatch" in error for error in _validate(tmp_path))


def test_parent_variant_manifest_hash_mismatch_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["parent_variant_manifest"]["manifest_hash"] = "sha256:" + "1" * 64
    result_population["lineage"]["parent_hash_chain"]["variant_manifest_hash"] = "sha256:" + "1" * 64
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("parent_variant_manifest.manifest_hash mismatch" in error for error in _validate(tmp_path))


def test_parent_sweep_plan_identity_hash_mismatch_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["parent_sweep_plan"]["sweep_plan_identity_hash"] = "sha256:" + "2" * 64
    result_population["lineage"]["parent_hash_chain"]["sweep_plan_identity_hash"] = "sha256:" + "2" * 64
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("parent_sweep_plan.sweep_plan_identity_hash mismatch" in error for error in _validate(tmp_path))


def test_parent_hash_chain_mismatch_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["lineage"]["parent_hash_chain"]["variant_manifest_hash"] = "sha256:" + "3" * 64
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("lineage.parent_hash_chain.variant_manifest_hash mismatch" in error for error in _validate(tmp_path))


def test_input_identity_hash_mismatch_fails_when_non_null(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["input_identity_hash"]["hash"] = "sha256:" + "4" * 64
    result_population["lineage"]["parent_hash_chain"]["input_identity_hash"] = "sha256:" + "4" * 64
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("input_identity_hash.hash mismatch" in error for error in _validate(tmp_path))


def test_missing_parent_manifest_under_block_policy_fails(tmp_path):
    _write_valid_fixture(tmp_path)
    _, variant_manifests_dir, _, _ = _fixture_paths(tmp_path)
    (variant_manifests_dir / "VM-0001.variant_manifest.json").unlink()

    assert any("parent variant manifest VM-0001 missing" in error for error in _validate(tmp_path))


def test_missing_parent_sweep_plan_under_block_policy_fails(tmp_path):
    _write_valid_fixture(tmp_path)
    _, _, sweep_plans_dir, _ = _fixture_paths(tmp_path)
    (sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json").unlink()

    assert any("parent sweep plan SWEEP-PLAN-0001 missing" in error for error in _validate(tmp_path))


def test_committed_denominator_differs_from_parent_manifest_count_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["committed_denominator_snapshot"]["committed_denominator"] = 1
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("committed denominator" in error for error in _validate(tmp_path))


def test_committed_denominator_differs_from_parent_sweep_plan_count_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["parent_sweep_plan"]["committed_population_count"] = 1
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("parent_sweep_plan.committed_population_count" in error for error in _validate(tmp_path))


def test_outcome_counts_sum_differs_from_committed_denominator_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["outcome_category_counts"]["failed"] = 0
    result_population["outcome_category_counts"]["counts_sum"] = 1
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("outcome category counts must sum" in error for error in _validate(tmp_path))


def test_counts_sum_differs_from_actual_category_sum_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["outcome_category_counts"]["counts_sum"] = 99
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("counts_sum must equal actual category sum" in error for error in _validate(tmp_path))


def test_result_row_count_differs_from_committed_denominator_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["variant_result_rows"].pop()
    result_population["committed_denominator_snapshot"]["result_row_count"] = 1
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("result row count must equal committed denominator" in error for error in _validate(tmp_path))


def test_duplicate_variant_result_row_ids_fail(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["variant_result_rows"][1]["row_id"] = "RP-0001-ROW-000001"
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("duplicate variant result row_id" in error for error in _validate(tmp_path))


def test_duplicate_variant_ids_fail(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["variant_result_rows"][1]["variant_id"] = "VAR-000001"
    result_population["variant_result_rows"][1]["lineage"]["parent_variant_id"] = "VAR-000001"
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("duplicate variant result variant_id VAR-000001" in error for error in _validate(tmp_path))


def test_result_row_variant_outside_parent_manifest_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["variant_result_rows"][1]["variant_id"] = "VAR-999999"
    result_population["variant_result_rows"][1]["lineage"]["parent_variant_id"] = "VAR-999999"
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("outside parent manifest" in error for error in _validate(tmp_path))


def test_missing_parent_manifest_variant_row_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["variant_result_rows"].pop()
    result_population["committed_denominator_snapshot"]["committed_denominator"] = 1
    result_population["committed_denominator_snapshot"]["result_row_count"] = 1
    result_population["committed_denominator_snapshot"]["outcome_counts_sum"] = 1
    result_population["outcome_category_counts"]["failed"] = 0
    result_population["outcome_category_counts"]["counts_sum"] = 1
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("parent manifest variant missing result row: VAR-000002" in error for error in _validate(tmp_path))


def test_non_success_row_with_denominator_flag_false_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["variant_result_rows"][1]["non_success"]["counts_in_denominator"] = False
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("counts_in_denominator" in error for error in _validate(tmp_path))


def test_row_mutation_policy_false_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["variant_result_rows"][0]["row_mutation_policy"][
        "post_commit_in_place_mutation_forbidden"
    ] = False
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("row_mutation_policy.post_commit_in_place_mutation_forbidden" in error for error in _validate(tmp_path))


def test_append_only_ledger_flag_false_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["append_only_ledger"]["append_only"] = False
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("append_only_ledger.append_only" in error for error in _validate(tmp_path))


def test_missing_created_ledger_event_fails_for_non_draft_artifact(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["append_only_ledger"]["events"][0]["event_type"] = "validated"
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("must include a created event" in error for error in _validate(tmp_path))


def test_ledger_event_with_authority_key_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["append_only_ledger"]["events"][0]["approval_action"] = "approve"
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("Additional properties are not allowed" in error for error in _validate(tmp_path))


def test_non_authority_flag_false_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["non_authority_declaration"]["not_runtime_authority"] = False
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("not_runtime_authority" in error for error in _validate(tmp_path))


def test_review_status_approved_or_authority_like_field_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["review"]["review_status"] = "approved"
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("approved" in error for error in _validate(tmp_path))


def test_canonical_evidence_relationship_not_reference_only_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["non_authority_declaration"]["canonical_evidence_relationship"] = "replacement"
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("reference_only" in error or "reference" in error for error in _validate(tmp_path))


def test_forbidden_executable_key_fails(tmp_path):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["validation_summary"]["blocking_errors"] = []
    result_population["execution_context"]["command"] = "run"
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)

    assert any("Additional properties are not allowed" in error for error in _validate(tmp_path))


def test_cli_returns_success_for_clean_temp_fixtures(tmp_path, monkeypatch, capsys):
    _write_valid_fixture(tmp_path)
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir, result_populations_dir = _fixture_paths(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_result_populations",
            "--result-populations-dir",
            str(result_populations_dir),
            "--strategy-specs-dir",
            str(strategy_specs_dir),
            "--variant-manifests-dir",
            str(variant_manifests_dir),
            "--sweep-plans-dir",
            str(sweep_plans_dir),
        ],
    )

    assert main() == 0
    assert "OK:" in capsys.readouterr().out


def test_cli_returns_failure_for_invalid_temp_fixtures(tmp_path, monkeypatch, capsys):
    *_, result_population, _, _, _, result_populations_dir = _write_valid_fixture(tmp_path)
    result_population["input_identity_hash"]["hash"] = "sha256:" + "5" * 64
    _write_json(result_populations_dir / "RP-0001.result_population.json", result_population)
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir, result_populations_dir = _fixture_paths(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_result_populations",
            "--result-populations-dir",
            str(result_populations_dir),
            "--strategy-specs-dir",
            str(strategy_specs_dir),
            "--variant-manifests-dir",
            str(variant_manifests_dir),
            "--sweep-plans-dir",
            str(sweep_plans_dir),
        ],
    )

    assert main() == 1
    assert "ERROR:" in capsys.readouterr().out


def test_local_strategy_spec_helper_exists_for_fixture_completeness():
    assert _strategy_spec_fixture("STRAT-SPEC-9001")["strategy_spec_id"] == "STRAT-SPEC-9001"
