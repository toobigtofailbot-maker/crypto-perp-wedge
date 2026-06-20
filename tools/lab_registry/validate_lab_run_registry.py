"""Validate lab_run_registry.v1 JSON files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft7Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "lab_run_registry.schema.json"
STATUS_VOCAB = {"PASS", "WARN", "FAIL", "BLOCKED", "UNKNOWN", "NOT_AVAILABLE"}
FORBIDDEN_KEYS = {
    "rank",
    "leaderboard",
    "best_variant",
    "recommended_variant",
    "approved_strategy",
    "readiness",
    "ready_for_live",
    "ready_for_paper",
    "promotion_status",
    "execute",
    "place_order",
    "cancel_order",
    "start_paper_run",
    "start_live_run",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", key.strip().lower()).strip("_")


def _walk_keys(value: Any, parts: list[str]) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = ".".join([*parts, str(key)])
            keys.append((path, str(key)))
            keys.extend(_walk_keys(child, [*parts, str(key)]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            keys.extend(_walk_keys(child, [*parts, str(index)]))
    return keys


def _schema_errors(path: Path, payload: Mapping[str, Any], schema_path: Path) -> list[str]:
    schema = _load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    return [
        f"{path}: {'.'.join(str(part) for part in error.absolute_path)}: {error.message}"
        for error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    ]


def _semantic_errors(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key_path, key in _walk_keys(payload, []):
        if _normalize_key(key) in FORBIDDEN_KEYS:
            errors.append(f"{path}: forbidden authority/ranking key at {key_path}: {key}")

    records = payload.get("records", [])
    if isinstance(records, list):
        seen: set[str] = set()
        for index, record in enumerate(records):
            if not isinstance(record, Mapping):
                continue
            run_id = record.get("run_id")
            if isinstance(run_id, str):
                if run_id in seen:
                    errors.append(f"{path}: duplicate run_id {run_id!r}")
                seen.add(run_id)
            flags = record.get("non_authority_flags")
            if isinstance(flags, Mapping):
                for flag in [
                    "display_only",
                    "not_ranking_authority",
                    "not_recommendation",
                    "not_readiness",
                    "not_promotion",
                    "not_approval",
                    "not_execution",
                    "not_paper_live",
                ]:
                    if flags.get(flag) is not True:
                        errors.append(f"{path}: records.{index}.non_authority_flags.{flag} must be true")
            summary = record.get("result_summary")
            if isinstance(summary, Mapping):
                variant_ids = summary.get("variant_ids")
                if isinstance(variant_ids, list):
                    for pos in range(1, len(variant_ids)):
                        if str(variant_ids[pos]) <= str(variant_ids[pos - 1]):
                            errors.append(
                                f"{path}: records.{index}.result_summary.variant_ids must be ascending variant_id order"
                            )
                            break
    return errors


def validate_lab_run_registry_file(path: Path, schema_path: Path = DEFAULT_SCHEMA_PATH) -> list[str]:
    try:
        payload = _load_json(path)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"]
    except OSError as exc:
        return [f"{path}: cannot read JSON: {exc}"]
    errors = _schema_errors(path, payload, schema_path)
    if errors:
        return errors
    errors.extend(_semantic_errors(path, payload))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    args = parser.parse_args(argv)
    errors = validate_lab_run_registry_file(args.path, args.schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.path} validates as lab_run_registry.v1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

