import json
import types
from pathlib import Path

import pandas as pd
import pytest

from tools.sidecars import vectorbt_triage_sidecar as sidecar


class _FakeTrades:
    def count(self):
        return 1


class _FakePortfolio:
    trades = _FakeTrades()

    def value(self):
        index = pd.date_range("2026-01-01", periods=4, freq="15min", tz="UTC")
        return pd.Series([10_000.0, 10_100.0, 10_050.0, 10_200.0], index=index)


class _FakePortfolioFactory:
    calls = []

    @classmethod
    def from_signals(cls, **kwargs):
        cls.calls.append(kwargs)
        return _FakePortfolio()


def _fake_vbt():
    _FakePortfolioFactory.calls = []
    return types.SimpleNamespace(__version__="fake-vectorbt", Portfolio=_FakePortfolioFactory)


def _fixture_frame():
    index = pd.date_range("2026-01-01", periods=4, freq="15min", tz="UTC")
    return pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [100.5, 101.5, 102.5, 103.5],
            "volume": [1000.0] * 4,
        },
        index=index,
    )


def test_non_authority_labels_are_explicit():
    labels = sidecar.NON_AUTHORITY_LABELS
    assert "NOT CANONICAL EVIDENCE" in labels
    assert "NOT CANDIDATE EVIDENCE" in labels
    assert "NOT RANKING / SCREEN-GATE / READINESS AUTHORITY" in labels
    assert "CANONICAL RUNNER CONFIRMATION REQUIRED FOR EVERY FINALIST" in labels


def test_selected_variants_are_bounded_and_ordered():
    manifest = {
        "variant_assignments": [
            {"variant_id": "VAR-2", "assignment_status": "included"},
            {"variant_id": "VAR-1", "assignment_status": "included"},
        ]
    }
    sweep = {"test_selection": {"selected_variant_ids": ["VAR-2", "VAR-1"]}}

    rows = sidecar._selected_variants(manifest, sweep, max_variants=2)

    assert [row["variant_id"] for row in rows] == ["VAR-1", "VAR-2"]
    with pytest.raises(sidecar.VectorbtTriageError, match="exceeds bounded cap"):
        sidecar._selected_variants(manifest, sweep, max_variants=1)
    with pytest.raises(sidecar.VectorbtTriageError, match="between 1"):
        sidecar._selected_variants(manifest, sweep, max_variants=0)


def test_execution_signals_use_next_bar_open_alignment():
    index = pd.date_range("2026-01-01", periods=5, freq="15min", tz="UTC")
    signal = pd.Series([0.0, 1.0, 1.0, -1.0, 0.0], index=index)

    long_entries, long_exits, short_entries, short_exits = sidecar._execution_signals(signal)

    assert long_entries.tolist() == [False, False, True, False, False]
    assert long_exits.tolist() == [False, False, False, False, True]
    assert short_entries.tolist() == [False, False, False, False, True]
    assert short_exits.tolist() == [False, False, False, False, False]


def test_unavailable_vectorbt_produces_deterministic_deferred_report(monkeypatch):
    monkeypatch.setattr(
        sidecar,
        "_load_vectorbt_optional",
        lambda: (None, "ModuleNotFoundError: vectorbt"),
    )

    first = sidecar.build_report()
    second = sidecar.build_report()

    assert first == second
    assert first["execution_status"] == "DEFERRED_OPTIONAL_DEPENDENCY_UNAVAILABLE"
    assert first["decision_label"] == "BLOCKED"
    assert first["fixture"]["processed_variant_count"] == 0
    assert first["canonical_confirmation_required"] is True
    assert first["output_checksum"].startswith("sha256:")


def test_available_vectorbt_generates_noncanonical_triage(monkeypatch):
    frame = _fixture_frame()
    signal = pd.Series([0.0, 1.0, 1.0, 0.0], index=frame.index)
    monkeypatch.setattr(sidecar, "_load_vectorbt_optional", lambda: (_fake_vbt(), None))
    monkeypatch.setattr(
        sidecar,
        "_load_execution_context",
        lambda **kwargs: types.SimpleNamespace(
            ohlcv=frame,
            timeframe="15m",
            data_slice_identity="fixture:sha256:test",
        ),
    )
    monkeypatch.setattr(sidecar, "compile_signal", lambda spec, variant, ohlcv: signal)

    report = sidecar.build_report()

    assert report["execution_status"] == "COMPLETED_NON_CANONICAL_TRIAGE"
    assert report["decision_label"] == "ADOPT_AS_NON_CANONICAL_TRIAGE_SIDECAR"
    assert report["dependency"]["version"] == "fake-vectorbt"
    assert report["fixture"]["processed_variant_count"] == 8
    assert [row["variant_id"] for row in report["triage_rows"]] == sorted(
        row["variant_id"] for row in report["triage_rows"]
    )
    assert len(_FakePortfolioFactory.calls) == 8
    assert _FakePortfolioFactory.calls[0]["price"].equals(frame["open"])
    assert _FakePortfolioFactory.calls[0]["fees"] == 0.0004
    assert _FakePortfolioFactory.calls[0]["slippage"] == 0.0001


def test_report_checksum_covers_report_payload(monkeypatch):
    monkeypatch.setattr(sidecar, "_load_vectorbt_optional", lambda: (None, "missing"))
    report = sidecar.build_report()
    payload = dict(report)
    checksum = payload.pop("output_checksum")

    assert checksum == sidecar._sha256_payload(payload)


def test_run_writes_only_sidecar_report_files(tmp_path, monkeypatch):
    monkeypatch.setattr(sidecar, "_load_vectorbt_optional", lambda: (None, "missing"))

    report = sidecar.run(output_dir=tmp_path)

    assert {path.name for path in tmp_path.iterdir()} == {
        "vectorbt_triage_report.json",
        "vectorbt_triage_report.md",
        "vectorbt_triage_report.sha256",
    }
    written = json.loads((tmp_path / "vectorbt_triage_report.json").read_text(encoding="utf-8"))
    assert written == report
    checksum = (tmp_path / "vectorbt_triage_report.sha256").read_text(encoding="utf-8").strip()
    assert checksum == report["output_checksum"]


def test_default_report_provenance_is_repo_relative(monkeypatch):
    monkeypatch.setattr(sidecar, "_load_vectorbt_optional", lambda: (None, "missing"))
    report = sidecar.build_report()

    paths = [item["path"] for item in report["fixture"]["provenance"].values()]
    assert all(not Path(path).is_absolute() for path in paths)
    assert all(":\\" not in path for path in paths)


def test_boundary_statement_denies_authority(monkeypatch):
    monkeypatch.setattr(sidecar, "_load_vectorbt_optional", lambda: (None, "missing"))
    boundary = sidecar.build_report()["boundary_statement"]

    assert all(value is False for value in boundary.values())


def test_source_does_not_invoke_canonical_runner_or_write_canonical_artifacts():
    source = (
        sidecar.REPO_ROOT / "tools/sidecars/vectorbt_triage_sidecar.py"
    ).read_text(encoding="utf-8")

    assert "runner.run_offline_sweep" not in source
    assert "research/result_populations" not in source
    assert "trial_log" not in source
