"""CLI for the read-only lab data/simulator readiness display.

Usage:
    python -m tools.lab_readiness.run --json
    python -m tools.lab_readiness.run --markdown
    python -m tools.lab_readiness.run --out-dir build/lab_readiness
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.lab_readiness.readiness import build_readiness_projection, render_markdown


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--json", action="store_true", help="Print readiness JSON")
    mode.add_argument("--markdown", action="store_true", help="Print readiness markdown")
    mode.add_argument(
        "--out-dir",
        type=Path,
        help="Write readiness.json and readiness.md to the provided directory",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    data = build_readiness_projection()

    if args.json:
        print(_json(data), end="")
        return 0
    if args.markdown:
        print(render_markdown(data), end="")
        return 0

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "readiness.json").write_text(_json(data), encoding="utf-8")
    (out_dir / "readiness.md").write_text(render_markdown(data), encoding="utf-8")
    print(f"readiness_json: {out_dir / 'readiness.json'}")
    print(f"readiness_md:   {out_dir / 'readiness.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
