"""Generate the local/offline static dashboard MVP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.dashboard.collector import collect_dashboard_data
from tools.dashboard.renderer import render_dashboard
from tools.dashboard.validate_dashboard_data import validate_dashboard_data_file


def generate_dashboard(repo_root: Path, data_dir: Path, output_dir: Path) -> tuple[Path, Path]:
    data_dir.mkdir(parents=True, exist_ok=True)
    dashboard_data_path = data_dir / "dashboard_data.json"

    dashboard_data = collect_dashboard_data(repo_root)
    dashboard_data_path.write_text(
        json.dumps(dashboard_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    errors = validate_dashboard_data_file(dashboard_data_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    index_path = render_dashboard(dashboard_data, output_dir)
    return dashboard_data_path, index_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--data-dir", type=Path, default=Path("dashboard_data"))
    parser.add_argument("--output-dir", type=Path, default=Path("dashboard_build"))
    args = parser.parse_args(argv)

    dashboard_data_path, index_path = generate_dashboard(
        args.repo_root.resolve(),
        args.data_dir,
        args.output_dir,
    )
    print(f"dashboard_data: {dashboard_data_path}")
    print(f"dashboard_html: {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
