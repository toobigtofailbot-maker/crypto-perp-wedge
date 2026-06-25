"""CLI that emits the read-only lab approval / gate queue (data / HTML / markdown).

The CLI projects the committed coordinator-state subjects into a deterministic
read-only gate queue. It performs no writes unless ``--out-dir`` is given (in
which case it writes only the static artifacts), runs no strategy, fetches no
data, executes no gate, and renders no executable control.

Usage::

    python -m tools.lab_approval_queue.run --data-json
    python -m tools.lab_approval_queue.run --html
    python -m tools.lab_approval_queue.run --markdown
    python -m tools.lab_approval_queue.run --list-statuses
    python -m tools.lab_approval_queue.run --out-dir build/lab_approval_queue
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.lab_approval_queue.queue_model import QUEUE_STATUSES, build_queue_data
from tools.lab_approval_queue.render import render_html, render_markdown
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
        "--list-statuses", action="store_true", help="List the queue status vocabulary"
    )
    mode.add_argument(
        "--out-dir",
        type=Path,
        help="Write approval_queue_data.json, approval_queue.html, approval_queue.md",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list_statuses:
        print("\n".join(QUEUE_STATUSES))
        return 0

    data = build_queue_data(repo_root=REPO_ROOT)

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
    (out_dir / "approval_queue_data.json").write_text(_data_json(data), encoding="utf-8")
    (out_dir / "approval_queue.html").write_text(render_html(data), encoding="utf-8")
    (out_dir / "approval_queue.md").write_text(render_markdown(data), encoding="utf-8")
    print(f"approval_queue_data: {out_dir / 'approval_queue_data.json'}")
    print(f"approval_queue_html: {out_dir / 'approval_queue.html'}")
    print(f"approval_queue_md:   {out_dir / 'approval_queue.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
