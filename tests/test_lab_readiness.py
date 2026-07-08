"""Tests for the read-only lab data/simulator readiness display."""

from __future__ import annotations

import json
import socket
from pathlib import Path

from tools.lab_readiness import model
from tools.lab_readiness.readiness import build_readiness_projection, render_markdown
from tools.lab_readiness.run import main


def _item(data: dict, subject_id: str) -> dict:
    return next(item for item in data["items"] if item["subject_id"] == subject_id)


def test_closed_taxonomy_contains_required_statuses() -> None:
    assert model.READINESS_STATUSES == (
        "testable_now_with_current_public_history",
        "testable_now_with_current_caveats",
        "needs_local_full_history_materialization",
        "needs_vendor_or_captured_history",
        "needs_runner_or_compiler_support",
        "needs_simulator_realism_upgrade",
        "go_gated_or_paper_phase_only",
        "protected_or_out_of_scope",
        "unknown_needs_review",
    )
    data = build_readiness_projection()
    assert data["status_taxonomy"] == list(model.READINESS_STATUSES)
    assert set(data["summary_by_status"]) == set(model.READINESS_STATUSES)


def test_minimum_coverage_rows_are_present() -> None:
    data = build_readiness_projection()
    subjects = {item["subject_id"] for item in data["items"]}
    assert {
        "READINESS-OHLCV-INDICATORS",
        "READINESS-FUNDING-RATE-FEATURE-HISTORY",
        "READINESS-FUNDING-PNL-COST-REALISM",
        "READINESS-TAKER-FLOW-ARCHIVE",
        "READINESS-OPEN-INTEREST",
        "READINESS-LONG-SHORT-RATIO",
        "READINESS-LIQUIDATION-HISTORY",
        "READINESS-L2-ORDERBOOK",
        "READINESS-MARK-INDEX-PREMIUM-FIELDS",
        "READINESS-UTC-TIME-FIELDS",
        "READINESS-DONCHIAN-BREAKOUT",
        "READINESS-SMA-STDDEV-MEAN-REVERSION",
        "READINESS-EMA-RVOL-VWAP-SESSION",
        "READINESS-SIMULATOR-PAPER-SHADOW-BOUNDARY",
    } <= subjects


def test_funding_pnl_cost_realism_not_falsely_marked_complete() -> None:
    data = build_readiness_projection()
    item = _item(data, "READINESS-FUNDING-PNL-COST-REALISM")
    assert item["status"] == "needs_runner_or_compiler_support"
    assert "zero_funding" in " ".join(item["current_repo_support"])
    assert "not funding-carry-PnL tests" in " ".join(item["current_repo_support"])


def test_oi_liquidation_l2_are_not_full_history_testable() -> None:
    data = build_readiness_projection()
    for subject_id in (
        "READINESS-OPEN-INTEREST",
        "READINESS-LIQUIDATION-HISTORY",
        "READINESS-L2-ORDERBOOK",
    ):
        item = _item(data, subject_id)
        assert item["status"] != "testable_now_with_current_public_history"
    assert _item(data, "READINESS-OPEN-INTEREST")["status"] == "needs_vendor_or_captured_history"
    assert _item(data, "READINESS-LIQUIDATION-HISTORY")["status"] == "needs_vendor_or_captured_history"
    assert _item(data, "READINESS-L2-ORDERBOOK")["status"] == "needs_vendor_or_captured_history"


def test_taker_flow_uses_repo_truth_availability_class() -> None:
    data = build_readiness_projection()
    item = _item(data, "READINESS-TAKER-FLOW-ARCHIVE")
    support = " ".join(item["current_repo_support"])
    assert "PUBLIC_TRADE_ARCHIVE_DERIVATION" in support
    assert "FULL_HISTORY_PUBLIC_ARCHIVE" in support
    assert "PUBLIC_REST_TAKER_RATIO" in support
    assert item["status"] == "needs_local_full_history_materialization"


def test_unknown_missing_evidence_fails_closed(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "research" / "data_feature_availability").mkdir(parents=True)
    (repo / "research" / "indicator_catalogs").mkdir(parents=True)
    data = build_readiness_projection(repo_root=repo)
    ohlcv = _item(data, "READINESS-OHLCV-INDICATORS")
    assert ohlcv["status"] == "unknown_needs_review"
    assert "none" in " ".join(ohlcv["current_repo_support"])


def test_output_is_deterministic() -> None:
    first = build_readiness_projection()
    second = build_readiness_projection()
    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert render_markdown(first) == render_markdown(second)


def test_markdown_and_json_include_non_authority_flags() -> None:
    data = build_readiness_projection()
    assert data["non_authority_declaration"]["read_only_display_only"] is True
    assert data["non_authority_declaration"]["contacts_network_or_provider_api"] is False
    assert all(item["non_authority_flags"] for item in data["items"])
    md = render_markdown(data)
    assert "Read-only readiness display only" in md
    assert "`not_provider_api_or_credential_authority`" in md


def test_cli_writes_only_when_out_dir_is_provided(tmp_path: Path, capsys) -> None:
    out = tmp_path / "readiness"
    assert main(["--out-dir", str(out)]) == 0
    captured = capsys.readouterr().out
    assert "readiness_json:" in captured
    assert (out / "readiness.json").exists()
    assert (out / "readiness.md").exists()


def test_no_network_provider_api_call_occurs(monkeypatch) -> None:
    def fail_connect(*args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise AssertionError("network call attempted")

    monkeypatch.setattr(socket.socket, "connect", fail_connect)
    data = build_readiness_projection()
    assert data["non_authority_declaration"]["contacts_network_or_provider_api"] is False


def test_no_data_acquisition_path_is_invoked() -> None:
    data = build_readiness_projection()
    text = json.dumps(data, sort_keys=True).lower()
    for forbidden in ("fetch_", "download", "api key", "private endpoint"):
        assert forbidden not in text
