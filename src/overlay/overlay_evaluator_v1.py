from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


PERMISSION_TO_MULTIPLIER = {
    "ALLOW": 1.0,
    "ALLOW_REDUCED": 0.5,
    "BLOCK": 0.0,
}

SEVERITY_RANK = {
    "BLOCK": 0,
    "ALLOW_REDUCED": 1,
    "ALLOW": 2,
}


def _to_utc_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _base_result(
    desired_position: Mapping[str, Any],
    evaluation_time_utc: str,
    trade_permission: str,
    size_multiplier: float,
    context_missing: bool,
    reason_code: str,
) -> dict[str, Any]:
    return {
        "symbol": desired_position.get("symbol"),
        "decision_id": desired_position.get("decision_id"),
        "correlation_id": desired_position.get("correlation_id"),
        "run_id": desired_position.get("run_id"),
        "evaluation_time_utc": evaluation_time_utc,
        "trade_permission": trade_permission,
        "size_multiplier": size_multiplier,
        "context_missing": context_missing,
        "reason_code": reason_code,
    }


def _fail_open(
    desired_position: Mapping[str, Any],
    evaluation_time_utc: str,
    reason_code: str,
) -> dict[str, Any]:
    return _base_result(
        desired_position=desired_position,
        evaluation_time_utc=evaluation_time_utc,
        trade_permission="ALLOW",
        size_multiplier=1.0,
        context_missing=True,
        reason_code=reason_code,
    )


def _build_audit_event(result: Mapping[str, Any], macro_flags_path: str) -> dict[str, Any]:
    event_seed = "|".join(
        [
            str(result.get("decision_id") or ""),
            str(result.get("correlation_id") or ""),
            str(result.get("run_id") or ""),
            str(result.get("evaluation_time_utc") or ""),
            str(result.get("trade_permission") or ""),
            str(result.get("reason_code") or ""),
        ]
    )
    event_id = hashlib.sha256(event_seed.encode("utf-8")).hexdigest()[:16]

    return {
        "timestamp_utc": result["evaluation_time_utc"],
        "run_id": result.get("run_id"),
        "correlation_id": result.get("correlation_id"),
        "event_id": event_id,
        "event_type": "OVERLAY_EVALUATED",
        "decision_id": result.get("decision_id"),
        "symbol": result.get("symbol"),
        "severity": "INFO",
        "payload": {
            "trade_permission": result["trade_permission"],
            "size_multiplier": result["size_multiplier"],
            "context_missing": result["context_missing"],
            "reason_code": result["reason_code"],
            "macro_flags_path": macro_flags_path,
        },
    }


def _append_jsonl(audit_path: str | None, event: Mapping[str, Any]) -> None:
    if not audit_path:
        return

    path = Path(audit_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(event), sort_keys=True) + "\n")


def _finalize_result(
    result: dict[str, Any],
    macro_flags_path: str,
    audit_path: str | None,
) -> dict[str, Any]:
    _append_jsonl(audit_path, _build_audit_event(result, macro_flags_path))
    return result


def evaluate_overlay(
    desired_position: Mapping[str, Any],
    evaluation_time_utc: str,
    macro_flags_path: str = "reports/overlay/macro_window_flags.json",
    audit_path: str | None = None,
) -> dict[str, Any]:
    try:
        evaluation_dt = _to_utc_datetime(evaluation_time_utc)
    except Exception as exc:
        raise ValueError(f"Invalid evaluation_time_utc: {evaluation_time_utc}") from exc

    path = Path(macro_flags_path)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _finalize_result(
            _fail_open(desired_position, evaluation_time_utc, "FLAGS_FILE_MISSING"),
            macro_flags_path,
            audit_path,
        )
    except (OSError, json.JSONDecodeError, ValueError):
        return _finalize_result(
            _fail_open(desired_position, evaluation_time_utc, "FLAGS_FILE_INVALID"),
            macro_flags_path,
            audit_path,
        )

    if not isinstance(payload, dict):
        return _finalize_result(
            _fail_open(desired_position, evaluation_time_utc, "FLAGS_PAYLOAD_INVALID"),
            macro_flags_path,
            audit_path,
        )

    payload_context_missing = bool(payload.get("context_missing", False))

    windows = payload.get("windows")
    if not isinstance(windows, list) or len(windows) == 0:
        return _finalize_result(
            _fail_open(desired_position, evaluation_time_utc, "FLAGS_WINDOWS_EMPTY"),
            macro_flags_path,
            audit_path,
        )

    active_windows: list[dict[str, str]] = []

    for window in windows:
        if not isinstance(window, dict):
            continue

        try:
            permission = str(window["permission"]).upper()
            start_utc = str(window["start_utc"])
            end_utc = str(window["end_utc"])
            start_dt = _to_utc_datetime(start_utc)
            end_dt = _to_utc_datetime(end_utc)
        except (KeyError, TypeError, ValueError):
            continue

        if permission not in PERMISSION_TO_MULTIPLIER:
            continue

        if start_dt <= evaluation_dt <= end_dt:
            active_windows.append(
                {
                    "permission": permission,
                    "start_utc": start_utc,
                    "end_utc": end_utc,
                }
            )

    if not active_windows:
        return _finalize_result(
            _base_result(
                desired_position=desired_position,
                evaluation_time_utc=evaluation_time_utc,
                trade_permission="ALLOW",
                size_multiplier=1.0,
                context_missing=payload_context_missing,
                reason_code="NO_ACTIVE_WINDOW",
            ),
            macro_flags_path,
            audit_path,
        )

    chosen = sorted(
        active_windows,
        key=lambda item: (
            SEVERITY_RANK[item["permission"]],
            item["start_utc"],
            item["end_utc"],
            item["permission"],
        ),
    )[0]

    permission = chosen["permission"]

    return _finalize_result(
        _base_result(
            desired_position=desired_position,
            evaluation_time_utc=evaluation_time_utc,
            trade_permission=permission,
            size_multiplier=PERMISSION_TO_MULTIPLIER[permission],
            context_missing=payload_context_missing,
            reason_code="ACTIVE_WINDOW_MATCH",
        ),
        macro_flags_path,
        audit_path,
    )
