"""Fail-closed adapter from one consumed dispatch to the offline research runner.

The adapter records canonical control-plane history only.  It never creates a
dispatch, KDAUTH, canonical Result Population, runtime action, or capital action.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

if os.name == "nt":
    import ctypes
    import msvcrt
    from ctypes import wintypes

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

ADAPTER_VERSION = "canon-execution-runner-adapter-v2"
ADAPTER_SOURCE_PATH = "tools/canon_intake/execution_runner_adapter.py"
RUNNER_MODULE = "tools.research_runner.run_offline_sweep"
RUNNER_SOURCE_PATH = "tools/research_runner/run_offline_sweep.py"


class ExecutionRunnerAdapterError(RuntimeError):
    """Raised when the adapter cannot prove one complete lawful lifecycle."""


class RunnerProcessStartFailure(RuntimeError):
    """Raised by the invocation seam before the runner has started."""


@dataclass
class _InputLease:
    label: str
    path: Path
    raw: bytes
    stream: Any

    def close(self) -> None:
        try:
            self.stream.close()
        except OSError:
            pass


class _InputLeaseSet:
    """Hold exact input files read-only and deny write/delete until runner return."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._leases: list[_InputLease] = []
        self._by_path: dict[Path, _InputLease] = {}

    def acquire(
        self,
        path: Path,
        *,
        expected_sha256: str,
        label: str,
        expected_byte_length: int | None = None,
    ) -> _InputLease:
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(self.root)
        except (FileNotFoundError, OSError, ValueError) as exc:
            raise ExecutionRunnerAdapterError(
                f"{label} is missing, redirected, or outside the repository"
            ) from exc
        if path.is_symlink() or not resolved.is_file():
            raise ExecutionRunnerAdapterError(f"{label} must be a regular non-symlink file")

        existing = self._by_path.get(resolved)
        if existing is not None:
            if _digest(existing.raw) != expected_sha256:
                raise ExecutionRunnerAdapterError(
                    f"{label} conflicts with an already leased input binding"
                )
            if expected_byte_length is not None and len(existing.raw) != expected_byte_length:
                raise ExecutionRunnerAdapterError(f"{label} byte length differs from its binding")
            return existing

        lease = _open_exact_read_lease(resolved, label)
        try:
            if _digest(lease.raw) != expected_sha256:
                raise ExecutionRunnerAdapterError(f"{label} differs from its dispatch binding")
            if expected_byte_length is not None and len(lease.raw) != expected_byte_length:
                raise ExecutionRunnerAdapterError(f"{label} byte length differs from its binding")
        except BaseException:
            lease.close()
            raise
        self._leases.append(lease)
        self._by_path[resolved] = lease
        return lease

    def detach(self) -> tuple[_InputLease, ...]:
        leases = tuple(self._leases)
        self._leases = []
        self._by_path = {}
        return leases

    def close(self) -> None:
        for lease in reversed(self._leases):
            lease.close()
        self._leases = []
        self._by_path = {}


