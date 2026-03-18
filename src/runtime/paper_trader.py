from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.execution.interfaces import OrderIntent
from src.logging.event_writer import append_event_jsonl
from src.marketdata.price_ref_provider import PriceRefProvider, PriceReference
from src.overlay.overlay_evaluator_v1 import evaluate_overlay
from src.paper.ledger_state import (
    LedgerState,
    load_ledger_state,
    save_ledger_state,
    snapshot_ledger_state,
)
from src.paper.paper_broker import PaperBroker, PaperFill
from src.paper.position_state import (
    PositionState,
    apply_fill_to_position,
    load_position_state,
    position_delta_qty,
    save_position_state,
    snapshot_position_state,
)
from src.runtime.scheduler import next_hour_close_utc, sleep_until
from src.signal.provider import build_signal_provider


ZERO = Decimal("0")


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


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _decimal_from_config(config: dict[str, Any], key: str, default: str) -> Decimal:
    return Decimal(str(config.get(key, default)))


def _decimal_from_config_keys(config: dict[str, Any], keys: tuple[str, ...], default: str) -> Decimal:
    for key in keys:
        value = config.get(key)
        if value is not None:
            return Decimal(str(value))
    return Decimal(default)


def _default_paper_path(event_log_path: str, filename: str) -> str:
    return str(Path(event_log_path).with_name(filename))


def _serialize_price_reference(price_reference: PriceReference) -> dict[str, str]:
    return price_reference.to_event_fields()


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
    price_ref_metadata: dict[str, Any] | None = None,
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
    if price_ref_metadata is not None:
        event.update(price_ref_metadata)
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


def _serialize_desired_position(
    *,
    symbol: str,
    target_qty: Decimal | None,
    target_notional: Decimal | None,
    timestamp_utc: str,
    source_timeframe: str | None,
    decision_id: str,
    correlation_id: str,
    run_id: str,
    size_multiplier_applied: Decimal | None = None,
) -> dict[str, Any]:
    payload = {
        "symbol": symbol,
        "target_qty": _decimal_text(target_qty),
        "target_notional": _decimal_text(target_notional),
        "timestamp_utc": timestamp_utc,
        "source_timeframe": source_timeframe,
        "decision_id": decision_id,
        "correlation_id": correlation_id,
        "run_id": run_id,
    }
    if size_multiplier_applied is not None:
        payload["size_multiplier_applied"] = _decimal_text(size_multiplier_applied)
    return payload


def _serialize_order_intent(order_intent: OrderIntent) -> dict[str, Any]:
    return {
        "symbol": order_intent.symbol,
        "side": order_intent.side.value,
        "qty": _decimal_text(order_intent.qty),
        "price": _decimal_text(order_intent.price),
        "order_type": order_intent.order_type.value,
        "reduce_only": order_intent.reduce_only,
        "client_order_id": order_intent.client_order_id,
        "tif": order_intent.tif,
        "urgency": order_intent.urgency,
        "correlation_id": order_intent.correlation_id,
        "decision_id": order_intent.decision_id,
    }


def _serialize_fill(fill: PaperFill) -> dict[str, Any]:
    return fill.to_dict()


def _serialize_position(state: PositionState) -> dict[str, Any]:
    return state.to_dict()


