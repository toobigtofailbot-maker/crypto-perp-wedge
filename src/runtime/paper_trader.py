from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.logging.event_writer import append_event_jsonl
from src.overlay.overlay_evaluator_v1 import evaluate_overlay
from src.runtime.scheduler import next_hour_close_utc, sleep_until
from src.signal.provider import build_signal_provider


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"Expected timezone-aware UTC timestamp, got: {value}")
    return dt.astimezone(timezone.utc)


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _iso_utc(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _event(
    event_type: str,
    run_id: str,
    correlation_id: str,
    decision_id: str,
    env: str,
    timestamp_utc: str,
    bar_close_time_utc: str,
    symbol: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "timestamp_utc": timestamp_utc,
        "bar_close_time_utc": bar_close_time_utc,
        "event_type": event_type,
        "run_id": run_id,
        "correlation_id": correlation_id,
        "decision_id": decision_id,
        "env": env,
    }
    if symbol:
        event["symbol"] = symbol
    if payload is not None:
        event["payload"] = payload
    return event


def _is_data_fresh(latest_bar_time_path: str, bar_close_time_utc: str, tolerance_seconds: int) -> tuple[bool, str]:
    path = Path(latest_bar_time_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError, ValueError):
        return False, "LATEST_BAR_FILE_UNAVAILABLE"

    latest_raw = payload.get("latest_bar_timestamp_utc") or payload.get("timestamp_utc")
    if not isinstance(latest_raw, str):
        return False, "LATEST_BAR_TIMESTAMP_MISSING"

    try:
        latest_dt = _parse_iso_utc(latest_raw)
        close_dt = _parse_iso_utc(bar_close_time_utc)
    except ValueError:
        return False, "LATEST_BAR_TIMESTAMP_INVALID"

    delta_seconds = abs((close_dt - latest_dt).total_seconds())
    if delta_seconds <= tolerance_seconds:
        return True, "FRESH"

    return False, "LATEST_BAR_STALE"


def _freshness_gate_path(value: Any) -> str | None:
    if value is None:
        return None

    path = str(value).strip()
    if path == "" or path.lower() == "null":
        return None

    return path


def run_once(config_path: str, bar_close_time_utc: str | None = None) -> int:
    config = _load_json(config_path)

    env = str(config["env"])
    symbol = str(config["symbol"])
    macro_flags_path = str(config["macro_flags_path"])
    event_log_path = str(config["event_log_path"])
    signal_provider_name = str(config.get("signal_provider", "flat"))
    latest_bar_time_path = _freshness_gate_path(config.get("latest_bar_time_path"))
    freshness_tolerance_seconds = int(config.get("freshness_tolerance_seconds", 0))
    evaluation_time_source = str(config.get("evaluation_time_source", "now_utc"))
    decision_id = str(config.get("decision_id", "D-0001"))
    run_id = str(config.get("run_id", f"RUN-{uuid.uuid4().hex[:8]}"))
    correlation_id = str(config.get("correlation_id", run_id))

    if bar_close_time_utc is not None:
        evaluation_time_utc = bar_close_time_utc
    elif evaluation_time_source == "now_utc":
        evaluation_time_utc = _utc_now_iso()
    else:
        evaluation_time_utc = str(config["evaluation_time_utc"])

    append_event_jsonl(
        event_log_path,
        _event(
            event_type="SystemEvent",
            run_id=run_id,
            correlation_id=correlation_id,
            decision_id=decision_id,
            env=env,
            timestamp_utc=evaluation_time_utc,
            bar_close_time_utc=evaluation_time_utc,
            symbol=symbol,
            payload={"phase": "start", "mode": "once"},
        ),
    )

    fresh = True
    freshness_reason = "FRESHNESS_GATE_DISABLED"
    if latest_bar_time_path is not None:
        fresh, freshness_reason = _is_data_fresh(
            latest_bar_time_path=latest_bar_time_path,
            bar_close_time_utc=evaluation_time_utc,
            tolerance_seconds=freshness_tolerance_seconds,
        )

    if not fresh:
        append_event_jsonl(
            event_log_path,
            _event(
                event_type="SystemEvent",
                run_id=run_id,
                correlation_id=correlation_id,
                decision_id=decision_id,
                env=env,
                timestamp_utc=evaluation_time_utc,
                bar_close_time_utc=evaluation_time_utc,
                symbol=symbol,
                payload={
                    "phase": "skip",
                    "reason": "stale_data",
                    "freshness_reason": freshness_reason,
                    "latest_bar_time_path": latest_bar_time_path,
                    "freshness_tolerance_seconds": freshness_tolerance_seconds,
                },
            ),
        )
        append_event_jsonl(
            event_log_path,
            _event(
                event_type="SystemEvent",
                run_id=run_id,
                correlation_id=correlation_id,
                decision_id=decision_id,
                env=env,
                timestamp_utc=evaluation_time_utc,
                bar_close_time_utc=evaluation_time_utc,
                symbol=symbol,
                payload={"phase": "end", "mode": "once", "skipped": True},
            ),
        )
        return 0

    signal_provider = build_signal_provider(signal_provider_name)
    desired_position = signal_provider.compute_desired_position(
        evaluation_time_utc=evaluation_time_utc,
        inputs={
            "symbol": symbol,
            "decision_id": decision_id,
            "correlation_id": correlation_id,
            "run_id": run_id,
            "source_timeframe": "1m",
        },
    )

    desired_position_payload = {
        "symbol": desired_position.symbol,
        "target_qty": str(desired_position.target_qty) if desired_position.target_qty is not None else None,
        "target_notional": str(desired_position.target_notional) if desired_position.target_notional is not None else None,
        "timestamp_utc": desired_position.timestamp_utc,
        "source_timeframe": desired_position.source_timeframe,
        "decision_id": desired_position.decision_id,
        "correlation_id": desired_position.correlation_id,
        "run_id": desired_position.run_id,
    }

    append_event_jsonl(
        event_log_path,
        _event(
            event_type="SignalEvent",
            run_id=run_id,
            correlation_id=correlation_id,
            decision_id=decision_id,
            env=env,
            timestamp_utc=evaluation_time_utc,
            bar_close_time_utc=evaluation_time_utc,
            symbol=symbol,
            payload={
                "signal_provider": signal_provider_name,
                "evaluation_time_utc": evaluation_time_utc,
                "desired_position": desired_position_payload,
            },
        ),
    )

    overlay_result = evaluate_overlay(
        desired_position=desired_position_payload,
        evaluation_time_utc=evaluation_time_utc,
        macro_flags_path=macro_flags_path,
    )

    size_multiplier = Decimal(str(overlay_result.get("size_multiplier", 1.0)))
    adjusted_target_qty = desired_position.target_qty
    if adjusted_target_qty is not None:
        adjusted_target_qty = adjusted_target_qty * size_multiplier

    overlay_result["desired_position_after_overlay"] = {
        "symbol": desired_position.symbol,
        "target_qty": str(adjusted_target_qty) if adjusted_target_qty is not None else None,
        "target_notional": str(desired_position.target_notional) if desired_position.target_notional is not None else None,
        "timestamp_utc": desired_position.timestamp_utc,
        "source_timeframe": desired_position.source_timeframe,
        "decision_id": desired_position.decision_id,
        "correlation_id": desired_position.correlation_id,
        "run_id": desired_position.run_id,
        "size_multiplier_applied": str(size_multiplier),
    }

    append_event_jsonl(
        event_log_path,
        _event(
            event_type="OverlayDecision",
            run_id=run_id,
            correlation_id=correlation_id,
            decision_id=decision_id,
            env=env,
            timestamp_utc=evaluation_time_utc,
            bar_close_time_utc=evaluation_time_utc,
            symbol=symbol,
            payload=overlay_result,
        ),
    )

    append_event_jsonl(
        event_log_path,
        _event(
            event_type="RiskDecision",
            run_id=run_id,
            correlation_id=correlation_id,
            decision_id=decision_id,
            env=env,
            timestamp_utc=evaluation_time_utc,
            bar_close_time_utc=evaluation_time_utc,
            symbol=symbol,
            payload={"status": "no-op", "note": "D-0001 enforced elsewhere"},
        ),
    )

    append_event_jsonl(
        event_log_path,
        _event(
            event_type="OrderIntent",
            run_id=run_id,
            correlation_id=correlation_id,
            decision_id=decision_id,
            env=env,
            timestamp_utc=evaluation_time_utc,
            bar_close_time_utc=evaluation_time_utc,
            symbol=symbol,
            payload={"status": "stub", "note": "paper intent would be generated here"},
        ),
    )

    append_event_jsonl(
        event_log_path,
        _event(
            event_type="SystemEvent",
            run_id=run_id,
            correlation_id=correlation_id,
            decision_id=decision_id,
            env=env,
            timestamp_utc=evaluation_time_utc,
            bar_close_time_utc=evaluation_time_utc,
            symbol=symbol,
            payload={"phase": "end", "mode": "once"},
        ),
    )

    return 0


def _run_loop(config_path: str) -> int:
    while True:
        bar_close = next_hour_close_utc(datetime.now(timezone.utc))
        sleep_until(bar_close)
        run_once(config_path=config_path, bar_close_time_utc=_iso_utc(bar_close))


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper trader runtime")
    parser.add_argument("--once", action="store_true", help="Run exactly one paper-safe cycle")
    parser.add_argument("--loop", action="store_true", help="Run each UTC 1h bar close")
    parser.add_argument("--once-at", help="Run one cycle at explicit UTC bar-close timestamp (ISO8601)")
    parser.add_argument("--config", required=True, help="Path to runtime config JSON")
    args = parser.parse_args()

    selected_modes = sum(bool(mode) for mode in [args.once, args.loop, args.once_at])
    if selected_modes != 1:
        raise SystemExit("Select exactly one mode: --once, --loop, or --once-at")

    if args.once:
        return run_once(args.config)
    if args.once_at:
        return run_once(args.config, bar_close_time_utc=_iso_utc(_parse_iso_utc(args.once_at)))
    return _run_loop(args.config)


if __name__ == "__main__":
    raise SystemExit(main())