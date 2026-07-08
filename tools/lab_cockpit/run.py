"""CLI that emits the static read-only lab product cockpit.

The CLI projects committed lab evidence (the merged coordinator state model and
the concluded real-traffic batch) into a deterministic static cockpit. It
performs no writes unless ``--out-dir`` is given (in which case it writes only
the static artifacts), runs no strategy, fetches no data, and renders no
executable control.

Usage::

    python -m tools.lab_cockpit.run --data-json
    python -m tools.lab_cockpit.run --html
    python -m tools.lab_cockpit.run --markdown
    python -m tools.lab_cockpit.run --out-dir build/lab_cockpit
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.lab_cockpit.model import build_cockpit_data
from tools.lab_cockpit.render import render_html, render_markdown
from tools.lab_state.resolver import REPO_ROOT


def _data_json(data: dict[str, Any]) -> str:
    # Sorted keys keep the JSON byte-identical across runs.
    return json.dumps(data, indent=2, sort_keys=True, default=str) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--data-json", action="store_true", help="Print the data model JSON")
    mode.add_argument("--html", action="store_true", help="Print the static HTML")
    mode.add_argument("--markdown", action="store_true", help="Print the static markdown")
    mode.add_argument(
        "--out-dir",
        type=Path,
        help="Write cockpit_data.json, cockpit.html, cockpit.md to a directory",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    data = build_cockpit_data(repo_root=REPO_ROOT)

    if args.data_json:
        print(_data_json(data), end="")
        return 0
    if args.html:
        print(render_html(data), end="")
        return 0
    if args.markdown:
        print(render_markdown(data), end="")
        return 0

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "cockpit_data.json").write_text(_data_json(data), encoding="utf-8")
    (out_dir / "cockpit.html").write_text(render_html(data), encoding="utf-8")
    (out_dir / "cockpit.md").write_text(render_markdown(data), encoding="utf-8")
    print(f"cockpit_data: {out_dir / 'cockpit_data.json'}")
    print(f"cockpit_html: {out_dir / 'cockpit.html'}")
    print(f"cockpit_md:   {out_dir / 'cockpit.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
