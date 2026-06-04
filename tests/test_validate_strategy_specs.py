import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_strategy_specs import (
    DEFAULT_SCHEMA_PATH,
    main,
    validate_strategy_specs,
)


def _load_schema(path: Path = DEFAULT_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _operand(ref="close") -> dict:
    return {
        "operand_type": "data_ref",
        "ref": ref,
        "field": "close",
        "timeframe": "1h",
        "lookback": {"bars": 1},
    }


def _condition(condition_id: str = "COND-1", operator: str = "gt") -> dict:
    return {
        "condition_id": condition_id,
        "condition_role": "required",
        "left_operand": _operand("close"),
        "operator": operator,
        "right_operand": {
            "operand_type": "constant",
            "ref": 100.0,
            "field": None,
            "timeframe": None,
            "lookback": None,
        },
        "units": None,
        "notes": None,
    }


def _group(group_id: str = "GROUP-1", subgroups: list | None = None) -> dict:
    return {
        "group_id": group_id,
        "group_role": "required",
        "logic": "all",
        "conditions": [_condition()],
        "subgroups": subgroups or [],
        "notes": None,
    }


def _parameter(name: str = "lookback") -> dict:
    return {
        "name": name,
        "label": None,
        "description": None,
        "type": "integer",
        "units": "bars",
        "default": 20,
        "range": {
            "min": 5,
            "max": 50,
            "step": 5,
            "inclusive_min": True,
            "inclusive_max": True,
        },
        "allowed_values": [],
        "is_free_parameter": True,
        "included_in_variant_generation": True,
        "role": "entry",
        "rationale": "Pytest fixture parameter.",
        "constraints": [],
    }


def _true_flags(*names: str) -> dict:
    return {name: True for name in names}


def _base_strategy_spec(strategy_spec_id: str = "STRAT-SPEC-9001") -> dict:
    return {
        "schema_version": "v1",
        "strategy_spec_id": strategy_spec_id,
        "title": "Pytest Strategy Spec",
        "status": "draft",
        "non_execution_declaration": _true_flags(
            "human_review_surface_only",
            "not_executable",
            "not_runtime_authority",
            "not_paper_live_authority",
            "not_gate_authority",
            "not_candidate_approval",
            "not_exp_approval",
            "not_sweep_authority",
            "not_ranking_authority",
            "not_recommendation_authority",
            "not_readiness_authority",
            "not_transition_authority",
        ),
        "provenance": {
            "source_type": "manual_idea",
            "source_refs": ["pytest-fixture"],
            "prepared_by": "pytest",
            "created_at": "2026-06-01T00:00:00Z",
            "updated_at": "2026-06-01T00:00:00Z",
            "rationale": "Pytest fixture.",
            "source_constraints": [],
            "unresolved_claims": [],
        },
        "instruments": {
            "symbols": ["BTCUSDT"],
            "instrument_family": "crypto_perp",
            "venue_assumption": "Binance USDT-M",
            "market_type": "perpetual",
            "directions_allowed": ["long"],
            "leverage_assumption": None,
            "exchange_constraint_refs": [],
            "blockers": [],
        },
        "timeframe_and_data": {
            "primary_timeframe": "1h",
            "confirmation_timeframes": [],
            "host_data_refs": [
                {
                    "stream": "ohlcv",
                    "timeframe": "1h",
                    "field": "close",
                    "availability": "required",
                }
            ],
            "gap_handling_assumption": None,
            "missing_data_blockers": [],
        },
        "entry_logic": {
            "direction": "long",
            "groups": [_group()],
            "notes": None,
        },
        "exit_logic": {
            "groups": [],
            "max_holding_period": {"enabled": False, "bars": None},
            "notes": None,
        },
        "risk_model": {
            "sizing_intent": "review_only",
            "exposure_limits": [],
            "stop_distance": None,
            "target_distance": None,
            "leverage_visibility": None,
            "liquidation_sensitivity_notes": None,
        },
        "filters": {
            "groups": [],
            "none_declared": True,
        },
        "free_parameters": {
            "max_free_parameters": 5,
            "counting_rule": (
                "parameters contains only entries where is_free_parameter=true; "
                "maxItems 5 enforces the D2-006-style MVP free-parameter cap"
            ),
            "parameters": [],
            "no_free_parameters_declared": True,
        },
        "constraints": {
            "invalid_parameter_combinations": [],
            "unavailable_data_blockers": [],
            "deferred_pattern_blockers": [],
            "none_declared": True,
        },
        "review": {
            "human_review_required": True,
            "reviewer": None,
            "reviewed_at": None,
            "review_notes": [],
            "approval_scope": "none",
            "non_authority_acknowledgement": _true_flags(
                "not_candidate_approval",
                "not_exp_approval",
                "not_sweep_authority",
                "not_ranking_authority",
                "not_recommendation_authority",
                "not_readiness_authority",
                "not_transition_authority",
                "not_runtime_authority",
                "not_paper_live_authority",
                "not_gate_satisfaction",
            ),
        },
        "lineage": {
            "parent_refs": [],
            "supersedes": [],
            "amendment_of": None,
        },
        "hash_pinning": {
            "canonical_spec_hash": None,
            "hash_algorithm": None,
            "hash_scope_version": None,
            "hash_scope": [],
            "hash_status": "not_computed",
        },
        "pre_registration_support": {
            "intended_for_variant_manifest": False,
            "variant_manifest_ref": None,
            "frozen_snapshot_ref": None,
        },
        "backtest_realism_assumptions": {
            "fee_side_assumption": None,
            "exchange_constraints_disclosed": False,
            "funding_notional_mode": "unspecified",
            "slippage_model": "unspecified",
            "fill_mode": "unspecified",
            "order_size_assumption": None,
            "liquidity_capacity_assumption": None,
            "liquidation_mode": "unspecified",
            "maintenance_margin_assumption": None,
            "mark_price_source": "unspecified",
            "bar_path_assumption": "unspecified",
        },
        "max_condition_group_depth": 3,
    }


def _validate(
    tmp_path: Path,
    payload: dict,
    filename: str = "STRAT-SPEC-9001.strategy_spec.json",
) -> list[str]:
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    _write_json(strategy_specs_dir / filename, payload)
    return validate_strategy_specs(strategy_specs_dir=strategy_specs_dir)


def test_strategy_spec_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_strategy_spec_validator_noops_when_directory_missing(tmp_path):
    errors = validate_strategy_specs(strategy_specs_dir=tmp_path / "research" / "strategy_specs")

    assert errors == []


def test_strategy_spec_validator_noops_when_directory_empty(tmp_path):
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    strategy_specs_dir.mkdir(parents=True)

    errors = validate_strategy_specs(strategy_specs_dir=strategy_specs_dir)

    assert errors == []


def test_valid_temp_strategy_spec_passes(tmp_path):
    assert _validate(tmp_path, _base_strategy_spec()) == []


def test_invalid_json_fails(tmp_path):
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    path = strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json"
    path.parent.mkdir(parents=True)
    path.write_text("{", encoding="utf-8")

    errors = validate_strategy_specs(strategy_specs_dir=strategy_specs_dir)

    assert any("invalid JSON" in error for error in errors)


def test_missing_required_schema_field_fails(tmp_path):
    payload = _base_strategy_spec()
    del payload["title"]

    errors = _validate(tmp_path, payload)

    assert any("'title' is a required property" in error for error in errors)


def test_filename_strategy_spec_id_mismatch_fails(tmp_path):
    errors = _validate(
        tmp_path,
        _base_strategy_spec("STRAT-SPEC-9001"),
        filename="STRAT-SPEC-9999.strategy_spec.json",
    )

    assert any(
        "filename must be STRAT-SPEC-9001.strategy_spec.json" in error
        for error in errors
    )


def test_duplicate_strategy_spec_id_fails(tmp_path):
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    payload = _base_strategy_spec("STRAT-SPEC-9001")
    _write_json(strategy_specs_dir / "a" / "STRAT-SPEC-9001.strategy_spec.json", payload)
    _write_json(strategy_specs_dir / "b" / "STRAT-SPEC-9001.strategy_spec.json", payload)

    errors = validate_strategy_specs(strategy_specs_dir=strategy_specs_dir)

    assert any("duplicate strategy_spec_id STRAT-SPEC-9001" in error for error in errors)


def test_invalid_operator_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["entry_logic"]["groups"][0]["conditions"][0]["operator"] = "executes"

    errors = _validate(tmp_path, payload)

    assert any("invalid operator: 'executes'" in error for error in errors)


def test_condition_nesting_depth_greater_than_three_fails(tmp_path):
    payload = _base_strategy_spec()
    depth_4 = _group("GROUP-4")
    depth_3 = _group("GROUP-3", [depth_4])
    depth_2 = _group("GROUP-2", [depth_3])
    payload["entry_logic"]["groups"] = [_group("GROUP-1", [depth_2])]

    errors = _validate(tmp_path, payload)

    assert any("condition group depth 4 exceeds 3" in error for error in errors)


def test_max_condition_group_depth_not_exactly_three_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["max_condition_group_depth"] = 4

    errors = _validate(tmp_path, payload)

    assert any("max_condition_group_depth must be exactly 3" in error for error in errors)


def test_more_than_five_free_parameters_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["free_parameters"]["parameters"] = [_parameter(f"p{i}") for i in range(6)]
    payload["free_parameters"]["no_free_parameters_declared"] = False

    errors = _validate(tmp_path, payload)

    assert any("free_parameters.parameters has 6 entries" in error for error in errors)


def test_no_free_parameters_declared_with_non_empty_parameters_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["free_parameters"]["parameters"] = [_parameter("lookback")]
    payload["free_parameters"]["no_free_parameters_declared"] = True

    errors = _validate(tmp_path, payload)

    assert any("no_free_parameters_declared=true requires empty parameters" in error for error in errors)


def test_forbidden_executable_key_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["provenance"]["Formula"] = "close > 100"

    errors = _validate(tmp_path, payload)

    assert any("forbidden executable key name" in error and "Formula" in error for error in errors)


def test_non_authority_flag_false_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["review"]["non_authority_acknowledgement"]["not_recommendation_authority"] = False

    errors = _validate(tmp_path, payload)

    assert any(
        "review.non_authority_acknowledgement.not_recommendation_authority must be true"
        in error
        for error in errors
    )


def test_unsafe_host_data_reference_strings_fail(tmp_path):
    payload = _base_strategy_spec()
    payload["timeframe_and_data"]["host_data_refs"] = [
        {
            "stream": "ohlcv",
            "timeframe": "1h",
            "field": "https://example.test/close",
            "availability": "required",
        },
        {
            "stream": "ohlcv",
            "timeframe": "1h",
            "field": "..\\outside",
            "availability": "optional",
        },
        {
            "stream": "ohlcv",
            "timeframe": "1h",
            "field": "C:\\data\\close",
            "availability": "optional",
        },
    ]

    errors = _validate(tmp_path, payload)

    assert sum("unsafe host-data reference string" in error for error in errors) == 3


def test_cli_returns_success_for_clean_temp_fixture(tmp_path, monkeypatch, capsys):
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    _write_json(strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json", _base_strategy_spec())
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_strategy_specs", "--strategy-specs-dir", str(strategy_specs_dir)],
    )

    assert main() == 0
    assert "OK:" in capsys.readouterr().out


def test_cli_returns_failure_for_invalid_temp_fixture(tmp_path, monkeypatch, capsys):
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    payload = _base_strategy_spec()
    del payload["title"]
    _write_json(strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json", payload)
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_strategy_specs", "--strategy-specs-dir", str(strategy_specs_dir)],
    )

    assert main() == 1
    assert "ERROR:" in capsys.readouterr().out
