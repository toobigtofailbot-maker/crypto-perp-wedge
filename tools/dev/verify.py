"""Run the repo-local standard verification suite transparently."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


ADVISORY_NOTE = (
    "This helper is advisory orchestration only. It preserves raw command strings, "
    "exit codes, timeout status, and material output, but it does not replace direct "
    "command accountability, changed-file inspection, validators, integrity views, "
    "pytest, or semantic review."
)
DEFAULT_TIMEOUT_SECONDS = 300
DEFAULT_INTEGRITY_MAX_WORKERS = 4
REQUIRED_JSON_KEYS = [
    "overall_status",
    "commands",
    "integrity_views",
    "failures",
    "advisory_note",
]


@dataclass(frozen=True)
class CommandSpec:
    argv: list[str]
    required: bool = True
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS


class VerifyError(RuntimeError):
    pass


def _run_git(path: Path, args: Sequence[str]) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=path,
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
        raise VerifyError(f"repo root does not exist: {candidate}")
    code, output = _run_git(candidate, ["rev-parse", "--show-toplevel"])
    if code != 0 or not output:
        raise VerifyError(output or "not inside a git repository")
    return Path(output).resolve()


def _material_output(stdout: str, stderr: str, max_chars: int) -> dict[str, str]:
    stdout_text = stdout.strip()
    stderr_text = stderr.strip()
    return {
        "stdout": stdout_text[:max_chars],
        "stderr": stderr_text[:max_chars],
        "stdout_truncated": str(len(stdout_text) > max_chars).lower(),
        "stderr_truncated": str(len(stderr_text) > max_chars).lower(),
    }


def _command_text(argv: Sequence[str]) -> str:
    return " ".join(argv)


def run_command(repo_root: Path, spec: CommandSpec, max_chars: int) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            spec.argv,
            cwd=repo_root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=spec.timeout_seconds,
        )
        timed_out = False
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
    elapsed_seconds = time.monotonic() - started

    output = _material_output(stdout, stderr, max_chars)
    status = "timeout" if timed_out else ("pass" if returncode == 0 else "fail")
    return {
        "command": _command_text(spec.argv),
        "argv": spec.argv,
        "required": spec.required,
        "status": status,
        "exit_code": returncode,
        "timed_out": timed_out,
        "timeout_seconds": spec.timeout_seconds,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "_stdout_raw": stdout.strip(),
        "_stderr_raw": stderr.strip(),
        **output,
    }


def _python_cmd(args: Sequence[str]) -> list[str]:
    return [sys.executable, *args]


def build_standard_commands(args: argparse.Namespace) -> list[CommandSpec]:
    timeout = args.timeout_seconds
    diff_scope_args = ["tools/dev/diff_scope_summary.py", "--check-forbidden"]
    for path in args.authorized_canonical_result_population_write:
        diff_scope_args.extend(["--authorized-canonical-result-population-write", path])
    if args.authorized_package:
        diff_scope_args.extend(["--authorized-package", args.authorized_package])
    commands = [
        CommandSpec(["git", "diff", "--check"], timeout_seconds=timeout),
        CommandSpec(["git", "diff", "--cached", "--check"], timeout_seconds=timeout),
        CommandSpec(["git", "status", "--short"], timeout_seconds=timeout),
        CommandSpec(["git", "diff", "--name-only"], timeout_seconds=timeout),
        CommandSpec(["git", "diff", "--cached", "--name-only"], timeout_seconds=timeout),
        CommandSpec(_python_cmd(diff_scope_args), timeout_seconds=timeout),
        CommandSpec(_python_cmd(["-m", "tools.registry.validate_result_populations"]), timeout_seconds=timeout),
        CommandSpec(_python_cmd(["-m", "tools.research_query.run", "--list-views"]), timeout_seconds=timeout),
    ]
    for pytest_target in args.pytest:
        commands.append(CommandSpec(_python_cmd(["-m", "pytest", pytest_target, "-q"]), timeout_seconds=timeout))
    if args.full_pytest:
        commands.append(CommandSpec(_python_cmd(["-m", "pytest", "-q"]), timeout_seconds=args.full_pytest_timeout_seconds))
    return commands


def discover_integrity_views(repo_root: Path, timeout_seconds: int, max_chars: int) -> tuple[list[str], dict[str, Any]]:
    result = run_command(
        repo_root,
        CommandSpec(_python_cmd(["-m", "tools.research_query.run", "--list-views"]), timeout_seconds=timeout_seconds),
        max_chars,
    )
    if result["status"] != "pass":
        return [], result
    views = sorted(
        line.strip()
        for line in result["_stdout_raw"].splitlines()
        if line.strip().startswith("v_integrity_")
    )
    return views, result


def _summarize_integrity_view_result(view: str, result: dict[str, Any]) -> dict[str, Any]:
    rows: Any = None
    row_count: int | None = None
    error: str | None = None
    if result["status"] == "pass":
        try:
            rows = json.loads(result["_stdout_raw"] or "[]")
            row_count = len(rows) if isinstance(rows, list) else None
            if not isinstance(rows, list):
                error = "view output was not a JSON array"
        except json.JSONDecodeError as exc:
            result["status"] = "fail"
            error = f"invalid JSON output: {exc}"
    elif result["status"] == "timeout":
        error = f"timed out after {result['timeout_seconds']} seconds"
    else:
        error = result.get("_stderr_raw") or result.get("_stdout_raw") or "command failed"

    clean = result["status"] == "pass" and row_count == 0 and error is None
    return {
        "name": view,
        "status": "clean" if clean else "fail",
        "row_count": row_count,
        "elapsed_seconds": result.get("elapsed_seconds"),
        "error": error,
        "rows": rows if not clean else [],
        "command": result["command"],
    }


def run_integrity_views(
    repo_root: Path,
    timeout_seconds: int,
    max_chars: int,
    max_workers: int = DEFAULT_INTEGRITY_MAX_WORKERS,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    views, discovery = discover_integrity_views(repo_root, timeout_seconds, max_chars)
    command_results = [discovery]
    if discovery["status"] != "pass":
        return [], command_results

    def run_one(view: str) -> tuple[str, dict[str, Any]]:
        result = run_command(
            repo_root,
            CommandSpec(_python_cmd(["-m", "tools.research_query.run", "--view", view, "--json"]), timeout_seconds=timeout_seconds),
            max_chars,
        )
        return view, result

    completed_by_view: dict[str, dict[str, Any]] = {}
    worker_count = min(max_workers, len(views)) if views else 0
    if worker_count:
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(run_one, view) for view in views]
            for future in as_completed(futures):
                view, result = future.result()
                completed_by_view[view] = result

    view_results = []
    for view in sorted(views):
        result = completed_by_view[view]
        command_results.append(result)
        view_results.append(_summarize_integrity_view_result(view, result))
    return view_results, command_results


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args.repo_root)
    command_results = [
        run_command(repo_root, command, args.max_output_chars)
        for command in build_standard_commands(args)
    ]
    integrity_views: list[dict[str, Any]] = []
    if args.integrity_views:
        integrity_views, integrity_commands = run_integrity_views(
            repo_root,
            args.timeout_seconds,
            args.max_output_chars,
            args.integrity_max_workers,
        )
        command_results.extend(integrity_commands)

    failures = [
        result
        for result in command_results
        if result["required"] and result["status"] != "pass"
    ]
    failures.extend(view for view in integrity_views if view["status"] != "clean")
    overall_status = "fail" if failures else "pass"
    return {
        "overall_status": overall_status,
        "commands": command_results,
        "integrity_views": integrity_views,
        "failures": failures,
        "advisory_note": ADVISORY_NOTE,
    }


def _public_item(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _public_item(item) for key, item in value.items() if not key.startswith("_")}
    if isinstance(value, list):
        return [_public_item(item) for item in value]
    return value


def format_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Verification Summary",
        "",
        "## Overall status",
        f"- `{summary['overall_status']}`",
        "",
        "## Commands",
    ]
    for result in summary["commands"]:
        lines.append(
            f"- `{result['command']}`: {result['status']} "
            f"(exit={result['exit_code']}, timeout={str(result['timed_out']).lower()})"
        )
        if result["status"] != "pass":
            if result["stdout"]:
                lines.append(f"  - stdout: {result['stdout']}")
            if result["stderr"]:
                lines.append(f"  - stderr: {result['stderr']}")
    lines.extend(["", "## Integrity views"])
    if summary["integrity_views"]:
        for view in summary["integrity_views"]:
            lines.append(f"- `{view['name']}`: {view['status']} (rows={view['row_count']})")
    else:
        lines.append("- not run; pass `--integrity-views` to execute discovered `v_integrity_*` views")
    lines.extend(["", "## Advisory note", ADVISORY_NOTE])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, help="Optional repo root override")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    parser.add_argument("--integrity-views", action="store_true", help="Run all discovered v_integrity_* views")
    parser.add_argument("--pytest", action="append", default=[], help="Targeted pytest path or nodeid; may be repeated")
    parser.add_argument("--full-pytest", action="store_true", help="Run full pytest explicitly")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--full-pytest-timeout-seconds", type=int, default=1800)
    parser.add_argument("--max-output-chars", type=int, default=4000)
    parser.add_argument(
        "--integrity-max-workers",
        type=int,
        default=DEFAULT_INTEGRITY_MAX_WORKERS,
        help="Maximum parallel workers for discovered v_integrity_* view checks",
    )
    parser.add_argument(
        "--authorized-canonical-result-population-write",
        action="append",
        default=[],
        metavar="PATH",
        help="Pass an explicit new canonical result-population write authorization to diff_scope_summary.py",
    )
    parser.add_argument(
        "--authorized-package",
        help="Optional package id passed to diff_scope_summary.py with canonical write authorization evidence",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0 or args.full_pytest_timeout_seconds <= 0:
        parser.error("timeouts must be positive")
    if args.max_output_chars <= 0:
        parser.error("--max-output-chars must be positive")
    if args.integrity_max_workers <= 0:
        parser.error("--integrity-max-workers must be positive")
    try:
        summary = build_summary(args)
    except VerifyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    public_summary = _public_item({key: summary[key] for key in REQUIRED_JSON_KEYS})
    if args.json:
        print(json.dumps(public_summary, indent=2, sort_keys=True))
    else:
        print(format_markdown(public_summary))
    return 0 if summary["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(run())
