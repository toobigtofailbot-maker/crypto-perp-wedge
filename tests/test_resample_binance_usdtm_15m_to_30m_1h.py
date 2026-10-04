from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from tools.data import resample_binance_usdtm_15m_to_30m_1h as resampler


def _iso(open_ms: int) -> str:
    from datetime import datetime, timezone

    return (
        datetime.fromtimestamp(open_ms / 1000, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _rows(count: int, *, start_ms: int = 0) -> list[dict[str, str]]:
    rows = []
    for index in range(count):
        open_ms = start_ms + index * resampler.PARENT_CADENCE_MS
        base = 100 + index
        rows.append(
            {
                "open_time_ms": str(open_ms),
                "open_time": _iso(open_ms),
                "open": str(base),
                "high": str(base + 3),
                "low": str(base - 2),
                "close": str(base + 1),
                "volume": f"{index + 1}.25",
                "close_time_ms": str(open_ms + resampler.PARENT_CADENCE_MS - 1),
                "quote_asset_volume": f"{index + 10}.125",
                "num_trades": str(index + 5),
                "taker_buy_base_vol": f"{index + 1}.125",
                "taker_buy_quote_vol": f"{index + 2}.0625",
                "ignore": str(index),
            }
        )
    return rows


def _config(timeframe: str, group_size: int, row_count: int) -> resampler.TargetConfig:
    cadence_ms = group_size * resampler.PARENT_CADENCE_MS
    return replace(
        resampler.TARGETS[timeframe],
        group_size=group_size,
        cadence_ms=cadence_ms,
        expected_row_count=row_count,
        expected_start_utc=_iso(0),
        expected_end_utc=_iso((row_count - 1) * cadence_ms),
    )


def _patch_small_parent(monkeypatch: pytest.MonkeyPatch, rows: list[dict[str, str]]) -> None:
    monkeypatch.setattr(resampler, "PARENT_ROW_COUNT", len(rows))
    monkeypatch.setattr(resampler, "PARENT_START_UTC", rows[0]["open_time"])
    monkeypatch.setattr(resampler, "PARENT_END_UTC", rows[-1]["open_time"])


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=resampler.OUTPUT_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _json_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _metadata_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    rows: list[dict[str, str]],
) -> tuple[Path, Path, Path]:
    parent_csv = tmp_path / "parent.csv"
    parent_catalog = tmp_path / "parent.catalog.json"
    parent_validation = tmp_path / "parent.validation.json"
    _write_csv(parent_csv, rows)
    validation = {"ok": True, "validation": {"status": "PASS"}}
    parent_validation.write_bytes(_json_bytes(validation))
    parent_sha = hashlib.sha256(parent_csv.read_bytes()).hexdigest()
    validation_sha = hashlib.sha256(parent_validation.read_bytes()).hexdigest()
    catalog = {
        "dataset_id": resampler.PARENT_DATASET_ID,
        "timeframe": "15m",
        "catalog_ref": "fixture-parent-catalog",
        "normalized": {"sha256": parent_sha},
        "validation_report": {"sha256": validation_sha, "status": "PASS"},
        "slice_identity": {
            "data_slice_identity": resampler.PARENT_DATA_SLICE_IDENTITY
        },
    }
    parent_catalog.write_bytes(_json_bytes(catalog))
    _patch_small_parent(monkeypatch, rows)
    monkeypatch.setattr(resampler, "PARENT_NORMALIZED_SHA256", parent_sha)
    monkeypatch.setattr(resampler, "PARENT_VALIDATION_SHA256", validation_sha)
    return parent_csv, parent_catalog, parent_validation


def _derive_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    rows: list[dict[str, str]],
) -> resampler.ResampleResult:
    parent_csv, parent_catalog, parent_validation = _metadata_fixture(
        tmp_path, monkeypatch, rows
    )
    group_size = 2 if target == "30m" else 4
    config = _config(target, group_size, len(rows) // group_size)
    configs = dict(resampler.TARGETS)
    configs[target] = config
    monkeypatch.setattr(resampler, "TARGETS", configs)
    return resampler.derive_slice(
        target,
        parent_csv_path=parent_csv,
        parent_catalog_path=parent_catalog,
        parent_validation_path=parent_validation,
        output_csv_path=tmp_path / f"{target}.csv",
        validation_report_path=tmp_path / f"{target}.validation.json",
        derivation_report_path=tmp_path / f"{target}.derivation.json",
        catalog_path=tmp_path / f"{target}.catalog.json",
    )


def test_target_set_is_closed_and_configs_are_distinct_and_immutable():
    assert tuple(resampler.TARGETS) == ("30m", "1h")
    assert resampler.TARGETS["30m"].group_size == 2
    assert resampler.TARGETS["1h"].group_size == 4
    with pytest.raises(TypeError):
        resampler.TARGETS["4h"] = resampler.TARGETS["1h"]
    with pytest.raises(resampler.ResampleError, match="unsupported target"):
        resampler.derive_slice("4h")


@pytest.mark.parametrize(("target", "group_size"), [("30m", 2), ("1h", 4)])
def test_exact_grouping_aggregation_and_close_time(
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    group_size: int,
):
    rows = _rows(group_size * 2)
    _patch_small_parent(monkeypatch, rows)
    output, facts = resampler.resample_rows(rows, _config(target, group_size, 2))
    first = output[0]
    assert first == {
        "open_time_ms": "0",
        "open_time": "1970-01-01T00:00:00Z",
        "open": "100",
        "high": str(100 + group_size - 1 + 3),
        "low": "98",
        "close": str(100 + group_size - 1 + 1),
        "volume": resampler._decimal_string(
            sum((Decimal(index) + Decimal("1.25") for index in range(group_size)), Decimal(0))
        ),
        "close_time_ms": str(group_size * resampler.PARENT_CADENCE_MS - 1),
        "quote_asset_volume": resampler._decimal_string(
            sum((Decimal(index) + Decimal("10.125") for index in range(group_size)), Decimal(0))
        ),
        "num_trades": str(sum(index + 5 for index in range(group_size))),
        "taker_buy_base_vol": resampler._decimal_string(
            sum((Decimal(index) + Decimal("1.125") for index in range(group_size)), Decimal(0))
        ),
        "taker_buy_quote_vol": resampler._decimal_string(
            sum((Decimal(index) + Decimal("2.0625") for index in range(group_size)), Decimal(0))
        ),
        "ignore": str(sum(range(group_size))),
    }
    assert facts["partial_window_count"] == 0
    assert facts["gap_count"] == 0
    assert facts["duplicate_row_count"] == 0


def test_non_utc_boundary_fails(monkeypatch: pytest.MonkeyPatch):
    rows = _rows(4, start_ms=resampler.PARENT_CADENCE_MS)
    _patch_small_parent(monkeypatch, rows)
    config = replace(
        _config("30m", 2, 2),
        expected_start_utc=rows[0]["open_time"],
        expected_end_utc=rows[2]["open_time"],
    )
    with pytest.raises(resampler.ResampleError, match="non-UTC-boundary"):
        resampler.resample_rows(rows, config)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "partial"])
