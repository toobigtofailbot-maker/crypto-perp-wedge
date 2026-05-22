import ast
import json
import subprocess
from pathlib import Path

import pytest

from tools.dev import code_index as helper


REQUIRED_KEYS = {
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
        repo / "docs" / "ai" / "codex" / "GUIDE.md",
        "# Guide\n\nKeep this body out of summaries.\n\n## Setup\n\nMore body text.\n",
    )
    _write(
        repo / "tools" / "dev" / "sample.py",
        (
            '"""Module docstring first line.\n\nSecond line hidden."""\n'
            "import argparse\n"
            "import json as js\n"
            "from pathlib import Path\n\n"
            "class Worker:\n"
            "    def method(self):\n"
            "        return 'method body hidden'\n\n"
            "def top_level():\n"
            "    secret_body = 'function body hidden'\n"
            "    return secret_body\n"
        ),
    )
    _write(
        repo / "tests" / "test_sample.py",
        (
            "class TestThing:\n"
            "    def test_method(self):\n"
            "        assert 'body hidden'\n\n"
            "def test_example():\n"
            "    assert 'another body hidden'\n"
        ),
    )
    _write(repo / "docs" / "ai" / "codex" / ".env", "TOKEN=hidden\n")
    _write(repo / "docs" / "ai" / "codex" / "__pycache__" / "x.pyc", "hidden\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")
    return repo


def _run(args: list[str], capsys) -> tuple[int, str, str]:
    exit_code = helper.run(args)
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_markdown_output_for_docs_ai_scope_from_temp_repo(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, stderr = _run(["--repo-root", str(repo), "--scope", "docs-ai"], capsys)

    assert exit_code == 0
    assert stderr == ""
    assert "# Code Index" in stdout
    assert "## Advisory note" in stdout
    assert "## Documentation summaries" in stdout
    assert "`docs/ai/codex/GUIDE.md`" in stdout


def test_json_output_includes_required_keys(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "tools-dev", "--json"], capsys)

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
            "docs-ai",
            "--scope",
            "tools-dev",
            "--scope",
            "tests",
            "--json",
        ],
        capsys,
    )

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["index_scope"] == ["docs-ai", "tools-dev", "tests"]
    assert payload["included_paths"] == ["docs/ai/codex", "tools/dev", "tests"]


def test_unknown_scope_exits_nonzero(tmp_path, capsys):
    repo = _repo(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        helper.run(["--repo-root", str(repo), "--scope", "src"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert "invalid choice" in captured.err


def test_python_summaries_include_names_and_imports_but_not_bodies(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "tools-dev", "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    summary = payload["module_summaries"][0]
    assert summary["classes"] == ["Worker"]
    assert summary["functions"] == ["top_level"]
    assert summary["imports"] == ["argparse", "json", "pathlib"]
    assert summary["docstring_first_line"] == "Module docstring first line."
    serialized = json.dumps(summary)
    assert "function body hidden" not in serialized
    assert "method body hidden" not in serialized


def test_test_summaries_include_test_names_but_not_bodies(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "tests", "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    summary = payload["test_summaries"][0]
    assert summary["test_functions"] == ["test_example"]
    assert summary["test_classes"] == ["TestThing"]
    assert "body hidden" not in json.dumps(summary)


def test_markdown_summaries_include_headings_but_not_full_sections(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "docs-ai", "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    headings = payload["doc_summaries"][0]["headings"]
    assert headings == [{"level": 1, "text": "Guide"}, {"level": 2, "text": "Setup"}]
    assert "Keep this body out of summaries" not in json.dumps(payload["doc_summaries"])
    assert "More body text" not in json.dumps(payload["doc_summaries"])


def test_path_summaries_include_line_count_and_sha256(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "docs-ai", "--json"], capsys)

    assert exit_code == 0
    summary = json.loads(stdout)["path_summaries"][0]
    assert summary["path"] == "docs/ai/codex/GUIDE.md"
    assert summary["line_count"] == 7
    assert len(summary["sha256"]) == 64


def test_advisory_note_and_protected_path_notes_are_present(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "docs-ai", "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert "advisory only" in payload["advisory_note"]
    assert any("runtime/protected" in note for note in payload["protected_path_notes"])


def test_excluded_paths_are_not_indexed(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--scope", "docs-ai", "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    indexed_paths = {item["path"] for item in payload["path_summaries"]}
    assert "docs/ai/codex/.env" not in indexed_paths
    assert "docs/ai/codex/__pycache__/x.pyc" not in indexed_paths
    assert any(".env" in path for path in payload["excluded_paths"])


def test_output_writes_only_explicit_temp_output_path(tmp_path, capsys):
    repo = _repo(tmp_path)
    output = tmp_path / "out" / "index.json"
    before_status = _git(repo, "status", "--short").stdout

    exit_code, stdout, _ = _run(
        ["--repo-root", str(repo), "--scope", "tools-dev", "--json", "--output", str(output)],
        capsys,
    )

    assert exit_code == 0
    assert output.exists()
    assert "Wrote advisory code index" in stdout
    assert _git(repo, "status", "--short").stdout == before_status
    assert not (repo / "code_index.json").exists()


def test_check_stale_returns_fresh_for_unchanged_json(tmp_path, capsys):
    repo = _repo(tmp_path)
    output = tmp_path / "index.json"
    _run(["--repo-root", str(repo), "--scope", "tools-dev", "--json", "--output", str(output)], capsys)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--check-stale", str(output)], capsys)

    assert exit_code == 0
    assert stdout.splitlines()[0] == "fresh"


def test_check_stale_returns_stale_when_indexed_file_changes(tmp_path, capsys):
    repo = _repo(tmp_path)
    output = tmp_path / "index.json"
    _run(["--repo-root", str(repo), "--scope", "tools-dev", "--json", "--output", str(output)], capsys)
    _write(repo / "tools" / "dev" / "sample.py", "def changed():\n    return 1\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--check-stale", str(output)], capsys)

    assert exit_code == 1
    assert stdout.splitlines()[0] == "stale"
    assert "sha256 differs" in stdout


def test_check_stale_returns_stale_when_indexed_file_is_missing(tmp_path, capsys):
    repo = _repo(tmp_path)
    output = tmp_path / "index.json"
    _run(["--repo-root", str(repo), "--scope", "tools-dev", "--json", "--output", str(output)], capsys)
    (repo / "tools" / "dev" / "sample.py").unlink()

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--check-stale", str(output)], capsys)

    assert exit_code == 1
    assert stdout.splitlines()[0] == "stale"
    assert "indexed file is missing" in stdout


def test_helper_does_not_mutate_indexed_input_files(tmp_path, capsys):
    repo = _repo(tmp_path)
    indexed_file = repo / "tools" / "dev" / "sample.py"
    before_text = indexed_file.read_text(encoding="utf-8")
    before_status = _git(repo, "status", "--short").stdout

    exit_code, _, _ = _run(["--repo-root", str(repo), "--scope", "tools-dev"], capsys)

    assert exit_code == 0
    assert indexed_file.read_text(encoding="utf-8") == before_text
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
        "ast",
        "datetime",
        "fnmatch",
        "hashlib",
        "json",
        "pathlib",
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
