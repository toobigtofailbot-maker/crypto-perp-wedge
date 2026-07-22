from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from jsonschema import Draft7Validator

from tools.registry import validate_funding_series_provenance as validator


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "research/schemas/funding_series_provenance.schema.json"
PRODUCTION_ARTIFACT = next(
    (REPO_ROOT / "research/data_provenance/funding").glob("*.funding_provenance.json")
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(validator.canonical_json_bytes(payload))


def _fixture(
    root: Path,
    *,
    times: list[int] | None = None,
    rates: list[float] | None = None,
) -> tuple[Path, Path, dict[str, object]]:
    times = times or [1_704_067_200_000, 1_704_096_000_000, 1_704_124_800_000]
    rates = rates or [0.0001, -0.0002, 0.0]
    data_path = root / "data/processed/test_funding.parquet"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.table(
        {
            "symbol": pa.array(["BTCUSDT"] * len(times), type=pa.large_string()),
            "fundingTime": pa.array(times, type=pa.int64()),
            "fundingRate": pa.array(rates, type=pa.float64()),
            "markPrice": pa.array([None] + [50_000.0] * (len(times) - 1), type=pa.float64()),
        }
    )
    pq.write_table(table, data_path)
    digest = _sha256(data_path)
    start = validator._iso_from_ms(times[0])
    end = validator._iso_from_ms(times[-1])
    series_id = f"test_binance_usdtm_btcusdt_funding_{validator._compact_utc(start).lower()}_{validator._compact_utc(end).lower()}_sha256_{digest[:16]}"
    artifact_rel = f"research/data_provenance/funding/{series_id}.funding_provenance.json"
    payload = json.loads(PRODUCTION_ARTIFACT.read_text(encoding="utf-8"))
    payload["funding_series_id"] = series_id
    payload["provenance_artifact"]["path"] = artifact_rel
    payload["coverage"] = {"start_utc": start, "end_utc": end}
    payload["file_identity"].update(
        {
            "source_data_path": "data/processed/test_funding.parquet",
            "row_count": len(times),
            "byte_length": data_path.stat().st_size,
            "raw_sha256": f"sha256:{digest}",
            "column_schema": [
                {
                    "name": field.name,
                    "arrow_type": str(field.type),
                    "physical_nullable": field.nullable,
                    "required_non_null": field.name in validator.REQUIRED_NON_NULL_COLUMNS,
                    "observed_null_count": table.column(index).null_count,
                }
                for index, field in enumerate(table.schema)
            ],
        }
    )
    try:
        gaps, maximum_offset = validator._gap_inventory(pa.array(times).to_numpy())
    except validator.FundingProvenanceError:
        gaps, maximum_offset = [], 0
    payload["data_quality"]["gap_count"] = len(gaps)
    payload["data_quality"]["gap_inventory"] = gaps
    payload["cadence"]["observed_maximum_absolute_slot_offset_ms"] = maximum_offset
    payload["provenance_artifact"]["artifact_id"] = validator._expected_artifact_id(payload)
    artifact_path = root / artifact_rel
    _canonical_write(artifact_path, payload)
    return artifact_path, data_path, payload


def _rewrite(artifact_path: Path, payload: dict[str, object]) -> None:
    _canonical_write(artifact_path, payload)


def _validate(artifact_path: Path, root: Path):
    return validator.validate_artifact(
        artifact_path,
        schema_path=SCHEMA_PATH,
        repo_root=root,
        data_root=root,
    )


def test_schema_is_valid_draft_7_and_closed():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["additionalProperties"] is False


def test_valid_fixture_is_deterministic_and_binds_no_repair(tmp_path: Path):
    artifact, _, payload = _fixture(tmp_path)
    first = _validate(artifact, tmp_path)
    second = _validate(artifact, tmp_path)

    assert first == second
    assert first.ok is True
    assert first.row_count == 3
    assert first.gap_count == 0
    assert first.duplicate_timestamp_count == 0
    assert payload["policies"] == {
        "backfill": "forbidden",
        "duplicate_timestamp": "fail_closed",
        "forward_fill": "forbidden",
        "identity_mismatch": "fail_closed",
        "interpolation": "forbidden",
        "malformed_or_nonfinite_rate": "fail_closed",
        "missing_required_event": "fail_closed",
        "outside_declared_coverage": "reject",
        "repair": "none",
        "silent_repair": "forbidden",
        "zero_substitution": "forbidden",
    }


def test_wrong_hash_is_rejected(tmp_path: Path):
    artifact, _, payload = _fixture(tmp_path)
    payload["file_identity"]["raw_sha256"] = "sha256:" + "0" * 64
    _rewrite(artifact, payload)
    with pytest.raises(validator.FundingProvenanceError, match="RAW_SHA256_MISMATCH"):
        _validate(artifact, tmp_path)


def test_wrong_byte_length_is_rejected(tmp_path: Path):
    artifact, _, payload = _fixture(tmp_path)
    payload["file_identity"]["byte_length"] += 1
    _rewrite(artifact, payload)
    with pytest.raises(validator.FundingProvenanceError, match="BYTE_LENGTH_MISMATCH"):
        _validate(artifact, tmp_path)


def test_wrong_row_count_is_rejected(tmp_path: Path):
    artifact, _, payload = _fixture(tmp_path)
    payload["file_identity"]["row_count"] += 1
    _rewrite(artifact, payload)
    with pytest.raises(validator.FundingProvenanceError, match="ROW_COUNT_MISMATCH"):
        _validate(artifact, tmp_path)


def test_wrong_coverage_is_rejected(tmp_path: Path):
    artifact, _, payload = _fixture(tmp_path)
    payload["coverage"]["end_utc"] = "2024-01-02T00:00:00Z"
    payload["provenance_artifact"]["artifact_id"] = validator._expected_artifact_id(payload)
    _rewrite(artifact, payload)
    with pytest.raises(validator.FundingProvenanceError, match="COVERAGE_MISMATCH"):
        _validate(artifact, tmp_path)


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("event_fields.timestamp", "timezone", "America/New_York"),
        ("event_fields.funding_rate", "units", "percentage_points"),
        ("source", "public_private_classification", "private"),
        ("source", "network_fetch_allowed", True),
        ("source", "private_exchange_access_allowed", True),
        ("non_authority_declaration", "not_dispatch_or_execution_authority", False),
    ],
)
def test_forbidden_semantic_or_authority_claim_is_rejected(
    tmp_path: Path, section: str, field: str, value: object
):
    artifact, _, payload = _fixture(tmp_path)
    target = payload
    for part in section.split("."):
        target = target[part]
    target[field] = value
    _rewrite(artifact, payload)
    with pytest.raises(validator.FundingProvenanceError, match="SCHEMA_VALIDATION_ERROR"):
        _validate(artifact, tmp_path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("zero_substitution", "allowed"),
        ("interpolation", "allowed"),
        ("forward_fill", "allowed"),
        ("backfill", "allowed"),
        ("repair", "silent"),
    ],
)
def test_repair_or_fill_policy_is_rejected(tmp_path: Path, field: str, value: str):
    artifact, _, payload = _fixture(tmp_path)
    payload["policies"][field] = value
    _rewrite(artifact, payload)
    with pytest.raises(validator.FundingProvenanceError, match="SCHEMA_VALIDATION_ERROR"):
        _validate(artifact, tmp_path)


