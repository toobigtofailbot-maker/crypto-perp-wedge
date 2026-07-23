import json
import time
from pathlib import Path

import pytest

from tools.dev import verify as helper


def _profile(
    *,
    profile_id: str = "full-release-balanced-v1",
    shard_count: int = 3,
    isolated_files: tuple[str, ...] = ("tests/test_research_query.py",),
) -> helper.PytestShardProfile:
    return helper.PytestShardProfile(
        profile_id=profile_id,
        profile_version=1,
        shard_count=shard_count,
        isolated_files=isolated_files,
        isolated_execution=helper.SUPPORTED_ISOLATED_EXECUTION,
        partition_strategy=helper.SUPPORTED_PROFILE_PARTITION_STRATEGY,
        timeout_seconds=1800,
        exactly_once=True,
    )


def _tracked_files() -> list[str]:
    return [
        "tests/test_alpha.py",
        "tests/test_beta.py",
        "tests/test_gamma.py",
        "tests/test_research_query.py",
        "tests/test_zeta.py",
    ]


def _result(spec: helper.CommandSpec, status: str = "pass") -> dict:
    timed_out = status == "timeout"
    return {
        "command": helper._command_text(spec.argv),
        "argv": spec.argv,
        "label": spec.label,
        "metadata": spec.metadata or {},
        "required": True,
        "status": status,
        "exit_code": None if timed_out else (0 if status == "pass" else 1),
        "timed_out": timed_out,
        "timeout_seconds": spec.timeout_seconds,
        "elapsed_seconds": float(spec.metadata["shard_index"] + 1),
        "stdout": "",
        "stderr": "",
        "_stdout_raw": "",
        "_stderr_raw": "",
        "stdout_truncated": "false",
        "stderr_truncated": "false",
    }


def _profile_args(*extra: str):
    return helper.build_parser().parse_args(
        [
            "--full-pytest-sharded",
            "--pytest-shard-profile",
            "full-release-balanced-v1",
            *extra,
        ]
    )


def test_profile_assignment_is_deterministic_exact_and_isolates_query():
    files = _tracked_files()
    profile = _profile()

    first = helper._partition_by_profile(files, profile)
    second = helper._partition_by_profile(files, profile)
    first_proof = helper._assignment_proof(
        files,
        first,
        profile=profile,
        partition_strategy=profile.partition_strategy,
    )
    second_proof = helper._assignment_proof(
        files,
        second,
        profile=profile,
        partition_strategy=profile.partition_strategy,
    )

    assert first == second
    assert first[0] == ["tests/test_research_query.py"]
    assert sorted(path for shard in first for path in shard) == files
    assert first_proof["exact_coverage"] is True
    assert first_proof["assigned_file_count"] == len(files)
    assert first_proof["unique_assigned_file_count"] == len(files)
    assert first_proof["missing_files"] == []
    assert first_proof["duplicate_files"] == []
    assert first_proof["assignment_manifest_sha256"] == second_proof["assignment_manifest_sha256"]


def test_tracked_file_addition_and_removal_change_manifest_deterministically():
    profile = _profile()

    def manifest(files: list[str]) -> str:
        partitions = helper._partition_by_profile(files, profile)
        return helper._assignment_proof(
            files,
            partitions,
            profile=profile,
            partition_strategy=profile.partition_strategy,
        )["assignment_manifest_sha256"]

    baseline = _tracked_files()
    added = sorted([*baseline, "tests/test_new.py"])
    removed = [path for path in baseline if path != "tests/test_zeta.py"]

    assert manifest(baseline) == manifest(list(baseline))
    assert manifest(added) != manifest(baseline)
    assert manifest(removed) != manifest(baseline)


def test_untracked_isolated_file_fails_closed():
    with pytest.raises(helper.VerifyError, match="untracked isolated files"):
        helper._partition_by_profile(
            _tracked_files(),
            _profile(isolated_files=("tests/test_missing.py",)),
        )


