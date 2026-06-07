from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.data.catalog_binance_usdtm_15m import (
    CatalogError,
    build_catalog_entry,
    main,
    write_catalog_entry,
)
from tools.data.import_binance_usdtm_15m import import_file
from tools.data.validate_binance_usdtm_15m import validate_file


def _write_source_csv(path: Path, rows: list[list[object]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def _valid_slice(tmp_path: Path, rows: list[list[object]] | None = None) -> tuple[Path, Path, Path]:
    source = _write_source_csv(tmp_path / "source.csv", rows or _source_rows())
    normalized = tmp_path / "normalized.csv"
    import_report = tmp_path / "import_report.json"
    validation_report = tmp_path / "validation_report.json"
    import_result = import_file(source, normalized, import_report)
    assert import_result.ok is True
    validation_result = validate_file(normalized, validation_report)
    assert validation_result.ok is True
    return normalized, import_report, validation_report


def _entry(tmp_path: Path) -> dict:
    normalized, import_report, validation_report = _valid_slice(tmp_path)
    return build_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
    )


def _slice_identity(entry: dict) -> str:
    return entry["slice_identity"]["data_slice_identity"]


def _mutate_report(path: Path, mutator) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_valid_d2_d3_fixture_produces_deterministic_catalog_entry(tmp_path: Path):
    normalized, import_report, validation_report = _valid_slice(tmp_path)
    first_output = tmp_path / "catalog.json"
    second_output = tmp_path / "catalog_again.json"

    first = write_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
        output_path=first_output,
    )
    second = write_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
        output_path=second_output,
    )
    first_payload = json.loads(first_output.read_text(encoding="utf-8"))

    assert first.ok is True
    assert second.ok is True
    assert first.data_slice_identity == second.data_slice_identity
    assert first_output.read_bytes() == second_output.read_bytes()
    assert first_payload["catalog_status"] == "valid_offline_validated_slice"
    assert first_payload["timeframe"] == "15m"
    assert first_payload["source_type"] == "offline_bulk_or_local_file"
    assert ".offline_local.15m." in first_payload["catalog_ref"]
    assert first_payload["range"]["row_count"] == 4
    assert first_payload["range"]["expected_row_count"] == 4
    assert first_payload["gap_summary"]["missing_bar_count"] == 0
    assert first_payload["duplicate_summary"]["duplicate_row_count"] == 0
    assert first_payload["d5_handoff"]["karl_gate_required"] is True


def test_same_inputs_produce_same_slice_identity(tmp_path: Path):
    normalized, import_report, validation_report = _valid_slice(tmp_path)

    first = build_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
    )
    second = build_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
    )

    assert _slice_identity(first) == _slice_identity(second)


def test_source_hash_change_changes_slice_identity(tmp_path: Path):
    entry = _entry(tmp_path)
    normalized, _import_report, validation_report = _valid_slice(tmp_path / "changed")

    changed = build_catalog_entry(
        normalized_path=normalized,
        validation_report_path=validation_report,
        raw_source_sha256="f" * 64,
    )

    assert _slice_identity(changed) != _slice_identity(entry)


def test_normalized_hash_change_changes_slice_identity(tmp_path: Path):
    entry = _entry(tmp_path)
    rows = _source_rows()
    rows[1][5] = 99
    normalized, import_report, validation_report = _valid_slice(tmp_path / "changed", rows)

    changed = build_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
    )

    assert _slice_identity(changed) != _slice_identity(entry)


def test_validation_report_status_change_changes_or_blocks_identity(tmp_path: Path):
    entry = _entry(tmp_path)
    normalized, import_report, validation_report = _valid_slice(tmp_path / "changed")

    _mutate_report(validation_report, lambda payload: payload["validated_output"].__setitem__("path", "changed"))
    changed = build_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
    )
    assert _slice_identity(changed) != _slice_identity(entry)

    _mutate_report(validation_report, lambda payload: payload["validation"].__setitem__("status", "FAIL"))
    with pytest.raises(CatalogError, match="PASS"):
        build_catalog_entry(
            normalized_path=normalized,
            import_report_path=import_report,
            validation_report_path=validation_report,
        )


