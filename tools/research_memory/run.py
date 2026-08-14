"""CLI for migrations, repo bootstrap/rebuild, and bounded lookups."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.research_memory.migrations import apply_migrations
from tools.research_memory.repository import ResearchMemoryRepository


def _definition(value: str) -> dict[str, Any]:
    path = Path(value)
    payload = path.read_text(encoding="utf-8") if path.is_file() else value
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError("definition must be a JSON object")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dsn", required=True, help="PostgreSQL connection string")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("migrate")
    for name in ("bootstrap", "rebuild"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--repo-root", type=Path, default=Path.cwd())

    lookup = subparsers.add_parser("lookup")
    lookup.add_argument("--definition", required=True, type=_definition)
    lookup.add_argument("--repo-root", type=Path, default=Path.cwd())

    alias = subparsers.add_parser("lookup-alias")
    alias.add_argument("--alias", required=True)
    alias.add_argument("--alias-kind", default="candidate_id")
    alias.add_argument("--repo-root", type=Path, default=Path.cwd())

    negative = subparsers.add_parser("negative")
    negative.add_argument("--strategy-family")
    negative.add_argument("--primary-timeframe")
    negative.add_argument("--repo-root", type=Path, default=Path.cwd())
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "migrate":
        result = apply_migrations(args.dsn)
        print(json.dumps({"applied": result.applied, "already_applied": result.already_applied}))
        return 0

    with ResearchMemoryRepository.connect(args.dsn) as repository:
        if args.command in {"bootstrap", "rebuild"}:
            result = repository.refresh_from_repo(args.repo_root, rebuild=args.command == "rebuild")
        elif args.command == "lookup":
            result = repository.has_this_been_tried(args.definition, repo_root=args.repo_root)
        elif args.command == "lookup-alias":
            result = repository.lookup_alias(
                args.alias, alias_kind=args.alias_kind, repo_root=args.repo_root
            )
        else:
            result = repository.negative_results(
                repo_root=args.repo_root,
                strategy_family=args.strategy_family,
                primary_timeframe=args.primary_timeframe,
            )
    print(json.dumps(result, indent=2, default=str, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
