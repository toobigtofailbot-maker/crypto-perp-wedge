"""Catalog validated offline Binance USDT-M BTCUSDT 15m OHLCV data slices."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from tools.data.import_binance_usdtm_15m import (
    CONTRACT_VERSION,
    MARKET_TYPE,
    NORMALIZATION_VERSION,
    STREAM,
    SYMBOL,
    TIMEFRAME,
    sha256_bytes,
)
from tools.data.validate_binance_usdtm_15m import VALIDATOR_VERSION


CATALOG_VERSION = "wp-d4-offline-binance-usdtm-15m-catalog-v1"
SLICE_IDENTITY_VERSION = "binance-usdtm-btcusdt-ohlcv-15m-slice-identity-v1"
DATASET_ID = "binance_usdtm_btcusdt_ohlcv_15m"
SOURCE_TYPE = "offline_bulk_or_local_file"
VENUE = "Binance"
GAP_POLICY_REF = "docs/data/2026-06-binance_usdtm_15m_gap_policy.md"
CATALOG_DOC_REF = "docs/data/2026-06-binance_usdtm_15m_catalog_and_slice_identity.md"


class CatalogError(RuntimeError):
    """Raised when a validated data slice cannot be cataloged."""


@dataclass(frozen=True)
class CatalogResult:
    ok: bool
    catalog_path: str | None
    catalog_ref: str
    data_slice_identity: str
    normalized_sha256: str
    validation_report_sha256: str
    raw_source_sha256: str
    row_count: int
    expected_row_count: int
    start_utc: str
    end_utc: str


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CatalogError(f"cannot read JSON report: {path}") from exc
    if not isinstance(payload, dict):
        raise CatalogError(f"JSON report must be an object: {path}")
    return payload


def _hash_file(path: Path) -> str:
    if not path.exists():
        raise CatalogError(f"file does not exist: {path}")
    return sha256_bytes(path.read_bytes())


def _require_string(payload: dict[str, Any], key: str, label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise CatalogError(f"{label} must contain non-empty string field {key!r}")
    return value


def _import_report_raw_sha256(import_report: Path | None, raw_source_sha256: str | None) -> str:
    if raw_source_sha256:
        return raw_source_sha256
    if import_report is None:
        raise CatalogError("raw source sha256 is required via --import-report or --raw-source-sha256")
    payload = _load_json(import_report)
    source = payload.get("source")
    if not isinstance(source, dict):
        raise CatalogError("import report source object is required")
    return _require_string(source, "sha256", "import report source")


def _assert_expected_metadata(report: dict[str, Any], normalized_sha256: str) -> None:
    expected = {
        "data_contract_version": CONTRACT_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "symbol": SYMBOL,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": TIMEFRAME,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            raise CatalogError(f"validation report {key!r} must be {value!r}")

    if report.get("ok") is not True:
        raise CatalogError("validation report is not ok=true")
    validation = report.get("validation")
    if not isinstance(validation, dict) or validation.get("status") != "PASS":
        raise CatalogError("validation report status must be PASS")
    if validation.get("errors"):
        raise CatalogError("validation report PASS status must not include validation errors")

    source = report.get("source")
    if not isinstance(source, dict) or source.get("sha256") != normalized_sha256:
        raise CatalogError("normalized file sha256 does not match validation report source sha256")

    validated_output = report.get("validated_output")
    if isinstance(validated_output, dict) and validated_output.get("sha256") not in {None, normalized_sha256}:
        raise CatalogError("validated output sha256 conflicts with normalized file sha256")

    for summary_key, count_key in (
        ("gap_summary", "missing_bar_count"),
        ("duplicate_summary", "duplicate_row_count"),
    ):
        summary = report.get(summary_key)
        if not isinstance(summary, dict):
            raise CatalogError(f"validation report {summary_key} object is required")
        if int(summary.get(count_key, 0)) != 0:
            raise CatalogError(f"validation report {summary_key} must have zero {count_key}")


def _range_facts(report: dict[str, Any]) -> dict[str, Any]:
    range_payload = report.get("range")
    if not isinstance(range_payload, dict):
        raise CatalogError("validation report range object is required")
    start_utc = _require_string(range_payload, "start_utc", "validation report range")
    end_utc = _require_string(range_payload, "end_utc", "validation report range")
    row_count = int(range_payload.get("row_count", 0))
    expected_row_count = int(range_payload.get("expected_row_count", 0))
    if row_count <= 0:
        raise CatalogError("row_count must be positive")
    if row_count != expected_row_count:
        raise CatalogError("row_count must equal expected_row_count for a valid D4 catalog slice")
    return {
        "start_utc": start_utc,
        "end_utc": end_utc,
        "row_count": row_count,
        "expected_row_count": expected_row_count,
    }


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _identity_hash(identity_inputs: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json_bytes(identity_inputs)).hexdigest()


def _catalog_ref(start_utc: str, end_utc: str, slice_hash: str) -> str:
    start = start_utc.replace(":", "").replace("-", "").replace("Z", "Z")
    end = end_utc.replace(":", "").replace("-", "").replace("Z", "Z")
    return f"{DATASET_ID}.offline_local.{TIMEFRAME}.{start}.{end}.sha256_{slice_hash[:16]}"


def build_catalog_entry(
    *,
    normalized_path: Path,
    validation_report_path: Path,
    import_report_path: Path | None = None,
    raw_source_sha256: str | None = None,
) -> dict[str, Any]:
    normalized_sha256 = _hash_file(normalized_path)
    validation_report_sha256 = _hash_file(validation_report_path)
    raw_sha256 = _import_report_raw_sha256(import_report_path, raw_source_sha256)
    validation_report = _load_json(validation_report_path)
    _assert_expected_metadata(validation_report, normalized_sha256)
    range_facts = _range_facts(validation_report)

    gap_summary = {
        "gap_count": int(validation_report["gap_summary"].get("gap_count", 0)),
        "missing_bar_count": int(validation_report["gap_summary"].get("missing_bar_count", 0)),
        "gaps": validation_report["gap_summary"].get("gaps", []),
        "policy": validation_report["gap_summary"].get("policy"),
    }
    duplicate_summary = {
        "duplicate_group_count": int(validation_report["duplicate_summary"].get("duplicate_group_count", 0)),
        "duplicate_row_count": int(validation_report["duplicate_summary"].get("duplicate_row_count", 0)),
        "duplicates": validation_report["duplicate_summary"].get("duplicates", []),
        "policy": validation_report["duplicate_summary"].get("policy"),
    }
    identity_inputs = {
        "slice_identity_version": SLICE_IDENTITY_VERSION,
        "dataset_id": DATASET_ID,
        "symbol": SYMBOL,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": TIMEFRAME,
        "source_type": SOURCE_TYPE,
        "raw_source_sha256": raw_sha256,
        "normalized_sha256": normalized_sha256,
        "validation_report_sha256": validation_report_sha256,
        "validation_status": "PASS",
        "normalization_version": NORMALIZATION_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "gap_policy_ref": GAP_POLICY_REF,
        "range": range_facts,
        "gap_summary": gap_summary,
        "duplicate_summary": duplicate_summary,
    }
    slice_hash = _identity_hash(identity_inputs)
    data_slice_identity = f"{DATASET_ID}:sha256:{slice_hash}"
    catalog_ref = _catalog_ref(range_facts["start_utc"], range_facts["end_utc"], slice_hash)

    return {
        "catalog_version": CATALOG_VERSION,
        "catalog_ref": catalog_ref,
        "dataset_id": DATASET_ID,
        "catalog_status": "valid_offline_validated_slice",
        "source_type": SOURCE_TYPE,
        "symbol": SYMBOL,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": TIMEFRAME,
        "data_contract_version": CONTRACT_VERSION,
        "normalization_version": NORMALIZATION_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "gap_policy_ref": GAP_POLICY_REF,
        "catalog_doc_ref": CATALOG_DOC_REF,
        "source": {
            "raw_source_sha256": raw_sha256,
            "offline_local_input_only": True,
            "no_live_api": True,
            "no_credentials": True,
        },
        "normalized": {
            "path": str(normalized_path),
            "sha256": normalized_sha256,
        },
        "validation_report": {
            "path": str(validation_report_path),
            "sha256": validation_report_sha256,
            "status": "PASS",
        },
        "range": range_facts,
        "gap_summary": gap_summary,
        "duplicate_summary": duplicate_summary,
        "slice_identity": {
            "data_slice_identity": data_slice_identity,
            "hash": slice_hash,
            "hash_algorithm": "sha256",
            "identity_inputs": identity_inputs,
            "identity_input_ordering": "canonical_json_sort_keys_minified_ascii",
        },
        "d5_handoff": {
            "d3_validation_status_required": "PASS",
            "d4_catalog_status": "PASS",
            "karl_gate_required": True,
            "not_strategy_quality_evidence_by_itself": True,
            "no_result_population_created": True,
        },
        "boundary": {
            "offline_local_input_only": True,
            "no_exchange_contact": True,
            "no_runtime_contact": True,
            "no_paper_live_contact": True,
            "no_result_population_write": True,
            "no_strategy_artifact_mutation": True,
        },
    }


def write_catalog_entry(
    *,
    normalized_path: Path,
    validation_report_path: Path,
    output_path: Path,
    import_report_path: Path | None = None,
    raw_source_sha256: str | None = None,
) -> CatalogResult:
    entry = build_catalog_entry(
        normalized_path=normalized_path,
        validation_report_path=validation_report_path,
        import_report_path=import_report_path,
        raw_source_sha256=raw_source_sha256,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(entry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return CatalogResult(
        ok=True,
        catalog_path=str(output_path),
        catalog_ref=entry["catalog_ref"],
        data_slice_identity=entry["slice_identity"]["data_slice_identity"],
        normalized_sha256=entry["normalized"]["sha256"],
        validation_report_sha256=entry["validation_report"]["sha256"],
        raw_source_sha256=entry["source"]["raw_source_sha256"],
        row_count=int(entry["range"]["row_count"]),
        expected_row_count=int(entry["range"]["expected_row_count"]),
        start_utc=entry["range"]["start_utc"],
        end_utc=entry["range"]["end_utc"],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--normalized", required=True, type=Path, help="D2-normalized and D3-validated CSV.")
    parser.add_argument("--validation-report", required=True, type=Path, help="D3 PASS validation report JSON.")
    parser.add_argument("--output", required=True, type=Path, help="Catalog entry JSON output path.")
    parser.add_argument("--import-report", type=Path, help="Optional D2 import report carrying raw source sha256.")
    parser.add_argument("--raw-source-sha256", help="Explicit raw source sha256 if no D2 import report is supplied.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = write_catalog_entry(
            normalized_path=args.normalized,
            validation_report_path=args.validation_report,
            output_path=args.output,
            import_report_path=args.import_report,
            raw_source_sha256=args.raw_source_sha256,
        )
    except CatalogError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