def test_timestamp_range_change_changes_slice_identity(tmp_path: Path):
    entry = _entry(tmp_path)
    rows = _source_rows()
    rows.append(
        [
            1_704_067_200_000 + 4 * 900_000,
            104,
            107,
            102,
            105,
            14,
            1_704_067_200_000 + 4 * 900_000 + 899_999,
            1004,
            24,
            9,
            504,
            0,
        ]
    )
    normalized, import_report, validation_report = _valid_slice(tmp_path / "changed", rows)

    changed = build_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
    )

    assert _slice_identity(changed) != _slice_identity(entry)


def test_gap_facts_change_changes_slice_identity_when_report_is_materially_different(tmp_path: Path):
    entry = _entry(tmp_path)
    normalized, import_report, validation_report = _valid_slice(tmp_path / "changed")

    def mutate(payload: dict) -> None:
        payload["gap_summary"]["policy"] = "changed-policy-for-identity-test"

    _mutate_report(validation_report, mutate)
    changed = build_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
    )

    assert _slice_identity(changed) != _slice_identity(entry)


def test_duplicate_facts_change_changes_slice_identity_when_report_is_materially_different(tmp_path: Path):
    entry = _entry(tmp_path)
    normalized, import_report, validation_report = _valid_slice(tmp_path / "changed")

    def mutate(payload: dict) -> None:
        payload["duplicate_summary"]["policy"] = "changed-policy-for-identity-test"

    _mutate_report(validation_report, mutate)
    changed = build_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
    )

    assert _slice_identity(changed) != _slice_identity(entry)


def test_invalid_validation_cannot_produce_usable_catalog_entry(tmp_path: Path):
    source = _write_source_csv(tmp_path / "source.csv", _source_rows())
    normalized = tmp_path / "normalized.csv"
    import_report = tmp_path / "import_report.json"
    assert import_file(source, normalized, import_report).ok is True
    lines = normalized.read_text(encoding="utf-8").splitlines()
    del lines[2]
    normalized.write_text("\n".join(lines) + "\n", encoding="utf-8")
    validation_report = tmp_path / "validation_report.json"
    assert validate_file(normalized, validation_report).ok is False

    with pytest.raises(CatalogError):
        build_catalog_entry(
            normalized_path=normalized,
            import_report_path=import_report,
            validation_report_path=validation_report,
        )


def test_report_only_invalid_validation_cannot_write_catalog_output(tmp_path: Path):
    source = _write_source_csv(tmp_path / "source.csv", _source_rows())
    normalized = tmp_path / "normalized.csv"
    import_report = tmp_path / "import_report.json"
    assert import_file(source, normalized, import_report).ok is True
    lines = normalized.read_text(encoding="utf-8").splitlines()
    del lines[2]
    normalized.write_text("\n".join(lines) + "\n", encoding="utf-8")
    validation_report = tmp_path / "validation_report.json"
    assert validate_file(normalized, validation_report, allow_invalid_report_only=True).ok is False
    output = tmp_path / "catalog.json"

    exit_code = main(
        [
            "--normalized",
            str(normalized),
            "--import-report",
            str(import_report),
            "--validation-report",
            str(validation_report),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 1
    assert output.exists() is False


def test_catalog_output_is_sorted_stable_json(tmp_path: Path):
    normalized, import_report, validation_report = _valid_slice(tmp_path)
    output = tmp_path / "catalog.json"

    write_catalog_entry(
        normalized_path=normalized,
        import_report_path=import_report,
        validation_report_path=validation_report,
        output_path=output,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    expected = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    assert output.read_text(encoding="utf-8") == expected


def test_catalog_ref_is_explicit_about_offline_local_source_and_15m_timeframe(tmp_path: Path):
    entry = _entry(tmp_path)

    assert entry["source"]["offline_local_input_only"] is True
    assert entry["timeframe"] == "15m"
    assert ".offline_local.15m." in entry["catalog_ref"]
    assert entry["boundary"]["no_exchange_contact"] is True
