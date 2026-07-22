"""Validate offline funding-series provenance artifacts without mutating data."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from jsonschema import Draft7Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research/schemas/funding_series_provenance.schema.json"
DEFAULT_ARTIFACTS_DIR = REPO_ROOT / "research/data_provenance/funding"
EXPECTED_CADENCE_MS = 28_800_000
GAP_TOLERANCE_MS = 60_000
REQUIRED_NON_NULL_COLUMNS = {"symbol", "fundingTime", "fundingRate"}


class FundingProvenanceError(RuntimeError):
    """Deterministic fail-closed provenance validation error."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    artifact_id: str
    artifact_path: str
    artifact_sha256: str
    funding_series_id: str
    source_data_path: str
    source_data_sha256: str
    row_count: int
    coverage_start_utc: str
    coverage_end_utc: str
    duplicate_timestamp_count: int
    gap_count: int


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stat_signature(path: Path) -> tuple[int, int]:
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns


def _logical_path(value: str, *, label: str) -> str:
    if "\\" in value:
        raise FundingProvenanceError("PATH_NOT_POSIX", f"{label} must use forward slashes")
    path = PurePosixPath(value)
    if path.is_absolute() or "." in path.parts or ".." in path.parts:
        raise FundingProvenanceError(
            "PATH_NOT_CONFINED", f"{label} must be a normalized repository-relative path"
        )
    return path.as_posix()


def _reject_symlink_components(root: Path, path: Path, *, label: str) -> None:
    root_absolute = root.absolute()
    path_absolute = path.absolute()
    try:
        relative = path_absolute.relative_to(root_absolute)
    except ValueError as exc:
        raise FundingProvenanceError(
            "PATH_NOT_CONFINED", f"{label} is outside configured root"
        ) from exc
    current = root_absolute
    if current.is_symlink():
        raise FundingProvenanceError("SYMLINK_REJECTED", f"{label} root is a symlink")
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise FundingProvenanceError(
                "SYMLINK_REJECTED", f"{label} contains symlink component: {part}"
            )


def _confined_existing_file(root: Path, relative_path: str, *, label: str) -> Path:
    logical = _logical_path(relative_path, label=label)
    root_resolved = root.resolve(strict=True)
    candidate = root_resolved.joinpath(*PurePosixPath(logical).parts)
    _reject_symlink_components(root_resolved, candidate, label=label)
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise FundingProvenanceError("FILE_NOT_FOUND", f"{label} does not exist: {logical}") from exc
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise FundingProvenanceError(
            "PATH_NOT_CONFINED", f"{label} resolves outside configured root"
        ) from exc
    if not resolved.is_file():
        raise FundingProvenanceError("FILE_NOT_FOUND", f"{label} is not a file: {logical}")
    return resolved


