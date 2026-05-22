import ast
import json
import subprocess
from pathlib import Path

import pytest

from tools.dev import status_snapshot as helper


REQUIRED_KEYS = {
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
}


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@example.com")
    _write(
        repo / "docs" / "project_status.md",
        "\n".join(
            [
                "# Project Status",
                "",
                "- WP-12cc / WP-S2c-35 branch-state: code-index implementation is complete. After merge, Side may draft the next efficiency/tooling package from refreshed `main`, likely memory/status snapshot implementation, subject to no stop trigger and no competing `docs/project_status.md` PR. Do not resume evidence-runway work without explicit user/Karl instruction.",
            ]
        ),
    )
    _write(
        repo / "docs" / "ai" / "codex" / "CODEX_TOKEN_EFFICIENCY.md",
        "\n".join(
            [
                "# Codex Token Efficiency",
                "",
                "Compact WP template guidance is now implemented as guidance at `docs/ai/codex/COMPACT_WP_TEMPLATE.md`.",
                "The local diff/scope summary helper is now implemented as a repo-local advisory helper at `tools/dev/diff_scope_summary.py`.",
                "Optional RTK command-output compression guidance is now implemented as guidance only at `docs/ai/codex/OPTIONAL_COMMAND_OUTPUT_COMPRESSION.md`.",
                "Validation-summary helper or wrapper design is implemented design only in `docs/ai/codex/VALIDATION_SUMMARY_HELPER_DESIGN.md`.",
                "Validation-summary log helper is implemented repo-local advisory helper only at `tools/dev/validation_summary.py`.",
                "Code-index design is implemented design only in `docs/ai/codex/CODE_INDEX_DESIGN.md`.",
                "Code-index implementation is implemented repo-local advisory helper only at `tools/dev/code_index.py`.",
                "Memory/status snapshot design is implemented design only in `docs/ai/codex/MEMORY_STATUS_SNAPSHOT_DESIGN.md`.",
                "Memory/status snapshot implementation: not implemented.",
                "Validation-summary command-running wrapper modes: not implemented.",
                "Actual RTK/RTX/TRS tooling remains unimplemented.",
            ]
        ),
    )
    _write(repo / "docs" / "ai" / "codex" / "OPTIONAL_COMMAND_OUTPUT_COMPRESSION.md", "# Optional\n")
    _write(repo / "docs" / "ai" / "codex" / "CODE_INDEX_DESIGN.md", "# Code Index Design\n")
    _write(repo / "docs" / "ai" / "codex" / "MEMORY_STATUS_SNAPSHOT_DESIGN.md", "# Memory Design\n")
    _write(repo / "docs" / "ai" / "codex" / "VALIDATION_SUMMARY_HELPER_DESIGN.md", "# Validation Design\n")
    _write(repo / "docs" / "ai" / "codex" / "COMPACT_WP_TEMPLATE.md", "# Compact WP\n")
    _write(repo / "tools" / "dev" / "diff_scope_summary.py", "# helper\n")
    _write(repo / "tools" / "dev" / "validation_summary.py", "# helper\n")
    _write(repo / "tools" / "dev" / "code_index.py", "# helper\n")
    _write(repo / "tools" / "dev" / "status_snapshot.py", "# helper\n")
    _write(repo / "tests" / "test_diff_scope_summary.py", "# tests\n")
    _write(repo / "tests" / "test_validation_summary.py", "# tests\n")
    _write(repo / "tests" / "test_code_index.py", "# tests\n")
    _write(repo / "tests" / "test_status_snapshot.py", "# tests\n")
    _write(repo / "research" / "secret.md", "DO NOT READ RESEARCH SECRET\n")
    _write(repo / "data" / "secret.txt", "DO NOT READ DATA SECRET\n")
    _write(repo / "configs" / "secret.json", "DO NOT READ CONFIG SECRET\n")
    _write(repo / ".claude" / "secret.md", "DO NOT READ CLAUDE SECRET\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")
    return repo


