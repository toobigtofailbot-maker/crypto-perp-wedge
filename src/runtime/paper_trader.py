from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.logging.event_writer import append_event_jsonl
from src.overlay.overlay_evaluator_v1 import evaluate_overlay


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _event(
    event_type: str,
    run_id: str,
    correlation_id: str,
    decision_id: str,
    env: str,
    timestamp_utc: str,
    symbol: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "timestamp_utc": timestamp_utc,
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


def run_once(config_path: str) -> int:
    config = _load_json(config_path)

    env = str(config["env"])
    symbol = str(config["symbol"])
    macro_flags_path = str(config["macro_flags_path"])
    event_log_path = str(config["event_log_path"])
    evaluation_time_source = str(config.get("evaluation_time_source", "now_utc"))
    decision_id = str(config.get("decision_id", "D-0001"))
    run_id = str(config.get("run_id", f"RUN-{uuid.uuid4().hex[:8]}"))
    correlation_id = str(config.get("correlation_id", run_id))

    if evaluation_time_source == "now_utc":
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
            symbol=symbol,
            payload={"phase": "start", "mode": "once"},
        ),
    )

    desired_position = {
        "symbol": symbol,
        "target_qty": None,
        "target_notional": None,
        "source_timeframe": "1m",
        "decision_id": decision_id,
        "correlation_id": correlation_id,
        "run_id": run_id,
    }

    overlay_result = evaluate_overlay(
        desired_position=desired_position,
        evaluation_time_utc=evaluation_time_utc,
        macro_flags_path=macro_flags_path,
    )

    append_event_jsonl(
        event_log_path,
        _event(
            event_type="OverlayDecision",
            run_id=run_id,
            correlation_id=correlation_id,
            decision_id=decision_id,
            env=env,
            timestamp_utc=evaluation_time_utc,
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
            symbol=symbol,
            payload={"phase": "end", "mode": "once"},
        ),
    )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper trader runtime")
    parser.add_argument("--once", action="store_true", help="Run exactly one paper-safe cycle")
    parser.add_argument("--config", required=True, help="Path to runtime config JSON")
    args = parser.parse_args()

    if not args.once:
        raise SystemExit("Only --once mode is allowed in this batch")

    return run_once(args.config)


if __name__ == "__main__":
    raise SystemExit(main())
