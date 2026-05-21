import json
from pathlib import Path

import pytest

from tools.dev import validation_summary as helper


REQUIRED_KEYS = {
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
}


def _write_log(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "validation.log"
    path.write_text(text, encoding="utf-8")
    return path


def _run(args: list[str], capsys) -> tuple[int, str, str]:
    exit_code = helper.run(args)
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_markdown_output_for_all_green_log(tmp_path, capsys):
    log = _write_log(
        tmp_path,
        "\n".join(
            [
                "$ python -m pytest tests/test_validation_summary.py -q",
                "3 passed, 1 deselected, 0 warnings",
                "v_integrity_registry: clean (0)",
                "Registry validators: 4 passed",
                "Exit code: 0",
            ]
        ),
    )

    exit_code, stdout, stderr = _run(["--from-log", str(log)], capsys)

    assert exit_code == 0
    assert stderr == ""
    assert "# Validation Summary" in stdout
    assert "## Overall status" in stdout
    assert "`pass`" in stdout
    assert "## Advisory note" in stdout


def test_json_output_includes_required_keys(tmp_path, capsys):
    log = _write_log(tmp_path, "1 passed\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert set(payload) == REQUIRED_KEYS


def test_overall_status_pass_for_clear_all_green_log(tmp_path, capsys):
    log = _write_log(tmp_path, "Command: pytest\n12 passed, 2 warnings\nexit code: 0\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["overall_status"] == "pass"


def test_registry_pass_count_does_not_increment_pytest_passes(tmp_path, capsys):
    log = _write_log(tmp_path, "1 passed\nRegistry validators: 4 passed\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["pytest"]["passed"] == 1
    assert payload["registry_validators"][0]["count"] == 4


def test_overall_status_fail_for_pytest_failure(tmp_path, capsys):
    log = _write_log(tmp_path, "FAILED tests/test_example.py::test_case\n1 failed, 2 passed\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["overall_status"] == "fail"
    assert any("test_case" in item["text"] for item in payload["failures"])


def test_overall_status_fail_for_timeout(tmp_path, capsys):
    log = _write_log(tmp_path, "pytest timed out after 120 seconds\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["overall_status"] == "fail"
    assert payload["timeouts"][0]["text"] == "pytest timed out after 120 seconds"


def test_overall_status_fail_for_nonzero_exit_code(tmp_path, capsys):
    log = _write_log(tmp_path, "Command: pytest\nExit code: 2\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["overall_status"] == "fail"


def test_overall_status_fail_for_integrity_returned_rows(tmp_path, capsys):
    log = _write_log(tmp_path, "v_integrity_reconciliations returned rows: [{'id': 'bad'}]\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["overall_status"] == "fail"
    assert any("returned rows" in item["text"] for item in payload["failures"])


def test_overall_status_unknown_when_no_clear_markers(tmp_path, capsys):
    log = _write_log(tmp_path, "starting local checks\nnothing decisive here\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["overall_status"] == "unknown"


def test_diff_scope_clean_headings_do_not_create_failures(tmp_path, capsys):
    log = _write_log(tmp_path, "## Forbidden-path matches\n- none\n## Allowed-file check\n- none\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--json"], capsys)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["overall_status"] == "unknown"
    assert payload["diff_scope"]["forbidden_matches"] == []
    assert payload["diff_scope"]["allowed_file_violations"] == []


def test_fail_on_error_exits_nonzero_on_failure(tmp_path, capsys):
    log = _write_log(tmp_path, "returncode=1\nERROR validation failed\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--fail-on-error"], capsys)

    assert exit_code == 1
    assert "ERROR validation failed" in stdout


def test_raw_log_path_is_preserved(tmp_path, capsys):
    log = _write_log(tmp_path, "1 passed\n")

    exit_code, stdout, _ = _run(["--from-log", str(log), "--json"], capsys)

    assert exit_code == 0
    assert json.loads(stdout)["raw_log_paths"] == [str(log.resolve())]


def test_helper_does_not_mutate_input_log(tmp_path, capsys):
    content = "Traceback (most recent call last):\nAssertionError: bad\n"
    log = _write_log(tmp_path, content)
    before = log.read_text(encoding="utf-8")

    exit_code, _, _ = _run(["--from-log", str(log)], capsys)

    assert exit_code == 0
    assert log.read_text(encoding="utf-8") == before


def test_future_command_running_modes_are_not_implemented(capsys):
    with pytest.raises(SystemExit) as exc_info:
        helper.run(["--run-docs-standard"])
    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert helper.UNIMPLEMENTED_WRAPPER_MESSAGE in captured.err
