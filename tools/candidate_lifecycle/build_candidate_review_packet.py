"""Build a candidate lifecycle review packet from a lifecycle engine input."""

from __future__ import annotations

import argparse
from pathlib import Path

from tools.candidate_lifecycle.lifecycle_engine import DEFAULT_OUTPUT_DIR, run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    run(args.input, args.output_dir)
    print(f"OK: wrote candidate review packet to {args.output_dir / 'candidate_review_packet.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
