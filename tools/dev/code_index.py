"""Build a narrow advisory code index for scoped repo inspection."""

from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


SCOPE_PRESETS = {
    "docs-ai": "docs/ai/codex",
    "tools-dev": "tools/dev",
    "tests": "tests",
}
EXCLUDE_PATTERNS = [
    ".git/",
    "data/",
    "configs/",
    ".claude/",
    "__pycache__/",
    ".pytest_cache/",
    ".venv/",
    ".env",
    "*.pyc",
]
ADVISORY_NOTE = (
    "This code index is advisory only and does not replace current repo truth, "
    "docs/project_status.md, active package scope, direct file inspection, "
    "changed-file inspection, validators, integrity views, tests, artifact/query "
    "evidence, or semantic review."
)
PROTECTED_PATH_NOTES = [
    "Supported scopes do not walk runtime/protected implementation paths.",
    "Output is advisory only.",
    (
        "Index output does not authorize touching runtime, paper/live, OMS, risk, "
        "safe-mode, configs, dependencies, schemas, validators, query-layer code, "
        "data, or protected paths."
    ),
    "A future package must explicitly authorize any broader scope.",
]
STALENESS_RULES = [
    "Stale when source_commit differs from current HEAD.",
    "Stale when any indexed file is missing.",
    "Stale when any indexed file sha256 differs from the stored sha256.",
    "Stale when command metadata is missing.",
    "Stale when index_scope metadata is missing.",
    "Unknown when current HEAD cannot be determined.",
]
REQUIRED_JSON_KEYS = [
    "repo_root",
    "source_commit",
    "generated_at_utc",
    "command",
    "index_scope",
    "included_paths",
    "excluded_paths",
    "path_summaries",
    "module_summaries",
    "test_summaries",
    "doc_summaries",
    "protected_path_notes",
    "staleness_rules",
    "advisory_note",
]


class CodeIndexError(RuntimeError):
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
        raise CodeIndexError(f"repo root does not exist: {candidate}")
    code, output = _run_git(candidate, ["rev-parse", "--show-toplevel"])
    if code == 0 and output:
        return Path(output).resolve()
    return candidate


def current_commit(repo_root: Path) -> str:
    code, output = _run_git(repo_root, ["rev-parse", "HEAD"])
    if code != 0 or not output:
        return "unknown"
    return output


def _kind_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix == ".md":
        return "markdown"
    if suffix == ".json":
        return "json"
    if suffix in {".txt", ".rst", ".cfg", ".ini", ".toml", ".yaml", ".yml"}:
        return "text"
    return "other"


def _is_excluded(rel_path: str) -> bool:
    normalized = _normalize_path(rel_path)
    parts = normalized.split("/")
    for pattern in EXCLUDE_PATTERNS:
        if pattern.endswith("/"):
            directory = pattern.strip("/")
            if directory in parts or normalized.startswith(directory + "/"):
                return True
            continue
        if fnmatch.fnmatch(normalized, pattern) or any(fnmatch.fnmatch(part, pattern) for part in parts):
            return True
    return False