def _run(args: list[str], capsys) -> tuple[int, str, str]:
    exit_code = helper.run(args)
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_markdown_output_for_token_efficiency_scope_from_temp_repo(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, stderr = _run(["--repo-root", str(repo), "--scope", "token-efficiency"], capsys)

    assert exit_code == 0
    assert stderr == ""
    assert "# Memory / Status Snapshot" in stdout
    assert "## Advisory note" in stdout
    assert "## Implemented efficiency helpers" in stdout
    assert "token-efficiency" in stdout


def test_json_output_includes_required_keys(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "active-workflow", "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert set(payload) == REQUIRED_KEYS


def test_scope_presets_are_enforced(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--scope",
            "token-efficiency",
            "--scope",
            "active-workflow",
            "--json",
        ],
        capsys,
    )

    assert exit_code == 0
    assert json.loads(stdout)["snapshot_scope"] == ["token-efficiency", "active-workflow"]


def test_unknown_scope_exits_nonzero(tmp_path, capsys):
    repo = _repo(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        helper.run(["--repo-root", str(repo), "--scope", "src"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert "invalid choice" in captured.err


def test_latest_recorded_wp_is_extracted(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "active-workflow", "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["latest_recorded_wp"].startswith("WP-12cc / WP-S2c-35 branch-state")


def test_stop_discussion_boundary_is_captured(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "active-workflow", "--json"], capsys)

    assert exit_code == 0
    assert "Do not resume evidence-runway work" in json.loads(stdout)["paused_workflow_state"]


def test_next_expected_package_hints_are_captured(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "active-workflow", "--json"], capsys)

    assert exit_code == 0
    hints = json.loads(stdout)["next_expected_packages"]
    assert any("memory/status snapshot implementation" in hint for hint in hints)


def test_implemented_efficiency_helper_list_is_grounded(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "token-efficiency", "--json"], capsys)

    assert exit_code == 0
    helpers = json.loads(stdout)["implemented_efficiency_helpers"]
    assert "compact WP template guidance" in helpers
    assert "diff/scope summary helper" in helpers
    assert "optional RTK command-output compression guidance" in helpers
    assert "validation-summary design" in helpers
    assert "validation-summary log helper" in helpers
    assert "code-index design" in helpers
    assert "code-index implementation" in helpers
    assert "memory/status snapshot design" in helpers
    assert "memory/status snapshot implementation" in helpers


def test_future_efficiency_items_include_unimplemented_docs_items(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "token-efficiency", "--json"], capsys)

    assert exit_code == 0
    items = json.loads(stdout)["future_efficiency_items"]
    assert "RTK/RTX/TRS tooling" in items
    assert "validation command-running wrapper modes" in items


def test_open_pr_summary_and_project_status_conflict_state(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "active-workflow", "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert "Live open PR state is not checked" in payload["open_pr_summary"]
    assert payload["project_status_conflict_state"] == "not_checked_live"


def test_advisory_note_and_protected_boundary_notes_are_present(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "active-workflow", "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["advisory_note"] == helper.ADVISORY_NOTE
    assert any("runtime/protected" in note for note in payload["protected_boundary_notes"])


def test_snapshot_does_not_read_or_summarize_protected_paths(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "token-efficiency", "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    serialized = json.dumps(payload)
    assert "DO NOT READ RESEARCH SECRET" not in serialized
    assert "DO NOT READ DATA SECRET" not in serialized
    assert "DO NOT READ CONFIG SECRET" not in serialized
    assert "DO NOT READ CLAUDE SECRET" not in serialized
    included = set(payload["included_sources"])
    assert not any(path.startswith(("research/", "data/", "configs/", ".claude/")) for path in included)


def test_output_writes_only_explicit_temp_output_path(tmp_path, capsys):
    repo = _repo(tmp_path)
    output = tmp_path / "out" / "snapshot.json"
    before_status = _git(repo, "status", "--short").stdout

    exit_code, stdout, _ = _run(
        ["--repo-root", str(repo), "--scope", "token-efficiency", "--json", "--output", str(output)],
        capsys,
    )

    assert exit_code == 0
    assert output.exists()
    assert "Wrote advisory memory/status snapshot" in stdout
    assert _git(repo, "status", "--short").stdout == before_status
    assert not (repo / "status_snapshot.json").exists()


def test_check_stale_returns_fresh_for_unchanged_generated_json(tmp_path, capsys):
    repo = _repo(tmp_path)
    output = tmp_path / "snapshot.json"
    _run(["--repo-root", str(repo), "--scope", "active-workflow", "--json", "--output", str(output)], capsys)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--check-stale", str(output)], capsys)

    assert exit_code == 0
    assert stdout.splitlines()[0] == "fresh"


def test_check_stale_returns_stale_when_project_status_changes(tmp_path, capsys):
    repo = _repo(tmp_path)
    output = tmp_path / "snapshot.json"
    _run(["--repo-root", str(repo), "--scope", "active-workflow", "--json", "--output", str(output)], capsys)
    _write(repo / "docs" / "project_status.md", "# Project Status\n\nchanged\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--check-stale", str(output)], capsys)

    assert exit_code == 1
    assert stdout.splitlines()[0] == "stale"
    assert "docs/project_status.md changed after generation" in stdout


def test_check_stale_returns_stale_when_included_source_file_changes(tmp_path, capsys):
    repo = _repo(tmp_path)
    output = tmp_path / "snapshot.json"
    _run(["--repo-root", str(repo), "--scope", "token-efficiency", "--json", "--output", str(output)], capsys)
    _write(repo / "docs" / "ai" / "codex" / "CODE_INDEX_DESIGN.md", "# Changed\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--check-stale", str(output)], capsys)

    assert exit_code == 1
    assert stdout.splitlines()[0] == "stale"
    assert "included source file sha256 differs" in stdout


def test_check_stale_returns_stale_when_included_source_file_is_missing(tmp_path, capsys):
    repo = _repo(tmp_path)
    output = tmp_path / "snapshot.json"
    _run(["--repo-root", str(repo), "--scope", "token-efficiency", "--json", "--output", str(output)], capsys)
    (repo / "docs" / "ai" / "codex" / "CODE_INDEX_DESIGN.md").unlink()

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--check-stale", str(output)], capsys)

    assert exit_code == 1
    assert stdout.splitlines()[0] == "stale"
    assert "included source file is missing" in stdout


def test_helper_does_not_mutate_snapshotted_input_files(tmp_path, capsys):
    repo = _repo(tmp_path)
    source = repo / "docs" / "project_status.md"
    before_text = source.read_text(encoding="utf-8")
    before_status = _git(repo, "status", "--short").stdout

    exit_code, _, _ = _run(["--repo-root", str(repo), "--scope", "active-workflow"], capsys)

    assert exit_code == 0
    assert source.read_text(encoding="utf-8") == before_text
    assert _git(repo, "status", "--short").stdout == before_status


def test_helper_uses_only_standard_library_imports():
    source = Path(helper.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.module.startswith("__future__"):
            imports.add(node.module.split(".", 1)[0])

    assert imports <= {
        "argparse",
        "datetime",
        "hashlib",
        "json",
        "pathlib",
        "re",
        "subprocess",
        "sys",
        "typing",
    }


def test_helper_does_not_include_network_or_external_service_calls():
    source = Path(helper.__file__).read_text(encoding="utf-8")

    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "http.client" not in source
