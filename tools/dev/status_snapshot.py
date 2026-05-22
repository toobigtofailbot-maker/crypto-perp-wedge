"""Build a narrow advisory memory/status snapshot for scoped repo context."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


ALLOWED_SCOPES = ("token-efficiency", "active-workflow")
SOURCE_PRESETS = {
    "token-efficiency": [
        "docs/project_status.md",
        "docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md",
        "docs/ai/codex/OPTIONAL_COMMAND_OUTPUT_COMPRESSION.md",
        "docs/ai/codex/CODE_INDEX_DESIGN.md",
        "docs/ai/codex/MEMORY_STATUS_SNAPSHOT_DESIGN.md",
        "docs/ai/codex/VALIDATION_SUMMARY_HELPER_DESIGN.md",
        "docs/ai/codex/COMPACT_WP_TEMPLATE.md",
    ],
    "active-workflow": [
        "docs/project_status.md",
        "docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md",
        "docs/ai/codex/MEMORY_STATUS_SNAPSHOT_DESIGN.md",
    ],
}
HELPER_STATUS_PATHS = {
    "diff/scope summary helper": "tools/dev/diff_scope_summary.py",
    "validation-summary log helper": "tools/dev/validation_summary.py",
    "code-index implementation": "tools/dev/code_index.py",
    "memory/status snapshot implementation": "tools/dev/status_snapshot.py",
    "diff/scope summary helper tests": "tests/test_diff_scope_summary.py",
    "validation-summary log helper tests": "tests/test_validation_summary.py",
    "code-index implementation tests": "tests/test_code_index.py",
    "memory/status snapshot implementation tests": "tests/test_status_snapshot.py",
}
EXCLUDED_SOURCES = [
    "research/",
    "data/",
    "configs/",
    ".claude/",
    "lib/",
    "src/",
    "scripts/",
    "runtime/protected implementation paths",
    "paper/live, OMS, risk, safe-mode, schema, validator, and query-layer paths",
]
ADVISORY_NOTE = (
    "This memory/status snapshot is advisory only and does not replace current repo truth, "
    "docs/project_status.md, active package scope, refreshed-main preflight, branch/PR checks, "
    "direct file inspection, changed-file inspection, direct artifact/count verification, "
    "validators, integrity views, tests, artifact/query evidence, or semantic review."
)
OPEN_PR_SUMMARY = (
    "Live open PR state is not checked by this local-only helper and must be verified separately "
    "through GitHub or the existing review workflow before drafting or executing a WP."
)
PROJECT_STATUS_CONFLICT_NOTE = (
    "not_checked_live: competing docs/project_status.md PRs are not checked by this helper and "
    "must be verified separately before drafting or executing a WP."
)
PROTECTED_BOUNDARY_NOTES = [
    "Supported scopes do not read runtime/protected implementation paths.",
    "Output is advisory only.",
    (
        "Snapshot output does not authorize touching runtime, paper/live, OMS, risk, safe-mode, "
        "configs, dependencies, schemas, validators, query-layer code, data, research artifacts, "
        "or protected paths."
    ),
    "Evidence-runway work must not resume unless explicit user/Karl instruction says so.",
    "Artifact IDs/counts must be directly verified through repo/query surfaces before use.",
]
STALENESS_RULES = [
    "Stale when source_commit differs from current HEAD.",
    "Stale when branch differs from current branch.",
    "Stale when docs/project_status.md changed after generation.",
    "Stale when any included source file is missing.",
    "Stale when any included source file sha256 differs from the stored sha256.",
    "Stale when command metadata is missing.",
    "Stale when snapshot_scope metadata is missing.",
    "Unknown when current HEAD or current branch cannot be determined.",
]
REQUIRED_JSON_KEYS = [
    "repo_root",
    "source_commit",
    "branch",
    "generated_at_utc",
    "command",
    "snapshot_scope",
    "included_sources",
    "excluded_sources",
    "source_summaries",
    "latest_recorded_wp",
    "paused_workflow_state",
    "next_expected_packages",
    "implemented_efficiency_helpers",
    "future_efficiency_items",
    "open_pr_summary",
    "project_status_conflict_state",
    "staleness_rules",
    "protected_boundary_notes",
    "advisory_note",
]


class StatusSnapshotError(RuntimeError):
    pass


def _normalize_path(path: str | Path) -> str:
    text = str(path).replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text.strip("/")


def _run_git(repo_root: Path, args: Sequence[str]) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = completed.stdout.strip() or completed.stderr.strip()
    return completed.returncode, output


def resolve_repo_root(repo_root: Path | None) -> Path:
    candidate = repo_root.resolve() if repo_root else Path.cwd().resolve()
    if not candidate.exists():
        raise StatusSnapshotError(f"repo root does not exist: {candidate}")
    code, output = _run_git(candidate, ["rev-parse", "--show-toplevel"])
    if code == 0 and output:
        return Path(output).resolve()
    return candidate


def current_commit(repo_root: Path) -> str:
    code, output = _run_git(repo_root, ["rev-parse", "HEAD"])
    if code != 0 or not output:
        return "unknown"
    return output


def current_branch(repo_root: Path) -> str:
    code, output = _run_git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    if code != 0 or not output:
        return "unknown"
    return output


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_summary(repo_root: Path, rel_path: str) -> dict[str, Any]:
    path = repo_root / rel_path
    if not path.exists():
        return {"path": rel_path, "exists": False, "sha256": "", "line_count": 0, "hints": []}
    text = _read_text(path)
    hints = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            hints.append(stripped)
        if len(hints) >= 6:
            break
    return {
        "path": rel_path,
        "exists": True,
        "sha256": _sha256(path),
        "line_count": len(text.splitlines()),
        "hints": hints,
    }


def _ordered_unique(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for item in items:
        normalized = " ".join(item.split())
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _sentences(text: str) -> list[str]:
    compact = " ".join(text.split())
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+(?=-? ?[A-Z`])", compact) if part.strip()]


def _project_status_entries(text: str) -> list[str]:
    return re.findall(r"^- (WP-[^/]+ / WP-S2c-[^ ]+ branch-state: .+)$", text, flags=re.MULTILINE)


def latest_recorded_wp(project_status_text: str) -> str:
    entries = _project_status_entries(project_status_text)
    return entries[-1] if entries else "unknown"


def paused_workflow_state(project_status_text: str) -> str:
    entries = _project_status_entries(project_status_text)
    search_text = entries[-1] if entries else project_status_text
    candidates = []
    for sentence in _sentences(search_text):
        lower = sentence.lower()
        if (
            "must stop" in lower
            or "must not auto-draft" in lower
            or "do not resume evidence-runway work" in lower
            or "wp-s2c-30 remains paused" in lower
            or "must discuss" in lower
        ):
            candidates.append(sentence)
    if candidates:
        return candidates[-1]
    return "No compact stop/discussion boundary found; verify docs/project_status.md directly."


def next_expected_packages(project_status_text: str) -> list[str]:
    entries = _project_status_entries(project_status_text)
    search_text = entries[-1] if entries else project_status_text
    candidates = []
    for sentence in _sentences(search_text):
        lower = sentence.lower()
        if "after merge" in lower and ("side may draft" in lower or "likely" in lower or "must discuss" in lower):
            candidates.append(sentence)
    return _ordered_unique(candidates)


def _file_exists(repo_root: Path, rel_path: str) -> bool:
    return (repo_root / rel_path).exists()


def implemented_efficiency_helpers(repo_root: Path, source_text: str) -> list[str]:
    candidates: list[str] = []
    if "COMPACT_WP_TEMPLATE.md" in source_text:
        candidates.append("compact WP template guidance")
    if _file_exists(repo_root, "tools/dev/diff_scope_summary.py") or "diff/scope summary helper" in source_text:
        candidates.append("diff/scope summary helper")
    if "OPTIONAL_COMMAND_OUTPUT_COMPRESSION.md" in source_text:
        candidates.append("optional RTK command-output compression guidance")
    if "VALIDATION_SUMMARY_HELPER_DESIGN.md" in source_text:
        candidates.append("validation-summary design")
    if _file_exists(repo_root, "tools/dev/validation_summary.py") or "validation-summary log helper" in source_text:
        candidates.append("validation-summary log helper")
    if "CODE_INDEX_DESIGN.md" in source_text:
        candidates.append("code-index design")
    if _file_exists(repo_root, "tools/dev/code_index.py") or "code-index implementation" in source_text:
        candidates.append("code-index implementation")
    if "MEMORY_STATUS_SNAPSHOT_DESIGN.md" in source_text:
        candidates.append("memory/status snapshot design")
    if _file_exists(repo_root, "tools/dev/status_snapshot.py"):
        candidates.append("memory/status snapshot implementation")
    return _ordered_unique(candidates)


def future_efficiency_items(source_text: str) -> list[str]:
    candidates = []
    lower = source_text.lower()
    if "rtk/rtx/trs" in lower or "rtk/rtx/trs tooling remains unimplemented" in lower:
        candidates.append("RTK/RTX/TRS tooling")
    if "validation-summary command-running wrapper modes: not implemented" in lower:
        candidates.append("validation command-running wrapper modes")
    if "command-running validation wrappers" in lower:
        candidates.append("command-running validation wrappers")
    if "memory/status snapshot implementation: not implemented" in lower:
        candidates.append("memory/status snapshot implementation")
    return _ordered_unique(candidates)


def _helper_status(repo_root: Path) -> list[dict[str, Any]]:
    return [
        {"name": name, "path": rel_path, "exists": _file_exists(repo_root, rel_path)}
        for name, rel_path in HELPER_STATUS_PATHS.items()
    ]


def _included_sources(scopes: Sequence[str]) -> list[str]:
    paths = []
    for scope in scopes:
        paths.extend(SOURCE_PRESETS[scope])
    return _ordered_unique(paths)


def build_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args.repo_root)
    scope_names = list(dict.fromkeys(args.scope or []))
    unknown_scopes = sorted(set(scope_names) - set(ALLOWED_SCOPES))
    if unknown_scopes:
        raise StatusSnapshotError(f"unknown scope: {', '.join(unknown_scopes)}")

    included_sources = _included_sources(scope_names)
    source_summaries = [_source_summary(repo_root, rel_path) for rel_path in included_sources]
    source_text_by_path = {
        rel_path: _read_text(repo_root / rel_path) if (repo_root / rel_path).exists() else ""
        for rel_path in included_sources
    }
    project_status_text = source_text_by_path.get("docs/project_status.md", "")
    combined_source_text = "\n".join(source_text_by_path.values())
    commit = current_commit(repo_root)
    branch = current_branch(repo_root)
    staleness_rules = list(STALENESS_RULES)
    if commit == "unknown":
        staleness_rules.append("source_commit is unknown for this snapshot and is a staleness risk.")
    if branch == "unknown":
        staleness_rules.append("branch is unknown for this snapshot and is a staleness risk.")

    return {
        "repo_root": str(repo_root),
        "source_commit": commit,
        "branch": branch,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "command": " ".join(["status_snapshot.py", *(args.raw_argv or [])]),
        "snapshot_scope": scope_names,
        "included_sources": included_sources,
        "excluded_sources": EXCLUDED_SOURCES,
        "source_summaries": source_summaries,
        "latest_recorded_wp": latest_recorded_wp(project_status_text),
        "paused_workflow_state": paused_workflow_state(project_status_text),
        "next_expected_packages": next_expected_packages(project_status_text),
        "implemented_efficiency_helpers": implemented_efficiency_helpers(repo_root, combined_source_text),
        "future_efficiency_items": future_efficiency_items(combined_source_text),
        "open_pr_summary": OPEN_PR_SUMMARY,
        "project_status_conflict_state": "not_checked_live",
        "project_status_conflict_note": PROJECT_STATUS_CONFLICT_NOTE,
        "helper_file_status": _helper_status(repo_root),
        "artifact_count_note": "Artifact IDs/counts require direct repo/query verification before use.",
        "staleness_rules": staleness_rules,
        "protected_boundary_notes": PROTECTED_BOUNDARY_NOTES,
        "advisory_note": ADVISORY_NOTE,
    }


def _format_list(items: Sequence[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _format_metadata(snapshot: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"- repo_root: `{snapshot['repo_root']}`",
            f"- source_commit: `{snapshot['source_commit']}`",
            f"- branch: `{snapshot['branch']}`",
            f"- generated_at_utc: `{snapshot['generated_at_utc']}`",
            f"- command: `{snapshot['command']}`",
            "- included_sources:",
            _format_list([f"`{path}`" for path in snapshot["included_sources"]]),
            "- excluded_sources:",
            _format_list(snapshot["excluded_sources"]),
        ]
    )


def _format_source_summaries(items: Sequence[dict[str, Any]]) -> str:
    if not items:
        return "- none"
    lines = []
    for item in items:
        exists = "exists" if item.get("exists") else "missing"
        sha = item.get("sha256") or "none"
        lines.append(f"- `{item['path']}`: {exists}, {item.get('line_count', 0)} lines, sha256 `{sha}`")
    return "\n".join(lines)


def format_markdown(snapshot: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Memory / Status Snapshot",
            "",
            "## Advisory note",
            snapshot["advisory_note"],
            "",
            "## Metadata",
            _format_metadata(snapshot),
            "",
            "## Snapshot scopes",
            _format_list(snapshot["snapshot_scope"]),
            "",
            "## Source summaries",
            _format_source_summaries(snapshot["source_summaries"]),
            "",
            "## Latest recorded WP",
            snapshot["latest_recorded_wp"],
            "",
            "## Paused workflow state",
            snapshot["paused_workflow_state"],
            "",
            "## Next expected packages",
            _format_list(snapshot["next_expected_packages"]),
            "",
            "## Implemented efficiency helpers",
            _format_list(snapshot["implemented_efficiency_helpers"]),
            "",
            "## Future efficiency items",
            _format_list(snapshot["future_efficiency_items"]),
            "",
            "## Open PR summary",
            snapshot["open_pr_summary"],
            "",
            "## Project-status conflict state",
            f"- `{snapshot['project_status_conflict_state']}`",
            f"- {snapshot['project_status_conflict_note']}",
            "",
            "## Protected boundary notes",
            _format_list(snapshot["protected_boundary_notes"]),
            "",
            "## Staleness rules",
            _format_list(snapshot["staleness_rules"]),
        ]
    )


def _load_json_snapshot(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise StatusSnapshotError(f"cannot read JSON snapshot: {exc}") from exc
    if not isinstance(payload, dict):
        raise StatusSnapshotError("JSON snapshot must be an object")
    return payload


def check_stale(snapshot_path: Path, repo_root_override: Path | None = None) -> tuple[str, list[str]]:
    payload = _load_json_snapshot(snapshot_path)
    repo_root = resolve_repo_root(repo_root_override or Path(str(payload.get("repo_root") or Path.cwd())))
    commit = current_commit(repo_root)
    branch = current_branch(repo_root)
    if commit == "unknown" or branch == "unknown":
        return "unknown", ["current HEAD or current branch cannot be determined"]

    reasons: list[str] = []
    if not payload.get("command"):
        reasons.append("command metadata is missing")
    if not payload.get("snapshot_scope"):
        reasons.append("snapshot_scope metadata is missing")
    if payload.get("source_commit") != commit:
        reasons.append("source_commit differs from current HEAD")
    if payload.get("branch") != branch:
        reasons.append("branch differs from current branch")

    summaries = payload.get("source_summaries")
    if not isinstance(summaries, list):
        reasons.append("source_summaries metadata is missing")
        summaries = []

    for item in summaries:
        rel_path = item.get("path") if isinstance(item, dict) else None
        expected_sha = item.get("sha256") if isinstance(item, dict) else None
        if not rel_path or not expected_sha:
            reasons.append("source summary is missing path or sha256")
            continue
        path = repo_root / rel_path
        if not path.exists():
            reasons.append(f"included source file is missing: {rel_path}")
            continue
        actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            if rel_path == "docs/project_status.md":
                reasons.append("docs/project_status.md changed after generation")
            else:
                reasons.append(f"included source file sha256 differs: {rel_path}")

    if reasons:
        return "stale", reasons
    return "fresh", ["snapshot metadata and included source hashes match current repo state"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", action="append", choices=ALLOWED_SCOPES, help="Scope preset; may be repeated")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    parser.add_argument("--output", type=Path, help="Write output to the explicit path and print a short summary")
    parser.add_argument("--check-stale", type=Path, help="Check a previously generated JSON snapshot for staleness")
    parser.add_argument("--repo-root", type=Path, help="Optional repo root override for tests")
    return parser


def _write_output(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(argv: Sequence[str] | None = None) -> int:
    raw_argv = list(argv if argv is not None else sys.argv[1:])
    parser = build_parser()
    args = parser.parse_args(raw_argv)
    args.raw_argv = raw_argv

    if args.check_stale:
        try:
            status, reasons = check_stale(args.check_stale, args.repo_root)
        except StatusSnapshotError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print(status)
        for reason in reasons:
            print(f"- {reason}")
        return 0 if status == "fresh" else 1

    if not args.scope:
        parser.error("--scope is required unless --check-stale is used")

    try:
        snapshot = build_snapshot(args)
    except StatusSnapshotError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    public_snapshot = {key: snapshot[key] for key in REQUIRED_JSON_KEYS}
    output = json.dumps(public_snapshot, indent=2, sort_keys=True) if args.json else format_markdown(snapshot)
    if args.output:
        _write_output(args.output, output)
        print(
            "Wrote advisory memory/status snapshot to "
            f"{args.output} (scopes: {', '.join(snapshot['snapshot_scope'])})"
        )
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