@pytest.mark.parametrize(("field", "value"), [("instrument", "ETHUSDT"), ("venue", "Other")])
def test_wrong_instrument_or_venue_is_rejected(
    tmp_path: Path, field: str, value: str
):
    artifact, _, payload = _fixture(tmp_path)
    payload["market_identity"][field] = value
    if field == "instrument":
        payload["provenance_artifact"]["artifact_id"] = validator._expected_artifact_id(payload)
    _rewrite(artifact, payload)
    with pytest.raises(validator.FundingProvenanceError):
        _validate(artifact, tmp_path)


def test_duplicate_timestamp_is_rejected(tmp_path: Path):
    artifact, _, _ = _fixture(
        tmp_path,
        times=[1_704_067_200_000, 1_704_067_200_000, 1_704_096_000_000],
    )
    with pytest.raises(validator.FundingProvenanceError, match="DUPLICATE_TIMESTAMP"):
        _validate(artifact, tmp_path)


def test_mismatched_gap_inventory_is_rejected(tmp_path: Path):
    artifact, _, payload = _fixture(
        tmp_path,
        times=[1_704_067_200_000, 1_704_124_800_000],
        rates=[0.0001, 0.0002],
    )
    payload["data_quality"]["gap_count"] = 0
    payload["data_quality"]["gap_inventory"] = []
    _rewrite(artifact, payload)
    with pytest.raises(validator.FundingProvenanceError, match="GAP_INVENTORY_MISMATCH"):
        _validate(artifact, tmp_path)


def test_nonfinite_rate_is_rejected(tmp_path: Path):
    artifact, _, _ = _fixture(tmp_path, rates=[0.0001, float("nan"), 0.0])
    with pytest.raises(validator.FundingProvenanceError, match="NONFINITE_FUNDING_RATE"):
        _validate(artifact, tmp_path)


def test_path_escape_is_rejected(tmp_path: Path):
    artifact, _, payload = _fixture(tmp_path)
    payload["file_identity"]["source_data_path"] = "../escape.parquet"
    _rewrite(artifact, payload)
    with pytest.raises(validator.FundingProvenanceError):
        _validate(artifact, tmp_path)


def test_source_symlink_is_rejected(tmp_path: Path):
    artifact, source, _ = _fixture(tmp_path)
    target = source.with_name("target.parquet")
    source.rename(target)
    try:
        source.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")
    with pytest.raises(validator.FundingProvenanceError, match="SYMLINK_REJECTED"):
        _validate(artifact, tmp_path)


def test_source_mutation_during_validation_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    artifact, source, _ = _fixture(tmp_path)
    original = validator._stat_signature(source)
    signatures = iter([original, (original[0], original[1] + 1)])
    monkeypatch.setattr(validator, "_stat_signature", lambda _: next(signatures))
    with pytest.raises(
        validator.FundingProvenanceError, match="SOURCE_MUTATED_DURING_VALIDATION"
    ):
        _validate(artifact, tmp_path)


def test_exact_local_production_artifact_when_data_root_is_supplied():
    configured = os.environ.get("FUNDING_PROVENANCE_DATA_ROOT")
    if not configured:
        pytest.skip("set FUNDING_PROVENANCE_DATA_ROOT to validate the gitignored local Parquet")
    result = validator.validate_artifact(
        PRODUCTION_ARTIFACT,
        schema_path=SCHEMA_PATH,
        repo_root=REPO_ROOT,
        data_root=Path(configured),
    )
    assert result.ok is True
    assert result.row_count == 7220
    assert result.source_data_sha256 == (
        "sha256:5f0da7478ccf3514af41dff9958b579cd2f797a2716001b0fa10a11059912798"
    )