def test_duplicate_isolated_file_fails_profile_parsing():
    raw = {
        "profile_id": "duplicate-v1",
        "profile_version": 1,
        "shard_count": 3,
        "isolated_files": ["tests/test_alpha.py", "tests/test_alpha.py"],
        "isolated_execution": helper.SUPPORTED_ISOLATED_EXECUTION,
        "partition_strategy": helper.SUPPORTED_PROFILE_PARTITION_STRATEGY,
        "timeout_seconds": 1800,
        "exactly_once": True,
    }

    with pytest.raises(helper.VerifyError, match="duplicate isolated files"):
        helper._parse_pytest_shard_profile("duplicate-v1", raw)


@pytest.mark.parametrize(
    "path",
    [
        "",
        "../tests/test_alpha.py",
        "tests\\test_alpha.py",
        "/tests/test_alpha.py",
        "tests/not_a_test.py",
        " tests/test_alpha.py",
    ],
)
def test_invalid_profile_paths_fail_closed(path):
    with pytest.raises(helper.VerifyError):
        helper._validate_profile_path(path)


@pytest.mark.parametrize(
    "profile",
    [
        _profile(shard_count=6),
        _profile(shard_count=1),
        _profile(shard_count=2, isolated_files=("tests/test_alpha.py", "tests/test_beta.py")),
    ],
)
def test_impossible_profiles_fail_before_pytest(profile):
    with pytest.raises(helper.VerifyError):
        helper._partition_by_profile(_tracked_files(), profile)


def test_empty_profile_object_fails_closed():
    with pytest.raises(helper.VerifyError):
        helper._parse_pytest_shard_profile("empty-v1", {})


def test_named_profile_parses_and_conflicting_raw_shards_fail(capsys):
    args = _profile_args()
    assert args.pytest_shard_profile == "full-release-balanced-v1"

    with pytest.raises(SystemExit) as exc_info:
        helper.run(
            [
                "--full-pytest-sharded",
                "--pytest-shard-profile",
                "full-release-balanced-v1",
                "--pytest-shards",
                "48",
            ]
        )

    assert exc_info.value.code == 2
    assert "conflicts with --pytest-shards" in capsys.readouterr().err


def test_raw_index_modulo_partitioning_is_unchanged():
    files = _tracked_files()
    assert helper._partition_by_index(files, 3) == [
        [files[0], files[3]],
        [files[1], files[4]],
        [files[2]],
    ]


@pytest.mark.parametrize(
    ("status_by_shard", "all_complete", "all_passed"),
    [
        ({}, True, True),
        ({1: "fail"}, True, False),
        ({2: "timeout"}, False, False),
    ],
)
def test_named_profile_completion_and_failure_evidence(
    monkeypatch,
    tmp_path,
    status_by_shard,
    all_complete,
    all_passed,
):
    args = _profile_args()
    profile = _profile()
    monkeypatch.setattr(helper, "discover_pytest_files", lambda repo_root: _tracked_files())
    monkeypatch.setattr(helper, "load_pytest_shard_profile", lambda repo_root, name: profile)
    monkeypatch.setattr(
        helper,
        "run_command",
        lambda repo_root, spec, max_chars: _result(
            spec,
            status_by_shard.get(spec.metadata["shard_index"], "pass"),
        ),
    )

    summary, results = helper.run_pytest_shards(tmp_path, args)

    assert len(results) == 3
    assert summary["all_shards_complete"] is all_complete
    assert summary["all_shards_passed"] is all_passed
    assert summary["slowest_shard"] == {"shard_index": 2, "elapsed_seconds": 3.0}
    assert summary["maximum_elapsed_seconds"] == 3.0
    assert summary["shards"][0]["files"] == ["tests/test_research_query.py"]
    assert summary["assignments"][0]["files"] == ["tests/test_research_query.py"]


def test_selected_profile_shard_execution_is_deterministic(monkeypatch, tmp_path):
    args = _profile_args("--pytest-shard-index", "1")
    profile = _profile()
    seen_commands: list[list[str]] = []
    monkeypatch.setattr(helper, "discover_pytest_files", lambda repo_root: _tracked_files())
    monkeypatch.setattr(helper, "load_pytest_shard_profile", lambda repo_root, name: profile)

    def fake_run(repo_root, spec, max_chars):
        seen_commands.append(spec.argv)
        return _result(spec)

    monkeypatch.setattr(helper, "run_command", fake_run)

    first, _ = helper.run_pytest_shards(tmp_path, args)
    first_command = list(seen_commands[-1])
    second, _ = helper.run_pytest_shards(tmp_path, args)

    assert first["selected_indices"] == [1]
    assert first["all_shards_selected"] is False
    assert first["all_shards_complete"] is False
    assert first_command == seen_commands[-1]
    assert first["assignment_manifest_sha256"] == second["assignment_manifest_sha256"]


