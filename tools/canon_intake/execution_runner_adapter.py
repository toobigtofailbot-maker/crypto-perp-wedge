"""Fail-closed adapter from one consumed dispatch to the offline research runner.

The adapter records canonical control-plane history only.  It never creates a
dispatch, KDAUTH, canonical Result Population, runtime action, or capital action.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from tools.canon_intake.execution_event import (
    OUTCOME_REASONS,
    TERMINAL_REASONS,
    ExecutionEventError,
    read_and_validate_execution_stream,
)
from tools.canon_intake.execution_event_writer import (
    ExecutionEventWriterError,
    write_execution_event,
)
from tools.research_runner import run_offline_sweep as offline_runner

ADAPTER_VERSION = "canon-execution-runner-adapter-v1"
ADAPTER_SOURCE_PATH = "tools/canon_intake/execution_runner_adapter.py"
RUNNER_MODULE = "tools.research_runner.run_offline_sweep"
RUNNER_SOURCE_PATH = "tools/research_runner/run_offline_sweep.py"


class ExecutionRunnerAdapterError(RuntimeError):
    """Raised when the adapter cannot prove one complete lawful lifecycle."""


class RunnerProcessStartFailure(RuntimeError):
    """Raised by the invocation seam before the runner has started."""


@dataclass(frozen=True)
class _RunnerRequest:
    repo_root: Path
    strategy_spec_path: Path
    variant_manifest_path: Path
    sweep_plan_path: Path
    funding_provenance_path: Path
    deterministic_seed: int
    max_workers: int
    run_label: str


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _repo_path(root: Path, value: str, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ExecutionRunnerAdapterError(f"{label} must be one repo-relative path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or "\\" in value or any(part in {"", ".", ".."} for part in pure.parts):
        raise ExecutionRunnerAdapterError(f"{label} is not a safe repo-relative path")
    selected = root.joinpath(*pure.parts)
    try:
        resolved = selected.resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise ExecutionRunnerAdapterError(
            f"{label} is missing, redirected, or outside the repository"
        ) from exc
    if selected.is_symlink() or not resolved.is_file():
        raise ExecutionRunnerAdapterError(f"{label} must be a regular non-symlink file")
    return resolved


def _read_bound_json(
    root: Path,
    *,
    path: str,
    expected_sha256: str,
    label: str,
) -> tuple[dict[str, Any], Path]:
    selected = _repo_path(root, path, label)
    raw = selected.read_bytes()
    if _digest(raw) != expected_sha256:
        raise ExecutionRunnerAdapterError(f"{label} differs from its dispatch binding")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ExecutionRunnerAdapterError(f"{label} is not one UTF-8 JSON object") from exc
    if not isinstance(payload, dict):
        raise ExecutionRunnerAdapterError(f"{label} is not one JSON object")
    return payload, selected


def _actor(actor_id: str) -> dict[str, Any]:
    if not isinstance(actor_id, str) or not actor_id:
        raise ExecutionRunnerAdapterError("actor_id must be explicitly supplied")
    source = Path(__file__).read_bytes()
    return {
        "actor_id": actor_id,
        "tool_name": "canonical-execution-runner-adapter",
        "tool_version": ADAPTER_VERSION,
        "tool_source_path": ADAPTER_SOURCE_PATH,
        "tool_source_sha256": _digest(source),
    }


def _prepare_runner_request(
    root: Path,
    dispatch: Mapping[str, Any],
) -> _RunnerRequest:
    runner_binding = dispatch["runner_binding"]
    expected_runner = {
        "invocation_kind": "python_module",
        "module": RUNNER_MODULE,
        "source_path": RUNNER_SOURCE_PATH,
        "version": offline_runner.RUNNER_VERSION,
        "source_sha256": _digest(
            _repo_path(root, RUNNER_SOURCE_PATH, "runner source").read_bytes()
        ),
    }
    if runner_binding != expected_runner:
        raise ExecutionRunnerAdapterError(
            "dispatch runner binding is not the established offline research runner"
        )
    if dispatch["dataset_binding"]["timeframe"] != "1d":
        raise ExecutionRunnerAdapterError(
            "adapter is restricted to the merged canonical 1d runner route"
        )

    manifest_binding = dispatch["manifest_derivation"]
    manifest, _ = _read_bound_json(
        root,
        path=manifest_binding["manifest_path"],
        expected_sha256=manifest_binding["manifest_whole_file_sha256"],
        label="dispatch manifest",
    )
    if manifest.get("dataset", {}).get("canonical_route") != "1d":
        raise ExecutionRunnerAdapterError("dispatch manifest canonical route is not 1d")
    if manifest.get("funding", {}).get("funding_mode") != "on":
        raise ExecutionRunnerAdapterError("dispatch manifest funding mode is not on")

    artifact_paths: dict[str, Path] = {}
    for name in ("strategy_spec", "variant_manifest", "sweep_plan"):
        binding = dispatch["artifact_bindings"][name]
        _, artifact_paths[name] = _read_bound_json(
            root,
            path=binding["path"],
            expected_sha256=binding["sha256"],
            label=name.replace("_", " "),
        )
    _, funding_path = _read_bound_json(
        root,
        path=manifest["funding"]["provenance_artifact_path"],
        expected_sha256=manifest["funding"]["provenance_artifact_sha256"],
        label="funding provenance",
    )
    dataset_path = _repo_path(root, dispatch["dataset_binding"]["path"], "dispatch dataset")
    if (
        manifest["dataset"]["data_path"] != dispatch["dataset_binding"]["path"]
        or manifest["dataset"]["data_sha256"] != dispatch["dataset_binding"]["sha256"]
        or _digest(dataset_path.read_bytes()) != dispatch["dataset_binding"]["sha256"]
    ):
        raise ExecutionRunnerAdapterError("manifest/dispatch dataset hash mismatch")
    funding_data = _repo_path(root, manifest["funding"]["funding_data_path"], "funding data")
    if _digest(funding_data.read_bytes()) != manifest["funding"]["funding_data_sha256"]:
        raise ExecutionRunnerAdapterError("funding data differs from its manifest binding")

    return _RunnerRequest(
        repo_root=root,
        strategy_spec_path=artifact_paths["strategy_spec"],
        variant_manifest_path=artifact_paths["variant_manifest"],
        sweep_plan_path=artifact_paths["sweep_plan"],
        funding_provenance_path=funding_path,
        deterministic_seed=dispatch["execution_parameters"]["seed"],
        max_workers=dispatch["execution_parameters"]["workers"],
        run_label=dispatch["run_binding"]["run_id"],
    )


def _invoke_existing_runner(
    request: _RunnerRequest,
    *,
    on_process_started: Callable[[], None],
) -> Mapping[str, Any]:
    """Invoke only the merged dry-run research interface, with no RP write."""
    try:
        if request.repo_root != offline_runner.REPO_ROOT.resolve():
            raise RunnerProcessStartFailure(
                "offline runner repository root differs from the consumed dispatch root"
            )
        on_process_started()
    except ExecutionEventWriterError:
        raise
    except RunnerProcessStartFailure:
        raise
    except Exception as exc:
        raise RunnerProcessStartFailure("offline runner could not start") from exc
    return offline_runner.run_offline_sweep(
        request.strategy_spec_path,
        request.variant_manifest_path,
        request.sweep_plan_path,
        output_dir=None,
        write_result_population=False,
        run_label=request.run_label,
        deterministic_seed=request.deterministic_seed,
        canonical_1d=True,
        funding_cost_mode="on",
        funding_provenance_path=request.funding_provenance_path,
        funding_data_root=request.repo_root,
        max_workers=request.max_workers,
    )


def _normalize_attempts(
    runner_result: Mapping[str, Any],
    *,
    planned: int,
) -> tuple[list[dict[str, str]], str]:
    if not isinstance(runner_result, Mapping):
        raise ExecutionRunnerAdapterError("runner result must be one mapping")
    if not (
        runner_result.get("dry_run") is True
        and runner_result.get("wrote") is False
        and runner_result.get("output_path") is None
    ):
        raise ExecutionRunnerAdapterError(
            "runner result does not prove dry-run/no-Result-Population posture"
        )
    population = runner_result.get("result_population")
    if not isinstance(population, Mapping):
        raise ExecutionRunnerAdapterError("runner result population is unavailable")
    if runner_result.get("committed_denominator") != planned:
        raise ExecutionRunnerAdapterError("runner denominator differs from dispatch")
    rows = population.get("variant_result_rows")
    if not isinstance(rows, list):
        raise ExecutionRunnerAdapterError("runner variant rows are unavailable")
    if len(rows) > planned:
        raise ExecutionRunnerAdapterError("runner denominator overflow")
    if len(rows) != planned:
        raise ExecutionRunnerAdapterError("runner rows do not preserve the full denominator")

    snapshot = population.get("committed_denominator_snapshot")
    if not isinstance(snapshot, Mapping) or not (
        snapshot.get("committed_denominator") == planned
        and snapshot.get("result_row_count") == planned
        and snapshot.get("outcome_counts_sum") == planned
    ):
        raise ExecutionRunnerAdapterError("runner denominator snapshot is inconsistent")

    variant_ids: list[str] = []
    attempts: list[dict[str, str]] = []
    not_attempted = 0
    for number, row in enumerate(rows, 1):
        if not isinstance(row, Mapping):
            raise ExecutionRunnerAdapterError(f"runner row {number} is not one mapping")
        variant_id = row.get("variant_id")
        category = row.get("outcome_category")
        if not isinstance(variant_id, str) or not variant_id:
            raise ExecutionRunnerAdapterError(f"runner row {number} has no variant ID")
        expected_suffix = f"-ROW-{number:06d}"
        if not isinstance(row.get("row_id"), str) or not row["row_id"].endswith(expected_suffix):
            raise ExecutionRunnerAdapterError("runner row ordering drift")
        if category not in {*OUTCOME_REASONS, "not_attempted"}:
            raise ExecutionRunnerAdapterError("runner outcome is outside the closed vocabulary")
        variant_ids.append(variant_id)
        if category == "not_attempted":
            not_attempted += 1
            continue
        attempts.append(
            {
                "variant_id": variant_id,
                "outcome_category": category,
                "reason_code": OUTCOME_REASONS[category],
            }
        )
    if len(variant_ids) != len(set(variant_ids)):
        raise ExecutionRunnerAdapterError("runner returned a duplicate variant")
    if variant_ids != sorted(variant_ids):
        raise ExecutionRunnerAdapterError("runner variant ordering drift")

    observed = Counter(row["outcome_category"] for row in rows)
    for source in (
        runner_result.get("outcome_category_counts"),
        population.get("outcome_category_counts"),
    ):
        if not isinstance(source, Mapping) or any(
            source.get(category) != observed[category]
            for category in (*OUTCOME_REASONS, "not_attempted")
        ):
            raise ExecutionRunnerAdapterError("runner outcome accounting is inconsistent")

    aborted = runner_result.get("aborted")
    completed = runner_result.get("ok")
    if not isinstance(aborted, bool) or not isinstance(completed, bool):
        raise ExecutionRunnerAdapterError("runner lifecycle flags are unavailable")
    if not_attempted:
        terminal_state = "run_failed_midrun" if aborted and attempts else "run_blocked"
    elif completed:
        terminal_state = "run_completed"
    else:
        terminal_state = "run_blocked"
    return attempts, terminal_state


def _terminal_input(state: str, *, process_started: bool) -> dict[str, Any]:
    if state not in TERMINAL_REASONS:
        raise ExecutionRunnerAdapterError("terminal state is outside the closed vocabulary")
    return {
        "terminal_state": state,
        "terminal_reason_code": TERMINAL_REASONS[state],
        "process_started": process_started,
    }


def _attach_terminal_result(
    error: BaseException,
    terminal: Mapping[str, Any],
    state: str,
) -> None:
    error.terminal_recorded = True  # type: ignore[attr-defined]
    error.terminal_state = state  # type: ignore[attr-defined]
    error.terminal_writer_result = dict(terminal)  # type: ignore[attr-defined]


def run_consumed_dispatch(
    *,
    repo_root: Path,
    dispatch_path: Path,
    reviewed_dispatch_whole_file_sha256: str,
    run_id: str,
    stream_path: str,
    actor_id: str,
    clock: Callable[[], str] = _utc_now,
) -> dict[str, Any]:
    """Run one consumed dispatch and close its canonical execution lifecycle."""
    try:
        root = Path(repo_root).resolve(strict=True)
        validated = read_and_validate_execution_stream(
            repo_root=root,
            dispatch_path=dispatch_path,
            reviewed_dispatch_whole_file_sha256=reviewed_dispatch_whole_file_sha256,
            allow_missing=True,
            require_terminal=False,
            scan_retained_history=True,
        )
    except (OSError, ExecutionEventError) as exc:
        raise ExecutionRunnerAdapterError(f"consumed dispatch validation failed: {exc}") from exc
    dispatch = validated["dispatch"]
    if run_id != dispatch["run_binding"]["run_id"]:
        raise ExecutionRunnerAdapterError("requested run ID differs from exact dispatch")
    if stream_path != dispatch["run_binding"]["execution_event_stream_path"]:
        raise ExecutionRunnerAdapterError("requested stream path differs from exact dispatch")
    if validated["state"] != "missing":
        raise ExecutionRunnerAdapterError(
            "dispatch invocation is a duplicate/replay because its execution stream already exists"
        )

    actor = _actor(actor_id)
    common = {
        "repo_root": root,
        "dispatch_path": dispatch_path,
        "reviewed_dispatch_whole_file_sha256": reviewed_dispatch_whole_file_sha256,
        "run_id": run_id,
        "stream_path": stream_path,
        "actor": actor,
    }

    def append(event_type: str, event_input: Mapping[str, Any]) -> dict[str, Any]:
        return write_execution_event(
            **common,
            event_type=event_type,
            timestamp_utc=clock(),
            event_input=event_input,
        )

    def close_or_raise(
        state: str,
        *,
        process_started: bool,
        primary: BaseException,
    ) -> None:
        try:
            terminal = append(
                "run_terminal",
                _terminal_input(state, process_started=process_started),
            )
        except ExecutionEventWriterError as terminal_error:
            terminal_error.adapter_primary_error = primary  # type: ignore[attr-defined]
            raise
        _attach_terminal_result(primary, terminal, state)
        raise primary

    try:
        request = _prepare_runner_request(root, dispatch)
    except ExecutionRunnerAdapterError as exc:
        try:
            append("run_start", {"runner_process_started": False})
        except ExecutionEventWriterError as writer_error:
            writer_error.adapter_primary_error = exc  # type: ignore[attr-defined]
            try:
                append(
                    "run_terminal",
                    _terminal_input("run_blocked", process_started=False),
                )
            except ExecutionEventWriterError as terminal_error:
                writer_error.terminal_emission_error = terminal_error  # type: ignore[attr-defined]
            raise
        close_or_raise("run_blocked", process_started=False, primary=exc)

    process_started = False

    def mark_process_started() -> None:
        nonlocal process_started
        if process_started:
            raise ExecutionRunnerAdapterError("runner process-start callback recurred")
        append("run_start", {"runner_process_started": True})
        process_started = True

    try:
        runner_result = _invoke_existing_runner(
            request,
            on_process_started=mark_process_started,
        )
    except ExecutionEventWriterError as writer_error:
        try:
            append(
                "run_terminal",
                _terminal_input("run_blocked", process_started=process_started),
            )
        except ExecutionEventWriterError as terminal_error:
            writer_error.terminal_emission_error = terminal_error  # type: ignore[attr-defined]
        raise
    except RunnerProcessStartFailure as exc:
        if process_started:
            close_or_raise("run_failed_midrun", process_started=True, primary=exc)
        try:
            append("run_start", {"runner_process_started": False})
        except ExecutionEventWriterError as writer_error:
            writer_error.adapter_primary_error = exc  # type: ignore[attr-defined]
            raise
        close_or_raise("run_failed_process_start", process_started=False, primary=exc)
    except Exception as exc:  # noqa: BLE001 - the runner seam may raise any process error
        wrapped = ExecutionRunnerAdapterError(f"offline runner failed: {exc}")
        if process_started:
            close_or_raise("run_failed_midrun", process_started=True, primary=wrapped)
        try:
            append("run_start", {"runner_process_started": False})
        except ExecutionEventWriterError as writer_error:
            writer_error.adapter_primary_error = wrapped  # type: ignore[attr-defined]
            raise
        close_or_raise("run_failed_process_start", process_started=False, primary=wrapped)

    if not process_started:
        error = ExecutionRunnerAdapterError("runner returned without recording process start")
        append("run_start", {"runner_process_started": False})
        close_or_raise("run_failed_process_start", process_started=False, primary=error)

    try:
        attempts, terminal_state = _normalize_attempts(
            runner_result,
            planned=dispatch["denominator"]["planned"],
        )
    except ExecutionRunnerAdapterError as exc:
        close_or_raise("run_blocked", process_started=True, primary=exc)

    for attempt in attempts:
        try:
            append("attempt_outcome", attempt)
        except ExecutionEventWriterError as writer_error:
            try:
                append(
                    "run_terminal",
                    _terminal_input("run_blocked", process_started=True),
                )
            except ExecutionEventWriterError as terminal_error:
                writer_error.terminal_emission_error = terminal_error  # type: ignore[attr-defined]
            raise

    terminal = append(
        "run_terminal",
        _terminal_input(terminal_state, process_started=True),
    )
    try:
        closed = read_and_validate_execution_stream(
            repo_root=root,
            dispatch_path=dispatch_path,
            reviewed_dispatch_whole_file_sha256=reviewed_dispatch_whole_file_sha256,
            require_terminal=True,
            scan_retained_history=True,
        )
    except ExecutionEventError as exc:
        raise ExecutionRunnerAdapterError(
            f"terminal execution stream could not be verified: {exc}"
        ) from exc

    result = {
        "adapter_status": "closed",
        "terminal_state": terminal_state,
        "run_id": run_id,
        "stream_path": stream_path,
        "planned_denominator": dispatch["denominator"]["planned"],
        "attempts_recorded": len(attempts),
        "not_attempted": dispatch["denominator"]["planned"] - len(attempts),
        "stream_file_sha256": closed["stream_file_sha256"],
        "stream_byte_length": closed["stream_byte_length"],
        "terminal_event_id": terminal["event_id"],
        "runner_output": dict(runner_result),
        "non_authority": {
            "advisory_output_only": True,
            "control_plane_history_only": True,
            "canonical_result_population_written": False,
            "does_not_create_dispatch_or_kdauth": True,
            "does_not_authorize_runtime_paper_live_or_capital": True,
        },
    }
    if terminal_state != "run_completed":
        error = ExecutionRunnerAdapterError(f"runner lifecycle closed as {terminal_state}")
        _attach_terminal_result(error, terminal, terminal_state)
        error.adapter_result = result  # type: ignore[attr-defined]
        raise error
    return result