def test_missing_duplicate_and_partial_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
):
    rows = _rows(4)
    if mutation == "missing":
        rows.pop(1)
    elif mutation == "duplicate":
        rows[1] = dict(rows[0])
    else:
        rows = rows[:3]
    _patch_small_parent(monkeypatch, rows)
    with pytest.raises(resampler.ResampleError):
        resampler.resample_rows(rows, _config("30m", 2, 2))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("open_time_ms", "bad"),
        ("open", "nan"),
        ("num_trades", "1.5"),
        ("open_time", "1970-01-02T00:00:00Z"),
        ("close_time_ms", "1"),
    ],
)
def test_malformed_parent_fails(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: str,
):
    rows = _rows(4)
    rows[0][field] = value
    _patch_small_parent(monkeypatch, rows)
    with pytest.raises(resampler.ResampleError):
        resampler.resample_rows(rows, _config("30m", 2, 2))


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("parent_sha", "parent normalized SHA differs"),
        ("catalog_identity", "parent identity differs"),
        ("validation_sha", "parent validation SHA differs"),
        ("validation_status", "validation status"),
    ],
)
def test_parent_metadata_binding_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
    message: str,
):
    rows = _rows(4)
    parent_csv, catalog_path, validation_path = _metadata_fixture(
        tmp_path, monkeypatch, rows
    )
    if mutation == "parent_sha":
        monkeypatch.setattr(resampler, "PARENT_NORMALIZED_SHA256", "0" * 64)
    elif mutation == "catalog_identity":
        catalog = json.loads(catalog_path.read_text())
        catalog["slice_identity"]["data_slice_identity"] = "wrong"
        catalog_path.write_bytes(_json_bytes(catalog))
    elif mutation == "validation_sha":
        monkeypatch.setattr(resampler, "PARENT_VALIDATION_SHA256", "0" * 64)
    else:
        validation = json.loads(validation_path.read_text())
        validation["validation"]["status"] = "FAIL"
        validation_path.write_bytes(_json_bytes(validation))
        changed_sha = hashlib.sha256(validation_path.read_bytes()).hexdigest()
        monkeypatch.setattr(resampler, "PARENT_VALIDATION_SHA256", changed_sha)
        catalog = json.loads(catalog_path.read_text())
        catalog["validation_report"]["sha256"] = changed_sha
        catalog_path.write_bytes(_json_bytes(catalog))
    with pytest.raises(resampler.ResampleError, match=message):
        resampler.derive_slice(
            "30m",
            parent_csv_path=parent_csv,
            parent_catalog_path=catalog_path,
            parent_validation_path=validation_path,
        )


