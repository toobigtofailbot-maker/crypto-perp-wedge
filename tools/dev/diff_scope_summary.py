"""Summarize local git diff scope for advisory PR review evidence."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


TRIAL_LOG_PATH = "research/trial_log.jsonl"
DEFAULT_FORBIDDEN_PREFIXES = [
    "research/",
    "lib/",
    "src/",
    "scripts/",
    "configs/",
    "data/",
    ".claude/",
    "pyproject.toml",
    "requirements",
]
REQUIRED_JSON_KEYS = [
    "tracked_changed_files",
    "staged_changed_files",
    "untracked_files",
    "numstat",
    "forbidden_matches",
    "authorized_canonical_result_population_writes",
    "authorized_path_writes",
    "allowed_file_violations",
    "trial_log",
    "exit_reason",
]
CANONICAL_RESULT_POPULATION_RE = re.compile(
    r"^research/result_populations/RP-\d+\.result_population\.json$"
)
STRATEGY_SPEC_RE = re.compile(r"^research/strategy_specs/STRAT-SPEC-\d+\.strategy_spec\.json$")
RESEARCH_PIPELINE_DOC_RE = re.compile(r"^docs/research_pipeline/[^/]+\.md$")
STATUS_ENTRY_RE = re.compile(r"^docs/status_entries/WP-[^/]+\.md$")


@dataclass(frozen=True)
class GitResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def failed(self) -> bool:
        return self.returncode != 0


class RepoError(RuntimeError):
    pass


def _normalize_path(value: str | Path) -> str:
    text = str(value).replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text.strip("/")


def _run_git(repo_root: Path, args: Sequence[str]) -> GitResult:
    command = ["git", *args]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return GitResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _repo_root_from_path(path: Path) -> Path:
    result = _run_git(path, ["rev-parse", "--show-toplevel"])
    if result.failed:
        message = result.stderr.strip() or result.stdout.strip() or "not inside a git repository"
        raise RepoError(message)
    return Path(result.stdout.strip()).resolve()


def resolve_repo_root(repo_root: Path | None) -> Path:
    candidate = repo_root.resolve() if repo_root is not None else Path.cwd().resolve()
    if not candidate.exists():
        raise RepoError(f"repo root does not exist: {candidate}")
    return _repo_root_from_path(candidate)


def _split_lines(result: GitResult) -> list[str]:
    if result.failed:
        return []
    return [_normalize_path(line) for line in result.stdout.splitlines() if line.strip()]


def _parse_numstat(result: GitResult) -> list[dict[str, str]]:
    if result.failed:
        return []
    entries: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3:
            entries.append({"added": "", "deleted": "", "path": "", "raw": line})
            continue
        added, deleted, path = parts
        entries.append(
            {
                "added": added,
                "deleted": deleted,
                "path": _normalize_path(path),
                "raw": line,
            }
        )
    return entries


def _path_matches_prefix(path: str, prefix: str) -> bool:
    normalized_path = _normalize_path(path)
    normalized_prefix = _normalize_path(prefix)
    if prefix.endswith("/") or normalized_prefix.endswith("/"):
        return normalized_path.startswith(normalized_prefix.rstrip("/") + "/")
    return normalized_path == normalized_prefix or normalized_path.startswith(normalized_prefix)


def _unique_paths(*path_groups: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for group in path_groups:
        for path in group:
            normalized = _normalize_path(path)
            if normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)
    return ordered


def _git_failures(results: Sequence[GitResult]) -> list[dict[str, Any]]:
    failures = []
    for result in results:
        if result.failed:
            failures.append(
                {
                    "command": " ".join(result.command),
                    "returncode": result.returncode,
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                }
            )
    return failures


def _path_exists_in_head(repo_root: Path, path: str) -> bool:
    result = _run_git(repo_root, ["cat-file", "-e", f"HEAD:{path}"])
    return result.returncode == 0


def _authorized_canonical_result_population_paths(
    repo_root: Path,
    changed_files: Sequence[str],
    authorized_paths: Sequence[str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    changed_set = {_normalize_path(path) for path in changed_files}
    authorized: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []

    for raw_path in authorized_paths:
        path = _normalize_path(raw_path)
        if path not in changed_set:
            rejected.append({"path": path, "reason": "path not changed"})
            continue
        if not CANONICAL_RESULT_POPULATION_RE.match(path):
            rejected.append({"path": path, "reason": "path does not match canonical result-population pattern"})
            continue
        if _path_exists_in_head(repo_root, path):
            rejected.append({"path": path, "reason": "path exists in HEAD; existing RP mutation is not authorized"})
            continue
        authorized.append(
            {
                "path": path,
                "status": "authorized",
                "scope": "new canonical result-population write",
            }
        )

    return authorized, rejected


def _authorized_path_scope_rejection(path: str, scope: str) -> str | None:
    normalized_scope = scope.strip().lower()
    if not normalized_scope:
        return "authorized scope is empty"

    if normalized_scope in {
        "strategy-spec-schema",
        "schema",
        "research-schema",
        "schema-validator",
    }:
        if path.startswith("research/schemas/") and path.endswith(".schema.json"):
            return None
        return "scope requires an exact research/schemas/*.schema.json path"

    if normalized_scope in {
        "strategy-spec",
        "strategy-spec-prereg",
        "strategy-spec-preregistration",
        "strategy-spec-artifact",
    }:
        if STRATEGY_SPEC_RE.match(path):
            return None
        return "strategy-spec scope is limited to research/strategy_specs/STRAT-SPEC-<digits>.strategy_spec.json"

    if normalized_scope in {"research-compiler", "strategy-spec-compiler", "compiler"}:
        if path == "tools/research_runner/spec_signal_compiler.py":
            return None
        return "compiler scope is limited to tools/research_runner/spec_signal_compiler.py"

    if normalized_scope in {
        "research-validator",
        "strategy-spec-validator",
        "validator",
        "schema-validator-tooling",
    }:
        if path.startswith("tools/registry/validate_") and path.endswith(".py"):
            return None
        return "validator scope is limited to tools/registry/validate_*.py"

    if normalized_scope in {
        "research-pipeline-prereg",
        "research-pipeline-preregistration",
        "prereg-doc",
    }:
        path_name = Path(path).name.lower()
        if RESEARCH_PIPELINE_DOC_RE.match(path) and ("prereg" in path_name or "pre_registration" in path_name):
            return None
        return "research-pipeline prereg scope is limited to docs/research_pipeline/*prereg*.md paths"

    if normalized_scope in {"research-pipeline-status", "status-entry", "wp-status"}:
        if STATUS_ENTRY_RE.match(path):
            return None
        return "status scope is limited to docs/status_entries/WP-*.md paths"

    return f"unsupported authorized scope: {scope}"


def _authorized_general_paths(
    changed_files: Sequence[str],
    authorized_paths: Sequence[str],
    authorized_scope: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    changed_set = {_normalize_path(path) for path in changed_files}
    authorized: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    scope = authorized_scope or ""

    for raw_path in authorized_paths:
        path = _normalize_path(raw_path)
        if path not in changed_set:
            rejected.append({"path": path, "scope": scope, "reason": "path not changed"})
            continue
        scope_rejection = _authorized_path_scope_rejection(path, scope)
        if scope_rejection:
            rejected.append({"path": path, "scope": scope, "reason": scope_rejection})
            continue
        authorized.append(
            {
                "path": path,
                "status": "authorized",
                "scope": scope,
            }
        )

    return authorized, rejected


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args.repo_root)

    tracked_result = _run_git(repo_root, ["diff", "--name-only"])
    staged_result = _run_git(repo_root, ["diff", "--cached", "--name-only"])
    untracked_result = _run_git(repo_root, ["ls-files", "--others", "--exclude-standard"])
    numstat_result = _run_git(repo_root, ["diff", "--numstat"])
    staged_numstat_result = _run_git(repo_root, ["diff", "--cached", "--numstat"])

    tracked_files = _split_lines(tracked_result)
    staged_files = _split_lines(staged_result)
    untracked_files = _split_lines(untracked_result)
    changed_files = _unique_paths(tracked_files, staged_files, untracked_files)

    forbidden_prefixes = [*DEFAULT_FORBIDDEN_PREFIXES, *args.forbidden_prefix]
    authorized_canonical_writes, rejected_authorized_canonical_writes = (
        _authorized_canonical_result_population_paths(
            repo_root,
            changed_files,
            args.authorized_canonical_result_population_write,
        )
    )
    authorized_canonical_paths = {item["path"] for item in authorized_canonical_writes}
    authorized_general_writes, rejected_authorized_general_writes = _authorized_general_paths(
        changed_files,
        args.authorized_path,
        args.authorized_scope,
    )
    authorized_general_paths = {item["path"] for item in authorized_general_writes}
    authorized_paths = authorized_canonical_paths | authorized_general_paths
    forbidden_matches = [
        {"path": path, "prefix": prefix}
        for path in changed_files
        for prefix in forbidden_prefixes
        if path not in authorized_paths
        if _path_matches_prefix(path, prefix)
    ]

    allowed_files = {_normalize_path(path) for path in args.allowed_file}
    allowed_file_violations = [path for path in changed_files if allowed_files and path not in allowed_files]

    trial_log_touched = TRIAL_LOG_PATH in changed_files
    trial_log_checked = bool(args.trial_log or trial_log_touched)
    trial_log_results: list[GitResult] = []
    if trial_log_checked:
        trial_working_result = _run_git(repo_root, ["diff", "--numstat", "--", TRIAL_LOG_PATH])
        trial_staged_result = _run_git(repo_root, ["diff", "--cached", "--numstat", "--", TRIAL_LOG_PATH])
        trial_log_results.extend([trial_working_result, trial_staged_result])
        trial_working = _parse_numstat(trial_working_result)
        trial_staged = _parse_numstat(trial_staged_result)
    else:
        trial_working = []
        trial_staged = []

    git_results = [
        tracked_result,
        staged_result,
        untracked_result,
        numstat_result,
        staged_numstat_result,
        *trial_log_results,
    ]
    failures = _git_failures(git_results)

    exit_reason = "ok"
    if failures:
        exit_reason = "git command failed"
    elif args.check_forbidden and forbidden_matches:
        exit_reason = "forbidden path match"

    summary = {
        "tracked_changed_files": tracked_files,
        "staged_changed_files": staged_files,
        "untracked_files": untracked_files,
        "numstat": {
            "working_tree": _parse_numstat(numstat_result),
            "staged": _parse_numstat(staged_numstat_result),
            "errors": _git_failures([numstat_result, staged_numstat_result]),
        },
        "forbidden_matches": forbidden_matches,
        "authorized_canonical_result_population_writes": {
            "package": args.authorized_package,
            "authorized": authorized_canonical_writes,
            "rejected": rejected_authorized_canonical_writes,
        },
        "authorized_path_writes": {
            "package": args.authorized_package,
            "scope": args.authorized_scope,
            "authorized": authorized_general_writes,
            "rejected": rejected_authorized_general_writes,
        },
        "allowed_file_violations": allowed_file_violations,
        "trial_log": {
            "path": TRIAL_LOG_PATH,
            "checked": trial_log_checked,
            "touched": trial_log_touched,
            "working_tree": trial_working,
            "staged": trial_staged,
            "errors": _git_failures(trial_log_results),
        },
        "exit_reason": exit_reason,
        "_meta": {
            "repo_root": repo_root.as_posix(),
            "base_ref": args.base_ref,
            "base_ref_note": "accepted for future compatibility; current summary uses working tree and staged git diff state",
            "forbidden_prefixes": forbidden_prefixes,
            "authorized_canonical_result_population_paths": sorted(authorized_canonical_paths),
            "authorized_general_paths": sorted(authorized_general_paths),
            "git_errors": failures,
            "advisory_note": (
                "Advisory only. Does not replace direct changed-file inspection, integrity views, "
                "registry validators, scoped pytest, full pytest, or semantic review."
            ),
        },
    }
    return summary


def _format_path_list(paths: Sequence[str]) -> str:
    if not paths:
        return "- none"
    return "\n".join(f"- `{path}`" for path in paths)


def _format_numstat_entries(entries: Sequence[dict[str, str]]) -> str:
    if not entries:
        return "- none"
    lines = []
    for entry in entries:
        path = entry.get("path") or entry.get("raw", "")
        added = entry.get("added", "")
        deleted = entry.get("deleted", "")
        if path:
            lines.append(f"- `{path}`: +{added} / -{deleted}")
        else:
            lines.append(f"- {entry.get('raw', '')}")
    return "\n".join(lines)


def format_markdown(summary: dict[str, Any]) -> str:
    meta = summary["_meta"]
    forbidden_matches = summary["forbidden_matches"]
    allowed_file_violations = summary["allowed_file_violations"]
    trial_log = summary["trial_log"]
    authorized_canonical = summary["authorized_canonical_result_population_writes"]
    authorized_general = summary["authorized_path_writes"]
    git_errors = meta["git_errors"]

    if forbidden_matches:
        forbidden_text = "\n".join(
            f"- `{match['path']}` matched `{match['prefix']}`" for match in forbidden_matches
        )
    else:
        forbidden_text = "- none"

    authorized_lines = []
    if authorized_canonical["package"]:
        authorized_lines.append(f"- package: `{authorized_canonical['package']}`")
    else:
        authorized_lines.append("- package: not supplied")
    if authorized_canonical["authorized"]:
        authorized_lines.extend(
            f"- authorized: `{item['path']}` ({item['scope']})"
            for item in authorized_canonical["authorized"]
        )
    else:
        authorized_lines.append("- authorized: none")
    if authorized_canonical["rejected"]:
        authorized_lines.extend(
            f"- rejected: `{item['path']}` ({item['reason']})"
            for item in authorized_canonical["rejected"]
        )
    else:
        authorized_lines.append("- rejected: none")
    authorized_text = "\n".join(authorized_lines)

    authorized_general_lines = []
    if authorized_general["package"]:
        authorized_general_lines.append(f"- package: `{authorized_general['package']}`")
    else:
        authorized_general_lines.append("- package: not supplied")
    if authorized_general["scope"]:
        authorized_general_lines.append(f"- scope: `{authorized_general['scope']}`")
    else:
        authorized_general_lines.append("- scope: not supplied")
    if authorized_general["authorized"]:
        authorized_general_lines.extend(
            f"- authorized: `{item['path']}` ({item['scope']})"
            for item in authorized_general["authorized"]
        )
    else:
        authorized_general_lines.append("- authorized: none")
    if authorized_general["rejected"]:
        authorized_general_lines.extend(
            f"- rejected: `{item['path']}` ({item['reason']})"
            for item in authorized_general["rejected"]
        )
    else:
        authorized_general_lines.append("- rejected: none")
    authorized_general_text = "\n".join(authorized_general_lines)

    if trial_log["checked"]:
        trial_log_text = "\n".join(
            [
                f"- touched: `{str(trial_log['touched']).lower()}`",
                "- working tree:",
                _format_numstat_entries(trial_log["working_tree"]),
                "- staged:",
                _format_numstat_entries(trial_log["staged"]),
            ]
        )
    else:
        trial_log_text = "- not checked; pass `--trial-log` or touch `research/trial_log.jsonl` to include numstat"

    if git_errors:
        git_error_text = "\n".join(
            f"- `{error['command']}` exited {error['returncode']}: {error['stderr'] or error['stdout']}"
            for error in git_errors
        )
    else:
        git_error_text = "- none"

    return "\n".join(
        [
            "# Diff / Scope Summary",
            "",
            "## Tracked changed files",
            _format_path_list(summary["tracked_changed_files"]),
            "",
            "## Staged changed files",
            _format_path_list(summary["staged_changed_files"]),
            "",
            "## Untracked files",
            _format_path_list(summary["untracked_files"]),
            "",
            "## Numstat",
            "- working tree:",
            _format_numstat_entries(summary["numstat"]["working_tree"]),
            "- staged:",
            _format_numstat_entries(summary["numstat"]["staged"]),
            "",
            "## Forbidden-path matches",
            forbidden_text,
            "",
            "## Authorized canonical result-population writes",
            authorized_text,
            "",
            "## Authorized path writes",
            authorized_general_text,
            "",
            "## Allowed-file check",
            _format_path_list(allowed_file_violations),
            "",
            "## Trial-log check",
            trial_log_text,
            "",
            "## Notes",
            f"- exit reason: `{summary['exit_reason']}`",
            f"- repo root: `{meta['repo_root']}`",
            f"- base ref: `{meta['base_ref'] or 'not supplied'}`",
            f"- {meta['base_ref_note']}",
            f"- {meta['advisory_note']}",
            "- git command errors:",
            git_error_text,
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    parser.add_argument(
        "--check-forbidden",
        action="store_true",
        help="Exit nonzero when forbidden-path matches are found",
    )
    parser.add_argument("--base-ref", help="Optional future comparison ref; current summary remains local diff state")
    parser.add_argument("--trial-log", action="store_true", help=f"Include {TRIAL_LOG_PATH} numstat")
    parser.add_argument(
        "--forbidden-prefix",
        action="append",
        default=[],
        help="Additional forbidden prefix; may be repeated",
    )
    parser.add_argument(
        "--allowed-file",
        action="append",
        default=[],
        help="Allowed changed file path; may be repeated",
    )
    parser.add_argument(
        "--authorized-canonical-result-population-write",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "Explicitly authorize one new canonical result-population write path "
            "matching research/result_populations/RP-<digits>.result_population.json; may be repeated"
        ),
    )
    parser.add_argument(
        "--authorized-path",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "Explicitly authorize one exact changed path within a bounded authorized scope; "
            "requires --authorized-package plus --authorized-scope and may be repeated"
        ),
    )
    parser.add_argument(
        "--authorized-scope",
        help=(
            "Bounded scope for --authorized-path, for example strategy-spec-schema, "
            "research-compiler, or research-validator"
        ),
    )
    parser.add_argument(
        "--authorized-package",
        help="Explicit package id recorded with authorized-path evidence",
    )
    parser.add_argument("--repo-root", type=Path, help="Optional repo root override")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.authorized_path and not args.authorized_scope:
        parser.error("--authorized-path requires --authorized-scope")
    if args.authorized_scope and not args.authorized_path:
        parser.error("--authorized-scope requires --authorized-path")
    if args.authorized_path and not args.authorized_package:
        parser.error("--authorized-path requires --authorized-package")

    try:
        summary = build_summary(args)
    except RepoError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    public_summary = {key: summary[key] for key in REQUIRED_JSON_KEYS}
    if args.json:
        print(json.dumps(public_summary, indent=2, sort_keys=True))
    else:
        print(format_markdown(summary))

    if summary["_meta"]["git_errors"]:
        return 1
    if args.check_forbidden and summary["forbidden_matches"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
