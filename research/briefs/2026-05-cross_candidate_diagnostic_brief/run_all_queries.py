"""Regenerate the WP-S2c-119 diagnostic query outputs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    brief_dir = Path(__file__).resolve().parent
    repo_root = Path(__file__).resolve().parents[3]
    queries_dir = brief_dir / "queries"
    outputs_dir = brief_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    for query_path in sorted(queries_dir.glob("Q*.sql")):
        output_path = outputs_dir / f"{query_path.stem}.json"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.research_query.run",
                "--sql",
                query_path.read_text(encoding="utf-8"),
                "--json",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            return result.returncode

        rows = json.loads(result.stdout)
        output_path.write_text(
            json.dumps(rows, indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output_path.relative_to(repo_root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
