import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests import test_dispatch_writer as dispatch_support
from tests import test_execution_runner_adapter as adapter_support
from tools.canon_intake import dispatch_writer, execution_readiness
from tools.canon_intake import execution_runner_adapter as adapter
from tools.canon_intake.execution_event import EXECUTION_WRITER_INTEGRITY_ROOT


def _hash(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        check=True,
        text=True,
        encoding="utf-8",
    )


def _commit_local_data_posture(root: Path, paths: list[str]) -> None:
    ignore = root / ".gitignore"
    ignore.write_text("".join(f"/{path}\n" for path in paths), encoding="utf-8")
    _git(root, "rm", "--cached", "--", *paths)
    _git(root, "add", ".gitignore")
    _git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "make canonical data local-only",
    )


@pytest.fixture(scope="module")
def base_fixture(tmp_path_factory: pytest.TempPathFactory) -> dict:
    source_repo = Path(__file__).resolve().parents[1]
    prepared = dispatch_support._prepare_fixture(
        tmp_path_factory.mktemp("execution-readiness-base"), source_repo
    )
    schema = source_repo / "research/schemas/canon_execution_event.schema.json"
    shutil.copy2(schema, prepared["root"] / "research/schemas" / schema.name)
    dispatch_writer.write_dispatch_record(**dispatch_support._writer_kwargs(prepared))
    dispatch_raw = prepared["dispatch_path"].read_bytes()
    (prepared["root"] / EXECUTION_WRITER_INTEGRITY_ROOT).mkdir(parents=True, exist_ok=True)

    manifest = json.loads(prepared["manifest_path"].read_bytes())
    data_paths = [
        manifest["dataset"]["data_path"],
        manifest["funding"]["funding_data_path"],
    ]
    _commit_local_data_posture(prepared["root"], data_paths)

    for relative in (
        adapter.ADAPTER_SOURCE_PATH,
        "tools/canon_intake/execution_event_writer.py",
        "tools/canon_intake/scratch_persistence.py",
    ):
        target = prepared["root"] / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_repo / relative, target)

    return {
        "root": prepared["root"],
        "dispatch_relative": prepared["dispatch_path"].relative_to(prepared["root"]),
        "dispatch_hash": _hash(dispatch_raw),
        "dispatch_raw": dispatch_raw,
        "source_repo": source_repo,
    }


