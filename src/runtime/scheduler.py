from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return value.astimezone(timezone.utc)


def next_hour_close_utc(now_utc: datetime) -> datetime:
    now = _ensure_utc(now_utc)
    floored = now.replace(minute=0, second=0, microsecond=0)
    return floored + timedelta(hours=1)


def sleep_until(dt_utc: datetime) -> None:
    target = _ensure_utc(dt_utc)
    now = datetime.now(timezone.utc)
    remaining_seconds = (target - now).total_seconds()
    if remaining_seconds > 0:
        time.sleep(remaining_seconds)
