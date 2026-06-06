from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from tools.data.import_binance_usdtm_15m import import_file, main


def _write_csv(path: Path, rows: list[list[object]], *, header: bool = True) -> Path:
    lines: list[str] = []
    if header:
        lines.append(
            ",".join(
                [
                    "open_time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "close_time",
                    "quote_volume",
                    "trade_count",
                    "taker_buy_base_volume",
                    "taker_buy_quote_volume",
                    "ignore",
                ]
            )
        )
    for row in rows:
        lines.append(",".join(str(value) for value in row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _rows() -> list[list[object]]:
    base = 1_704_067_200_000
    rows: list[list[object]] = []
    for index in range(4):
        open_time = base + index * 900_000
        close_time = open_time + 899_999
        open_price = 100 + index
        close = open_price + 1
        rows.append(
            [
                open_time,
                open_price,
                close + 2,
                open_price - 2,
                close,
                10 + index,
                close_time,
                1000 + index,
                20 + index,
                5 + index,
                500 + index,
                0,
            ]
        )
    return rows


def _run_import(tmp_path: Path, source: Path):
    return import_file(
        source,
        tmp_path / "normalized.csv",
        tmp_path / "report.json",
    )


def test_valid_offline_fixture_imports_deterministically(tmp_path: Path):
    source = _write_csv(tmp_path / "source.csv", _rows())

    first = _run_import(tmp_path, source)
    first_bytes = (tmp_path / "normalized.csv").read_bytes()
    first_report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

    second = import_file(source, tmp_path / "normalized_again.csv", tmp_path / "report_again.json")
    second_bytes = (tmp_path / "normalized_again.csv").read_bytes()

    assert first.ok is True
    assert second.ok is True
    assert first.normalized_sha256 == second.normalized_sha256
    assert first_bytes == second_bytes
    assert first_report["range"]["row_count"] == 4
    assert first_report["range"]["expected_row_count"] == 4
    assert first_report["gap_summary"]["missing_bar_count"] == 0
    assert first_report["duplicate_summary"]["duplicate_row_count"] == 0
    assert first_report["boundary"]["no_exchange_contact"] is True
    assert "open_time_ms,open_time,open,high,low,close,volume" in first_bytes.decode("utf-8")


def test_headerless_binance_csv_imports(tmp_path: Path):
    source = _write_csv(tmp_path / "source.csv", _rows(), header=False)
    result = _run_import(tmp_path, source)
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

    assert result.ok is True
    assert report["normalized"]["sha256"] == result.normalized_sha256


def test_zip_with_single_csv_imports(tmp_path: Path):
    csv_path = _write_csv(tmp_path / "source.csv", _rows())
    zip_path = tmp_path / "source.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.write(csv_path, "nested/source.csv")

    result = _run_import(tmp_path, zip_path)
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

    assert result.ok is True
    assert report["source"]["member"] == "source.zip:nested/source.csv"


def test_duplicate_timestamps_are_detected_without_deduplication(tmp_path: Path):
    rows = _rows()
    rows[2][0] = rows[1][0]
    source = _write_csv(tmp_path / "source.csv", rows)

    result = _run_import(tmp_path, source)
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

    assert result.ok is False
    assert result.normalized_path is None
    assert report["duplicate_summary"]["duplicate_group_count"] == 1
    assert report["duplicate_summary"]["policy"] == "detect_report_do_not_deduplicate"
    assert not (tmp_path / "normalized.csv").exists()


def test_missing_15m_bar_is_detected_as_gap(tmp_path: Path):
    rows = _rows()
    rows.pop(2)
    source = _write_csv(tmp_path / "source.csv", rows)

    result = _run_import(tmp_path, source)
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

    assert result.ok is False
    assert report["gap_summary"]["missing_bar_count"] == 1
    assert report["gap_summary"]["policy"] == "detect_report_do_not_fill"


@pytest.mark.parametrize(
    ("column_index", "bad_value", "expected"),
    [
        (3, 105, "low is above open/close"),
        (2, 99, "high is below open/close"),
        (5, -1, "volume is negative"),
    ],
)
def test_ohlcv_inconsistency_or_negative_volume_is_rejected(
    tmp_path: Path, column_index: int, bad_value: object, expected: str
):
    rows = _rows()
    rows[1][column_index] = bad_value
    source = _write_csv(tmp_path / "source.csv", rows)

    result = _run_import(tmp_path, source)

    assert result.ok is False
    assert any(expected in error for error in result.errors)


def test_cli_returns_nonzero_for_invalid_source_unless_report_only(tmp_path: Path):
    rows = _rows()
    rows.pop(1)
    source = _write_csv(tmp_path / "source.csv", rows)
    output = tmp_path / "normalized.csv"
    report = tmp_path / "report.json"

    assert main(["--input", str(source), "--output", str(output), "--report", str(report)]) == 1
    assert output.exists() is False
    assert main(
        [
            "--input",
            str(source),
            "--output",
            str(output),
            "--report",
            str(report),
            "--allow-invalid-report-only",
        ]
    ) == 0
    assert output.exists() is True


def test_no_live_api_or_credential_path_is_used(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BINANCE_API_KEY", "must-not-be-read")
    monkeypatch.setenv("BINANCE_API_SECRET", "must-not-be-read")
    source = _write_csv(tmp_path / "source.csv", _rows())

    result = _run_import(tmp_path, source)
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

    assert result.ok is True
    assert report["source"]["no_live_api"] is True
    assert report["source"]["no_credentials"] is True
    assert report["boundary"]["no_runtime_contact"] is True
    assert report["boundary"]["no_result_population_write"] is True
