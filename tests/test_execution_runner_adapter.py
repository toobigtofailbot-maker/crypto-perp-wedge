import hashlib
import json
import os
import shutil
from pathlib import Path

import pytest

from tests import test_dispatch_writer as dispatch_support
from tools.canon_intake import dispatch_writer
from tools.canon_intake import execution_event_writer as event_writer
from tools.canon_intake import execution_runner_adapter as adapter
from tools.canon_intake.execution_event import (
    EXECUTION_WRITER_INTEGRITY_ROOT,
    read_and_validate_execution_stream,
)


def _hash(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


@pytest.fixture
def fixture(tmp_path: Path) -> dict:
    source_repo = Path(__file__).resolve().parents[1]
    prepared = dispatch_support._prepare_fixture(tmp_path, source_repo)
    schema = source_repo / "research/schemas/canon_execution_event.schema.json"
    shutil.copy2(schema, prepared["root"] / "research/schemas" / schema.name)
    dispatch_writer.write_dispatch_record(**dispatch_support._writer_kwargs(prepared))
    dispatch_raw = prepared["dispatch_path"].read_bytes()
    dispatch = json.loads(dispatch_raw)
    stream_relative = dispatch["run_binding"]["execution_event_stream_path"]
    stream_path = prepared["root"] / stream_relative
    stream_path.parent.mkdir(parents=True, exist_ok=True)
    (prepared["root"] / EXECUTION_WRITER_INTEGRITY_ROOT).mkdir(parents=True, exist_ok=True)
    prepared.update(
        {
            "dispatch": dispatch,
            "dispatch_hash": _hash(dispatch_raw),
            "dispatch_raw": dispatch_raw,
            "run_id": dispatch["run_binding"]["run_id"],
            "stream_relative": stream_relative,
            "stream_path": stream_path,
        }
    )
    return prepared


class _Clock:
    def __init__(self) -> None:
        self.second = 0

    def __call__(self) -> str:
        self.second += 1
        return f"2026-07-20T19:00:{self.second:02d}Z"


def _kwargs(fixture: dict) -> dict:
    return {
        "repo_root": fixture["root"],
        "dispatch_path": fixture["dispatch_path"],
        "reviewed_dispatch_whole_file_sha256": fixture["dispatch_hash"],
        "run_id": fixture["run_id"],
        "stream_path": fixture["stream_relative"],
        "actor_id": "synthetic-operator",
        "clock": _Clock(),
    }


def _row(number: int, category: str = "successful", *, variant_id: str | None = None) -> dict:
    return {
        "row_id": f"RP-9001-ROW-{number:06d}",
        "variant_id": variant_id or f"VAR-{number:06d}",
        "outcome_category": category,
        "attempted": category != "not_attempted",
    }


def _runner_result(categories: tuple[str, ...]) -> dict:
    aborted = "aborted" in categories
    counts = {
        category: categories.count(category)
        for category in (*adapter.OUTCOME_REASONS, "not_attempted")
    }
    return {
        "ok": not aborted,
        "aborted": aborted,
        "dry_run": True,
        "wrote": False,
        "output_path": None,
        "committed_denominator": len(categories),
        "outcome_category_counts": counts,
        "result_population": {
            "committed_denominator_snapshot": {
                "committed_denominator": len(categories),
                "result_row_count": len(categories),
                "outcome_counts_sum": len(categories),
            },
            "variant_result_rows": [
                _row(number, category) for number, category in enumerate(categories, 1)
            ],
            "outcome_category_counts": counts,
        },
    }


def _install_request_and_runner(monkeypatch, result: dict, calls: list[str]) -> None:
    monkeypatch.setattr(
        adapter,
        "_prepare_runner_request",
        lambda root, dispatch, **kwargs: object(),
    )

    def invoke(request, *, on_process_started):
        del request
        calls.append("runner")
        on_process_started()
        return result

    monkeypatch.setattr(adapter, "_invoke_existing_runner", invoke)


def _validated(fixture: dict, *, terminal: bool = True) -> dict:
    return read_and_validate_execution_stream(
        repo_root=fixture["root"],
        dispatch_path=fixture["dispatch_path"],
        reviewed_dispatch_whole_file_sha256=fixture["dispatch_hash"],
        require_terminal=terminal,
    )


def _configure_exact_input_prepare(
    fixture: dict,
    monkeypatch: pytest.MonkeyPatch,
    runner_result: dict,
    calls: list[str],
) -> dict:
    manifest = json.loads(fixture["manifest_path"].read_bytes())
    runner_binding = fixture["dispatch"]["runner_binding"]
    dataset = manifest["dataset"]
    funding = manifest["funding"]

    def bound_runner(*args, **kwargs):
        del args, kwargs
        calls.append("bound-runner")
        return runner_result

    bound_runner.__module__ = runner_binding["module"]
    runner_path = fixture["root"] / runner_binding["source_path"]
    monkeypatch.setattr(adapter, "RUNNER_MODULE", runner_binding["module"])
    monkeypatch.setattr(adapter, "RUNNER_SOURCE_PATH", runner_binding["source_path"])
    monkeypatch.setattr(adapter.offline_runner, "__name__", runner_binding["module"])
    monkeypatch.setattr(adapter.offline_runner, "__file__", str(runner_path))
    monkeypatch.setattr(adapter.offline_runner, "REPO_ROOT", fixture["root"])
    monkeypatch.setattr(adapter.offline_runner, "RUNNER_VERSION", runner_binding["version"])
    monkeypatch.setattr(adapter.offline_runner, "run_offline_sweep", bound_runner)
    monkeypatch.setattr(
        adapter.offline_runner,
        "DEFAULT_1D_CATALOG_SLICE_PATH",
        fixture["root"] / dataset["catalog_path"],
    )
    monkeypatch.setattr(
        adapter.offline_runner,
        "DEFAULT_1D_VALIDATOR_PATH",
        fixture["root"] / dataset["validator_path"],
    )
    monkeypatch.setattr(
        adapter.offline_runner,
        "OFFICIAL_1D_CATALOG_ARTIFACT_SHA256",
        dataset["catalog_sha256"].removeprefix("sha256:"),
    )
    monkeypatch.setattr(
        adapter.offline_runner,
        "OFFICIAL_1D_SOURCE_SHA256",
        dataset["data_sha256"].removeprefix("sha256:"),
    )
    monkeypatch.setattr(
        adapter.offline_runner,
        "OFFICIAL_1D_SOURCE_BYTE_LENGTH",
        dataset["data_byte_length"],
    )
    monkeypatch.setattr(
        adapter.offline_runner,
        "CANONICAL_FUNDING_EXPECTED_IDENTITY",
        {
            "provenance_artifact_path": funding["provenance_artifact_path"],
            "provenance_artifact_sha256": funding["provenance_artifact_sha256"],
            "funding_parquet_path": funding["funding_data_path"],
            "funding_parquet_sha256": funding["funding_data_sha256"],
            "funding_parquet_byte_length": funding["funding_data_byte_length"],
        },
    )
    return manifest


def _bound_input_path(fixture: dict, manifest: dict, label: str) -> Path:
    dispatch = fixture["dispatch"]
    if label == "dispatch record":
        return fixture["dispatch_path"]
    relative_by_label = {
        "dispatch manifest": dispatch["manifest_derivation"]["manifest_path"],
        "runner source": dispatch["runner_binding"]["source_path"],
        "strategy spec": dispatch["artifact_bindings"]["strategy_spec"]["path"],
        "variant manifest": dispatch["artifact_bindings"]["variant_manifest"]["path"],
        "sweep plan": dispatch["artifact_bindings"]["sweep_plan"]["path"],
        "funding provenance": manifest["funding"]["provenance_artifact_path"],
        "funding data": manifest["funding"]["funding_data_path"],
        "dataset catalog": manifest["dataset"]["catalog_path"],
        "dataset input": manifest["dataset"]["data_path"],
        "dataset validator": manifest["dataset"]["validator_path"],
    }
    return fixture["root"] / relative_by_label[label]


def test_completed_synthetic_run_records_every_attempt_and_no_authority_artifact(
    fixture, monkeypatch
):
    calls: list[str] = []
    _install_request_and_runner(
        monkeypatch,
        _runner_result(("successful", "failed", "invalid", "data_unavailable")),
        calls,
    )
    before_dispatch = fixture["dispatch_path"].read_bytes()
    before_authorization = fixture["authorization_path"].read_bytes()

    result = adapter.run_consumed_dispatch(**_kwargs(fixture))

    stream = _validated(fixture)
    assert calls == ["runner"]
    assert result["terminal_state"] == "run_completed"
    assert result["attempts_recorded"] == 4
    assert result["not_attempted"] == 0
    assert result["non_authority"]["advisory_output_only"] is True
    assert [event["event_type"] for event in stream["events"]] == [
        "run_start",
        "attempt_outcome",
        "attempt_outcome",
        "attempt_outcome",
        "attempt_outcome",
        "run_terminal",
    ]
    assert fixture["dispatch_path"].read_bytes() == before_dispatch
    assert fixture["authorization_path"].read_bytes() == before_authorization
    assert not (fixture["root"] / "research/result_populations").exists()
    assert not (fixture["root"] / "scratch/FIXTURE-RUN/dispatch").exists()


def test_process_start_failure_records_start_and_closed_terminal(fixture, monkeypatch):
    monkeypatch.setattr(
        adapter,
        "_prepare_runner_request",
        lambda root, dispatch, **kwargs: object(),
    )

    def fail_start(request, *, on_process_started):
        del request, on_process_started
        raise adapter.RunnerProcessStartFailure("synthetic process-start failure")

    monkeypatch.setattr(adapter, "_invoke_existing_runner", fail_start)
    with pytest.raises(adapter.RunnerProcessStartFailure) as caught:
        adapter.run_consumed_dispatch(**_kwargs(fixture))

    stream = _validated(fixture)
    assert caught.value.terminal_state == "run_failed_process_start"
    assert [event["event_type"] for event in stream["events"]] == [
        "run_start",
        "run_terminal",
    ]
    assert stream["events"][0]["run_start"]["runner_process_started"] is False
    terminal = stream["events"][-1]["run_terminal"]
    assert terminal["terminal_state"] == "run_failed_process_start"
    assert terminal["denominator_accounting"]["attempts_recorded"] == 0
    assert terminal["denominator_accounting"]["not_attempted"] == 4


def test_midrun_failure_retains_partial_outcomes_and_denominator_only_remainder(
    fixture, monkeypatch
):
    calls: list[str] = []
    _install_request_and_runner(
        monkeypatch,
        _runner_result(("successful", "aborted", "not_attempted", "not_attempted")),
        calls,
    )
    with pytest.raises(adapter.ExecutionRunnerAdapterError) as caught:
        adapter.run_consumed_dispatch(**_kwargs(fixture))

    stream = _validated(fixture)
    attempts = [
        event["attempt_outcome"]
        for event in stream["events"]
        if event["event_type"] == "attempt_outcome"
    ]
    assert caught.value.terminal_state == "run_failed_midrun"
    assert [attempt["outcome_category"] for attempt in attempts] == [
        "successful",
        "aborted",
    ]
    assert all(attempt["outcome_category"] != "not_attempted" for attempt in attempts)
    terminal = stream["events"][-1]["run_terminal"]
    assert terminal["terminal_state"] == "run_failed_midrun"
    assert terminal["denominator_accounting"]["attempts_recorded"] == 2
    assert terminal["denominator_accounting"]["not_attempted"] == 2


def test_fail_closed_pre_attempt_block_writes_no_attempt_outcome(fixture, monkeypatch):
    monkeypatch.setattr(
        adapter,
        "_prepare_runner_request",
        lambda root, dispatch, **kwargs: (_ for _ in ()).throw(
            adapter.ExecutionRunnerAdapterError("synthetic binding block")
        ),
    )
    with pytest.raises(adapter.ExecutionRunnerAdapterError) as caught:
        adapter.run_consumed_dispatch(**_kwargs(fixture))

    stream = _validated(fixture)
    assert caught.value.terminal_state == "run_blocked"
    assert [event["event_type"] for event in stream["events"]] == [
        "run_start",
        "run_terminal",
    ]
    assert stream["events"][-1]["run_terminal"]["terminal_state"] == "run_blocked"


def test_invalid_and_unconsumed_dispatches_are_rejected_before_runner(fixture, monkeypatch):
    invoked: list[bool] = []
    monkeypatch.setattr(
        adapter,
        "_invoke_existing_runner",
        lambda *args, **kwargs: invoked.append(True),
    )
    invalid = _kwargs(fixture)
    invalid["reviewed_dispatch_whole_file_sha256"] = "sha256:" + "0" * 64
    with pytest.raises(adapter.ExecutionRunnerAdapterError, match="validation failed"):
        adapter.run_consumed_dispatch(**invalid)
    assert invoked == []
    assert not fixture["stream_path"].exists()

    audit_lines = fixture["audit_path"].read_bytes().splitlines(keepends=True)
    fixture["audit_path"].write_bytes(audit_lines[0])
    with pytest.raises(adapter.ExecutionRunnerAdapterError, match="exactly consumed"):
        adapter.run_consumed_dispatch(**_kwargs(fixture))
    assert invoked == []
    assert not fixture["stream_path"].exists()


def test_duplicate_adapter_invocation_is_rejected_without_second_runner_call(fixture, monkeypatch):
    calls: list[str] = []
    _install_request_and_runner(
        monkeypatch,
        _runner_result(("successful",) * 4),
        calls,
    )
    adapter.run_consumed_dispatch(**_kwargs(fixture))
    retained = fixture["stream_path"].read_bytes()

    with pytest.raises(adapter.ExecutionRunnerAdapterError, match="duplicate/replay"):
        adapter.run_consumed_dispatch(**_kwargs(fixture))

    assert calls == ["runner"]
    assert fixture["stream_path"].read_bytes() == retained


@pytest.mark.parametrize(
    ("failure_event", "after_write", "expected_state"),
    [
        ("run_start", False, "missing"),
        ("attempt_outcome", True, "terminal"),
        ("run_terminal", False, "in_progress"),
    ],
)
def test_writer_failures_never_return_or_repair_history(
    fixture, monkeypatch, failure_event, after_write, expected_state
):
    calls: list[str] = []
    _install_request_and_runner(
        monkeypatch,
        _runner_result(("successful",) * 4),
        calls,
    )
    real_write = event_writer.write_execution_event
    failed = False

    def fail_once(**kwargs):
        nonlocal failed
        if kwargs["event_type"] == failure_event and not failed:
            failed = True
            if after_write:
                real_write(**kwargs)
            error_type = (
                event_writer.ExecutionEventWriterIntegrityCriticalError
                if failure_event == "attempt_outcome"
                else event_writer.ExecutionEventWriterError
            )
            raise error_type(f"synthetic {failure_event} writer uncertainty")
        return real_write(**kwargs)

    monkeypatch.setattr(adapter, "write_execution_event", fail_once)
    with pytest.raises(
        event_writer.ExecutionEventWriterError,
        match=f"synthetic {failure_event}",
    ) as caught:
        adapter.run_consumed_dispatch(**_kwargs(fixture))

    if expected_state == "missing":
        assert not fixture["stream_path"].exists()
    else:
        observed = _validated(fixture, terminal=expected_state == "terminal")
        assert observed["state"] == expected_state
    if failure_event == "attempt_outcome":
        assert isinstance(
            caught.value,
            event_writer.ExecutionEventWriterIntegrityCriticalError,
        )
    assert failed is True


@pytest.mark.parametrize("case", ["overflow", "duplicate", "order", "vocabulary", "write_claim"])
def test_invalid_runner_accounting_closes_blocked_without_fabricated_attempts(
    fixture, monkeypatch, case
):
    result = _runner_result(("successful",) * 4)
    rows = result["result_population"]["variant_result_rows"]
    if case == "overflow":
        rows.append(_row(5))
    elif case == "duplicate":
        rows[1]["variant_id"] = rows[0]["variant_id"]
    elif case == "order":
        rows[0], rows[1] = rows[1], rows[0]
    elif case == "vocabulary":
        rows[0]["outcome_category"] = "not_lawful"
    else:
        result["dry_run"] = False
        result["wrote"] = True
        result["output_path"] = "research/result_populations/RP-9001.json"
    calls: list[str] = []
    _install_request_and_runner(monkeypatch, result, calls)

    with pytest.raises(adapter.ExecutionRunnerAdapterError):
        adapter.run_consumed_dispatch(**_kwargs(fixture))

    stream = _validated(fixture)
    assert [event["event_type"] for event in stream["events"]] == [
        "run_start",
        "run_terminal",
    ]
    terminal = stream["events"][-1]["run_terminal"]
    assert terminal["terminal_state"] == "run_blocked"
    assert terminal["denominator_accounting"]["not_attempted"] == 4


def test_unlawful_terminal_vocabulary_is_rejected():
    with pytest.raises(adapter.ExecutionRunnerAdapterError, match="closed vocabulary"):
        adapter._terminal_input("success", process_started=True)


@pytest.mark.parametrize(
    ("label", "operation"),
    [
        ("dispatch record", "replace"),
        ("dispatch manifest", "write"),
        ("runner source", "replace"),
        ("strategy spec", "write"),
        ("variant manifest", "replace"),
        ("sweep plan", "write"),
        ("funding provenance", "replace"),
        ("funding data", "write"),
        ("dataset catalog", "replace"),
        ("dataset input", "write"),
        ("dataset validator", "replace"),
    ],
)
def test_post_validation_input_substitution_is_denied_and_lifecycle_fails_closed(
    fixture,
    monkeypatch,
    label,
    operation,
):
    calls: list[str] = []
    manifest = _configure_exact_input_prepare(
        fixture,
        monkeypatch,
        _runner_result(("successful",) * 4),
        calls,
    )
    target = _bound_input_path(fixture, manifest, label)
    original = target.read_bytes()

    def substitute_after_start(request, *, on_process_started):
        del request
        on_process_started()
        if operation == "write":
            target.write_bytes(b"post-validation substituted bytes\n")
        else:
            replacement = target.with_name(target.name + ".substitution")
            replacement.write_bytes(b"post-validation replacement bytes\n")
            os.replace(replacement, target)
        pytest.fail("bound input substitution unexpectedly succeeded")

    monkeypatch.setattr(adapter, "_invoke_existing_runner", substitute_after_start)
    with pytest.raises(adapter.ExecutionRunnerAdapterError) as caught:
        adapter.run_consumed_dispatch(**_kwargs(fixture))

    stream = _validated(fixture)
    assert calls == []
    assert target.read_bytes() == original
    assert not [event for event in stream["events"] if event["event_type"] == "attempt_outcome"]
    expected_terminal = "run_failed_midrun" if os.name == "nt" else "run_blocked"
    assert caught.value.terminal_state == expected_terminal
    assert [event["event_type"] for event in stream["events"]] == [
        "run_start",
        "run_terminal",
    ]
    assert stream["events"][-1]["run_terminal"]["terminal_state"] == expected_terminal
    accounting = stream["events"][-1]["run_terminal"]["denominator_accounting"]
    assert accounting["planned"] == 4
    assert accounting["attempts_recorded"] == 0
    assert accounting["not_attempted"] == 4
    assert not (fixture["root"] / "research/result_populations").exists()
    assert not (fixture["root"] / "scratch/FIXTURE-RUN/dispatch").exists()


def test_runner_callable_is_captured_before_module_rebinding(fixture, monkeypatch):
    calls: list[str] = []
    _configure_exact_input_prepare(
        fixture,
        monkeypatch,
        _runner_result(("successful",) * 4),
        calls,
    )
    if os.name != "nt":
        with pytest.raises(adapter.ExecutionRunnerAdapterError, match="exact-byte"):
            adapter.run_consumed_dispatch(**_kwargs(fixture))
        return

    real_prepare = adapter._prepare_runner_request

    def replacement_runner(*args, **kwargs):
        del args, kwargs
        calls.append("replacement-runner")
        return _runner_result(("failed",) * 4)

    def prepare_and_rebind(*args, **kwargs):
        request = real_prepare(*args, **kwargs)
        monkeypatch.setattr(adapter.offline_runner, "run_offline_sweep", replacement_runner)
        return request

    monkeypatch.setattr(adapter, "_prepare_runner_request", prepare_and_rebind)
    result = adapter.run_consumed_dispatch(**_kwargs(fixture))

    assert calls == ["bound-runner"]
    assert result["terminal_state"] == "run_completed"
    assert result["attempts_recorded"] == 4
    assert not (fixture["root"] / "research/result_populations").exists()


def test_existing_runner_seam_is_dry_run_only(monkeypatch):
    captured: dict = {}
    started: list[bool] = []

    def fake_run(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return {"fixture": True}

    monkeypatch.setattr(adapter.offline_runner, "run_offline_sweep", fake_run)
    root = adapter.offline_runner.REPO_ROOT.resolve()
    request = adapter._RunnerRequest(
        repo_root=root,
        strategy_spec_path=root / "research/strategy_specs/fixture.json",
        variant_manifest_path=root / "research/variant_manifests/fixture.json",
        sweep_plan_path=root / "research/sweep_plans/fixture.json",
        funding_provenance_path=root / "research/data_provenance/funding/fixture.json",
        deterministic_seed=7,
        max_workers=1,
        run_label="RUN-20260720-TEST9001",
        runner_callable=fake_run,
        input_leases=(),
    )

    assert adapter._invoke_existing_runner(
        request,
        on_process_started=lambda: started.append(True),
    ) == {"fixture": True}
    assert started == [True]
    assert captured["kwargs"]["write_result_population"] is False
    assert captured["kwargs"]["output_dir"] is None
    assert captured["kwargs"]["canonical_1d"] is True
    assert captured["kwargs"]["funding_cost_mode"] == "on"
