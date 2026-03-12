from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if ROOT.as_posix() not in sys.path:
    sys.path.insert(0, ROOT.as_posix())

from src.context.fmp_client import fetch_fmp_events, read_snapshot_json
from src.context.macro_calendar import build_snapshot
from src.context.macro_flags import generate_macro_flags


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _default_fetch_range() -> tuple[str, str]:
    today = date.today()
    return (today - timedelta(days=30)).isoformat(), (today + timedelta(days=365)).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic macro window flags.")
    parser.add_argument("--fetch", action="store_true", help="Fetch FMP and write snapshot+flags")
    parser.add_argument("--from-snapshot", type=Path, default=None, help="Offline mode: use cached snapshot")
    parser.add_argument("--config", type=Path, default=Path("configs/fmp_macro_flags.json"))
    parser.add_argument("--out-snapshot", type=Path, default=Path("reports/context/context_snapshot.json"))
    parser.add_argument("--out-flags", type=Path, default=Path("reports/overlay/macro_window_flags.json"))
    args = parser.parse_args()

    config = _read_json(args.config)
    snapshot = None

    if args.fetch:
        api_key = os.environ.get("FMP_API_KEY", "")
        if api_key:
            date_from, date_to = _default_fetch_range()
            try:
                events = fetch_fmp_events(api_key=api_key, date_from=date_from, date_to=date_to)
                snapshot = build_snapshot(events, source="fmp_api")
            except Exception:
                snapshot = None
        if snapshot is None:
            snapshot = build_snapshot([], source="fmp_api_unavailable")
        _write_json(args.out_snapshot, snapshot)
    elif args.from_snapshot:
        try:
            snapshot = read_snapshot_json(args.from_snapshot)
        except Exception:
            snapshot = None

    flags = generate_macro_flags(snapshot=snapshot, config=config)
    _write_json(args.out_flags, flags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
