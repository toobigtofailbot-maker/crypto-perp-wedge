"""Validate a producer manifest carrying a generic research feature table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft7Validator

from tools.research_domain.feature_data import (
    FeatureDataContractError,
    validate_feature_table_contract,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "research_feature_table_manifest.schema.json"


def _schema_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path) or "<root>"
    return f"schema {path}: {error.message}"


def validate_manifest_payload(
    manifest: Mapping[str, Any],
    *,
    schema: Mapping[str, Any] | None = None,
) -> list[str]:
    block = manifest.get("research_feature_table")
    if not isinstance(block, Mapping):
        return ["manifest missing research_feature_table object"]
    active_schema = dict(schema) if schema is not None else json.loads(
        DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    Draft7Validator.check_schema(active_schema)
    schema_errors = sorted(
        Draft7Validator(active_schema).iter_errors(block),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    errors = [_schema_error(error) for error in schema_errors]
    if schema_errors:
        return errors
    source_files = manifest.get("source_files")
    source_identity_context = manifest.get("source_set_identity_context")
    stable_sources = None
    if isinstance(source_files, list):
        stable_sources = [
            {
                "logical_filename": Path(str(item.get("path", ""))).name,
                "sha256": item.get("sha256"),
                "size_bytes": item.get("size_bytes"),
                "parsed_row_count": item.get("parsed_row_count"),
                "source_type": item.get("source_type", manifest.get("archive_type")),
            }
            for item in source_files
            if isinstance(item, Mapping)
        ]
    try:
        validate_feature_table_contract(
            block,
            source_files=stable_sources,
            source_identity_context=(
                source_identity_context
                if isinstance(source_identity_context, Mapping)
                else None
            ),
        )
    except FeatureDataContractError as exc:
        errors.append(str(exc))
    return errors


def validate_research_feature_table_manifest(
    manifest_path: Path,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> list[str]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [str(exc)]
    if not isinstance(manifest, Mapping) or not isinstance(schema, Mapping):
        return ["manifest and schema must be JSON objects"]
    return validate_manifest_payload(manifest, schema=schema)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    args = parser.parse_args(argv)
    errors = validate_research_feature_table_manifest(args.manifest, args.schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: research feature-table manifest {args.manifest} validates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