def _iter_scope_files(repo_root: Path, scope_names: Sequence[str]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    excluded: list[str] = []
    seen: set[str] = set()

    for scope_name in scope_names:
        scope_path = repo_root / SCOPE_PRESETS[scope_name]
        if not scope_path.exists():
            continue
        for path in sorted(item for item in scope_path.rglob("*") if item.is_file()):
            rel_path = _normalize_path(path.relative_to(repo_root))
            if _is_excluded(rel_path):
                excluded.append(rel_path)
                continue
            if rel_path in seen:
                continue
            seen.add(rel_path)
            files.append(path)
    return files, sorted(set(excluded))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _path_summary(repo_root: Path, path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    return {
        "path": _normalize_path(path.relative_to(repo_root)),
        "kind": _kind_for_path(path),
        "line_count": len(text.splitlines()),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def _import_root(name: str) -> str:
    return name.split(".", 1)[0]


def _module_summary(repo_root: Path, path: Path) -> dict[str, Any]:
    rel_path = _normalize_path(path.relative_to(repo_root))
    summary: dict[str, Any] = {
        "path": rel_path,
        "classes": [],
        "functions": [],
        "imports": [],
        "docstring_first_line": "",
        "parse_warnings": [],
    }
    try:
        tree = ast.parse(_read_text(path), filename=rel_path)
    except SyntaxError as exc:
        summary["parse_warnings"].append(f"{exc.__class__.__name__}: {exc.msg}")
        return summary

    docstring = ast.get_docstring(tree)
    if docstring:
        summary["docstring_first_line"] = docstring.strip().splitlines()[0]

    imports: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            summary["classes"].append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            summary["functions"].append(node.name)
        elif isinstance(node, ast.Import):
            imports.update(_import_root(alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__":
            imports.add(_import_root(node.module))
    summary["imports"] = sorted(imports)
    return summary


def _test_summary(repo_root: Path, path: Path) -> dict[str, Any]:
    rel_path = _normalize_path(path.relative_to(repo_root))
    summary = {"path": rel_path, "test_functions": [], "test_classes": [], "parse_warnings": []}
    try:
        tree = ast.parse(_read_text(path), filename=rel_path)
    except SyntaxError as exc:
        summary["parse_warnings"].append(f"{exc.__class__.__name__}: {exc.msg}")
        return summary

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            summary["test_functions"].append(node.name)
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            summary["test_classes"].append(node.name)
    return summary


def _doc_summary(repo_root: Path, path: Path) -> dict[str, Any]:
    headings = []
    for line in _read_text(path).splitlines():
        stripped = line.lstrip()
        if not stripped.startswith("#"):
            continue
        marker, _, text = stripped.partition(" ")
        if marker and set(marker) == {"#"} and 1 <= len(marker) <= 6 and text.strip():
            headings.append({"level": len(marker), "text": text.strip()})
    return {"path": _normalize_path(path.relative_to(repo_root)), "headings": headings}


def build_index(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args.repo_root)
    scope_names = args.scope or []
    unknown_scopes = sorted(set(scope_names) - set(SCOPE_PRESETS))
    if unknown_scopes:
        raise CodeIndexError(f"unknown scope: {', '.join(unknown_scopes)}")

    files, excluded_files = _iter_scope_files(repo_root, scope_names)
    path_summaries = [_path_summary(repo_root, path) for path in files]
    module_summaries = [_module_summary(repo_root, path) for path in files if path.suffix.lower() == ".py"]
    test_summaries = [
        _test_summary(repo_root, path)
        for path in files
        if path.suffix.lower() == ".py" and _normalize_path(path.relative_to(repo_root)).startswith("tests/")
    ]
    doc_summaries = [_doc_summary(repo_root, path) for path in files if path.suffix.lower() == ".md"]

    included_paths = [SCOPE_PRESETS[scope] for scope in dict.fromkeys(scope_names)]
    excluded_paths = sorted(set(EXCLUDE_PATTERNS + excluded_files))
    commit = current_commit(repo_root)
    staleness_rules = list(STALENESS_RULES)
    if commit == "unknown":
        staleness_rules.append("source_commit is unknown for this index and is a staleness risk.")

    return {
        "repo_root": str(repo_root),
        "source_commit": commit,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "command": " ".join(["code_index.py", *(args.raw_argv or [])]),
        "index_scope": list(dict.fromkeys(scope_names)),
        "included_paths": included_paths,
        "excluded_paths": excluded_paths,
        "path_summaries": path_summaries,
        "module_summaries": module_summaries,
        "test_summaries": test_summaries,
        "doc_summaries": doc_summaries,
        "protected_path_notes": PROTECTED_PATH_NOTES,
        "staleness_rules": staleness_rules,
        "advisory_note": ADVISORY_NOTE,
    }


def _format_path_summaries(items: Sequence[dict[str, Any]]) -> str:
    if not items:
        return "- none"
    return "\n".join(
        f"- `{item['path']}` ({item['kind']}): {item['line_count']} lines, sha256 `{item['sha256']}`"
        for item in items
    )


def _format_module_summaries(items: Sequence[dict[str, Any]]) -> str:
    if not items:
        return "- none"
    lines = []
    for item in items:
        lines.append(f"- `{item['path']}`")
        lines.append(f"  - classes: {', '.join(item['classes']) or 'none'}")
        lines.append(f"  - functions: {', '.join(item['functions']) or 'none'}")
        lines.append(f"  - imports: {', '.join(item['imports']) or 'none'}")
        if item.get("docstring_first_line"):
            lines.append(f"  - docstring: {item['docstring_first_line']}")
        if item.get("parse_warnings"):
            lines.append(f"  - parse warnings: {', '.join(item['parse_warnings'])}")
    return "\n".join(lines)


def _format_test_summaries(items: Sequence[dict[str, Any]]) -> str:
    if not items:
        return "- none"
    lines = []
    for item in items:
        lines.append(f"- `{item['path']}`")
        lines.append(f"  - test functions: {', '.join(item['test_functions']) or 'none'}")
        lines.append(f"  - test classes: {', '.join(item['test_classes']) or 'none'}")
        if item.get("parse_warnings"):
            lines.append(f"  - parse warnings: {', '.join(item['parse_warnings'])}")
    return "\n".join(lines)


def _format_doc_summaries(items: Sequence[dict[str, Any]]) -> str:
    if not items:
        return "- none"
    lines = []
    for item in items:
        lines.append(f"- `{item['path']}`")
        if item["headings"]:
            for heading in item["headings"]:
                lines.append(f"  - H{heading['level']}: {heading['text']}")
        else:
            lines.append("  - headings: none")
    return "\n".join(lines)


def _format_list(items: Sequence[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- `{item}`" for item in items)


def format_markdown(index: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Code Index",
            "",
            "## Advisory note",
            index["advisory_note"],
            "",
            "## Metadata",
            f"- repo_root: `{index['repo_root']}`",
            f"- source_commit: `{index['source_commit']}`",
            f"- generated_at_utc: `{index['generated_at_utc']}`",
            f"- command: `{index['command']}`",
            "",
            "## Scopes",
            "- index_scope:",
            _format_list(index["index_scope"]),
            "- included_paths:",
            _format_list(index["included_paths"]),
            "- excluded_paths:",
            _format_list(index["excluded_paths"]),
            "",
            "## Path summaries",
            _format_path_summaries(index["path_summaries"]),
            "",
            "## Module summaries",
            _format_module_summaries(index["module_summaries"]),
            "",
            "## Test summaries",
            _format_test_summaries(index["test_summaries"]),
            "",
            "## Documentation summaries",
            _format_doc_summaries(index["doc_summaries"]),
            "",
            "## Protected path notes",
            "\n".join(f"- {note}" for note in index["protected_path_notes"]),
            "",
            "## Staleness rules",
            "\n".join(f"- {rule}" for rule in index["staleness_rules"]),
        ]
    )


def _load_json_index(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise CodeIndexError(f"cannot read JSON index: {exc}") from exc
    if not isinstance(payload, dict):
        raise CodeIndexError("JSON index must be an object")
    return payload


def check_stale(index_path: Path, repo_root_override: Path | None = None) -> tuple[str, list[str]]:
    payload = _load_json_index(index_path)
    repo_root = resolve_repo_root(repo_root_override or Path(str(payload.get("repo_root") or Path.cwd())))
    current = current_commit(repo_root)
    if current == "unknown":
        return "unknown", ["current HEAD cannot be determined"]

    reasons: list[str] = []
    if not payload.get("command"):
        reasons.append("command metadata is missing")
    if not payload.get("index_scope"):
        reasons.append("index_scope metadata is missing")
    if payload.get("source_commit") != current:
        reasons.append("source_commit differs from current HEAD")

    for item in payload.get("path_summaries", []):
        rel_path = item.get("path")
        expected_sha = item.get("sha256")
        if not rel_path or not expected_sha:
            reasons.append("path summary is missing path or sha256")
            continue
        path = repo_root / rel_path
        if not path.exists():
            reasons.append(f"indexed file is missing: {rel_path}")
            continue
        actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            reasons.append(f"indexed file sha256 differs: {rel_path}")

    if reasons:
        return "stale", reasons
    return "fresh", ["index metadata and indexed file hashes match current repo state"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", action="append", choices=sorted(SCOPE_PRESETS), help="Scope preset; may be repeated")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    parser.add_argument("--output", type=Path, help="Write output to the explicit path and print a short summary")
    parser.add_argument("--check-stale", type=Path, help="Check a previously generated JSON index for staleness")
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
        except CodeIndexError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print(status)
        for reason in reasons:
            print(f"- {reason}")
        return 0 if status == "fresh" else 1

    if not args.scope:
        parser.error("--scope is required unless --check-stale is used")

    try:
        index = build_index(args)
    except CodeIndexError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    output = json.dumps(index, indent=2, sort_keys=True) if args.json else format_markdown(index)
    if args.output:
        _write_output(args.output, output)
        print(
            "Wrote advisory code index to "
            f"{args.output} ({len(index['path_summaries'])} files, scopes: {', '.join(index['index_scope'])})"
        )
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