def _open_exact_read_lease(path: Path, label: str) -> _InputLease:
    if os.name != "nt":
        raise ExecutionRunnerAdapterError(
            "exact-byte runner input consumption requires Windows deny-write/delete file leases"
        )

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = kernel32.CreateFileW
    create_file.argtypes = (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    )
    create_file.restype = wintypes.HANDLE
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = (wintypes.HANDLE,)
    close_handle.restype = wintypes.BOOL

    generic_read = 0x80000000
    file_share_read = 0x00000001
    open_existing = 3
    file_attribute_normal = 0x00000080
    invalid_handle = ctypes.c_void_p(-1).value
    handle = create_file(
        str(path),
        generic_read,
        file_share_read,
        None,
        open_existing,
        file_attribute_normal,
        None,
    )
    if handle == invalid_handle:
        error = ctypes.WinError(ctypes.get_last_error())
        raise ExecutionRunnerAdapterError(
            f"could not acquire exact-byte lease for {label}: {error}"
        )

    try:
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        descriptor = msvcrt.open_osfhandle(handle, flags)
        handle = None
        stream = os.fdopen(descriptor, "rb", closefd=True)
        raw = stream.read()
        stream.seek(0)
    except BaseException:
        if handle is not None:
            close_handle(handle)
        raise
    return _InputLease(label=label, path=path, raw=raw, stream=stream)


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
    runner_callable: Callable[..., Mapping[str, Any]]
    input_leases: tuple[_InputLease, ...]

    def close_input_leases(self) -> None:
        for lease in reversed(self.input_leases):
            lease.close()


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
    leases: _InputLeaseSet,
    path: str,
    expected_sha256: str,
    label: str,
    expected_byte_length: int | None = None,
) -> tuple[dict[str, Any], Path]:
    selected = _repo_path(root, path, label)
    lease = leases.acquire(
        selected,
        expected_sha256=expected_sha256,
        expected_byte_length=expected_byte_length,
        label=label,
    )
    try:
        payload = json.loads(lease.raw.decode("utf-8"))
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
    *,
    dispatch_path: Path,
    reviewed_dispatch_whole_file_sha256: str,
) -> _RunnerRequest:
    leases = _InputLeaseSet(root)
    try:
        leases.acquire(
            dispatch_path,
            expected_sha256=reviewed_dispatch_whole_file_sha256,
            label="dispatch record",
        )

        runner_binding = dispatch["runner_binding"]
        expected_runner_core = {
            "invocation_kind": "python_module",
            "module": RUNNER_MODULE,
            "source_path": RUNNER_SOURCE_PATH,
            "version": offline_runner.RUNNER_VERSION,
        }
        if any(runner_binding.get(key) != value for key, value in expected_runner_core.items()):
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
            leases=leases,
            path=manifest_binding["manifest_path"],
            expected_sha256=manifest_binding["manifest_whole_file_sha256"],
            expected_byte_length=manifest_binding["manifest_byte_length"],
            label="dispatch manifest",
        )
        if manifest.get("dataset", {}).get("canonical_route") != "1d":
            raise ExecutionRunnerAdapterError("dispatch manifest canonical route is not 1d")
        if manifest.get("funding", {}).get("funding_mode") != "on":
            raise ExecutionRunnerAdapterError("dispatch manifest funding mode is not on")

        manifest_runner = manifest["runner"]
        if any(manifest_runner.get(key) != value for key, value in runner_binding.items()):
            raise ExecutionRunnerAdapterError("manifest/dispatch runner binding mismatch")
        runner_source = _repo_path(root, RUNNER_SOURCE_PATH, "runner source")
        leases.acquire(
            runner_source,
            expected_sha256=runner_binding["source_sha256"],
            expected_byte_length=manifest_runner["source_byte_length"],
            label="runner source",
        )
        module_source = Path(offline_runner.__file__).resolve(strict=True)
        runner_callable = offline_runner.run_offline_sweep
        if (
            module_source != runner_source
            or offline_runner.__name__ != RUNNER_MODULE
            or not callable(runner_callable)
            or getattr(runner_callable, "__module__", None) != RUNNER_MODULE
        ):
            raise ExecutionRunnerAdapterError(
                "loaded runner module/callable differs from the dispatch-bound source"
            )

        artifact_paths: dict[str, Path] = {}
        for name in ("strategy_spec", "variant_manifest", "sweep_plan"):
            binding = dispatch["artifact_bindings"][name]
            _, artifact_paths[name] = _read_bound_json(
                root,
                leases=leases,
                path=binding["path"],
                expected_sha256=binding["sha256"],
                label=name.replace("_", " "),
            )

        funding_binding = manifest["funding"]
        funding_payload, funding_path = _read_bound_json(
            root,
            leases=leases,
            path=funding_binding["provenance_artifact_path"],
            expected_sha256=funding_binding["provenance_artifact_sha256"],
            expected_byte_length=funding_binding["provenance_artifact_byte_length"],
            label="funding provenance",
        )
        if (
            funding_payload.get("file_identity", {}).get("source_data_path")
            != funding_binding["funding_data_path"]
        ):
            raise ExecutionRunnerAdapterError(
                "funding provenance source path differs from manifest"
            )
        funding_data = _repo_path(root, funding_binding["funding_data_path"], "funding data")
        leases.acquire(
            funding_data,
            expected_sha256=funding_binding["funding_data_sha256"],
            expected_byte_length=funding_binding["funding_data_byte_length"],
            label="funding data",
        )

        dataset_binding = manifest["dataset"]
        dispatch_dataset = dispatch["dataset_binding"]
        if (
            dataset_binding["data_path"] != dispatch_dataset["path"]
            or dataset_binding["data_sha256"] != dispatch_dataset["sha256"]
        ):
            raise ExecutionRunnerAdapterError("manifest/dispatch dataset hash mismatch")
        catalog, catalog_path = _read_bound_json(
            root,
            leases=leases,
            path=dataset_binding["catalog_path"],
            expected_sha256=dataset_binding["catalog_sha256"],
            expected_byte_length=dataset_binding["catalog_byte_length"],
            label="dataset catalog",
        )
        if catalog.get("path") != dataset_binding["data_path"]:
            raise ExecutionRunnerAdapterError("dataset catalog source path differs from manifest")
        dataset_path = _repo_path(root, dataset_binding["data_path"], "dispatch dataset")
        leases.acquire(
            dataset_path,
            expected_sha256=dataset_binding["data_sha256"],
            expected_byte_length=dataset_binding["data_byte_length"],
            label="dispatch dataset",
        )
        validator_path = _repo_path(root, dataset_binding["validator_path"], "dataset validator")
        leases.acquire(
            validator_path,
            expected_sha256=dataset_binding["validator_sha256"],
            expected_byte_length=dataset_binding["validator_byte_length"],
            label="dataset validator",
        )

        if (
            Path(offline_runner.DEFAULT_1D_CATALOG_SLICE_PATH).resolve(strict=True) != catalog_path
            or Path(offline_runner.DEFAULT_1D_VALIDATOR_PATH).resolve(strict=True) != validator_path
            or "sha256:" + offline_runner.OFFICIAL_1D_CATALOG_ARTIFACT_SHA256
            != dataset_binding["catalog_sha256"]
            or "sha256:" + offline_runner.OFFICIAL_1D_SOURCE_SHA256
            != dataset_binding["data_sha256"]
            or offline_runner.OFFICIAL_1D_SOURCE_BYTE_LENGTH != dataset_binding["data_byte_length"]
        ):
            raise ExecutionRunnerAdapterError(
                "loaded runner canonical dataset binding differs from dispatch manifest"
            )

        expected_funding = offline_runner.CANONICAL_FUNDING_EXPECTED_IDENTITY
        if any(
            expected_funding[field] != funding_binding[manifest_field]
            for field, manifest_field in (
                ("provenance_artifact_path", "provenance_artifact_path"),
                ("provenance_artifact_sha256", "provenance_artifact_sha256"),
                ("funding_parquet_path", "funding_data_path"),
                ("funding_parquet_sha256", "funding_data_sha256"),
                ("funding_parquet_byte_length", "funding_data_byte_length"),
            )
        ):
            raise ExecutionRunnerAdapterError(
                "loaded runner canonical funding binding differs from dispatch manifest"
            )

        return _RunnerRequest(
            repo_root=root,
            strategy_spec_path=artifact_paths["strategy_spec"],
            variant_manifest_path=artifact_paths["variant_manifest"],
            sweep_plan_path=artifact_paths["sweep_plan"],
            funding_provenance_path=funding_path,
            deterministic_seed=dispatch["execution_parameters"]["seed"],
            max_workers=dispatch["execution_parameters"]["workers"],
            run_label=dispatch["run_binding"]["run_id"],
            runner_callable=runner_callable,
            input_leases=leases.detach(),
        )
    except BaseException:
        leases.close()
        raise


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
    return request.runner_callable(
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
        request = _prepare_runner_request(
            root,
            dispatch,
            dispatch_path=dispatch_path,
            reviewed_dispatch_whole_file_sha256=reviewed_dispatch_whole_file_sha256,
        )
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
        try:
            runner_result = _invoke_existing_runner(
                request,
                on_process_started=mark_process_started,
            )
        finally:
            if isinstance(request, _RunnerRequest):
                request.close_input_leases()
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
