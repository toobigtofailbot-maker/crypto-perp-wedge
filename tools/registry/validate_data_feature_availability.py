"""Validate the data-derived feature availability catalog."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPILER_PATH = REPO_ROOT / "tools" / "research_runner" / "spec_signal_compiler.py"
DEFAULT_CATALOG_PATH = (
    REPO_ROOT
    / "research"
    / "data_feature_availability"
    / "PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
)
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "data_feature_availability.schema.json"
COVERAGE_CLASSES = {
    "FULL_HISTORY_PUBLIC_ARCHIVE",
    "RECENT_ONLY_PUBLIC_REST",
    "STREAMING_ONLY_PUBLIC_WS",
    "VENDOR_ONLY_FOR_HISTORY",
    "PUBLIC_SNAPSHOT_ONLY",
    "UNKNOWN_OR_BLOCKED",
}
TAKER_FLOW_FEATURES = {"taker_buy_sell_ratio", "taker_buy_volume", "taker_sell_volume"}


def _load_compiler_literal_set(name: str) -> set[str]:
    tree = ast.parse(COMPILER_PATH.read_text(encoding="utf-8"), filename=str(COMPILER_PATH))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            value = ast.literal_eval(node.value)
            if isinstance(value, set) and all(isinstance(item, str) for item in value):
                return value
    raise RuntimeError(f"compiler literal set not found or invalid: {name}")


DATA_DERIVED_COMPILER_FEATURES = _load_compiler_literal_set("ALLOWED_DATA_DERIVED_FIELDS")
TIMESTAMP_DERIVED_FEATURES = _load_compiler_literal_set("ALLOWED_TIMESTAMP_DERIVED_FIELDS")
CURRENT_COMPILER_FEATURES = DATA_DERIVED_COMPILER_FEATURES | TIMESTAMP_DERIVED_FEATURES


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_schema_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path) or "<root>"
    return f"schema {path}: {error.message}"


def build_catalog_index(
    catalog: Mapping[str, Any],
) -> dict[tuple[str, str], Mapping[str, Any]]:
    """Return availability entries keyed by feature and source class."""

    index: dict[tuple[str, str], Mapping[str, Any]] = {}
    entries = catalog.get("entries")
    if not isinstance(entries, list):
        return index
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        feature_name = entry.get("feature_name")
        source_class = entry.get("source_class")
        if isinstance(feature_name, str) and isinstance(source_class, str):
            index[(feature_name, source_class)] = entry
    return index


def validate_catalog_payload(catalog: Mapping[str, Any]) -> list[str]:
    """Return deterministic semantic errors for a schema-valid catalog payload."""

    errors: list[str] = []
    declared_classes = catalog.get("coverage_classes")
    if isinstance(declared_classes, list) and set(declared_classes) != COVERAGE_CLASSES:
        errors.append("coverage_classes must declare the exact locked coverage-class set")

    entries = catalog.get("entries")
    if not isinstance(entries, list):
        return errors

    seen_keys: set[tuple[str, str]] = set()
    compiler_labeled: set[str] = set()
    entries_by_feature: dict[str, list[Mapping[str, Any]]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            continue
        feature = entry.get("feature_name")
        source = entry.get("source_class")
        if not isinstance(feature, str) or not isinstance(source, str):
            continue
        key = (feature, source)
        if key in seen_keys:
            errors.append(f"entries.{index}: duplicate feature/source key {feature}/{source}")
        seen_keys.add(key)
        entries_by_feature.setdefault(feature, []).append(entry)
        if entry.get("compiler_visible") is True:
            compiler_labeled.add(feature)

        coverage_class = entry.get("coverage_class")
        allowed = entry.get("canonical_full_history_allowed")
        if coverage_class != "FULL_HISTORY_PUBLIC_ARCHIVE" and allowed != "no":
            errors.append(
                f"entries.{index}: {coverage_class} must set canonical_full_history_allowed to no"
            )
        if coverage_class == "FULL_HISTORY_PUBLIC_ARCHIVE" and allowed == "no":
            errors.append(
                f"entries.{index}: full-history public archive entry must be yes or conditional"
            )
        if source == "PUBLIC_TRADE_ARCHIVE_DERIVATION" and feature not in TAKER_FLOW_FEATURES:
            errors.append(
                f"entries.{index}: trade archives may classify taker-flow features only, not {feature}"
            )

    missing = sorted(CURRENT_COMPILER_FEATURES - compiler_labeled)
    unknown = sorted(compiler_labeled - CURRENT_COMPILER_FEATURES)
    if missing:
        errors.append(f"current compiler features missing availability labels: {', '.join(missing)}")
    if unknown:
        errors.append(f"unknown features marked compiler_visible: {', '.join(unknown)}")

    for feature in sorted(TIMESTAMP_DERIVED_FEATURES):
        feature_entries = entries_by_feature.get(feature, [])
        if not any(
            entry.get("source_class") == "DERIVED_FROM_BAR_TIMESTAMP"
            and entry.get("coverage_class") == "FULL_HISTORY_PUBLIC_ARCHIVE"
            and entry.get("canonical_full_history_allowed") == "conditional"
            for entry in feature_entries
        ):
            errors.append(
                f"{feature} must be bar-timestamp-derived and full-history-if-bars-exist"
            )

    for feature in ("open_interest", "open_interest_value"):
        for entry in entries_by_feature.get(feature, []):
            if entry.get("coverage_class") == "FULL_HISTORY_PUBLIC_ARCHIVE":
                errors.append(f"{feature} must not claim public archive full-history coverage")
            notes = str(entry.get("notes", "")).lower()
            if feature == "open_interest" and "cannot reconstruct true open interest" not in notes:
                errors.append(
                    "open_interest notes must state that trades cannot reconstruct true open interest"
                )

    for feature in sorted(TAKER_FLOW_FEATURES):
        feature_entries = entries_by_feature.get(feature, [])
        if not any(
            entry.get("source_class") == "PUBLIC_REST_TAKER_RATIO"
            and entry.get("coverage_class") == "RECENT_ONLY_PUBLIC_REST"
            for entry in feature_entries
        ):
            errors.append(f"{feature} must retain a recent-only public REST classification")
        if not any(
            entry.get("source_class") == "PUBLIC_TRADE_ARCHIVE_DERIVATION"
            and entry.get("coverage_class") == "FULL_HISTORY_PUBLIC_ARCHIVE"
            for entry in feature_entries
        ):
            errors.append(f"{feature} must expose the conditional public archive derivation")

    return errors


def validate_data_feature_availability(
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> list[str]:
    """Return catalog validation errors, or an empty list when valid."""

    if not catalog_path.exists():
        return [f"availability catalog not found: {catalog_path}"]
    if not schema_path.exists():
        return [f"availability schema not found: {schema_path}"]

    try:
        schema = load_json(schema_path)
        catalog = load_json(catalog_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [str(exc)]

    Draft7Validator.check_schema(schema)
    schema_errors = sorted(
        Draft7Validator(schema).iter_errors(catalog),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    errors = [_format_schema_error(error) for error in schema_errors]
    if not schema_errors:
        errors.extend(validate_catalog_payload(catalog))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_data_feature_availability(args.catalog, args.schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: data feature availability catalog {args.catalog} validates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
