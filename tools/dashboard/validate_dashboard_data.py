"""Validate versioned dashboard_data JSON files.

The validator is offline and read-only. It checks the dashboard_data contract
shape, then applies deterministic semantic checks so future renderers only
consume contract-valid repo facts and cannot receive execution controls or
authority-like fields.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft7Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "dashboard_data.schema.json"
STATUS_VOCAB = {"PASS", "WARN", "FAIL", "BLOCKED", "UNKNOWN", "NOT_AVAILABLE"}
STALENESS_VOCAB = {"FRESH", "STALE", "UNKNOWN", "NOT_APPLICABLE"}
NON_AUTHORITY_TRUE_FLAGS = {
    "read_only_mirror",
    "renderer_must_not_invent_facts",
    "not_executable",
    "not_runtime_authority",
    "not_paper_live_authority",
    "not_order_authority",
    "not_broker_exchange_authority",
    "not_ranking_authority",
    "not_recommendation_authority",
    "not_readiness_authority",
    "not_promotion_authority",
    "not_transition_authority",
    "not_gate_authority",
}
FORBIDDEN_AUTHORITY_KEYS = {
    "best_variant",
    "recommended_variant",
    "approved_strategy",
    "ready_for_live",
    "ready_for_paper",
    "promote",
    "promotion_status",
    "execute",
    "place_order",
    "cancel_order",
    "start_paper_run",
    "start_live_run",
    "approve_button",
    "promote_to_paper",
    "live_enabled",
}
FORBIDDEN_AUTHORITY_VALUES = {
    "best_variant",
    "recommended_variant",
    "approved_strategy",
    "ready_for_live",
    "ready_for_paper",
    "promote",
    "promotion_status",
    "execute",
    "place_order",
    "cancel_order",
    "start_paper_run",
    "start_live_run",
    "approve_button",
    "promote_to_paper",
    "live_enabled",
}
COMMAND_LIKE_GATE_ACTION_RE = re.compile(
    r"(?i)(https?://|\b(?:python|powershell|pwsh|bash|curl|git|gh)\b|(?:POST|PUT|PATCH|DELETE)\s+/)"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", key.strip().lower()).strip("_")


def _path_label(parts: list[str]) -> str:
    return ".".join(parts)


def _walk(value: Any, path_parts: list[str]) -> list[tuple[list[str], Any]]:
    items = [(path_parts, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            items.extend(_walk(child, [*path_parts, str(key)]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_walk(child, [*path_parts, str(index)]))
    return items


def _walk_keys(value: Any, path_parts: list[str]) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_path = _path_label([*path_parts, str(key)])
            keys.append((key_path, str(key)))
            keys.extend(_walk_keys(child, [*path_parts, str(key)]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            keys.extend(_walk_keys(child, [*path_parts, str(index)]))
    return keys


def _get_path(document: Mapping[str, Any], dotted_path: str) -> tuple[bool, Any]:
    current: Any = document
    for part in dotted_path.split("."):
        if isinstance(current, Mapping) and part in current:
            current = current[part]
            continue
        if isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
            continue
        return False, None
    return True, current


def _validate_json_file(
    path: Path,
    validator: Draft7Validator,
) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]
    except OSError as exc:
        return None, [f"{path}: cannot read JSON: {exc}"]

    errors = [
        f"{path}: {_format_schema_error(schema_error)}"
        for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    ]
    return payload, errors


def _validate_forbidden_keys(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key_path, key in _walk_keys(payload, []):
        normalized = _normalize_key(key)
        if normalized in FORBIDDEN_AUTHORITY_KEYS:
            errors.append(f"{path}: forbidden authority/execution key at {key_path}: {key}")
    return errors


def _validate_forbidden_values(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for path_parts, value in _walk(payload, []):
        if not isinstance(value, str):
            continue
        normalized = _normalize_key(value)
        if normalized in FORBIDDEN_AUTHORITY_VALUES:
            errors.append(
                f"{path}: forbidden authority/execution value at {_path_label(path_parts)}: {value}"
            )
    return errors


def _validate_true_flags(path: Path, payload: Mapping[str, Any]) -> list[str]:
    found, declaration = _get_path(payload, "non_authority_declaration")
    if not found or not isinstance(declaration, Mapping):
        return [f"{path}: non_authority_declaration must be present as an object"]
    return [
        f"{path}: non_authority_declaration.{flag} must be true"
        for flag in sorted(NON_AUTHORITY_TRUE_FLAGS)
        if declaration.get(flag) is not True
    ]


def _validate_status_vocab(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for path_parts, value in _walk(payload, []):
        if not path_parts:
            continue
        key = str(path_parts[-1])
        if key == "status" and value not in STATUS_VOCAB:
            errors.append(f"{path}: {_path_label(path_parts)} invalid status: {value!r}")
        if key == "staleness_status" and value not in STALENESS_VOCAB:
            errors.append(f"{path}: {_path_label(path_parts)} invalid staleness_status: {value!r}")
    return errors


def _validate_source_refs(path: Path, payload: Mapping[str, Any]) -> list[str]:
    source_refs = payload.get("source_refs")
    if not isinstance(source_refs, list):
        return [f"{path}: source_refs must be present as an array"]

    errors: list[str] = []
    known_ref_ids: set[str] = set()
    for index, ref in enumerate(source_refs):
        if not isinstance(ref, Mapping):
            continue
        ref_id = ref.get("ref_id")
        if not isinstance(ref_id, str):
            continue
        if ref_id in known_ref_ids:
            errors.append(f"{path}: duplicate source_refs ref_id {ref_id!r}")
        known_ref_ids.add(ref_id)

    for path_parts, value in _walk(payload, []):
        if not path_parts or str(path_parts[-1]) != "source_refs":
            continue
        if len(path_parts) == 1:
            continue
        if not isinstance(value, list):
            continue
        for ref_id in value:
            if isinstance(ref_id, str) and ref_id not in known_ref_ids:
                errors.append(f"{path}: {_path_label(path_parts)} references unknown ref_id {ref_id!r}")
    return errors


def _validate_gate_actions(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    found, gates = _get_path(payload, "pages.gates.gates")
    if not found or not isinstance(gates, list):
        return errors
    for index, gate in enumerate(gates):
        if not isinstance(gate, Mapping):
            continue
        action = gate.get("required_human_action")
        if isinstance(action, str) and COMMAND_LIKE_GATE_ACTION_RE.search(action):
            errors.append(
                f"{path}: pages.gates.gates.{index}.required_human_action must not contain "
                "commands, endpoint URLs, or executable action text"
            )
    return errors


def validate_dashboard_data_file(path: Path, schema_path: Path = DEFAULT_SCHEMA_PATH) -> list[str]:
    """Return validation errors for one dashboard_data JSON file, or [] when valid."""

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    payload, errors = _validate_json_file(path, validator)
    if payload is None:
        return errors
    if errors:
        return errors

    errors.extend(_validate_forbidden_keys(path, payload))
    errors.extend(_validate_forbidden_values(path, payload))
    errors.extend(_validate_true_flags(path, payload))
    errors.extend(_validate_status_vocab(path, payload))
    errors.extend(_validate_source_refs(path, payload))
    errors.extend(_validate_gate_actions(path, payload))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="dashboard_data JSON file to validate.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    args = parser.parse_args(argv)

    errors = validate_dashboard_data_file(args.path, schema_path=args.schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: {args.path} validates as dashboard_data.v1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
