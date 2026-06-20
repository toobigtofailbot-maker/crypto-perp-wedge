"""Validate draft-only structured research idea artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "research_idea.schema.json"

ACCEPTED_CLASSIFICATIONS = {
    "current_lab_testable",
    "near_term_minor_upgrade",
    "upgrade_dependent_data",
    "upgrade_dependent_simulator",
    "needs_research",
}
REJECTED_CLASSIFICATIONS = {"rejected_non_causal", "rejected_untestable"}

# These checks intentionally target directive-like language, not isolated words
# such as "future" in a failure-mode discussion.
FORBIDDEN_TEXT_PATTERNS = (
    ("unbounded_search", re.compile(r"\b(unbounded|all possible|any possible|no bounds?)\b", re.I)),
    ("magic_optimizer", re.compile(r"\b(ai|llm)\s+(optimi[sz]e|find)\s+(everything|anything|the best)\b", re.I)),
    ("future_lookahead", re.compile(r"\b(look[ -]?ahead|future price|tomorrow'?s (price|close)|next bar close)\b", re.I)),
    ("same_bar_leakage", re.compile(r"\b(same[ -]?bar (close )?(entry|fill)|enter at (the )?current close)\b", re.I)),
    ("executable_code", re.compile(r"(```|\bdef\s+[A-Za-z_]\w*\s*\(|\bimport\s+[A-Za-z_]|\beval\s*\(|\bexec\s*\()", re.I)),
    ("trade_instruction", re.compile(r"\b(place|submit|cancel|execute)\s+(a |an )?(live |paper )?(order|trade)\b", re.I)),
    ("capital_instruction", re.compile(r"\b(risk|allocate|use)\s+(all|\d+(?:\.\d+)?\s*%)\s+(of\s+)?(capital|equity|account)\b", re.I)),
)


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load JSON from {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def _walk_strings(value: Any, path: str = "") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from _walk_strings(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_strings(child, f"{path}.{index}")


def _schema_errors(payload: dict[str, Any], schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{location}: {error.message}")
    return errors


def _semantic_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    created_at = payload.get("created_at_utc")
    if isinstance(created_at, str):
        try:
            parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            if parsed.utcoffset() != timedelta(0):
                errors.append("created_at_utc must be UTC")
        except ValueError:
            pass  # JSON Schema reports malformed date-time values.

    for location, text in _walk_strings(payload):
        if location.startswith("rejection_reasons"):
            continue
        for label, pattern in FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(text):
                errors.append(f"{location}: forbidden {label} directive")

    classification = payload.get("classification")
    rejection_reasons = payload.get("rejection_reasons")
    if classification in REJECTED_CLASSIFICATIONS:
        errors.append(f"classification {classification} is an early-rejection outcome, not a valid accepted research idea")
    elif classification in ACCEPTED_CLASSIFICATIONS and rejection_reasons:
        errors.append("accepted classification requires empty rejection_reasons")

    parameters = payload.get("parameter_ranges")
    if classification in ACCEPTED_CLASSIFICATIONS:
        if not isinstance(parameters, list) or not parameters:
            errors.append("accepted research ideas require at least one bounded parameter range")
        else:
            seen: set[str] = set()
            variant_count = 1
            for parameter in parameters:
                if not isinstance(parameter, dict):
                    continue
                name = parameter.get("name")
                if isinstance(name, str):
                    if name in seen:
                        errors.append(f"duplicate parameter range name: {name}")
                    seen.add(name)
                minimum = parameter.get("minimum")
                maximum = parameter.get("maximum")
                values = parameter.get("values")
                if isinstance(minimum, (int, float)) and isinstance(maximum, (int, float)):
                    if minimum > maximum:
                        errors.append(f"parameter {name}: minimum must be <= maximum")
                    if isinstance(values, list):
                        for value in values:
                            if isinstance(value, (int, float)) and not minimum <= value <= maximum:
                                errors.append(f"parameter {name}: value {value} is outside declared bounds")
                if parameter.get("value_type") == "integer" and isinstance(values, list):
                    if any(not isinstance(value, int) or isinstance(value, bool) for value in values):
                        errors.append(f"parameter {name}: integer range contains a non-integer value")
                if isinstance(values, list):
                    variant_count *= len(values)
            if variant_count > 500:
                errors.append(f"bounded parameter grid expands to {variant_count} variants; maximum is 500")

    compatibility = payload.get("current_lab_compatibility")
    dependencies = payload.get("upgrade_dependencies")
    is_testable = compatibility.get("is_testable") if isinstance(compatibility, dict) else None
    if classification == "current_lab_testable":
        if is_testable is not True:
            errors.append("current_lab_testable requires current_lab_compatibility.is_testable=true")
        if dependencies:
            errors.append("current_lab_testable requires empty upgrade_dependencies")
    if classification in {"near_term_minor_upgrade", "upgrade_dependent_data", "upgrade_dependent_simulator"}:
        if is_testable is not False:
            errors.append(f"{classification} requires current_lab_compatibility.is_testable=false")
        if not dependencies:
            errors.append(f"{classification} requires at least one blocking upgrade dependency")
    if classification == "upgrade_dependent_data" and isinstance(dependencies, list):
        if not any(item.get("dependency_type") == "data" for item in dependencies if isinstance(item, dict)):
            errors.append("upgrade_dependent_data requires a data dependency")
    if classification == "upgrade_dependent_simulator" and isinstance(dependencies, list):
        if not any(item.get("dependency_type") == "simulator" for item in dependencies if isinstance(item, dict)):
            errors.append("upgrade_dependent_simulator requires a simulator dependency")

    timeframe = payload.get("timeframe")
    if isinstance(timeframe, dict) and timeframe.get("primary") in timeframe.get("confirmations", []):
        errors.append("primary timeframe must not be repeated in confirmation timeframes")

    return errors


def validate_payload(
    payload: dict[str, Any], *, schema_path: Path = DEFAULT_SCHEMA_PATH
) -> list[str]:
    """Return deterministic structural and semantic validation errors."""

    return _schema_errors(payload, schema_path) + _semantic_errors(payload)


def validate_path(path: Path, *, schema_path: Path = DEFAULT_SCHEMA_PATH) -> list[str]:
    try:
        payload = load_json(path)
    except ValueError as exc:
        return [str(exc)]
    return validate_payload(payload, schema_path=schema_path)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    errors = validate_path(args.path, schema_path=args.schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
