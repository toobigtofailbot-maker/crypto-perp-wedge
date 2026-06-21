import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_indicator_catalogs import (
    DEFAULT_INDICATOR_CATALOGS_DIR,
    DEFAULT_SCHEMA_PATH,
    main,
    validate_indicator_catalogs,
)


CATALOG_PATH = DEFAULT_INDICATOR_CATALOGS_DIR / "IND-CATALOG-0001.indicator_catalog.json"


def _load_schema(path: Path = DEFAULT_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_committed_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _entry(payload: dict, indicator_id: str) -> dict:
    return next(entry for entry in payload["entries"] if entry["indicator_id"] == indicator_id)


def _parameter(entry: dict, name: str) -> dict:
    return next(
        parameter
        for parameter in entry["parameter_contract"]["parameters"]
        if parameter["name"] == name
    )


def _validate(
    tmp_path: Path,
    payload: dict,
    filename: str = "IND-CATALOG-0001.indicator_catalog.json",
) -> list[str]:
    indicator_catalogs_dir = tmp_path / "research" / "indicator_catalogs"
    _write_json(indicator_catalogs_dir / filename, payload)
    return validate_indicator_catalogs(indicator_catalogs_dir=indicator_catalogs_dir)


def test_indicator_catalog_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_committed_indicator_catalog_validates():
    assert validate_indicator_catalogs() == []


def test_schema_rejects_indicator_id_builtin_key_mismatch():
    payload = _load_committed_catalog()
    _entry(payload, "sma")["implementation_binding"]["builtin_key"] = "ema_v1"
    schema = _load_schema()

    errors = list(Draft7Validator(schema).iter_errors(payload))

    assert errors


def test_validator_rejects_indicator_id_builtin_key_mismatch(tmp_path):
    payload = _load_committed_catalog()
    _entry(payload, "sma")["implementation_binding"]["builtin_key"] = "ema_v1"

    errors = _validate(tmp_path, payload)

    assert any("builtin_key" in error for error in errors)


def test_validator_rejects_computation_defined_in_catalog_true(tmp_path):
    payload = _load_committed_catalog()
    _entry(payload, "ema")["implementation_binding"]["computation_defined_in_catalog"] = True

    errors = _validate(tmp_path, payload)

    assert any("computation_defined_in_catalog" in error for error in errors)


def test_validator_rejects_arbitrary_expression_allowed_true(tmp_path):
    payload = _load_committed_catalog()
    _entry(payload, "atr")["implementation_binding"]["arbitrary_expression_allowed"] = True

    errors = _validate(tmp_path, payload)

    assert any("arbitrary_expression_allowed" in error for error in errors)


def test_validator_rejects_forbidden_keys_recursively(tmp_path):
    payload = _load_committed_catalog()
    _entry(payload, "sma")["parameter_contract"]["parameters"][0]["formula"] = "close.mean()"

    errors = _validate(tmp_path, payload)

    assert any("forbidden executable/authority key name" in error for error in errors)
    assert any("formula" in error for error in errors)


def test_validator_rejects_unapproved_ema_convention_value(tmp_path):
    payload = _load_committed_catalog()
    smoothing = _parameter(_entry(payload, "ema"), "smoothing_convention")
    smoothing["allowed_values"] = ["free_string"]

    errors = _validate(tmp_path, payload)

    assert any("entries.ema parameter smoothing_convention allowed_values" in error for error in errors)


def test_validator_rejects_unapproved_atr_convention_value(tmp_path):
    payload = _load_committed_catalog()
    convention = _parameter(_entry(payload, "atr"), "true_range_convention")
    convention["allowed_values"] = ["free_string"]

    errors = _validate(tmp_path, payload)

    assert any("entries.atr parameter true_range_convention allowed_values" in error for error in errors)


def test_validator_rejects_stddev_ddof_outside_closed_set(tmp_path):
    payload = _load_committed_catalog()
    ddof = _parameter(_entry(payload, "stddev"), "ddof")
    ddof["allowed_values"] = [0, 2]

    errors = _validate(tmp_path, payload)

    assert any("entries.stddev parameter ddof allowed_values" in error for error in errors)


def test_validator_rejects_unapproved_rsi_zero_movement_policy(tmp_path):
    payload = _load_committed_catalog()
    policy = _parameter(_entry(payload, "rsi"), "zero_movement_policy")
    policy["allowed_values"] = ["epsilon"]

    errors = _validate(tmp_path, payload)

    assert any("entries.rsi parameter zero_movement_policy allowed_values" in error for error in errors)


def test_validator_rejects_mutated_donchian_output_set(tmp_path):
    payload = _load_committed_catalog()
    _entry(payload, "donchian")["output_contract"]["outputs"].pop()

    errors = _validate(tmp_path, payload)

    assert any("entries.donchian output fields" in error for error in errors)


def test_validator_rejects_unapproved_ma_distance_ma_kind(tmp_path):
    payload = _load_committed_catalog()
    ma_kind = _parameter(_entry(payload, "ma_distance"), "ma_kind")
    ma_kind["allowed_values"] = ["sma", "ema"]

    errors = _validate(tmp_path, payload)

    assert any("entries.ma_distance parameter ma_kind allowed_values" in error for error in errors)


def test_validator_rejects_extra_catalog_entry(tmp_path):
    payload = _load_committed_catalog()
    extra = copy.deepcopy(_entry(payload, "sma"))
    extra["indicator_id"] = "mfi"
    extra["implementation_binding"]["builtin_key"] = "mfi_v1"
    payload["entries"].append(extra)

    errors = _validate(tmp_path, payload)

    assert any("entries must contain exactly 7 entries" in error for error in errors)


def test_validator_rejects_missing_required_contract_objects(tmp_path):
    payload = _load_committed_catalog()
    del _entry(payload, "atr")["output_contract"]

    errors = _validate(tmp_path, payload)

    assert any("entries.atr.output_contract must be present as an object" in error for error in errors)


def test_validator_rejects_filename_catalog_id_mismatch(tmp_path):
    payload = _load_committed_catalog()

    errors = _validate(tmp_path, payload, filename="IND-CATALOG-9999.indicator_catalog.json")

    assert any("filename must be IND-CATALOG-0001.indicator_catalog.json" in error for error in errors)


def test_cli_module_entrypoint_returns_success_for_committed_instance(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["validate_indicator_catalogs"])

    assert main() == 0
    assert "OK: 1 indicator catalog file(s) validate" in capsys.readouterr().out


def test_validator_does_not_require_or_invoke_compiler_code():
    protected_modules = {
        "tools.research_runner.run_offline_sweep",
        "lib.backtest",
        "lib.evaluation",
    }
    before = {name for name in protected_modules if name in sys.modules}

    errors = validate_indicator_catalogs()

    assert errors == []
    after = {name for name in protected_modules if name in sys.modules}
    assert after == before


def test_validator_does_not_import_protected_runner_or_backtester_modules():
    source = Path("tools/registry/validate_indicator_catalogs.py").read_text(encoding="utf-8")

    assert "tools.research_runner.run_offline_sweep" not in source
    assert "lib.backtest" not in source
    assert "lib.evaluation" not in source
