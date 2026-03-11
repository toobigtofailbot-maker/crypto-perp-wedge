"""Deterministic macro-window flag generation.

Merging policy: all generated event windows are first sorted by (start_utc, end_utc,
permission, size_multiplier). Overlapping windows are merged by splitting at every
start/end boundary and assigning each segment the most restrictive active permission
(minimum size_multiplier => BLOCK > ALLOW_REDUCED > ALLOW). Adjacent segments with
identical permission are coalesced.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

PERMISSION_TO_MULTIPLIER = {"ALLOW": 1.0, "ALLOW_REDUCED": 0.5, "BLOCK": 0.0}
MULTIPLIER_TO_PERMISSION = {v: k for k, v in PERMISSION_TO_MULTIPLIER.items()}
FAIL_OPEN_WINDOW = {
    "start_utc": "1970-01-01T00:00:00Z",
    "end_utc": "2100-01-01T00:00:00Z",
    "permission": "ALLOW",
    "size_multiplier": 1.0,
}


def _to_utc_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _to_utc_iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _permission_for_event(config: dict[str, Any], event_type: str) -> str:
    configured = str(config.get("per_event_permission", {}).get(event_type, "ALLOW")).upper()
    # TODO(decision:D-0001): keep fail-open default ALLOW until explicitly changed by decision entry.
    return configured if configured in PERMISSION_TO_MULTIPLIER else "ALLOW"


def _window_minutes(config: dict[str, Any], event_type: str) -> tuple[int, int]:
    per_event = config.get("per_event_window_minutes", {}).get(event_type, {})
    # TODO(decision:D-0001): keep missing window values at 0 minutes until policy updates.
    pre = int(per_event.get("pre", 0))
    post = int(per_event.get("post", 0))
    return max(pre, 0), max(post, 0)


def _merge_windows(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not windows:
        return []

    boundaries = sorted({_to_utc_datetime(w["start_utc"]) for w in windows} | {_to_utc_datetime(w["end_utc"]) for w in windows})
    merged: list[dict[str, Any]] = []

    for i in range(len(boundaries) - 1):
        start = boundaries[i]
        end = boundaries[i + 1]
        if end <= start:
            continue

        active = [w for w in windows if _to_utc_datetime(w["start_utc"]) <= start and _to_utc_datetime(w["end_utc"]) >= end]
        if not active:
            continue

        chosen_multiplier = min(w["size_multiplier"] for w in active)
        candidate = {
            "start_utc": _to_utc_iso(start),
            "end_utc": _to_utc_iso(end),
            "permission": MULTIPLIER_TO_PERMISSION[chosen_multiplier],
            "size_multiplier": chosen_multiplier,
        }
        if merged and merged[-1]["end_utc"] == candidate["start_utc"] and merged[-1]["permission"] == candidate["permission"]:
            merged[-1]["end_utc"] = candidate["end_utc"]
        else:
            merged.append(candidate)

    return merged


def _is_context_missing(snapshot: dict[str, Any] | None) -> bool:
    if snapshot is None or not isinstance(snapshot, dict):
        return True
    events = snapshot.get("events")
    if not isinstance(events, list):
        return True
    return len(events) == 0


def generate_macro_flags(snapshot: dict[str, Any] | None, config: dict[str, Any]) -> dict[str, Any]:
    context_missing = _is_context_missing(snapshot)
    fail_open = bool(config.get("fail_open", True))

    if context_missing:
        asof = "1970-01-01T00:00:00Z"
        snapshot_hash = ""
        if isinstance(snapshot, dict):
            asof = str(snapshot.get("asof_timestamp_utc", asof))
            snapshot_hash = str(snapshot.get("snapshot_hash", snapshot_hash))
        windows = [dict(FAIL_OPEN_WINDOW)] if fail_open else []
        return {
            "asof_timestamp_utc": asof,
            "snapshot_hash": snapshot_hash,
            "decision_id": "D-0001",
            "context_missing": True,
            "windows": windows,
        }

    events = snapshot.get("events", [])
    windows = []
    for event in events:
        event_type = str(event.get("event_type", "")).upper()
        if event_type not in {"CPI", "FOMC", "NFP"}:
            continue

        event_time = _to_utc_datetime(str(event.get("event_timestamp_utc")))
        pre, post = _window_minutes(config, event_type)
        permission = _permission_for_event(config, event_type)
        windows.append(
            {
                "start_utc": _to_utc_iso(event_time - timedelta(minutes=pre)),
                "end_utc": _to_utc_iso(event_time + timedelta(minutes=post)),
                "permission": permission,
                "size_multiplier": PERMISSION_TO_MULTIPLIER[permission],
            }
        )

    windows.sort(key=lambda w: (w["start_utc"], w["end_utc"], w["permission"], w["size_multiplier"]))
    windows = _merge_windows(windows)

    if not windows and fail_open:
        return {
            "asof_timestamp_utc": str(snapshot.get("asof_timestamp_utc", "1970-01-01T00:00:00Z")),
            "snapshot_hash": str(snapshot.get("snapshot_hash", "")),
            "decision_id": "D-0001",
            "context_missing": True,
            "windows": [dict(FAIL_OPEN_WINDOW)],
        }

    return {
        "asof_timestamp_utc": str(snapshot.get("asof_timestamp_utc", "1970-01-01T00:00:00Z")),
        "snapshot_hash": str(snapshot.get("snapshot_hash", "")),
        "decision_id": "D-0001",
        "context_missing": False,
        "windows": windows,
    }