def test_isolated_profile_shard_completes_before_parallel_shards_start(monkeypatch, tmp_path):
    args = _profile_args()
    profile = _profile()
    events: list[str] = []
    monkeypatch.setattr(helper, "discover_pytest_files", lambda repo_root: _tracked_files())
    monkeypatch.setattr(helper, "load_pytest_shard_profile", lambda repo_root, name: profile)

    def fake_run(repo_root, spec, max_chars):
        shard_index = spec.metadata["shard_index"]
        if shard_index == 0:
            events.append("isolated-start")
            time.sleep(0.05)
            events.append("isolated-end")
        else:
            assert "isolated-end" in events
            events.append(f"parallel-{shard_index}")
        return _result(spec)

    monkeypatch.setattr(helper, "run_command", fake_run)

    summary, _ = helper.run_pytest_shards(tmp_path, args)

    assert events[0:2] == ["isolated-start", "isolated-end"]
    assert summary["exclusive_shard_indices"] == [0]
    assert summary["parallel_workers"] == 2


@pytest.mark.parametrize("isolated_status", ["fail", "timeout"])
def test_isolated_profile_failure_skips_parallel_phase(
    monkeypatch,
    tmp_path,
    isolated_status,
):
    args = _profile_args()
    profile = _profile()
    started: list[int] = []
    monkeypatch.setattr(helper, "discover_pytest_files", lambda repo_root: _tracked_files())
    monkeypatch.setattr(helper, "load_pytest_shard_profile", lambda repo_root, name: profile)

    def fake_run(repo_root, spec, max_chars):
        shard_index = spec.metadata["shard_index"]
        started.append(shard_index)
        return _result(spec, isolated_status if shard_index == 0 else "pass")

    monkeypatch.setattr(helper, "run_command", fake_run)

    summary, results = helper.run_pytest_shards(tmp_path, args)

    assert started == [0]
    assert len(results) == 1
    assert summary["executed_indices"] == [0]
    assert summary["not_run_indices"] == [1, 2]
    assert summary["all_selected_shards_executed"] is False
    assert summary["parallel_phase_skipped"] is True
    assert summary["all_shards_complete"] is False
    assert summary["all_shards_passed"] is False


def test_json_and_markdown_include_profile_assignment_proof(monkeypatch, tmp_path):
    args = _profile_args()
    profile = _profile()
    monkeypatch.setattr(helper, "discover_pytest_files", lambda repo_root: _tracked_files())
    monkeypatch.setattr(helper, "load_pytest_shard_profile", lambda repo_root, name: profile)
    monkeypatch.setattr(
        helper,
        "run_command",
        lambda repo_root, spec, max_chars: _result(spec),
    )

    shard_summary, _ = helper.run_pytest_shards(tmp_path, args)
    payload = {
        "overall_status": "pass",
        "commands": [],
        "integrity_views": [],
        "pytest_shards": shard_summary,
        "failures": [],
        "advisory_note": helper.ADVISORY_NOTE,
    }
    serialized = json.loads(json.dumps(payload))
    markdown = helper.format_markdown(payload)

    assert serialized["pytest_shards"]["profile_id"] == "full-release-balanced-v1"
    assert serialized["pytest_shards"]["exact_coverage"] is True
    assert serialized["pytest_shards"]["assignment_manifest_sha256"].startswith("sha256:")
    assert "`full-release-balanced-v1`" in markdown
    assert "assignment coverage: exact=true" in markdown
    assert "assignment manifest: `sha256:" in markdown


def test_repo_profile_is_loadable_and_has_locked_shape():
    profile = helper.load_pytest_shard_profile(Path.cwd(), "full-release-balanced-v1")

    assert profile.profile_version == 1
    assert profile.shard_count == 48
    assert profile.isolated_files == ("tests/test_research_query.py",)
    assert profile.isolated_execution == "exclusive"
    assert profile.timeout_seconds == 1800
    assert profile.exactly_once is True
