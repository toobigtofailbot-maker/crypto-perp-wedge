from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.registry.validate_walkforward_fold_manifest import (
    validate_walkforward_fold_manifests,
)
from tools.walkforward import purged_folds as subject


DATA_SLICE_ID = (
    "binance_usdtm_btcusdt_ohlcv_15m:sha256:"
    "3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664"
)


def _config(**overrides) -> subject.PurgedFoldConfig:
    values = {
        "manifest_id": "WFM-9002",
        "created_at_utc": "2026-06-20T12:00:00Z",
        "strategy_spec_id": "STRAT-SPEC-0004",
        "variant_manifest_id": "VM-0004",
        "sweep_plan_id": "SWEEP-PLAN-0004",
        "data_slice_id": DATA_SLICE_ID,
        "timeframe": "15m",
        "start_utc": "2026-01-01T00:00:00Z",
        "selection_bars": 384,
        "evaluation_bars": 96,
        "purge_bars": 12,
        "embargo_bars": 8,
        "fold_count": 2,
        "declared_variant_count": 8,
    }
    values.update(overrides)
    return subject.PurgedFoldConfig(**values)


def test_build_manifest_applies_purge_and_embargo_deterministically():
    manifest, comparison = subject.build_purged_manifest_and_comparison(
        _config(), source_commit="4da388a"
    )

    assert manifest["source_commit"] == "4da388a"
    assert [fold["fold_id"] for fold in manifest["folds"]] == ["FOLD-001", "FOLD-002"]
    assert manifest["folds"][0]["selection_window_end_utc"] == "2026-01-04T21:00:00Z"
    assert manifest["folds"][0]["evaluation_window_start_utc"] == "2026-01-05T00:00:00Z"
    assert manifest["folds"][0]["purge"] == {"mode": "bars", "bars": 12, "duration": None}
    assert manifest["folds"][0]["embargo"] == {"mode": "bars", "bars": 8, "duration": None}
    assert manifest["folds"][1]["selection_window_start_utc"] == "2026-01-06T02:00:00Z"
    assert comparison["comparison_summary"]["total_selection_bars_removed"] == 32
    assert comparison["comparison_summary"]["material_difference_observed"] is True


def test_generated_manifest_validates_against_existing_contract(tmp_path):
    output = tmp_path / "purged_fold_manifest.json"
    comparison = tmp_path / "purged_fold_comparison_report.json"
    provenance = tmp_path / "provenance.json"

    subject.write_purged_fold_artifacts(
        output_path=output,
        comparison_output_path=comparison,
        provenance_output_path=provenance,
        config=_config(),
    )

    assert validate_walkforward_fold_manifests(explicit_paths=[output]) == []
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["non_authority_declaration"]["not_runtime_authority"] is True
    assert json.loads(provenance.read_text(encoding="utf-8"))["contract_validation"]["passed"] is True


def test_invalid_purge_that_consumes_selection_window_is_rejected():
    with pytest.raises(subject.PurgedFoldError, match="selection_bars must be greater"):
        subject.build_purged_manifest_and_comparison(
            _config(selection_bars=12, purge_bars=12), source_commit="4da388a"
        )


def test_invalid_embargo_that_eliminates_later_selection_window_is_rejected():
    with pytest.raises(subject.PurgedFoldError, match="FOLD-002 invalid"):
        subject.build_purged_manifest_and_comparison(
            _config(selection_bars=20, evaluation_bars=5, purge_bars=2, embargo_bars=30),
            source_commit="4da388a",
        )


def test_cli_writes_default_sidecars(tmp_path, monkeypatch, capsys):
    output = tmp_path / "purged_fold_manifest.json"
    monkeypatch.setattr(subject, "_source_commit", lambda: "4da388a")

    result = subject.main(
        [
            "--output",
            str(output),
            "--start-utc",
            "2026-01-01T00:00:00Z",
            "--selection-bars",
            "384",
            "--evaluation-bars",
            "96",
            "--purge-bars",
            "12",
            "--embargo-bars",
            "8",
            "--fold-count",
            "2",
        ]
    )

    assert result == 0
    assert output.exists()
    assert (tmp_path / "purged_fold_comparison_report.json").exists()
    assert (tmp_path / "provenance.json").exists()
    assert "OK: purged fold manifest written" in capsys.readouterr().out