def test_csv_json_and_identity_are_deterministic(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    rows = _rows(8)
    first = _derive_fixture(tmp_path / "first", monkeypatch, "1h", rows)
    first_bytes = {
        Path(first.output_csv_path).name: Path(first.output_csv_path).read_bytes(),
        Path(first.validation_report_path).name: Path(first.validation_report_path).read_bytes(),
        Path(first.derivation_report_path).name: Path(first.derivation_report_path).read_bytes(),
        Path(first.catalog_path).name: Path(first.catalog_path).read_bytes(),
    }
    second = _derive_fixture(tmp_path / "first", monkeypatch, "1h", rows)
    assert first == second
    assert first_bytes == {
        Path(second.output_csv_path).name: Path(second.output_csv_path).read_bytes(),
        Path(second.validation_report_path).name: Path(second.validation_report_path).read_bytes(),
        Path(second.derivation_report_path).name: Path(second.derivation_report_path).read_bytes(),
        Path(second.catalog_path).name: Path(second.catalog_path).read_bytes(),
    }
    assert b"\r\n" not in Path(second.catalog_path).read_bytes()
    catalog = json.loads(Path(second.catalog_path).read_text())
    derivation = catalog["derivation"]
    assert derivation["no_fill"] is True
    assert derivation["no_interpolation"] is True
    assert derivation["no_deduplication"] is True
    assert derivation["no_synthetic_bars"] is True


def test_parent_byte_change_changes_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    rows = _rows(4)
    first = _derive_fixture(tmp_path / "same", monkeypatch, "30m", rows)
    changed = [dict(row) for row in rows]
    changed[0]["volume"] = "9.25"
    changed[0]["quote_asset_volume"] = "900.125"
    second = _derive_fixture(tmp_path / "same", monkeypatch, "30m", changed)
    assert first.output_csv_sha256 != second.output_csv_sha256
    assert first.data_slice_identity != second.data_slice_identity
