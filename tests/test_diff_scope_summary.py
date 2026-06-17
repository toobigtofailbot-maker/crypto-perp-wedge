import json
import subprocess
from pathlib import Path

import pytest

from tools.dev import diff_scope_summary as helper


REQUIRED_KEYS = {
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


def test_markdown_output_succeeds_inside_temp_git_repo(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, stderr = _run(["--repo-root", str(repo)], capsys)

    assert exit_code == 0
    assert stderr == ""
    assert "# Diff / Scope Summary" in stdout
    assert "## Tracked changed files" in stdout
    assert "Advisory only" in stdout


def test_json_output_includes_required_keys(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert set(payload) == REQUIRED_KEYS


def test_untracked_file_detection(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "notes.md", "draft\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["untracked_files"] == ["notes.md"]


def test_tracked_changed_file_detection(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "README.md", "changed\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["tracked_changed_files"] == ["README.md"]


def test_staged_changed_file_detection(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "README.md", "staged\n")
    _git(repo, "add", "README.md")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["staged_changed_files"] == ["README.md"]


def test_forbidden_prefix_detection(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "src" / "runtime.py", "changed\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["forbidden_matches"] == [{"path": "src/runtime.py", "prefix": "src/"}]


def test_check_forbidden_exits_nonzero_on_forbidden_match(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "research" / "note.md", "changed\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--check-forbidden"], capsys)

    assert exit_code == 1
    assert json.loads(stdout)["exit_reason"] == "forbidden path match"


def test_unauthorized_result_population_write_is_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/result_populations/RP-9001.result_population.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--check-forbidden"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "research/"}]


def test_authorized_new_result_population_write_is_not_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/result_populations/RP-9001.result_population.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-canonical-result-population-write",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_canonical_result_population_writes"]["package"] == "WP-TEST"
    assert payload["authorized_canonical_result_population_writes"]["authorized"][0]["path"] == path


def test_authorized_schema_path_is_not_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "strategy-spec-schema",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_path_writes"]["package"] == "WP-TEST"
    assert payload["authorized_path_writes"]["scope"] == "strategy-spec-schema"
    assert payload["authorized_path_writes"]["authorized"] == [
        {"path": path, "status": "authorized", "scope": "strategy-spec-schema"}
    ]


def test_online_ohlcv_schema_regression_authorized_path_is_not_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01",
            "--authorized-scope",
            "strategy-spec-schema",
            "--authorized-path",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_path_writes"]["package"] == "WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01"


def test_unauthorized_schema_path_remains_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--check-forbidden"], capsys)

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "research/"}]


def test_authorized_scope_requires_exact_changed_path(tmp_path, capsys):
    repo = _repo(tmp_path)
    changed_path = "research/schemas/strategy_spec.schema.json"
    authorized_path = "research/schemas/candidate_registry.schema.json"
    _write(repo / changed_path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            authorized_path,
            "--authorized-scope",
            "strategy-spec-schema",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["rejected"] == [
        {"path": authorized_path, "scope": "strategy-spec-schema", "reason": "path not changed"}
    ]
    assert payload["forbidden_matches"] == [{"path": changed_path, "prefix": "research/"}]


def test_authorized_schema_path_does_not_allow_different_schema_file(tmp_path, capsys):
    repo = _repo(tmp_path)
    authorized_path = "research/schemas/strategy_spec.schema.json"
    other_schema_path = "research/schemas/result_population.schema.json"
    _write(repo / authorized_path, "{}\n")
    _write(repo / other_schema_path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            authorized_path,
            "--authorized-scope",
            "strategy-spec-schema",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"][0]["path"] == authorized_path
    assert payload["forbidden_matches"] == [{"path": other_schema_path, "prefix": "research/"}]


def test_authorized_schema_scope_does_not_allow_lib_path(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "lib/backtest.py"
    _write(repo / path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "strategy-spec-schema",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["rejected"] == [
        {
            "path": path,
            "scope": "strategy-spec-schema",
            "reason": "scope requires an exact research/schemas/*.schema.json path",
        }
    ]
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "lib/"}]


def test_authorized_compiler_path_records_evidence(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "tools/research_runner/spec_signal_compiler.py"
    _write(repo / path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "research-compiler",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["authorized_path_writes"]["authorized"] == [
        {"path": path, "status": "authorized", "scope": "research-compiler"}
    ]


def test_compiler_scope_rejects_noncompiler_exact_path(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "research-compiler",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["rejected"] == [
        {
            "path": path,
            "scope": "research-compiler",
            "reason": "compiler scope is limited to tools/research_runner/spec_signal_compiler.py",
        }
    ]
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "research/"}]


def test_authorized_strategy_spec_path_is_not_forbidden(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "strategy-spec-prereg",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 0
    assert payload["forbidden_matches"] == []
    assert payload["authorized_path_writes"]["authorized"] == [
        {"path": path, "status": "authorized", "scope": "strategy-spec-prereg"}
    ]


def test_authorized_strategy_spec_scope_does_not_allow_result_population(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/result_populations/RP-9001.result_population.json"
    _write(repo / path, "{}\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            path,
            "--authorized-scope",
            "strategy-spec-prereg",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["rejected"] == [
        {
            "path": path,
            "scope": "strategy-spec-prereg",
            "reason": "strategy-spec scope is limited to research/strategy_specs/STRAT-SPEC-<digits>.strategy_spec.json",
        }
    ]
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "research/"}]


def test_authorized_mode_does_not_allow_runtime_or_lib_changes(tmp_path, capsys):
    repo = _repo(tmp_path)
    rp_path = "research/result_populations/RP-9001.result_population.json"
    lib_path = "lib/backtest.py"
    _write(repo / rp_path, "{}\n")
    _write(repo / lib_path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-canonical-result-population-write",
            rp_path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["forbidden_matches"] == [{"path": lib_path, "prefix": "lib/"}]


def test_authorized_mode_does_not_allow_existing_result_population_mutation(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/result_populations/RP-9001.result_population.json"
    _write(repo / path, "{}\n")
    _git(repo, "add", path)
    _git(repo, "commit", "-m", "add rp")
    _write(repo / path, '{"changed": true}\n')

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-canonical-result-population-write",
            path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["forbidden_matches"] == [{"path": path, "prefix": "research/"}]
    assert payload["authorized_canonical_result_population_writes"]["rejected"] == [
        {"path": path, "reason": "path exists in HEAD; existing RP mutation is not authorized"}
    ]


def test_mixed_authorized_rp_plus_unauthorized_protected_file_fails(tmp_path, capsys):
    repo = _repo(tmp_path)
    rp_path = "research/result_populations/RP-9001.result_population.json"
    runtime_path = "src/runtime/paper_trader.py"
    _write(repo / rp_path, "{}\n")
    _write(repo / runtime_path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-canonical-result-population-write",
            rp_path,
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_canonical_result_population_writes"]["authorized"][0]["path"] == rp_path
    assert payload["forbidden_matches"] == [{"path": runtime_path, "prefix": "src/"}]


def test_mixed_authorized_schema_plus_unauthorized_research_file_fails(tmp_path, capsys):
    repo = _repo(tmp_path)
    schema_path = "research/schemas/strategy_spec.schema.json"
    note_path = "research/notes/unapproved.md"
    _write(repo / schema_path, "{}\n")
    _write(repo / note_path, "changed\n")

    exit_code, stdout, _ = _run(
        [
            "--repo-root",
            str(repo),
            "--json",
            "--check-forbidden",
            "--authorized-package",
            "WP-TEST",
            "--authorized-path",
            schema_path,
            "--authorized-scope",
            "strategy-spec-schema",
        ],
        capsys,
    )

    payload = json.loads(stdout)
    assert exit_code == 1
    assert payload["authorized_path_writes"]["authorized"][0]["path"] == schema_path
    assert payload["forbidden_matches"] == [{"path": note_path, "prefix": "research/"}]


def test_authorized_path_requires_scope(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    with pytest.raises(SystemExit) as exc_info:
        helper.run(["--repo-root", str(repo), "--authorized-path", path])
    stderr = capsys.readouterr().err

    assert exc_info.value.code == 2
    assert "--authorized-path requires --authorized-scope" in stderr


def test_authorized_path_requires_package(tmp_path, capsys):
    repo = _repo(tmp_path)
    path = "research/schemas/strategy_spec.schema.json"
    _write(repo / path, "{}\n")

    with pytest.raises(SystemExit) as exc_info:
        helper.run(
            [
                "--repo-root",
                str(repo),
                "--authorized-path",
                path,
                "--authorized-scope",
                "strategy-spec-schema",
            ]
        )
    stderr = capsys.readouterr().err

    assert exc_info.value.code == 2
    assert "--authorized-path requires --authorized-package" in stderr


def test_allowed_file_reports_violations(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "allowed.md", "allowed\n")
    _write(repo / "outside.md", "outside\n")

    exit_code, stdout, _ = _run(
        ["--repo-root", str(repo), "--json", "--allowed-file", "allowed.md"],
        capsys,
    )

    assert exit_code == 0
    assert json.loads(stdout)["allowed_file_violations"] == ["outside.md"]


def test_trial_log_check_reports_empty_clean_state_when_untouched(tmp_path, capsys):
    repo = _repo(tmp_path)

    exit_code, stdout, _ = _run(["--repo-root", str(repo), "--json", "--trial-log"], capsys)

    assert exit_code == 0
    trial_log = json.loads(stdout)["trial_log"]
    assert trial_log["checked"] is True
    assert trial_log["touched"] is False
    assert trial_log["working_tree"] == []
    assert trial_log["staged"] == []
    assert trial_log["errors"] == []


def test_helper_does_not_mutate_files_or_git_state(tmp_path, capsys):
    repo = _repo(tmp_path)
    _write(repo / "README.md", "changed\n")
    _write(repo / "untracked.md", "new\n")
    before_status = _git(repo, "status", "--short").stdout
    before_readme = (repo / "README.md").read_text(encoding="utf-8")

    exit_code, _, _ = _run(["--repo-root", str(repo)], capsys)

    after_status = _git(repo, "status", "--short").stdout
    after_readme = (repo / "README.md").read_text(encoding="utf-8")
    assert exit_code == 0
    assert after_status == before_status
    assert after_readme == before_readme
