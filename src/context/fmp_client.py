"""FMP calendar client (stdlib-only)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

FMP_ECONOMIC_CALENDAR_URL = "https://financialmodelingprep.com/api/v3/economic_calendar"
TARGET_EVENT_TYPES = {"CPI", "FOMC", "NFP"}


def _classify_event_type(title: str) -> str | None:
    text = (title or "").upper()
    if "FOMC" in text:
        return "FOMC"
    if "NON FARM PAYROLL" in text or "NFP" in text:
        return "NFP"
    if "CONSUMER PRICE INDEX" in text or text.startswith("CPI") or " CPI" in text:
        return "CPI"
    return None


def fetch_fmp_events(api_key: str, date_from: str, date_to: str) -> list[dict[str, Any]]:
    """Fetch CPI/FOMC/NFP events from FMP economic calendar endpoint."""
    query = urlencode({"from": date_from, "to": date_to, "apikey": api_key})
    url = f"{FMP_ECONOMIC_CALENDAR_URL}?{query}"
    with urlopen(url, timeout=20) as response:  # nosec B310 - fixed HTTPS endpoint
        payload = json.loads(response.read().decode("utf-8"))

    events: list[dict[str, Any]] = []
    for item in payload if isinstance(payload, list) else []:
        title = str(item.get("event", ""))
        event_type = _classify_event_type(title)
        if event_type not in TARGET_EVENT_TYPES:
            continue
        event = dict(item)
        event["event_type"] = event_type
        events.append(event)

    return events


def read_snapshot_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
