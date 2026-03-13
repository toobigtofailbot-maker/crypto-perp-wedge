from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from src.overlay.overlay_evaluator_v1 import evaluate_overlay


def _desired_position(decision_id: str, correlation_id: str, run_id: str) -> dict:
    return {
        "symbol": "BTCUSDT",
        "target_qty": Decimal("0.01"),
        "target_notional": None,
        "source_timeframe": "1m",
        "decision_id": decision_id,
        "correlation_id": correlation_id,
        "run_id": run_id,
    }


def _write_flags(path: Path, windows: list[dict], context_missing: bool = False) -> None:
    payload = {
        "asof_timestamp_utc": "2026-01-01T00:00:00Z",
        "snapshot_hash": "samplehash",
        "context_missing": context_missing,
        "decision_id": "D-0001",
        "windows": windows,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_missing_flags_fail_open(tmp_path: Path) -> None:
    result = evaluate_overlay(
        desired_position=_desired_position("dec-001", "corr-001", "run-001"),
        evaluation_time_utc="2026-01-01T00:00:00Z",
        macro_flags_path=str(tmp_path / "missing_macro_window_flags.json"),
    )

    assert result["trade_permission"] == "ALLOW"
    assert result["size_multiplier"] == 1.0
    assert result["context_missing"] is True
    assert result["reason_code"] == "FLAGS_FILE_MISSING"


def test_invalid_flags_fail_open(tmp_path: Path) -> None:
    flags_path = tmp_path / "macro_window_flags.json"
    flags_path.write_text("{not-json", encoding="utf-8")

    result = evaluate_overlay(
        desired_position=_desired_position("dec-002", "corr-002", "run-002"),
        evaluation_time_utc="2026-01-01T00:00:00Z",
        macro_flags_path=str(flags_path),
    )

    assert result["trade_permission"] == "ALLOW"
    assert result["size_multiplier"] == 1.0
    assert result["context_missing"] is True
    assert result["reason_code"] == "FLAGS_FILE_INVALID"


def test_block_window_maps_exactly_to_zero(tmp_path: Path) -> None:
    flags_path = tmp_path / "macro_window_flags.json"
    _write_flags(
        flags_path,
        windows=[
            {
                "start_utc": "2025-12-31T23:30:00Z",
                "end_utc": "2026-01-01T00:30:00Z",
                "permission": "BLOCK",
                "size_multiplier": 999.0,
            }
        ],
    )

    result = evaluate_overlay(
        desired_position=_desired_position("dec-003", "corr-003", "run-003"),
        evaluation_time_utc="2026-01-01T00:00:00Z",
        macro_flags_path=str(flags_path),
    )

    assert result["trade_permission"] == "BLOCK"
    assert result["size_multiplier"] == 0.0
    assert result["context_missing"] is False
    assert result["reason_code"] == "ACTIVE_WINDOW_MATCH"


def test_reduced_window_maps_exactly_to_half(tmp_path: Path) -> None:
    flags_path = tmp_path / "macro_window_flags.json"
    _write_flags(
        flags_path,
        windows=[
            {
                "start_utc": "2025-12-31T23:30:00Z",
                "end_utc": "2026-01-01T00:30:00Z",
                "permission": "ALLOW_REDUCED",
                "size_multiplier": 0.123,
            }
        ],
    )

    result = evaluate_overlay(
        desired_position=_desired_position("dec-004", "corr-004", "run-004"),
        evaluation_time_utc="2026-01-01T00:00:00Z",
        macro_flags_path=str(flags_path),
    )

    assert result["trade_permission"] == "ALLOW_REDUCED"
    assert result["size_multiplier"] == 0.5
    assert result["context_missing"] is False
    assert result["reason_code"] == "ACTIVE_WINDOW_MATCH"


def test_no_active_window_defaults_to_allow_without_context_missing(tmp_path: Path) -> None:
    flags_path = tmp_path / "macro_window_flags.json"
    _write_flags(
        flags_path,
        windows=[
            {
                "start_utc": "2026-01-01T01:00:00Z",
                "end_utc": "2026-01-01T02:00:00Z",
                "permission": "BLOCK",
                "size_multiplier": 0.0,
            }
        ],
    )

    result = evaluate_overlay(
        desired_position=_desired_position("dec-005", "corr-005", "run-005"),
        evaluation_time_utc="2026-01-01T00:00:00Z",
        macro_flags_path=str(flags_path),
    )

    assert result["trade_permission"] == "ALLOW"
    assert result["size_multiplier"] == 1.0
    assert result["context_missing"] is False
    assert result["reason_code"] == "NO_ACTIVE_WINDOW"

def test_overlapping_windows_block_dominates_reduced(tmp_path: Path) -> None:
    flags_path = tmp_path / "macro_window_flags.json"
    _write_flags(
        flags_path,
        windows=[
            {
                "start_utc": "2025-12-31T23:30:00Z",
                "end_utc": "2026-01-01T00:30:00Z",
                "permission": "ALLOW_REDUCED",
                "size_multiplier": 0.5,
            },
            {
                "start_utc": "2025-12-31T23:45:00Z",
                "end_utc": "2026-01-01T00:15:00Z",
                "permission": "BLOCK",
                "size_multiplier": 0.0,
            },
        ],
    )

    result = evaluate_overlay(
        desired_position=_desired_position("dec-006", "corr-006", "run-006"),
        evaluation_time_utc="2026-01-01T00:00:00Z",
        macro_flags_path=str(flags_path),
    )

    assert result["trade_permission"] == "BLOCK"
    assert result["size_multiplier"] == 0.0
    assert result["context_missing"] is False
    assert result["reason_code"] == "ACTIVE_WINDOW_MATCH"


def test_payload_context_missing_is_preserved(tmp_path: Path) -> None:
    flags_path = tmp_path / "macro_window_flags.json"
    _write_flags(
        flags_path,
        windows=[
            {
                "start_utc": "2025-12-31T23:00:00Z",
                "end_utc": "2026-01-01T01:00:00Z",
                "permission": "ALLOW",
                "size_multiplier": 1.0,
            }
        ],
        context_missing=True,
    )

    result = evaluate_overlay(
        desired_position=_desired_position("dec-007", "corr-007", "run-007"),
        evaluation_time_utc="2026-01-01T00:00:00Z",
        macro_flags_path=str(flags_path),
    )

    assert result["trade_permission"] == "ALLOW"
    assert result["size_multiplier"] == 1.0
    assert result["context_missing"] is True
    assert result["reason_code"] == "ACTIVE_WINDOW_MATCH"


def test_audit_event_is_appended_jsonl(tmp_path: Path) -> None:
    flags_path = tmp_path / "macro_window_flags.json"
    audit_path = tmp_path / "overlay_decisions.jsonl"

    _write_flags(
        flags_path,
        windows=[
            {
                "start_utc": "2025-12-31T23:30:00Z",
                "end_utc": "2026-01-01T00:30:00Z",
                "permission": "ALLOW_REDUCED",
                "size_multiplier": 0.5,
            }
        ],
    )

    result = evaluate_overlay(
        desired_position=_desired_position("dec-008", "corr-008", "run-008"),
        evaluation_time_utc="2026-01-01T00:00:00Z",
        macro_flags_path=str(flags_path),
        audit_path=str(audit_path),
    )

    assert audit_path.exists() is True

    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    event = json.loads(lines[0])
    assert event["event_type"] == "OVERLAY_EVALUATED"
    assert event["decision_id"] == "dec-008"
    assert event["correlation_id"] == "corr-008"
    assert event["run_id"] == "run-008"
    assert event["timestamp_utc"] == "2026-01-01T00:00:00Z"
    assert event["payload"]["trade_permission"] == result["trade_permission"]
    assert event["payload"]["size_multiplier"] == result["size_multiplier"]
    assert event["payload"]["context_missing"] == result["context_missing"]
