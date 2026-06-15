import json
import subprocess
from pathlib import Path

from tools.dev import verify as helper


REQUIRED_KEYS = {
    "overall_status",
    "commands",
    "integrity_views",
    "failures",
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
    _write(repo / "README.md", "initial\n")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "initial")
    return repo


def _run(args: list[str], capsys) -> tuple[int, str, str]:
    exit_code = helper.run(args)
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_json_output_includes_required_keys(monkeypatch, tmp_path, capsys):
    repo = _repo(tmp_path)

    monkeypatch.setattr(
        helper,
        "build_standard_commands",
        lambda args: [helper.CommandSpec(["git", "status", "--short"], timeout_seconds=5)],
    )

    exit_code, stdout, stderr = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    assert stderr == ""
    payload = json.loads(stdout)
    assert set(payload) == REQUIRED_KEYS
    assert payload["overall_status"] == "pass"
    assert payload["commands"][0]["command"] == "git status --short"


def test_nonzero_underlying_command_fails_closed(monkeypatch, tmp_path, capsys):
    repo = _repo(tmp_path)

    monkeypatch.setattr(
        helper,
        "build_standard_commands",
        lambda args: [helper.CommandSpec(["git", "not-a-command"], timeout_seconds=5)],
    )

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["overall_status"] == "fail"
    assert payload["commands"][0]["exit_code"] != 0
    assert "git not-a-command" in payload["failures"][0]["command"]
    assert payload["failures"][0]["stderr"]


def test_timeout_is_reported_and_fails_closed(monkeypatch, tmp_path, capsys):
    repo = _repo(tmp_path)

    monkeypatch.setattr(
        helper,
        "build_standard_commands",
        lambda args: [helper.CommandSpec(["python", "-c", "import time; time.sleep(2)"], timeout_seconds=1)],
    )

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["commands"][0]["status"] == "timeout"
    assert payload["commands"][0]["timed_out"] is True


def test_helper_does_not_mutate_files_or_git_state(monkeypatch, tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "README.md", "changed\n")
    before_status = _git(repo, "status", "--short").stdout
    before_readme = (repo / "README.md").read_text(encoding="utf-8")

    monkeypatch.setattr(
        helper,
        "build_standard_commands",
        lambda args: [helper.CommandSpec(["git", "status", "--short"], timeout_seconds=5)],
    )

    exit_code, _, _ = _run(["--repo-root", str(repo)], capsys)

    assert exit_code == 0
    assert _git(repo, "status", "--short").stdout == before_status
    assert (repo / "README.md").read_text(encoding="utf-8") == before_readme


def test_integrity_view_rows_fail_closed(monkeypatch, tmp_path, capsys):
    repo = _repo(tmp_path)
    list_result = {
        "command": "list",
        "argv": [],
        "required": True,
        "status": "pass",
        "exit_code": 0,
        "timed_out": False,
        "timeout_seconds": 5,
        "stdout": "v_integrity_example\n",
        "stderr": "",
        "_stdout_raw": "v_integrity_example\n",
        "_stderr_raw": "",
        "stdout_truncated": "false",
        "stderr_truncated": "false",
    }
    view_result = {
        **list_result,
        "command": "view",
        "stdout": '[{"issue": "bad"}]',
        "_stdout_raw": '[{"issue": "bad"}]',
    }

    monkeypatch.setattr(helper, "build_standard_commands", lambda args: [])
    monkeypatch.setattr(helper, "discover_integrity_views", lambda repo_root, timeout, max_chars: (["v_integrity_example"], list_result))
    monkeypatch.setattr(helper, "run_command", lambda repo_root, spec, max_chars: view_result)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--integrity-views"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["integrity_views"][0]["status"] == "fail"
    assert payload["integrity_views"][0]["row_count"] == 1


def test_integrity_all_zero_mock_views_pass_in_sorted_order(monkeypatch, tmp_path, capsys):
    repo = _repo(tmp_path)
    list_result = {
        "command": "list",
        "argv": [],
        "required": True,
        "status": "pass",
        "exit_code": 0,
        "timed_out": False,
        "timeout_seconds": 5,
        "elapsed_seconds": 0.01,
        "stdout": "v_integrity_beta\nv_integrity_alpha\n",
        "stderr": "",
        "_stdout_raw": "v_integrity_beta\nv_integrity_alpha\n",
        "_stderr_raw": "",
        "stdout_truncated": "false",
        "stderr_truncated": "false",
    }

    def fake_run_command(repo_root, spec, max_chars):
        view = spec.argv[-2]
        return {
            **list_result,
            "command": f"view {view}",
            "stdout": "[]",
            "_stdout_raw": "[]",
        }

    monkeypatch.setattr(helper, "build_standard_commands", lambda args: [])
    monkeypatch.setattr(
        helper,
        "discover_integrity_views",
        lambda repo_root, timeout, max_chars: (["v_integrity_beta", "v_integrity_alpha"], list_result),
    )
    monkeypatch.setattr(helper, "run_command", fake_run_command)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--integrity-views"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["overall_status"] == "pass"
    assert [view["name"] for view in payload["integrity_views"]] == [
        "v_integrity_alpha",
        "v_integrity_beta",
    ]
    assert {view["row_count"] for view in payload["integrity_views"]} == {0}


