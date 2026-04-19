"""CLI for the research DuckDB query layer."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_named_view,
    run_sql,
)


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _format_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "(no rows)"

    columns = list(rows[0].keys())
    widths = {
        column: max(len(column), *(len(_stringify(row.get(column))) for row in rows))
        for column in columns
    }
    header = " | ".join(column.ljust(widths[column]) for column in columns)
    divider = "-+-".join("-" * widths[column] for column in columns)
    body = [
        " | ".join(_stringify(row.get(column)).ljust(widths[column]) for column in columns)
        for row in rows
    ]
    return "\n".join([header, divider, *body])


def _print_rows(rows: list[dict[str, Any]], as_json: bool) -> None:
    if as_json:
        print(json.dumps(rows, indent=2, default=str))
        return
    print(_format_table(rows))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list-views", action="store_true", help="List available named views")
    mode.add_argument("--view", help="Run SELECT * FROM the named view")
    mode.add_argument("--sql", help="Run one read-only SELECT or WITH...SELECT statement")
    parser.add_argument("--json", action="store_true", help="Emit rows as a JSON array")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        conn = init_duckdb()
        views = list_views(conn)

        if args.list_views:
            if args.json:
                print(json.dumps(views, indent=2))
            else:
                print("\n".join(views))
            return 0

        if args.view:
            if args.view not in views:
                print(f"ERROR: unknown view: {args.view}", file=sys.stderr)
                print("Available views:", file=sys.stderr)
                for view in views:
                    print(f"  {view}", file=sys.stderr)
                return 1
            _print_rows(run_named_view(conn, args.view), args.json)
            return 0

        _print_rows(run_sql(conn, args.sql), args.json)
        return 0
    except ReadOnlyQueryError as exc:
        print(f"ERROR: read-only query violation: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

