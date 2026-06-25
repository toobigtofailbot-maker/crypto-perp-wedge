"""CLI for the inert, default-off research-lab scheduler shell.

The CLI loads a static run-queue fixture, validates the default-off
configuration, renders queue status, and prints a dry-run plan whose actions are
all no-ops. It performs no writes, creates no runs, and contacts no runtime.

Usage::

    python -m tools.lab_scheduler_shell.run --snapshot
    python -m tools.lab_scheduler_shell.run --snapshot --json
    python -m tools.lab_scheduler_shell.run --queue-status
    python -m tools.lab_scheduler_shell.run --dry-run --json
    python -m tools.lab_scheduler_shell.run --validate-config
    python -m tools.lab_scheduler_shell.run --list-statuses
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from tools.lab_scheduler_shell import model
from tools.lab_scheduler_shell.config import DEFAULT_OFF_FLAGS, default_config
from tools.lab_scheduler_shell.shell import SchedulerShell
from tools.lab_state.resolver import REPO_ROOT

DEFAULT_FIXTURE = (
    REPO_ROOT
    / "scratch"
    / "WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01"
    / "run_queue_fixture.json"
)


def _format_snapshot(snap: dict[str, Any]) -> str:
    cfg = snap["default_off_config"]
    val = snap["config_validation"]
    qs = snap["queue_status"]
    dr = snap["dry_run"]
    lines = [
        f"Inert scheduler shell ({snap['schema_version']})  [{snap['surface_kind']}]",
        "",
        "  Default-off config:",
    ]
    for name in DEFAULT_OFF_FLAGS:
        lines.append(f"    {name:<38} {str(cfg[name]).lower()}")
    lines.append(f"    all_default_off: {str(val['all_default_off']).lower()}")
    lines.append("")
    lines.append(f"  Run queue ({qs['entry_count']} entries):")
    for entry in qs["entries"]:
        retry = entry["retry"]
        block = (
            f"  block={retry['block_reason_code']}"
            if retry["block_reason_code"]
            else ""
        )
        lines.append(
            f"    {entry['run_id']:<22} {entry['status']:<18} "
            f"{entry['subject_id']} -> {entry['target_stage']}{block}"
        )
    lines.append("")
    lines.append(
        f"  Dry-run: {dr['planned_action_count']} planned, "
        f"all no-op = {str(dr['all_actions_noop']).lower()} "
        f"(reason {dr['noop_reason_code']}); executed_any_action = "
        f"{str(dr['executed_any_action']).lower()}"
    )
    lines.append("")
    lines.append(f"  {snap['edge_search_hold']}")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--snapshot", action="store_true", help="Print the full shell snapshot")
    mode.add_argument("--queue-status", action="store_true", help="Print queue status")
    mode.add_argument("--dry-run", action="store_true", help="Print the dry-run no-op plan")
    mode.add_argument("--validate-config", action="store_true", help="Validate default-off config")
    mode.add_argument("--list-statuses", action="store_true", help="List run-status vocabulary")
    parser.add_argument(
        "--fixture", type=Path, default=DEFAULT_FIXTURE, help="Run-queue fixture path"
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser


def _emit(payload: Any, as_json: bool, text: str | None = None) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        print(text if text is not None else payload)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list_statuses:
        payload = {
            "run_statuses": list(model.RUN_STATUSES),
            "retry_states": list(model.RETRY_STATES),
            "block_reason_codes": list(model.BLOCK_REASON_CODES),
        }
        _emit(payload, args.json, "\n".join(model.RUN_STATUSES))
        return 0

    if args.validate_config:
        config = default_config()
        from tools.lab_scheduler_shell.config import validate_default_off

        result = validate_default_off(config)
        text = (
            f"all_default_off: {str(result['all_default_off']).lower()}\n"
            f"enabled_flags: {result['enabled_flags']}\n"
            f"missing_flags: {result['missing_flags']}"
        )
        _emit({"config": config.as_dict(), "validation": result}, args.json, text)
        return 0

    if not args.fixture.exists():
        print(f"ERROR: fixture not found: {args.fixture}", file=sys.stderr)
        return 1

    shell = SchedulerShell.from_fixture(args.fixture)

    if args.queue_status:
        _emit(shell.queue_status(), args.json, json.dumps(shell.queue_status(), indent=2))
        return 0
    if args.dry_run:
        _emit(shell.dry_run(), args.json, json.dumps(shell.dry_run(), indent=2))
        return 0

    snap = shell.snapshot()
    _emit(snap, args.json, _format_snapshot(snap))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
