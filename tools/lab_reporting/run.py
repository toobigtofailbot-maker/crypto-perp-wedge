"""CLI that emits the read-only operator daily brief / weekly report.

The CLI shapes the committed coordinator-state subjects (via the read-only lab
dashboard projection) into a deterministic operator daily brief and weekly
report. It performs no writes unless ``--out-dir`` is given (in which case it
writes only the static artifacts), runs no strategy, fetches no data, emits no
recommendation / decision label, and never sends or notifies.

``--as-of`` / ``--period`` are descriptive labels only; no clock is read, so
output is deterministic for a given checkout and labels.

Usage::

    python -m tools.lab_reporting.run --report-data
    python -m tools.lab_reporting.run --daily-brief --as-of 2026-06-25
    python -m tools.lab_reporting.run --weekly-report --period 2026-W26
    python -m tools.lab_reporting.run --weekly-report-html --period 2026-W26
    python -m tools.lab_reporting.run --out-dir build/lab_reporting --as-of D --period W
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.lab_reporting.report_model import build_report_data
from tools.lab_reporting.render import (
    render_daily_brief_markdown,
    render_weekly_report_html,
    render_weekly_report_markdown,
)
from tools.lab_state.resolver import REPO_ROOT


def _report_json(data: dict[str, Any]) -> str:
    # Sorted keys keep the JSON byte-identical across runs.
    return json.dumps(data, indent=2, sort_keys=True, default=str) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--report-data", action="store_true", help="Print the report data model JSON"
    )
    mode.add_argument(
        "--daily-brief", action="store_true", help="Print the daily brief markdown"
    )
    mode.add_argument(
        "--weekly-report", action="store_true", help="Print the weekly report markdown"
    )
    mode.add_argument(
        "--weekly-report-html",
        action="store_true",
        help="Print the weekly report static HTML",
    )
    mode.add_argument(
        "--out-dir",
        type=Path,
        help=(
            "Write report_data.json, daily_brief.md, weekly_report.md, "
            "weekly_report.html to a directory"
        ),
    )
    parser.add_argument(
        "--as-of", default=None, help="Descriptive as-of label for the daily brief"
    )
    parser.add_argument(
        "--period", default=None, help="Descriptive period label for the weekly report"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    data = build_report_data(
        as_of=args.as_of, period=args.period, repo_root=REPO_ROOT
    )

    if args.report_data:
        print(_report_json(data), end="")
        return 0
    if args.daily_brief:
        print(render_daily_brief_markdown(data), end="")
        return 0
    if args.weekly_report:
        print(render_weekly_report_markdown(data), end="")
        return 0
    if args.weekly_report_html:
        print(render_weekly_report_html(data), end="")
        return 0

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report_data.json").write_text(_report_json(data), encoding="utf-8")
    (out_dir / "daily_brief.md").write_text(
        render_daily_brief_markdown(data), encoding="utf-8"
    )
    (out_dir / "weekly_report.md").write_text(
        render_weekly_report_markdown(data), encoding="utf-8"
    )
    (out_dir / "weekly_report.html").write_text(
        render_weekly_report_html(data), encoding="utf-8"
    )
    print(f"report_data:    {out_dir / 'report_data.json'}")
    print(f"daily_brief:    {out_dir / 'daily_brief.md'}")
    print(f"weekly_report:  {out_dir / 'weekly_report.md'}")
    print(f"weekly_html:    {out_dir / 'weekly_report.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
