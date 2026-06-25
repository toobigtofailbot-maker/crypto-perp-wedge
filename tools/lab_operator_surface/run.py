"""CLI that emits the unified read-only operator-surface index.

The CLI composes the merged read-only research-lab surfaces (coordinator state
model, results dashboard, operator brief / weekly report, approval / gate queue,
inert scheduler shell) into one deterministic index (data / HTML / markdown). It
performs no writes unless ``--out-dir`` is given (in which case it writes only
the static artifacts), runs no strategy, fetches no data, executes nothing, and
renders no executable control.

``--as-of`` / ``--period`` are descriptive labels only (passed through to the
brief / report surface); no clock is read, so output is deterministic for a
given checkout and labels.

Usage::

    python -m tools.lab_operator_surface.run --data-json
    python -m tools.lab_operator_surface.run --markdown
    python -m tools.lab_operator_surface.run --html
    python -m tools.lab_operator_surface.run --markdown --as-of 2026-06-25
    python -m tools.lab_operator_surface.run --out-dir build/lab_operator_surface
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.lab_operator_surface.index_model import build_index_data
from tools.lab_operator_surface.render import render_html, render_markdown
from tools.lab_state.resolver import REPO_ROOT


def _data_json(data: dict[str, Any]) -> str:
    # Sorted keys keep the JSON byte-identical across runs.
    return json.dumps(data, indent=2, sort_keys=True, default=str) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--data-json", action="store_true", help="Print the index data JSON")
    mode.add_argument("--markdown", action="store_true", help="Print the static markdown")
    mode.add_argument("--html", action="store_true", help="Print the static HTML")
    mode.add_argument(
        "--out-dir",
        type=Path,
        help=(
            "Write operator_surface_index_data.json, operator_surface_index.md, "
            "operator_surface_index.html to a directory"
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

    data = build_index_data(
        as_of=args.as_of, period=args.period, repo_root=REPO_ROOT
    )

    if args.data_json:
        print(_data_json(data), end="")
        return 0
    if args.markdown:
        print(render_markdown(data), end="")
        return 0
    if args.html:
        print(render_html(data), end="")
        return 0

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "operator_surface_index_data.json").write_text(
        _data_json(data), encoding="utf-8"
    )
    (out_dir / "operator_surface_index.md").write_text(
        render_markdown(data), encoding="utf-8"
    )
    (out_dir / "operator_surface_index.html").write_text(
        render_html(data), encoding="utf-8"
    )
    print(f"index_data: {out_dir / 'operator_surface_index_data.json'}")
    print(f"index_md:   {out_dir / 'operator_surface_index.md'}")
    print(f"index_html: {out_dir / 'operator_surface_index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