def _confine_supplied_file(root: Path, path: Path, *, label: str) -> tuple[Path, str]:
    root_resolved = root.resolve(strict=True)
    supplied = path if path.is_absolute() else root_resolved / path
    _reject_symlink_components(root_resolved, supplied, label=label)
    try:
        resolved = supplied.resolve(strict=True)
        logical = resolved.relative_to(root_resolved).as_posix()
    except FileNotFoundError as exc:
        raise FundingProvenanceError("FILE_NOT_FOUND", f"{label} does not exist: {path}") from exc
    except ValueError as exc:
        raise FundingProvenanceError(
            "PATH_NOT_CONFINED", f"{label} resolves outside configured root"
        ) from exc
    if not resolved.is_file():
        raise FundingProvenanceError("FILE_NOT_FOUND", f"{label} is not a file: {path}")
    return resolved, logical


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FundingProvenanceError("JSON_READ_ERROR", f"cannot read {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise FundingProvenanceError("JSON_TYPE_ERROR", f"{label} must be a JSON object")
    return payload


def _validate_schema(payload: dict[str, Any], schema: dict[str, Any]) -> None:
    try:
        Draft7Validator.check_schema(schema)
    except Exception as exc:
        raise FundingProvenanceError("SCHEMA_META_ERROR", str(exc)) from exc
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise FundingProvenanceError(
            "SCHEMA_VALIDATION_ERROR", f"{location}: {error.message}"
        )


def _iso_from_ms(value: int) -> str:
    timestamp = pd.to_datetime(value, unit="ms", utc=True)
    if value % 1000:
        return timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def _compact_utc(value: str) -> str:
    parsed = pd.Timestamp(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise FundingProvenanceError("TIMEZONE_MISMATCH", "coverage timestamps must be UTC")
    parsed = parsed.tz_convert("UTC")
    if parsed.microsecond:
        fraction = f"{parsed.microsecond:06d}".rstrip("0")
        return parsed.strftime("%Y%m%dT%H%M%S") + fraction + "Z"
    return parsed.strftime("%Y%m%dT%H%M%SZ")


def _expected_artifact_id(payload: dict[str, Any]) -> str:
    market = payload["market_identity"]
    return "-".join(
        [
            "FUNDING-PROV",
            market["venue"].upper(),
            "USDTM",
            market["instrument"].upper(),
            _compact_utc(payload["coverage"]["start_utc"]),
            _compact_utc(payload["coverage"]["end_utc"]),
            payload["file_identity"]["raw_sha256"].split(":", 1)[1][:16].upper(),
        ]
    )


def _validate_identity(payload: dict[str, Any], artifact_logical_path: str) -> None:
    series_id = payload["funding_series_id"]
    raw_hash = payload["file_identity"]["raw_sha256"].split(":", 1)[1]
    expected_suffix = f"_sha256_{raw_hash[:16]}"
    if not series_id.endswith(expected_suffix):
        raise FundingProvenanceError(
            "SERIES_IDENTITY_MISMATCH", "funding_series_id does not bind the raw SHA-256 prefix"
        )
    expected_path = f"research/data_provenance/funding/{series_id}.funding_provenance.json"
    declared_path = _logical_path(payload["provenance_artifact"]["path"], label="artifact path")
    if declared_path != expected_path or artifact_logical_path != expected_path:
        raise FundingProvenanceError(
            "ARTIFACT_IDENTITY_MISMATCH",
            f"artifact path must equal {expected_path}",
        )
    expected_id = _expected_artifact_id(payload)
    if payload["provenance_artifact"]["artifact_id"] != expected_id:
        raise FundingProvenanceError(
            "ARTIFACT_IDENTITY_MISMATCH", f"artifact_id must equal {expected_id}"
        )


def _observed_columns(table: Any) -> list[dict[str, Any]]:
    observed: list[dict[str, Any]] = []
    for index, field in enumerate(table.schema):
        observed.append(
            {
                "name": field.name,
                "arrow_type": str(field.type),
                "physical_nullable": bool(field.nullable),
                "observed_null_count": int(table.column(index).null_count),
            }
        )
    return observed


def _validate_columns(payload: dict[str, Any], table: Any) -> None:
    declared = payload["file_identity"]["column_schema"]
    observed = _observed_columns(table)
    if len(declared) != len(observed):
        raise FundingProvenanceError(
            "PARQUET_SCHEMA_MISMATCH", "declared and observed column counts differ"
        )
    for index, (expected, actual) in enumerate(zip(declared, observed)):
        for key in ("name", "arrow_type", "physical_nullable", "observed_null_count"):
            if expected[key] != actual[key]:
                raise FundingProvenanceError(
                    "PARQUET_SCHEMA_MISMATCH",
                    f"column {index} {key}: declared={expected[key]!r}, observed={actual[key]!r}",
                )
        should_require_non_null = expected["name"] in REQUIRED_NON_NULL_COLUMNS
        if expected["required_non_null"] is not should_require_non_null:
            raise FundingProvenanceError(
                "PARQUET_SCHEMA_MISMATCH",
                f"column {expected['name']} required_non_null must be {should_require_non_null}",
            )
        if expected["required_non_null"] and actual["observed_null_count"]:
            raise FundingProvenanceError(
                "NULL_REQUIRED_FIELD", f"column {expected['name']} contains null values"
            )


def _gap_inventory(times_ms: np.ndarray) -> tuple[list[dict[str, str]], int]:
    slots = np.floor_divide(times_ms + EXPECTED_CADENCE_MS // 2, EXPECTED_CADENCE_MS)
    offsets = np.abs(times_ms - slots * EXPECTED_CADENCE_MS)
    maximum_offset = int(offsets.max(initial=0))
    if maximum_offset > GAP_TOLERANCE_MS:
        raise FundingProvenanceError(
            "CADENCE_TOLERANCE_EXCEEDED",
            f"maximum nominal-slot offset {maximum_offset}ms exceeds {GAP_TOLERANCE_MS}ms",
        )
    inventory: list[dict[str, str]] = []
    for previous_slot, current_slot in zip(slots[:-1], slots[1:]):
        delta = int(current_slot - previous_slot)
        if delta <= 0:
            raise FundingProvenanceError(
                "CADENCE_SLOT_COLLISION", "multiple events map to one nominal 8h slot"
            )
        for missing_slot in range(int(previous_slot) + 1, int(current_slot)):
            inventory.append(
                {"missing_nominal_event_utc": _iso_from_ms(missing_slot * EXPECTED_CADENCE_MS)}
            )
    return inventory, maximum_offset


def validate_artifact(
    artifact_path: Path,
    *,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    repo_root: Path = REPO_ROOT,
    data_root: Path | None = None,
) -> ValidationResult:
    """Validate one artifact and its bound Parquet without writing either file."""
    artifact, artifact_logical_path = _confine_supplied_file(
        repo_root, artifact_path, label="provenance artifact"
    )
    schema = _load_json(schema_path.resolve(strict=True), label="schema")
    payload = _load_json(artifact, label="provenance artifact")
    _validate_schema(payload, schema)

    source_root = (data_root or repo_root).resolve(strict=True)
    source_logical_path = _logical_path(
        payload["file_identity"]["source_data_path"], label="source data path"
    )
    if not source_logical_path.startswith("data/processed/"):
        raise FundingProvenanceError(
            "PATH_NOT_CONFINED", "source data path must be below data/processed"
        )
    source = _confined_existing_file(source_root, source_logical_path, label="source data")
    if source.suffix.lower() != ".parquet":
        raise FundingProvenanceError("FILE_FORMAT_MISMATCH", "source data must be Parquet")

    before = _stat_signature(source)
    observed_length = source.stat().st_size
    if observed_length != payload["file_identity"]["byte_length"]:
        raise FundingProvenanceError(
            "BYTE_LENGTH_MISMATCH",
            f"declared={payload['file_identity']['byte_length']}, observed={observed_length}",
        )
    observed_hash = _sha256_file(source)
    declared_hash = payload["file_identity"]["raw_sha256"].split(":", 1)[1]
    if observed_hash != declared_hash:
        raise FundingProvenanceError(
            "RAW_SHA256_MISMATCH", f"declared={declared_hash}, observed={observed_hash}"
        )
    _validate_identity(payload, artifact_logical_path)

    try:
        table = pq.read_table(source)
    except Exception as exc:
        raise FundingProvenanceError("PARQUET_READ_ERROR", str(exc)) from exc
    if table.num_rows != payload["file_identity"]["row_count"]:
        raise FundingProvenanceError(
            "ROW_COUNT_MISMATCH",
            f"declared={payload['file_identity']['row_count']}, observed={table.num_rows}",
        )
    _validate_columns(payload, table)
    frame = table.to_pandas()

    symbol_values = sorted(str(value) for value in frame["symbol"].dropna().unique())
    expected_instrument = payload["market_identity"]["instrument"]
    if symbol_values != [expected_instrument]:
        raise FundingProvenanceError(
            "MARKET_IDENTITY_MISMATCH",
            f"declared instrument={expected_instrument}, observed symbols={symbol_values}",
        )

    timestamp_field = payload["event_fields"]["timestamp"]["field"]
    times_ms = frame[timestamp_field].astype("int64").to_numpy()
    if len(times_ms) == 0:
        raise FundingProvenanceError("ROW_COUNT_MISMATCH", "funding series is empty")
    deltas = np.diff(times_ms)
    duplicate_count = int(pd.Series(times_ms).duplicated(keep=False).sum())
    if duplicate_count:
        raise FundingProvenanceError(
            "DUPLICATE_TIMESTAMP", f"observed duplicate timestamp rows={duplicate_count}"
        )
    if np.any(deltas <= 0):
        raise FundingProvenanceError(
            "TIMESTAMP_ORDER_ERROR", "funding timestamps must be strictly increasing"
        )

    coverage_start = _iso_from_ms(int(times_ms[0]))
    coverage_end = _iso_from_ms(int(times_ms[-1]))
    if payload["coverage"] != {"start_utc": coverage_start, "end_utc": coverage_end}:
        raise FundingProvenanceError(
            "COVERAGE_MISMATCH",
            f"declared={payload['coverage']}, observed={{'start_utc': '{coverage_start}', 'end_utc': '{coverage_end}'}}",
        )

    gap_inventory, maximum_offset = _gap_inventory(times_ms)
    declared_quality = payload["data_quality"]
    if declared_quality["gap_count"] != len(gap_inventory) or declared_quality["gap_inventory"] != gap_inventory:
        raise FundingProvenanceError(
            "GAP_INVENTORY_MISMATCH",
            f"declared count={declared_quality['gap_count']}, observed count={len(gap_inventory)}",
        )
    if payload["cadence"]["observed_maximum_absolute_slot_offset_ms"] != maximum_offset:
        raise FundingProvenanceError(
            "CADENCE_OFFSET_MISMATCH",
            f"declared={payload['cadence']['observed_maximum_absolute_slot_offset_ms']}, observed={maximum_offset}",
        )

    rate_field = payload["event_fields"]["funding_rate"]["field"]
    rates = pd.to_numeric(frame[rate_field], errors="coerce").to_numpy(dtype="float64")
    nonfinite_count = int((~np.isfinite(rates)).sum())
    if nonfinite_count:
        raise FundingProvenanceError(
            "NONFINITE_FUNDING_RATE", f"observed non-finite funding rates={nonfinite_count}"
        )

    after = _stat_signature(source)
    if before != after:
        raise FundingProvenanceError(
            "SOURCE_MUTATED_DURING_VALIDATION", f"before={before}, after={after}"
        )

    return ValidationResult(
        ok=True,
        artifact_id=payload["provenance_artifact"]["artifact_id"],
        artifact_path=artifact_logical_path,
        artifact_sha256=f"sha256:{_sha256_file(artifact)}",
        funding_series_id=payload["funding_series_id"],
        source_data_path=source_logical_path,
        source_data_sha256=f"sha256:{observed_hash}",
        row_count=int(table.num_rows),
        coverage_start_utc=coverage_start,
        coverage_end_utc=coverage_end,
        duplicate_timestamp_count=duplicate_count,
        gap_count=len(gap_inventory),
    )


def _artifact_paths(directory: Path) -> Iterable[Path]:
    return sorted(directory.glob("*.funding_provenance.json"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--artifact", type=Path)
    group.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Checkout root containing the read-only data/processed file; defaults to repo root.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = [args.artifact] if args.artifact else list(_artifact_paths(args.artifacts_dir))
    if not paths:
        print(json.dumps({"errors": ["NO_ARTIFACTS: no provenance artifacts found"], "ok": False}, indent=2, sort_keys=True))
        return 1
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in paths:
        try:
            results.append(
                asdict(
                    validate_artifact(
                        path,
                        schema_path=args.schema,
                        repo_root=args.repo_root,
                        data_root=args.data_root,
                    )
                )
            )
        except (FundingProvenanceError, OSError, ValueError) as exc:
            errors.append(f"{path}: {exc}")
    output = {"errors": sorted(errors), "ok": not errors, "results": results}
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