def test_integrity_timeout_fails_closed_and_names_view(monkeypatch, tmp_path, capsys):
    repo = _repo(tmp_path)
    list_result = {
        "command": "list",
        "argv": [],
        "required": True,
        "status": "pass",
        "exit_code": 0,
        "timed_out": False,
        "timeout_seconds": 5,
        "elapsed_seconds": 0.01,
        "stdout": "v_integrity_slow\n",
        "stderr": "",
        "_stdout_raw": "v_integrity_slow\n",
        "_stderr_raw": "",
        "stdout_truncated": "false",
        "stderr_truncated": "false",
    }
    timeout_result = {
        **list_result,
        "command": "view v_integrity_slow",
        "status": "timeout",
        "exit_code": None,
        "timed_out": True,
        "timeout_seconds": 7,
        "stdout": "",
        "_stdout_raw": "",
    }

    monkeypatch.setattr(helper, "build_standard_commands", lambda args: [])
    monkeypatch.setattr(
        helper,
        "discover_integrity_views",
        lambda repo_root, timeout, max_chars: (["v_integrity_slow"], list_result),
    )
    monkeypatch.setattr(helper, "run_command", lambda repo_root, spec, max_chars: timeout_result)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--integrity-views"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["integrity_views"][0]["name"] == "v_integrity_slow"
    assert payload["integrity_views"][0]["status"] == "fail"
    assert "timed out" in payload["integrity_views"][0]["error"]
    assert any(failure.get("name") == "v_integrity_slow" for failure in payload["failures"])


def test_integrity_command_error_fails_closed_and_names_view(monkeypatch, tmp_path, capsys):
    repo = _repo(tmp_path)
    list_result = {
        "command": "list",
        "argv": [],
        "required": True,
        "status": "pass",
        "exit_code": 0,
        "timed_out": False,
        "timeout_seconds": 5,
        "elapsed_seconds": 0.01,
        "stdout": "v_integrity_error\n",
        "stderr": "",
        "_stdout_raw": "v_integrity_error\n",
        "_stderr_raw": "",
        "stdout_truncated": "false",
        "stderr_truncated": "false",
    }
    error_result = {
        **list_result,
        "command": "view v_integrity_error",
        "status": "fail",
        "exit_code": 1,
        "stderr": "boom",
        "_stderr_raw": "boom",
    }

    monkeypatch.setattr(helper, "build_standard_commands", lambda args: [])
    monkeypatch.setattr(
        helper,
        "discover_integrity_views",
        lambda repo_root, timeout, max_chars: (["v_integrity_error"], list_result),
    )
    monkeypatch.setattr(helper, "run_command", lambda repo_root, spec, max_chars: error_result)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--integrity-views"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["integrity_views"][0]["name"] == "v_integrity_error"
    assert payload["integrity_views"][0]["error"] == "boom"


def test_verify_passes_authorized_canonical_write_to_diff_scope():
    parser = helper.build_parser()
    args = parser.parse_args(
        [
            "--authorized-package",
            "WP-TEST",
            "--authorized-canonical-result-population-write",
            "research/result_populations/RP-9001.result_population.json",
        ]
    )

    commands = helper.build_standard_commands(args)
    diff_scope_command = next(
        command.argv for command in commands if "tools/dev/diff_scope_summary.py" in command.argv
    )

    assert "--authorized-package" in diff_scope_command
    assert "WP-TEST" in diff_scope_command
    assert "--authorized-canonical-result-population-write" in diff_scope_command
    assert "research/result_populations/RP-9001.result_population.json" in diff_scope_command


def test_integrity_discovery_uses_raw_stdout_when_public_output_is_truncated(monkeypatch, tmp_path):
    repo = _repo(tmp_path)

    def fake_run(repo_root, spec, max_chars):
        return {
            "command": "list",
            "argv": [],
            "required": True,
            "status": "pass",
            "exit_code": 0,
            "timed_out": False,
            "timeout_seconds": 5,
            "_stdout_raw": "v_integrity_alpha\nv_integrity_result_population_denominator_mismatch\n",
            "_stderr_raw": "",
            "stdout": "v_integrity_alpha\nv_integrity_result",
            "stderr": "",
            "stdout_truncated": "true",
            "stderr_truncated": "false",
        }

    monkeypatch.setattr(helper, "run_command", fake_run)

    views, result = helper.discover_integrity_views(repo, 5, 24)

    assert result["stdout_truncated"] == "true"
    assert views == [
        "v_integrity_alpha",
        "v_integrity_result_population_denominator_mismatch",
    ]


def test_default_output_names_raw_commands(monkeypatch, tmp_path, capsys):
    repo = _repo(tmp_path)

    monkeypatch.setattr(
        helper,
        "build_standard_commands",
        lambda args: [helper.CommandSpec(["git", "status", "--short"], timeout_seconds=5)],
    )

    exit_code, stdout, _ = _run(["--repo-root", str(repo)], capsys)

    assert exit_code == 0
    assert "# Verification Summary" in stdout
    assert "`git status --short`: pass" in stdout
    assert "advisory orchestration only" in stdout