def _serialize_ledger_state(state: LedgerState) -> dict[str, Any]:
    return state.to_dict()


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
    paper_fill_price_mode = str(config.get("paper_fill_price_mode", "mid_bookticker")).strip().lower()
    paper_fill_price_fixed = _decimal_from_config(config, "paper_fill_price_fixed", "0")
    paper_slippage_bps = _decimal_from_config_keys(config, ("slippage_bps", "paper_slippage_bps"), "0")
    paper_fee_bps = _decimal_from_config_keys(config, ("fee_bps", "paper_fee_bps"), "0")
    initial_equity = _decimal_from_config(config, "initial_equity", "0")
    price_ref_paths = config.get("price_ref_paths") if isinstance(config.get("price_ref_paths"), dict) else {}
    price_ref_lookback_seconds = int(config.get("price_ref_lookback_seconds", 3600))
    decision_id = str(config.get("decision_id", "D-0001"))
    run_id = str(config.get("run_id", f"RUN-{uuid.uuid4().hex[:8]}"))
    correlation_id = str(config.get("correlation_id", run_id))
    position_state_path = str(config.get("paper_position_state_path", _default_paper_path(event_log_path, "position_state.json")))
    paper_ledger_path = str(config.get("paper_ledger_path", _default_paper_path(event_log_path, "ledger.jsonl")))
    paper_ledger_state_path = str(config.get("paper_ledger_state_path", _default_paper_path(event_log_path, "ledger_state.json")))

    if bar_close_time_utc is not None:
        evaluation_time_utc = bar_close_time_utc
    elif evaluation_time_source == "now_utc":
        evaluation_time_utc = _utc_now_iso()
    else:
        evaluation_time_utc = str(config["evaluation_time_utc"])

    price_ref_provider = PriceRefProvider(
        bookticker_parquet=(
            str(price_ref_paths.get("bookticker_parquet")) if price_ref_paths.get("bookticker_parquet") is not None else None
        ),
        premiumindex_parquet=(
            str(price_ref_paths.get("premiumindex_parquet")) if price_ref_paths.get("premiumindex_parquet") is not None else None
        ),
        lookback_seconds=price_ref_lookback_seconds,
        fixed_fallback=paper_fill_price_fixed,
    )
    price_reference = price_ref_provider.resolve(
        symbol=symbol,
        evaluation_time_utc=evaluation_time_utc,
        mode=paper_fill_price_mode,
    )
    price_ref_metadata = _serialize_price_reference(price_reference)

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
            price_ref_metadata=price_ref_metadata,
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
                price_ref_metadata=price_ref_metadata,
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
                price_ref_metadata=price_ref_metadata,
                payload={"phase": "end", "mode": "once", "skipped": True},
            ),
        )
        return 0

    signal_provider = build_signal_provider(signal_provider_name)
    broker = PaperBroker(ledger_path=paper_ledger_path)
    current_position = load_position_state(
        position_state_path,
        symbol=symbol,
        as_of_utc=evaluation_time_utc,
    )
    current_ledger = load_ledger_state(
        paper_ledger_state_path,
        symbol=symbol,
        initial_equity=initial_equity,
        as_of_utc=evaluation_time_utc,
        position_qty=current_position.qty,
        avg_entry_price=current_position.avg_entry_price,
    )
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

    desired_position_payload = _serialize_desired_position(
        symbol=desired_position.symbol,
        target_qty=desired_position.target_qty,
        target_notional=desired_position.target_notional,
        timestamp_utc=desired_position.timestamp_utc,
        source_timeframe=desired_position.source_timeframe,
        decision_id=desired_position.decision_id,
        correlation_id=desired_position.correlation_id,
        run_id=desired_position.run_id,
    )

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
            price_ref_metadata=price_ref_metadata,
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

    overlay_result["target_qty_after_multiplier"] = _decimal_text(adjusted_target_qty)
    overlay_result["desired_position_after_overlay"] = _serialize_desired_position(
        symbol=desired_position.symbol,
        target_qty=adjusted_target_qty,
        target_notional=desired_position.target_notional,
        timestamp_utc=desired_position.timestamp_utc,
        source_timeframe=desired_position.source_timeframe,
        decision_id=desired_position.decision_id,
        correlation_id=desired_position.correlation_id,
        run_id=desired_position.run_id,
        size_multiplier_applied=size_multiplier,
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
            bar_close_time_utc=evaluation_time_utc,
            symbol=symbol,
            price_ref_metadata=price_ref_metadata,
            payload=overlay_result,
        ),
    )

    delta_qty = ZERO
    no_trade_reason = "TARGET_QTY_MISSING"
    order_intent: OrderIntent | None = None
    if adjusted_target_qty is not None:
        delta_qty = position_delta_qty(current_position.qty, adjusted_target_qty)
        if delta_qty == ZERO:
            no_trade_reason = "TARGET_MATCHES_POSITION"
        else:
            order_intent = broker.build_rebalance_order_intent(
                symbol=symbol,
                current_qty=current_position.qty,
                target_qty=adjusted_target_qty,
                evaluation_time_utc=evaluation_time_utc,
                decision_id=decision_id,
                correlation_id=correlation_id,
            )
            if order_intent is None:
                no_trade_reason = "ORDER_INTENT_NOT_CREATED"

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
            price_ref_metadata=price_ref_metadata,
            payload={
                "status": "paper-safe",
                "note": "paper runtime only simulates deterministic local fills",
                "current_qty": _decimal_text(current_position.qty),
                "target_qty_after_multiplier": _decimal_text(adjusted_target_qty),
                "delta_qty": _decimal_text(delta_qty),
            },
        ),
    )

    order_intent_payload: dict[str, Any] = {
        "status": "trade_planned" if order_intent is not None else "no_trade",
        "current_qty": _decimal_text(current_position.qty),
        "target_qty_after_multiplier": _decimal_text(adjusted_target_qty),
        "delta_qty": _decimal_text(delta_qty),
        "paper_fill_price_mode": paper_fill_price_mode,
        "paper_fill_price_fixed": _decimal_text(paper_fill_price_fixed),
        "slippage_bps": _decimal_text(paper_slippage_bps),
        "fee_bps": _decimal_text(paper_fee_bps),
        "initial_equity": _decimal_text(initial_equity),
        "paper_slippage_bps": _decimal_text(paper_slippage_bps),
        "paper_fee_bps": _decimal_text(paper_fee_bps),
        "paper_position_state_path": position_state_path,
        "paper_ledger_path": paper_ledger_path,
        "paper_ledger_state_path": paper_ledger_state_path,
        "price_ref_lookup_mode": paper_fill_price_mode,
    }
    if order_intent is not None:
        order_intent_payload["order_intent"] = _serialize_order_intent(order_intent)
    else:
        order_intent_payload["reason"] = no_trade_reason

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
            price_ref_metadata=price_ref_metadata,
            payload=order_intent_payload,
        ),
    )

    next_position = snapshot_position_state(current_position, evaluation_time_utc)
    next_ledger = snapshot_ledger_state(current_ledger, evaluation_time_utc)
    if order_intent is not None:
        fill = broker.simulate_fill(
            order_intent,
            price_ref=price_reference.price_ref,
            slippage_bps=paper_slippage_bps,
            fee_bps=paper_fee_bps,
            price_ref_source=price_reference.price_ref_source,
            price_ref_asof_utc=price_reference.price_ref_asof_utc,
        )
        next_position = apply_fill_to_position(
            current_position,
            signed_fill_qty=fill.signed_qty,
            fill_price=fill.fill_price,
            as_of_utc=evaluation_time_utc,
        )
        next_ledger = current_ledger.apply_fill(fill, as_of_utc=evaluation_time_utc)
        broker.append_fill_ledger(
            fill,
            timestamp_utc=evaluation_time_utc,
            run_id=run_id,
            correlation_id=correlation_id,
            decision_id=decision_id,
            current_qty_before=current_position.qty,
            target_qty_after=adjusted_target_qty,
            position_qty_after=next_position.qty,
            ledger_state_after=_serialize_ledger_state(next_ledger),
        )
        append_event_jsonl(
            event_log_path,
            _event(
                event_type="FillEvent",
                run_id=run_id,
                correlation_id=correlation_id,
                decision_id=decision_id,
                env=env,
                timestamp_utc=evaluation_time_utc,
                bar_close_time_utc=evaluation_time_utc,
                symbol=symbol,
                price_ref_metadata=price_ref_metadata,
                payload={
                    "paper_ledger_path": paper_ledger_path,
                    "paper_ledger_state_path": paper_ledger_state_path,
                    "fill": _serialize_fill(fill),
                },
            ),
        )

    save_position_state(position_state_path, next_position)
    save_ledger_state(paper_ledger_state_path, next_ledger)
    ledger_payload = next_ledger.to_event_payload(
        evaluation_time_utc=evaluation_time_utc,
        mark_price=price_reference.price_ref,
    )
    ledger_payload["paper_ledger_path"] = paper_ledger_path
    ledger_payload["paper_ledger_state_path"] = paper_ledger_state_path
    ledger_payload["traded"] = order_intent is not None
    ledger_payload["ledger_state"] = _serialize_ledger_state(next_ledger)

    append_event_jsonl(
        event_log_path,
        _event(
            event_type="PositionEvent",
            run_id=run_id,
            correlation_id=correlation_id,
            decision_id=decision_id,
            env=env,
            timestamp_utc=evaluation_time_utc,
            bar_close_time_utc=evaluation_time_utc,
            symbol=symbol,
            price_ref_metadata=price_ref_metadata,
            payload={
                "evaluation_time_utc": evaluation_time_utc,
                "paper_position_state_path": position_state_path,
                "paper_ledger_path": paper_ledger_path,
                "current_qty_before": _decimal_text(current_position.qty),
                "target_qty_after_multiplier": _decimal_text(adjusted_target_qty),
                "delta_qty": _decimal_text(delta_qty),
                "position_qty_after": _decimal_text(next_position.qty),
                "traded": order_intent is not None,
                "position_state": _serialize_position(next_position),
            },
        ),
    )

    append_event_jsonl(
        event_log_path,
        _event(
            event_type="LedgerEvent",
            run_id=run_id,
            correlation_id=correlation_id,
            decision_id=decision_id,
            env=env,
            timestamp_utc=evaluation_time_utc,
            bar_close_time_utc=evaluation_time_utc,
            symbol=symbol,
            price_ref_metadata=price_ref_metadata,
            payload=ledger_payload,
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
            price_ref_metadata=price_ref_metadata,
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
