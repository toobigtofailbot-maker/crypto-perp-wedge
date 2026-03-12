"""Snapshot normalization for macro-calendar context."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_to_utc_iso(value: str) -> str:
    text = (value or "").strip()
    if not text:
        raise ValueError("missing datetime")

    if text.endswith("Z"):
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    else:
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            dt = datetime.fromisoformat(text.replace(" ", "T"))

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def build_snapshot(raw_events: list[dict[str, Any]], source: str, asof_timestamp_utc: str | None = None) -> dict[str, Any]:
    normalized_events: list[dict[str, str]] = []
    for event in raw_events:
        event_type = str(event.get("event_type", "")).upper()
        if event_type not in {"CPI", "FOMC", "NFP"}:
            continue

        event_time = event.get("date") or event.get("event_timestamp_utc")
        if not event_time:
            continue

        normalized_events.append(
            {
                "event_type": event_type,
                "event_timestamp_utc": _parse_to_utc_iso(str(event_time)),
                "title": str(event.get("event") or event.get("title") or event_type),
            }
        )

    normalized_events.sort(key=lambda row: (row["event_timestamp_utc"], row["event_type"], row["title"]))

    base = {
        "asof_timestamp_utc": asof_timestamp_utc or _utc_now_iso(),
        "source": source,
        "events": normalized_events,
    }
    snapshot_hash = hashlib.sha256(_canonical_json_bytes(base)).hexdigest()
    base["snapshot_hash"] = snapshot_hash
    return base
