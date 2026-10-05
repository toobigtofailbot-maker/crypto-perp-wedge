"""Bounded Prefect orchestration for the local JSON parameter-sweep consumer."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Final, Mapping, Sequence

from prefect import flow
from prefect.runner.storage import LocalStorage

from tools.research_automation.local_json_sweep_spec_loader import (
    run_local_json_parameter_sweep,
)
from tools.research_automation.local_parameter_sweep import DEFAULT_MAX_POINT_COUNT
from tools.research_storage.workspace import resolve_workspace_path


FLOW_NAME: Final = "cpw-local-json-sweep"
DEPLOYMENT_NAME: Final = "cpw-local-json-sweep-v1"
WORK_POOL_NAME: Final = "cpw-research-local-process"
RUN_NAMESPACE: Final = "prefect/local-json-sweep"

_ENTRYPOINT: Final = (
    "tools/prefect_integration/local_json_sweep_consumer.py:local_json_sweep_consumer"
)
_FULL_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


class LocalJsonSweepConsumerError(RuntimeError):
    """Operational failure of the bounded Prefect consumer wrapper."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_run_root(repo_root: Path, consumer_run_id: str) -> Path:
    if "/" in consumer_run_id or "\\" in consumer_run_id:
        raise ValueError("consumer_run_id must be one safe path component")
    return resolve_workspace_path(
        repo_root=repo_root,
        storage_class="active",
        namespace=RUN_NAMESPACE,
        artifact_path=consumer_run_id,
    )


def _prepare_fresh_run_namespace(repo_root: Path, consumer_run_id: str) -> tuple[Path, Path]:
    run_root = _resolve_run_root(repo_root, consumer_run_id)
    if run_root.exists():
        if not run_root.is_dir():
            raise LocalJsonSweepConsumerError(
                "consumer run namespace exists and is not a directory"
            )
        if any(run_root.iterdir()):
            raise LocalJsonSweepConsumerError("consumer run namespace is not empty")
    else:
        resolve_workspace_path(
            repo_root=repo_root,
            storage_class="active",
            namespace=RUN_NAMESPACE,
            artifact_path=consumer_run_id,
            create_parent=True,
        )
        run_root.mkdir()

    sweep_output = run_root / "sweep-output"
    registry_output = run_root / "registry-output"
    sweep_output.mkdir()
    registry_output.mkdir()
    return sweep_output, registry_output


def _resolve_spec(repo_root: Path, spec_namespace: str, spec_artifact_path: str) -> Path:
    spec_path = resolve_workspace_path(
        repo_root=repo_root,
        storage_class="active",
        namespace=spec_namespace,
        artifact_path=spec_artifact_path,
    )
    if not spec_path.is_file():
        raise LocalJsonSweepConsumerError("resolved spec path must be an existing regular file")
    return spec_path


def _existing_file(path: Any, *, root: Path | None = None) -> Path:
    candidate = path if isinstance(path, Path) else Path(str(path))
    if root is not None and not candidate.is_absolute():
        candidate = root / candidate
    if not candidate.is_file():
        raise LocalJsonSweepConsumerError(f"required consumer artifact is missing: {candidate}")
    return candidate


