from __future__ import annotations

import json
from pathlib import Path

from tools.data.import_binance_usdtm_15m import import_file
from tools.data.validate_binance_usdtm_15m import main, validate_file


def _write_source_csv(path: Path, rows: list[list[object]]) -> Path:
    lines = [
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
    ]
    lines.extend(",".join(str(value) for value in row) for row in rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _source_rows() -> list[list[object]]:
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


def _normalized_csv(tmp_path: Path, rows: list[list[object]] | None = None) -> Path:
    source = _write_source_csv(tmp_path / "source.csv", rows or _source_rows())
    normalized = tmp_path / "normalized.csv"
    result = import_file(source, normalized, tmp_path / "import_report.json")
    assert result.ok is True
    assert normalized.exists()
    return normalized


def _replace_line(path: Path, row_index: int, transform) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    row = lines[row_index + 1].split(",")
    lines[row_index + 1] = ",".join(transform(row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _drop_line(path: Path, row_index: int) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    del lines[row_index + 1]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_valid_d2_normalized_fixture_passes_and_can_write_validated_output(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)
    report = tmp_path / "validation_report.json"
    validated_output = tmp_path / "validated.csv"

    result = validate_file(normalized, report, validated_output_path=validated_output)
    payload = json.loads(report.read_text(encoding="utf-8"))

    assert result.ok is True
    assert result.row_count == 4
    assert result.expected_row_count == 4
    assert result.missing_bar_count == 0
    assert result.duplicate_row_count == 0
    assert validated_output.read_bytes() == normalized.read_bytes()
    assert payload["validation"]["status"] == "PASS"
    assert payload["validated_output"]["write_policy"] == "exact_input_bytes_only_after_validation_pass"
    assert payload["boundary"]["no_exchange_contact"] is True
    assert payload["boundary"]["no_result_population_write"] is True


def test_blank_optional_close_time_ms_is_allowed(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)
    lines = normalized.read_text(encoding="utf-8").splitlines()
    for index in range(1, len(lines)):
        row = lines[index].split(",")
        row[7] = ""
        lines[index] = ",".join(row)
    normalized.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = validate_file(normalized, tmp_path / "validation_report.json")

    assert result.ok is True


def test_gap_fixture_fails_with_explicit_missing_bar_count(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)
    _drop_line(normalized, 2)

    result = validate_file(normalized, tmp_path / "validation_report.json")

    assert result.ok is False
    assert result.missing_bar_count == 1
    assert any("missing 15m bars detected: 1 bars" in error for error in result.errors)


def test_duplicate_fixture_fails_with_duplicate_facts(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)

    def duplicate_timestamp(row: list[str]) -> list[str]:
        row[0] = "1704068100000"
        row[1] = "2024-01-01T00:15:00Z"
        return row

    _replace_line(normalized, 2, duplicate_timestamp)
    report = tmp_path / "validation_report.json"

    result = validate_file(normalized, report)
    payload = json.loads(report.read_text(encoding="utf-8"))

    assert result.ok is False
    assert result.duplicate_group_count == 1
    assert result.duplicate_row_count == 2
    assert payload["duplicate_summary"]["duplicates"] == [
        {"count": 2, "open_time_utc": "2024-01-01T00:15:00Z"}
    ]
    assert payload["duplicate_summary"]["policy"] == "detect_report_do_not_deduplicate"


def test_ohlc_inconsistency_fails(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)

    def bad_high(row: list[str]) -> list[str]:
        row[3] = "99"
        return row

    _replace_line(normalized, 1, bad_high)

    result = validate_file(normalized, tmp_path / "validation_report.json")

    assert result.ok is False
    assert any("high is below open/close" in error for error in result.errors)


def test_negative_volume_fails(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)

    def negative_volume(row: list[str]) -> list[str]:
        row[6] = "-1"
        return row

    _replace_line(normalized, 1, negative_volume)

    result = validate_file(normalized, tmp_path / "validation_report.json")

    assert result.ok is False
    assert any("volume is negative" in error for error in result.errors)


def test_timestamp_misalignment_fails(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)

    def misalign(row: list[str]) -> list[str]:
        row[0] = "1704068100001"
        return row

    _replace_line(normalized, 1, misalign)

    result = validate_file(normalized, tmp_path / "validation_report.json")

    assert result.ok is False
    assert any("open_time_ms and open_time disagree" in error for error in result.errors)
    assert any("not aligned to 15m UTC bars" in error for error in result.errors)


def test_open_time_ms_open_time_mismatch_fails(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)

    def mismatch(row: list[str]) -> list[str]:
        row[1] = "2024-01-01T00:16:00Z"
        return row

    _replace_line(normalized, 1, mismatch)

    result = validate_file(normalized, tmp_path / "validation_report.json")

    assert result.ok is False
    assert any("open_time_ms and open_time disagree" in error for error in result.errors)


def test_validation_report_is_deterministic(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)
    first_report = tmp_path / "validation_report.json"
    second_report = tmp_path / "validation_report_again.json"

    first = validate_file(normalized, first_report)
    second = validate_file(normalized, second_report)

    assert first.ok is True
    assert second.ok is True
    assert first_report.read_bytes() == second_report.read_bytes()


def test_invalid_input_does_not_create_downstream_consumable_output(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)
    _drop_line(normalized, 2)
    validated_output = tmp_path / "validated.csv"
    report = tmp_path / "validation_report.json"

    result = validate_file(normalized, report, validated_output_path=validated_output)
    payload = json.loads(report.read_text(encoding="utf-8"))

    assert result.ok is False
    assert result.validated_output_path is None
    assert validated_output.exists() is False
    assert payload["validation"]["status"] == "FAIL"
    assert payload["validated_output"]["path"] is None


def test_report_only_invalid_input_still_does_not_create_consumable_output(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)
    _drop_line(normalized, 2)
    validated_output = tmp_path / "validated.csv"
    report = tmp_path / "validation_report.json"

    exit_code = main(
        [
            "--input",
            str(normalized),
            "--report",
            str(report),
            "--validated-output",
            str(validated_output),
            "--allow-invalid-report-only",
        ]
    )
    payload = json.loads(report.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert validated_output.exists() is False
    assert payload["ok"] is False
    assert payload["validation"]["errors"]
    assert payload["boundary"]["invalid_data_report_only"] is True


def test_cli_invalid_without_report_only_returns_nonzero(tmp_path: Path):
    normalized = _normalized_csv(tmp_path)
    _drop_line(normalized, 2)

    exit_code = main(["--input", str(normalized), "--report", str(tmp_path / "report.json")])

    assert exit_code == 1