@pytest.fixture
def fixture(
    base_fixture: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> dict:
    root = tmp_path / "repo"
    shutil.copytree(base_fixture["root"], root)
    dispatch_path = root / base_fixture["dispatch_relative"]
    dispatch = json.loads(dispatch_path.read_bytes())
    prepared = {
        "root": root,
        "dispatch_path": dispatch_path,
        "dispatch": dispatch,
        "manifest_path": root / dispatch["manifest_derivation"]["manifest_path"],
    }
    manifest = adapter_support._configure_exact_input_prepare(
        prepared,
        monkeypatch,
        {},
        [],
    )
    stream_relative = dispatch["run_binding"]["execution_event_stream_path"]
    prepared.update(
        {
            "dispatch_hash": base_fixture["dispatch_hash"],
            "dispatch_raw": base_fixture["dispatch_raw"],
            "manifest": manifest,
            "run_id": dispatch["run_binding"]["run_id"],
            "stream_relative": stream_relative,
            "stream_path": root / stream_relative,
            "source_repo": base_fixture["source_repo"],
        }
    )
    return prepared


def _kwargs(fixture: dict) -> dict:
    root = fixture["root"]
    runner_path = root / fixture["dispatch"]["runner_binding"]["source_path"]
    return {
        "repo_root": root,
        "dispatch_path": fixture["dispatch_path"],
        "reviewed_dispatch_whole_file_sha256": fixture["dispatch_hash"],
        "run_id": fixture["run_id"],
        "stream_path": fixture["stream_relative"],
        "actor_id": "codex-execution-runner",
        "expected_runner_version": fixture["dispatch"]["runner_binding"]["version"],
        "expected_runner_source_sha256": _hash(runner_path.read_bytes()),
        "expected_adapter_version": adapter.ADAPTER_VERSION,
        "expected_adapter_source_sha256": _hash((root / adapter.ADAPTER_SOURCE_PATH).read_bytes()),
        "expected_scratch_source_sha256": _hash(
            (root / "tools/canon_intake/scratch_persistence.py").read_bytes()
        ),
        "expected_writer_source_sha256": _hash(
            (root / "tools/canon_intake/execution_event_writer.py").read_bytes()
        ),
        "result_population_id": "RP-0007",
        "require_clean": True,
    }


def _by_id(result: dict, check_id: str) -> dict:
    return next(row for row in result["checks"] if row["check_id"] == check_id)


def _inventory(root: Path) -> dict[str, tuple[str, str | None]]:
    rows: dict[str, tuple[str, str | None]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if relative.parts[0] == ".git":
            continue
        if path.is_symlink():
            rows[relative.as_posix()] = ("link", None)
        elif path.is_dir():
            rows[relative.as_posix()] = ("directory", None)
        else:
            rows[relative.as_posix()] = ("file", _hash(path.read_bytes()))
    return rows


def _bootstrap_stream_parent(fixture: dict) -> None:
    fixture["stream_path"].parent.mkdir(parents=True)


def test_missing_stream_parent_is_exact_blocker_and_checker_is_zero_effect(fixture):
    before = _inventory(fixture["root"])
    result = execution_readiness.check_execution_readiness(**_kwargs(fixture))
    after = _inventory(fixture["root"])

    assert result["ready"] is False
    finding = _by_id(result, "execution_stream_parent")
    assert finding["status"] == "fail"
    assert finding["subject"] == "research/queue/execution_events"
    assert finding["bootstrap_candidate"] is True
    assert before == after
    assert not fixture["stream_path"].exists()
    assert not (fixture["root"] / f"scratch/{fixture['run_id']}").exists()
    assert not list((fixture["root"] / "research/result_populations").glob("RP-0007*"))


def test_safe_empty_parent_bootstrap_makes_fresh_worktree_ready(fixture):
    missing = execution_readiness.check_execution_readiness(**_kwargs(fixture))
    assert _by_id(missing, "execution_stream_parent")["status"] == "fail"

    _bootstrap_stream_parent(fixture)
    before = _inventory(fixture["root"])
    ready = execution_readiness.check_execution_readiness(**_kwargs(fixture))

    assert ready["ready"] is True
    assert _by_id(ready, "execution_stream_parent")["status"] == "pass"
    assert _by_id(ready, "fixture_to_production_parity")["status"] == "pass"
    assert _inventory(fixture["root"]) == before
    assert not fixture["stream_path"].exists()


def test_redirected_stream_parent_fails_descriptor_anchored_check(fixture, tmp_path):
    _bootstrap_stream_parent(fixture)
    dispatch_support._make_directory_redirect(
        fixture["stream_path"].parent,
        tmp_path / "redirect-destination",
    )

    result = execution_readiness.check_execution_readiness(**_kwargs(fixture))

    assert result["ready"] is False
    assert _by_id(result, "execution_stream_parent")["status"] == "fail"
    assert _by_id(result, "execution_stream_parent").get("bootstrap_candidate") is None


def test_missing_integrity_parent_and_stale_lock_are_blockers(fixture):
    _bootstrap_stream_parent(fixture)
    integrity = fixture["root"] / EXECUTION_WRITER_INTEGRITY_ROOT
    integrity.rmdir()
    missing = execution_readiness.check_execution_readiness(**_kwargs(fixture))
    assert _by_id(missing, "execution_writer_integrity_parent")["status"] == "fail"

    integrity.mkdir()
    lock = (
        fixture["root"] / "research/queue" / (f".{fixture['run_id']}.execution_event_append.lock")
    )
    lock.write_text("stale\n", encoding="utf-8")
    stale = execution_readiness.check_execution_readiness(**_kwargs(fixture))
    assert _by_id(stale, "stale_execution_append_lock_absent")["status"] == "fail"


def test_existing_stream_scratch_and_result_population_each_block(fixture):
    _bootstrap_stream_parent(fixture)
    fixture["stream_path"].write_text("not-an-event\n", encoding="utf-8")
    stream = execution_readiness.check_execution_readiness(**_kwargs(fixture))
    assert _by_id(stream, "execution_stream_first_run_state")["status"] == "fail"
    fixture["stream_path"].unlink()

    scratch = fixture["root"] / fixture["dispatch"]["output_targets"]["provisional_result_paths"][0]
    scratch.parent.mkdir(parents=True)
    scratch.write_text("{}\n", encoding="utf-8")
    scratch_result = execution_readiness.check_execution_readiness(**_kwargs(fixture))
    assert _by_id(scratch_result, "scratch_provisional_preflight")["status"] == "fail"
    shutil.rmtree(fixture["root"] / "scratch")

    rp = fixture["root"] / "research/result_populations/RP-0007.result_population.json"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("{}\n", encoding="utf-8")
    rp_result = execution_readiness.check_execution_readiness(**_kwargs(fixture))
    assert _by_id(rp_result, "result_population_absent")["status"] == "fail"


def test_production_scratch_preflight_and_all_leases_are_zero_effect_and_released(
    fixture, monkeypatch
):
    _bootstrap_stream_parent(fixture)
    scratch_calls: list[str] = []
    prepared_requests = []
    real_scratch = execution_readiness.preflight_provisional_result_target
    real_prepare = adapter._prepare_runner_request

    def scratch_spy(*, repo_root, dispatch):
        result = real_scratch(repo_root=repo_root, dispatch=dispatch)
        scratch_calls.append(result.provisional_result_path)
        return result

    def prepare_spy(*args, **kwargs):
        request = real_prepare(*args, **kwargs)
        prepared_requests.append(request)
        return request

    monkeypatch.setattr(execution_readiness, "preflight_provisional_result_target", scratch_spy)
    monkeypatch.setattr(adapter, "_prepare_runner_request", prepare_spy)
    before = _inventory(fixture["root"])

    result = execution_readiness.check_execution_readiness(**_kwargs(fixture))

    lease_check = _by_id(result, "leased_input_preparation")
    assert result["ready"] is True
    assert scratch_calls == [fixture["dispatch"]["output_targets"]["provisional_result_paths"][0]]
    assert lease_check["actual"]["count"] == 11
    assert lease_check["actual"]["labels"] == list(execution_readiness.EXPECTED_LEASE_LABELS)
    assert lease_check["actual"]["released"] is True
    assert all(lease.stream.closed for lease in prepared_requests[0].input_leases)
    assert _inventory(fixture["root"]) == before


def test_executable_identity_mismatch_and_contract_shape(fixture):
    _bootstrap_stream_parent(fixture)
    kwargs = _kwargs(fixture)
    kwargs["expected_writer_source_sha256"] = "sha256:" + "0" * 64

    result = execution_readiness.check_execution_readiness(**kwargs)

    assert result["ready"] is False
    assert result["non_authority"] is True
    assert _by_id(result, "execution_event_writer_identity")["status"] == "fail"
    assert result["blocking_findings"]
    required = {"check_id", "status", "subject", "expected", "actual", "blocking", "reason"}
    assert all(required <= set(row) for row in result["checks"])


def test_cli_exit_codes_distinguish_ready_not_ready_and_tool_error(fixture, capsys):
    kwargs = _kwargs(fixture)
    cli = [
        "--repo-root",
        str(kwargs["repo_root"]),
        "--dispatch-path",
        str(kwargs["dispatch_path"]),
        "--dispatch-sha256",
        kwargs["reviewed_dispatch_whole_file_sha256"],
        "--run-id",
        kwargs["run_id"],
        "--stream-path",
        kwargs["stream_path"],
        "--actor-id",
        kwargs["actor_id"],
        "--runner-version",
        kwargs["expected_runner_version"],
        "--runner-sha256",
        kwargs["expected_runner_source_sha256"],
        "--adapter-version",
        kwargs["expected_adapter_version"],
        "--adapter-sha256",
        kwargs["expected_adapter_source_sha256"],
        "--scratch-sha256",
        kwargs["expected_scratch_source_sha256"],
        "--writer-sha256",
        kwargs["expected_writer_source_sha256"],
        "--result-population-id",
        kwargs["result_population_id"],
        "--require-clean",
    ]
    assert execution_readiness.main(cli) == 1
    capsys.readouterr()

    _bootstrap_stream_parent(fixture)
    assert execution_readiness.main(cli) == 0
    ready_payload = json.loads(capsys.readouterr().out)
    assert ready_payload["ready"] is True

    bad_sha = cli.copy()
    bad_sha[bad_sha.index("--writer-sha256") + 1] = "invalid"
    assert execution_readiness.main(bad_sha) == 2
    error_payload = json.loads(capsys.readouterr().out)
    assert error_payload["ready"] is False


def test_no_runner_is_invoked_by_readiness(fixture, monkeypatch):
    _bootstrap_stream_parent(fixture)

    def forbidden_runner(*args, **kwargs):
        del args, kwargs
        raise AssertionError("runner must not be invoked by readiness")

    monkeypatch.setattr(adapter, "_invoke_existing_runner", forbidden_runner)
    result = execution_readiness.check_execution_readiness(**_kwargs(fixture))
    assert result["ready"] is True
