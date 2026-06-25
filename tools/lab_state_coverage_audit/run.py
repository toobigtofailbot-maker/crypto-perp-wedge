"""CLI that emits the static, read-only coverage audit.

Enumerates git-tracked artifacts under the audited research roots, classifies
each via :mod:`tools.lab_state_coverage_audit.audit`, and prints/serializes the
inventory, summary, and a markdown report. It performs no writes to repo state,
runs no strategy, fetches no data, and changes no coordinator bindings.

Usage::

    python -m tools.lab_state_coverage_audit.run --summary
    python -m tools.lab_state_coverage_audit.run --summary --json
    python -m tools.lab_state_coverage_audit.run --inventory --json
    python -m tools.lab_state_coverage_audit.run --report
    python -m tools.lab_state_coverage_audit.run --list-categories
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from tools.lab_state.resolver import REPO_ROOT
from tools.lab_state.run import SUBJECTS
from tools.lab_state_coverage_audit import audit
from tools.lab_state_coverage_audit.audit import (
    CoverageContext,
    classify_artifact,
    coordinator_paths_from_subjects,
)

# Roots enumerated for committed research artifacts.
AUDITED_ROOTS: tuple[str, ...] = (
    "docs/research",
    "docs/status_entries",
    "research",
    "scratch",
)


def _git_tracked(roots: tuple[str, ...], repo_root: Path) -> list[str]:
    """Return git-tracked, repo-relative paths under ``roots`` (committed truth)."""
    out = subprocess.run(
        ["git", "ls-files", "-z", *roots],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    paths = [p for p in out.stdout.split("\0") if p]
    return sorted(paths)


def _maybe_malformed(path: str, ctx: CoverageContext, repo_root: Path) -> bool:
    """Fail-closed read: parse JSON evidence the audit relies on for coverage.

    Only JSON/JSONL artifacts in the coverage-bearing sets are parsed (coordinator
    paths and unmapped-conclusion/canonical evidence). A parse failure marks the
    artifact malformed so it never masquerades as covered or out-of-scope.
    """
    if not (path.endswith(".json") or path.endswith(".jsonl")):
        return False
    provisional = classify_artifact(path, ctx)
    if provisional.coverage_status not in {"covered", "unmapped_gap"}:
        return False
    file_path = repo_root / path
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError:
        return True
    try:
        if path.endswith(".jsonl"):
            for line in text.splitlines():
                if line.strip():
                    json.loads(line)
        else:
            json.loads(text)
    except json.JSONDecodeError:
        return True
    return False


def build_coverage_audit(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Assemble the full audit payload (inventory + summary) read-only."""
    surface_paths, consulted_paths = coordinator_paths_from_subjects(SUBJECTS)
    # Coordinator-bound fixture artifacts (replay/OOS) stay coordinator-covered;
    # no path is a pure test fixture outside that binding, so this set is empty.
    ctx = CoverageContext(
        surface_paths=surface_paths,
        consulted_paths=consulted_paths,
        fixture_paths=frozenset(),
    )

    classifications = []
    for path in _git_tracked(AUDITED_ROOTS, repo_root):
        malformed = _maybe_malformed(path, ctx, repo_root)
        classifications.append(classify_artifact(path, ctx, malformed=malformed))

    summary = audit.build_audit(classifications, subjects=SUBJECTS)
    return {
        "summary": summary,
        "context": {
            "audited_roots": list(AUDITED_ROOTS),
            "surface_paths": sorted(surface_paths),
            "consulted_paths": sorted(consulted_paths),
        },
        "inventory": [c.to_dict() for c in classifications],
    }


def _render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    totals = summary["totals"]
    lines = [
        "# Lab state-model coverage audit report",
        "",
        summary["non_authority_declaration"],
        "",
        f"Schema: `{summary['schema_version']}`",
        f"Coordinator subjects: {', '.join(summary['coordinator_subjects'])}",
        "",
        "## Totals",
        "",
        f"- total discovered artifacts: {totals['total_discovered_artifacts']}",
        f"- covered coordinator artifacts: {totals['covered_coordinator_artifacts']}",
        f"- surface-visible artifacts: {totals['surface_visible_artifacts']}",
        f"- unmapped gap artifacts: {totals['unmapped_gap_artifacts']}",
        f"- malformed / unreadable artifacts: "
        f"{totals['malformed_or_unreadable_artifacts']}",
        "",
        "## By category",
        "",
    ]
    for category, count in summary["by_category"].items():
        lines.append(f"- {category}: {count}")
    lines += ["", "## By coverage status", ""]
    for status, count in summary["by_coverage_status"].items():
        lines.append(f"- {status}: {count}")
    lines += ["", "## Findings (unmapped committed conclusions)", ""]
    if summary["findings"]:
        for finding in summary["findings"]:
            lines.append(
                f"- **{finding['subject_group']}** "
                f"({finding['artifact_count']} artifact(s)): {finding['detail']}"
            )
            for path in finding["example_paths"]:
                lines.append(f"    - `{path}`")
    else:
        lines.append("- none")
    lines += ["", "## Recommended follow-up packages", ""]
    if summary["recommended_follow_up_packages"]:
        for fu in summary["recommended_follow_up_packages"]:
            lines.append(f"- **{fu['package']}** — {fu['intent']}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--summary", action="store_true", help="Print the audit summary")
    mode.add_argument("--inventory", action="store_true", help="Print the artifact inventory")
    mode.add_argument("--report", action="store_true", help="Print the markdown report")
    mode.add_argument("--list-categories", action="store_true", help="List categories")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list_categories:
        print(json.dumps(list(audit.CATEGORIES), indent=2) if args.json
              else "\n".join(audit.CATEGORIES))
        return 0

    payload = build_coverage_audit()

    if args.summary:
        if args.json:
            print(json.dumps(payload["summary"], indent=2, sort_keys=True))
        else:
            print(_render_report(payload))
        return 0
    if args.inventory:
        if args.json:
            print(json.dumps(payload["inventory"], indent=2))
        else:
            for item in payload["inventory"]:
                print(f"{item['coverage_status']:<13} {item['category']:<30} {item['path']}")
        return 0
    if args.report:
        print(_render_report(payload))
        return 0
    return 1  # pragma: no cover - argparse enforces a mode


if __name__ == "__main__":
    raise SystemExit(main())
