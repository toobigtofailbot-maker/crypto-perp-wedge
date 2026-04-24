"""Re-run the WP-7v shadow-signal lineage slice queries."""

from __future__ import annotations

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
        query_prefix = query_path.stem.split("_", 1)[0]
        output_path = outputs_dir / f"{query_prefix}.json"
        sql_text = query_path.read_text(encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.research_query.run",
                "--sql",
                sql_text,
                "--json",
            ],
            cwd=repo_root,
            capture_output=True,
        )
        if result.returncode != 0:
            sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
            return result.returncode

        output_path.write_bytes(result.stdout)
        print(f"Wrote {output_path.relative_to(repo_root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