def _validate_success_result(result: Any, sweep_output: Path, registry_output: Path) -> Any:
    failures = tuple(str(reason) for reason in getattr(result, "failure_reasons", ()))
    if failures:
        raise LocalJsonSweepConsumerError("local JSON sweep failed: " + "; ".join(failures))
    if not bool(getattr(result, "protected_boundary_preserved", False)):
        raise LocalJsonSweepConsumerError(
            "local JSON sweep did not preserve the protected boundary"
        )
    for field_name, expected in (
        ("local_only", True),
        ("research_only", True),
        ("non_authoritative", True),
        ("creates_committed_evidence", False),
    ):
        if getattr(result, field_name, None) is not expected:
            raise LocalJsonSweepConsumerError(f"local JSON sweep returned invalid {field_name}")

    sweep_result = getattr(result, "sweep_result", None)
    if sweep_result is None:
        raise LocalJsonSweepConsumerError("local JSON sweep returned no sweep_result")
    summary = getattr(sweep_result, "summary", None)
    if summary is None:
        raise LocalJsonSweepConsumerError("local JSON sweep returned no final sweep summary")

    _existing_file(getattr(sweep_result, "summary_file", ""))
    batch_result = getattr(sweep_result, "batch_result", None)
    registry_result = getattr(sweep_result, "registry_result", None)
    if batch_result is None or registry_result is None:
        raise LocalJsonSweepConsumerError("local JSON sweep returned incomplete success results")

    manifest_result = getattr(batch_result, "manifest_result", None)
    for path in getattr(manifest_result, "written_files", {}).values():
        _existing_file(path, root=sweep_output)
    for path in getattr(batch_result, "written_files", {}).values():
        _existing_file(path, root=sweep_output)
    for item in getattr(getattr(batch_result, "summary", None), "item_results", ()):
        for path in getattr(item, "dry_run_written_files", {}).values():
            _existing_file(path, root=sweep_output)
    for path in getattr(registry_result, "written_files", {}).values():
        _existing_file(path, root=registry_output)
    _existing_file(getattr(registry_result, "registry_file", ""))
    return sweep_result


def _repo_relative(repo_root: Path, path: str | Path) -> str:
    return Path(path).resolve().relative_to(repo_root.resolve()).as_posix()


@flow(name=FLOW_NAME, retries=0, persist_result=False)
def local_json_sweep_consumer(
    spec_namespace: str,
    spec_artifact_path: str,
    consumer_run_id: str,
    max_point_count: int = DEFAULT_MAX_POINT_COUNT,
) -> Mapping[str, Any]:
    """Run one human-triggered, contained local JSON parameter sweep."""

    repo_root = _repo_root()
    spec_path = _resolve_spec(repo_root, spec_namespace, spec_artifact_path)
    sweep_output, registry_output = _prepare_fresh_run_namespace(repo_root, consumer_run_id)
    result = run_local_json_parameter_sweep(
        spec_path,
        sweep_output,
        registry_output,
        max_point_count=max_point_count,
    )
    sweep_result = _validate_success_result(result, sweep_output, registry_output)
    summary = sweep_result.summary
    return {
        "consumer_run_id": consumer_run_id,
        "sweep_id": summary.sweep_id,
        "point_count": summary.point_count,
        "success_point_count": summary.success_point_count,
        "failed_point_count": summary.failed_point_count,
        "blocked_point_count": summary.blocked_point_count,
        "skipped_point_count": summary.skipped_point_count,
        "sweep_summary_path": _repo_relative(repo_root, sweep_result.summary_file),
        "registry_path": _repo_relative(
            repo_root, sweep_result.registry_result.registry_file
        ),
        "local_only": True,
        "research_only": True,
        "non_authoritative": True,
        "creates_committed_evidence": False,
    }


def register_local_json_sweep_deployment(*, repo_root: str | Path, version: str) -> Any:
    """Register the one deployment from an explicit local worktree source."""

    source_root = Path(repo_root).resolve(strict=True)
    module_root = _repo_root().resolve(strict=True)
    if source_root != module_root:
        raise ValueError("repo_root must be the worktree containing this installed module")
    if not _FULL_GIT_SHA.fullmatch(version):
        raise ValueError("version must be an exact lowercase 40-character git commit SHA")
    sourced_flow = type(local_json_sweep_consumer).from_source(
        source=LocalStorage(str(source_root)),
        entrypoint=_ENTRYPOINT,
    )
    return sourced_flow.deploy(
        name=DEPLOYMENT_NAME,
        work_pool_name=WORK_POOL_NAME,
        version=version,
        build=False,
        push=False,
        paused=False,
        schedules=[],
        triggers=[],
        print_next_steps=False,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Register the bounded CPW local JSON-sweep deployment"
    )
    parser.add_argument("register", choices=("register",))
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--version", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    deployment_id = register_local_json_sweep_deployment(
        repo_root=args.repo_root,
        version=args.version,
    )
    print(f"registered {FLOW_NAME}/{DEPLOYMENT_NAME} ({deployment_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
