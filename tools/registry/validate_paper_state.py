"""Validate disconnected paper-state snapshot fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
PAPER_STATE_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "paper_state.schema.json"
DEFAULT_PAPER_STATE_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "paper_state"

NON_AUTHORITY_FLAGS = {
    "not_paper_engine",
    "not_runtime_authority",
    "not_live_authority",
    "not_broker_exchange_authority",
    "not_capital_authority",
    "not_order_execution_authority",
    "not_candidate_promotion_authority",
    "not_trading_recommendation",
}
HALT_REQUIRED_SAFE_MODE_STATES = {"safe_mode", "operator_halt", "frozen"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _validate_json_file(path: Path, validator: Draft7Validator) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]

    errors = [
        f"{path}: {_format_schema_error(schema_error)}"
        for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    ]
    return payload, errors


def _paper_state_files(paper_state_dir: Path) -> list[Path]:
    if not paper_state_dir.exists():
        return []
    return sorted(paper_state_dir.rglob("*.paper_state.json"))


def _non_authority_errors(path: Path, declaration: Any) -> list[str]:
    if not isinstance(declaration, dict):
        return []
    errors: list[str] = []
    for flag in sorted(NON_AUTHORITY_FLAGS):
        if declaration.get(flag) is not True:
            errors.append(f"{path}: forbidden authority flag is not true: {flag}")
    return errors


def _duplicate_value_errors(path: Path, label: str, values: list[str]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            errors.append(f"{path}: duplicate {label}: {value}")
        seen.add(value)
    return errors


def _validate_order_and_fill_ids(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    orders = payload.get("orders")
    fills = payload.get("fills")
    if not isinstance(orders, list) or not isinstance(fills, list):
        return errors

    order_ids = [
        order.get("order_id")
        for order in orders
        if isinstance(order, dict) and isinstance(order.get("order_id"), str)
    ]
    fill_ids = [
        fill.get("fill_id")
        for fill in fills
        if isinstance(fill, dict) and isinstance(fill.get("fill_id"), str)
    ]
    errors.extend(_duplicate_value_errors(path, "order_id", order_ids))
    errors.extend(_duplicate_value_errors(path, "fill_id", fill_ids))

    known_order_ids = set(order_ids)
    for fill in fills:
        if not isinstance(fill, dict):
            continue
        order_id = fill.get("order_id")
        fill_id = fill.get("fill_id")
        if isinstance(order_id, str) and order_id not in known_order_ids:
            errors.append(f"{path}: fill {fill_id} references unknown order_id {order_id}")
    return errors


def _validate_drift(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    drift = payload.get("drift")
    if not isinstance(drift, dict):
        return errors

    classification = drift.get("classification")
    reason = drift.get("reason")
    evidence_refs = drift.get("evidence_refs")
    if classification != "none":
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{path}: non-none drift requires a reason")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            errors.append(f"{path}: non-none drift requires evidence_refs")

    if drift.get("severity") == "halt_required":
        risk_state = payload.get("risk_state")
        if not isinstance(risk_state, dict):
            return errors
        safe_mode_state = risk_state.get("safe_mode_state")
        if safe_mode_state not in HALT_REQUIRED_SAFE_MODE_STATES:
            errors.append(
                f"{path}: halt_required drift requires safe_mode_state in "
                f"{sorted(HALT_REQUIRED_SAFE_MODE_STATES)}"
            )
        if risk_state.get("no_new_intent") is not True:
            errors.append(f"{path}: halt_required drift requires no_new_intent true")
        if risk_state.get("operator_halt") is not True:
            errors.append(f"{path}: halt_required drift requires operator_halt true")
    return errors


def _validate_paper_state_semantics(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(_non_authority_errors(path, payload.get("non_authority_declaration")))
    errors.extend(_validate_order_and_fill_ids(path, payload))
    errors.extend(_validate_drift(path, payload))
    return errors


def validate_paper_states(
    paper_state_dir: Path = DEFAULT_PAPER_STATE_FIXTURE_DIR,
    schema_path: Path = PAPER_STATE_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for paper-state snapshot fixtures."""

    if not schema_path.exists():
        return [f"schema file not found: {schema_path}"]

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    paper_state_files = _paper_state_files(paper_state_dir)
    if not paper_state_files:
        return []

    errors: list[str] = []
    for path in paper_state_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None or file_errors:
            continue
        errors.extend(_validate_paper_state_semantics(path, payload))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-state-dir", type=Path, default=DEFAULT_PAPER_STATE_FIXTURE_DIR)
    parser.add_argument("--schema", type=Path, default=PAPER_STATE_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_paper_states(
        paper_state_dir=args.paper_state_dir,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.paper_state_dir.exists():
        print(f"OK: {args.paper_state_dir} does not exist; nothing to validate")
    else:
        print(f"OK: paper-state fixtures under {args.paper_state_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
