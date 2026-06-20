from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.registry.validate_walkforward_run_report import validate_walkforward_run_reports


FIXTURES = Path(__file__).parent / "fixtures" / "walkforward_run"


def test_valid_walkforward_run_report_passes() -> None:
    assert validate_walkforward_run_reports(
        explicit_paths=[FIXTURES / "valid_walkforward_run_report.json"]
    ) == []


@pytest.mark.parametrize(
    "name",
    [
        "invalid_walkforward_run_report_authority.json",
        "invalid_walkforward_run_report_counts.json",
    ],
)
def test_invalid_walkforward_run_reports_fail(name: str) -> None:
    assert validate_walkforward_run_reports(explicit_paths=[FIXTURES / name])


def test_validator_rejects_semantic_fold_count_drift(tmp_path: Path) -> None:
    payload = json.loads((FIXTURES / "valid_walkforward_run_report.json").read_text())
    payload["aggregate_degradation"]["fold_count"] = 2
    path = tmp_path / "drift.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    errors = validate_walkforward_run_reports(explicit_paths=[path])
    assert any("aggregate fold_count" in error for error in errors)


def test_validator_cli_accepts_valid_fixture() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.registry.validate_walkforward_run_report",
            str(FIXTURES / "valid_walkforward_run_report.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "OK: walk-forward run reports validate" in completed.stdout

