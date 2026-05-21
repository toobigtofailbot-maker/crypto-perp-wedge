"""Summarize existing local validation logs for advisory report-back use."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


ADVISORY_NOTE = (
    "This summary is advisory only and does not replace raw logs, command execution, "
    "direct changed-file inspection, integrity views, registry validators, scoped pytest, "
    "full pytest, or semantic review."
)
UNIMPLEMENTED_WRAPPER_MESSAGE = (
    "not implemented in WP-S2c-29f; command-running wrappers require a later authorized package"
)
REQUIRED_JSON_KEYS = [
    "commands",
    "overall_status",
    "query_views",
    "integrity_views",
    "registry_validators",
    "pytest",
    "diff_scope",
    "failures",
    "timeouts",
    "warnings",
    "raw_log_paths",
    "advisory_note",
]

COMMAND_RE = re.compile(r"^\s*(?:\$|>)\s+(.+?)\s*$|^\s*COMMAND:\s*(.+?)\s*$|^\s*Command:\s*(.+?)\s*$")
EXIT_RE = re.compile(r"\b(?:exit code|Exit code):\s*(-?\d+)\b|\breturncode=(-?\d+)\b")
PYTEST_RE = re.compile(r"\b(\d+)\s+(passed|failed|errors?|deselected|warnings?)\b", re.IGNORECASE)
INTEGRITY_CLEAN_RE = re.compile(r"\b(v_integrity_[A-Za-z0-9_]+)\s*:\s*clean\s*\((\d+)\)", re.IGNORECASE)
VIEW_RE = re.compile(r"\b(v_[A-Za-z0-9_]+)\b")
VALIDATOR_RE = re.compile(r"\b(validate_[A-Za-z0-9_]+\.py)\b")
REGISTRY_PASSED_RE = re.compile(
    r"\bRegistry validators:\s*(\d+)\s+passed\b|\ball\s+(\d+)\s+tools/registry/validate_\*\.py\s+modules\s+passed\b",
    re.IGNORECASE,
)


@dataclass
class LogSource:
    path: Path
    label: str | None = None


@dataclass
class ParseState:
    commands: list[dict[str, str]] = field(default_factory=list)
    query_views: list[dict[str, Any]] = field(default_factory=list)
    integrity_views: list[dict[str, Any]] = field(default_factory=list)
    registry_validators: list[dict[str, Any]] = field(default_factory=list)
    pytest: dict[str, int] = field(
        default_factory=lambda: {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "deselected": 0,
            "warnings": 0,
        }
    )
    diff_scope: dict[str, Any] = field(
        default_factory=lambda: {
            "forbidden_matches": [],
            "allowed_file_violations": [],
        }
    )
    failures: list[dict[str, str]] = field(default_factory=list)
    timeouts: list[dict[str, str]] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)
    raw_log_paths: list[str] = field(default_factory=list)
    positive_markers: int = 0


def _line_entry(source: LogSource, line_number: int, text: str) -> dict[str, str]:
    entry = {
        "path": str(source.path),
        "line": str(line_number),
        "text": text.rstrip(),
    }
    if source.label:
        entry["label"] = source.label
    return entry


def _add_unique(items: list[dict[str, Any]], item: dict[str, Any], key: str) -> None:
    if not any(existing.get(key) == item.get(key) for existing in items):
        items.append(item)


def _is_zero_count_pytest_line(line: str) -> bool:
    matches = PYTEST_RE.findall(line)
    if not matches:
        return False
    return all(int(count) == 0 for count, _kind in matches)


def _is_clean_scope_line(lower: str) -> bool:
    if "forbidden" not in lower and "violation" not in lower:
        return False
    clean_tokens = ["none", "0 forbidden", "forbidden matches: 0", "allowed-file violations: 0"]
    return any(token in lower for token in clean_tokens)


def _is_scope_heading(lower: str) -> bool:
    stripped = lower.strip()
    return stripped.startswith("## forbidden") or stripped.startswith("## allowed-file")


def _record_pytest_counts(state: ParseState, source: LogSource, line_number: int, line: str) -> None:
    lower = line.lower()
    if "registry validators" in lower or "tools/registry/" in lower:
        return
    for count_text, raw_kind in PYTEST_RE.findall(line):
        count = int(count_text)
        kind = raw_kind.lower()
        if kind == "error":
            kind = "errors"
        elif kind == "warning":
            kind = "warnings"
        state.pytest[kind] = state.pytest.get(kind, 0) + count
        if count > 0:
            if kind in {"passed", "deselected", "warnings"}:
                state.positive_markers += 1
            if kind == "warnings":
                state.warnings.append(_line_entry(source, line_number, line))
            if kind in {"failed", "errors"}:
                state.failures.append(_line_entry(source, line_number, line))


def _record_registry(state: ParseState, source: LogSource, line_number: int, line: str) -> None:
    registry_match = REGISTRY_PASSED_RE.search(line)
    if registry_match:
        count = int(next(group for group in registry_match.groups() if group is not None))
        state.registry_validators.append(
            {
                "status": "passed",
                "count": count,
                "path": str(source.path),
                "line": line_number,
                "text": line.rstrip(),
            }
        )
        state.positive_markers += 1

    for validator in VALIDATOR_RE.findall(line):
        status = "failed" if _has_failure_marker(line) else "mentioned"
        _add_unique(
            state.registry_validators,
            {
                "name": validator,
                "status": status,
                "path": str(source.path),
                "line": line_number,
                "text": line.rstrip(),
            },
            "name",
        )


def _record_integrity(state: ParseState, source: LogSource, line_number: int, line: str) -> None:
    clean_match = INTEGRITY_CLEAN_RE.search(line)
    if clean_match:
        state.integrity_views.append(
            {
                "name": clean_match.group(1),
                "status": "clean",
                "rows": int(clean_match.group(2)),
                "path": str(source.path),
                "line": line_number,
            }
        )
        state.positive_markers += 1
        return

    lower = line.lower()
    for view in VIEW_RE.findall(line):
        if view.startswith("v_integrity_"):
            if any(token in lower for token in ["failed", "rows", "returned", "nonempty", "[{", "{"]):
                state.integrity_views.append(
                    {
                        "name": view,
                        "status": "rows_or_failure",
                        "path": str(source.path),
                        "line": line_number,
                        "text": line.rstrip(),
                    }
                )
                state.failures.append(_line_entry(source, line_number, line))
            else:
                _add_unique(
                    state.integrity_views,
                    {
                        "name": view,
                        "status": "mentioned",
                        "path": str(source.path),
                        "line": line_number,
                    },
                    "name",
                )
        else:
            _add_unique(
                state.query_views,
                {
                    "name": view,
                    "path": str(source.path),
                    "line": line_number,
                },
                "name",
            )


def _has_failure_marker(line: str) -> bool:
    lower = line.lower()
    if _is_zero_count_pytest_line(line) or _is_clean_scope_line(lower) or _is_scope_heading(lower):
        return False
    pytest_counts = PYTEST_RE.findall(line)
    if pytest_counts:
        failing_counts = [
            int(count)
            for count, raw_kind in pytest_counts
            if raw_kind.lower() in {"failed", "error", "errors"}
        ]
        if failing_counts and all(count == 0 for count in failing_counts):
            lower = re.sub(r"\b\d+\s+(?:failed|errors?)\b", "", lower)
    markers = [
        "failed",
        "error",
        "traceback",
        "assertionerror",
        "nonzero",
        "returned rows",
        "forbidden",
        "violation",
    ]
    return any(marker in lower for marker in markers)


def _record_diff_scope(state: ParseState, source: LogSource, line_number: int, line: str) -> None:
    lower = line.lower()
    if "forbidden matches" in lower or "forbidden-path matches" in lower:
        if _is_clean_scope_line(lower):
            state.positive_markers += 1
        elif not _is_scope_heading(lower):
            entry = _line_entry(source, line_number, line)
            state.diff_scope["forbidden_matches"].append(entry)
            state.failures.append(entry)
    if "allowed-file violations" in lower or "allowed-file check" in lower:
        if _is_clean_scope_line(lower):
            state.positive_markers += 1
        elif not _is_scope_heading(lower):
            entry = _line_entry(source, line_number, line)
            state.diff_scope["allowed_file_violations"].append(entry)
            state.failures.append(entry)


def parse_logs(sources: Sequence[LogSource]) -> dict[str, Any]:
    state = ParseState(raw_log_paths=[str(source.path) for source in sources])

    for source in sources:
        try:
            lines = source.path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            state.failures.append({"path": str(source.path), "line": "", "text": f"ERROR: {exc}"})
            continue

        for line_number, line in enumerate(lines, start=1):
            stripped = line.rstrip()
            lower = stripped.lower()

            command_match = COMMAND_RE.match(stripped)
            if command_match:
                command = next(group for group in command_match.groups() if group is not None)
                state.commands.append({**_line_entry(source, line_number, stripped), "command": command})

            for exit_match in EXIT_RE.findall(stripped):
                exit_code = int(next(group for group in exit_match if group))
                if exit_code == 0:
                    state.positive_markers += 1
                else:
                    state.failures.append({**_line_entry(source, line_number, stripped), "exit_code": str(exit_code)})

            if "timed out" in lower or "timeout" in lower:
                state.timeouts.append(_line_entry(source, line_number, stripped))

            _record_pytest_counts(state, source, line_number, stripped)
            _record_registry(state, source, line_number, stripped)
            _record_integrity(state, source, line_number, stripped)
            _record_diff_scope(state, source, line_number, stripped)

            if "warning" in lower and not PYTEST_RE.search(stripped):
                state.warnings.append(_line_entry(source, line_number, stripped))
            if _has_failure_marker(stripped):
                state.failures.append(_line_entry(source, line_number, stripped))

    seen_failures: set[tuple[str, str, str]] = set()
    unique_failures = []
    for item in state.failures:
        key = (item.get("path", ""), item.get("line", ""), item.get("text", ""))
        if key in seen_failures:
            continue
        seen_failures.add(key)
        unique_failures.append(item)
    state.failures = sorted(
        unique_failures,
        key=lambda item: (item.get("path", ""), int(item.get("line") or 0), item.get("text", "")),
    )

    if state.failures or state.timeouts:
        overall_status = "fail"
    elif state.positive_markers > 0:
        overall_status = "pass"
    else:
        overall_status = "unknown"

    return {
        "commands": state.commands,
        "overall_status": overall_status,
        "query_views": state.query_views,
        "integrity_views": state.integrity_views,
        "registry_validators": state.registry_validators,
        "pytest": state.pytest,
        "diff_scope": state.diff_scope,
        "failures": state.failures,
        "timeouts": state.timeouts,
        "warnings": state.warnings,
        "raw_log_paths": state.raw_log_paths,
        "advisory_note": ADVISORY_NOTE,
    }


def _format_entries(entries: Sequence[dict[str, Any]]) -> str:
    if not entries:
        return "- none"
    lines = []
    for entry in entries:
        location = entry.get("path", "")
        line = entry.get("line", "")
        text = entry.get("text", "")
        suffix = f": {text}" if text else ""
        lines.append(f"- `{location}` line {line}{suffix}")
    return "\n".join(lines)


def _format_commands(commands: Sequence[dict[str, str]]) -> str:
    if not commands:
        return "- none"
    return "\n".join(f"- `{entry['command']}` (`{entry['path']}` line {entry['line']})" for entry in commands)


def format_markdown(summary: dict[str, Any]) -> str:
    pytest = summary["pytest"]
    registry = summary["registry_validators"]
    registry_text = "- none" if not registry else "\n".join(f"- {item}" for item in registry)
    integrity_text = (
        "- none"
        if not summary["integrity_views"]
        else "\n".join(f"- {item}" for item in summary["integrity_views"])
    )
    query_text = "- none" if not summary["query_views"] else "\n".join(f"- {item}" for item in summary["query_views"])
    diff_scope = summary["diff_scope"]

    return "\n".join(
        [
            "# Validation Summary",
            "",
            "## Source logs",
            "\n".join(f"- `{path}`" for path in summary["raw_log_paths"]) or "- none",
            "",
            "## Overall status",
            f"- `{summary['overall_status']}`",
            "",
            "## Commands detected",
            _format_commands(summary["commands"]),
            "",
            "## Query / integrity summary",
            "- query views:",
            query_text,
            "- integrity views:",
            integrity_text,
            "",
            "## Registry summary",
            registry_text,
            "",
            "## Pytest summary",
            f"- passed: {pytest.get('passed', 0)}",
            f"- failed: {pytest.get('failed', 0)}",
            f"- errors: {pytest.get('errors', 0)}",
            f"- deselected: {pytest.get('deselected', 0)}",
            f"- warnings: {pytest.get('warnings', 0)}",
            "",
            "## Diff / scope summary",
            f"- forbidden matches: {len(diff_scope.get('forbidden_matches', []))}",
            f"- allowed-file violations: {len(diff_scope.get('allowed_file_violations', []))}",
            "",
            "## Failures and timeouts",
            "- failures:",
            _format_entries(summary["failures"]),
            "- timeouts:",
            _format_entries(summary["timeouts"]),
            "- warnings:",
            _format_entries(summary["warnings"]),
            "",
            "## Raw log paths",
            "\n".join(f"- `{path}`" for path in summary["raw_log_paths"]) or "- none",
            "",
            "## Advisory note",
            ADVISORY_NOTE,
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-log", action="append", type=Path, default=[], help="Existing local log file to summarize")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit nonzero when detected status is fail")
    parser.add_argument("--repo-root", type=Path, help="Optional repo root override for resolving relative log paths")
    parser.add_argument("--label", help="Optional label for the log source")
    parser.add_argument("--run-docs-standard", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--run-artifact-standard", action="store_true", help=argparse.SUPPRESS)
    return parser


def _resolve_sources(args: argparse.Namespace) -> list[LogSource]:
    root = args.repo_root.resolve() if args.repo_root else Path.cwd().resolve()
    sources = []
    for raw_path in args.from_log:
        path = raw_path if raw_path.is_absolute() else root / raw_path
        sources.append(LogSource(path=path.resolve(), label=args.label))
    return sources


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.run_docs_standard or args.run_artifact_standard:
        parser.error(UNIMPLEMENTED_WRAPPER_MESSAGE)
    if not args.from_log:
        parser.error("--from-log is required")

    summary = parse_logs(_resolve_sources(args))
    public_summary = {key: summary[key] for key in REQUIRED_JSON_KEYS}

    if args.json:
        print(json.dumps(public_summary, indent=2, sort_keys=True))
    else:
        print(format_markdown(public_summary))

    if args.fail_on_error and summary["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
