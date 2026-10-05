"""Manual Prefect handoff for one fixed-command bounded Hermes research turn."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from prefect import flow, task
from prefect.runner.storage import LocalStorage

from tools.mcp.project_evidence.research_intent import (
    BoundedResearchIntentV1,
    BoundedResearchRequestV1,
    semantic_content_sha256,
)
from tools.research_memory.fingerprint import (
    DEFAULT_INSTRUMENT_SCOPE,
    HypothesisDefinition,
    fingerprint,
)

FLOW_NAME: Final = "cpw-hermes-research-intake"
DEPLOYMENT_NAME: Final = "cpw-hermes-research-intake-v1"
WORK_POOL_NAME: Final = "cpw-research-local-process"
TASK_NAME: Final = "cpw-hermes-one-shot"

HERMES_TIMEOUT_SECONDS: Final = 300
MAX_STDOUT_BYTES: Final = 1_000_000
MAX_STDERR_BYTES: Final = 64_000
_ENTRYPOINT: Final = (
    "tools/prefect_integration/hermes_research_intake.py:hermes_research_intake"
)
_FULL_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_SESSION_LINE = re.compile(r"^session_id: ([A-Za-z0-9][A-Za-z0-9._:-]{0,127})$")
_REQUIRED_ENV = (
    "HERMES_PROJECT_HOME",
    "HERMES_PROPOSAL_OUTBOX_HOST",
    "HERMES_MODEL",
    "PROJECT_REPO_SHA",
    "PROJECT_REPO_BRANCH",
    "RESEARCH_MEMORY_READONLY_DSN",
)
_PASSTHROUGH_ENV = (
    "PATH", "SystemRoot", "SYSTEMROOT", "ComSpec", "COMSPEC", "TEMP", "TMP",
    "HOME", "USERPROFILE", "DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_CONFIG",
)


class HermesResearchIntakeError(RuntimeError):
    """Fail-closed operational error for the bounded Hermes handoff."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _repo_head(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, check=True,
        capture_output=True, text=True, timeout=10,
    )
    head = result.stdout.strip()
    if _FULL_GIT_SHA.fullmatch(head) is None:
        raise HermesResearchIntakeError("worktree HEAD is not an exact git SHA")
    return head


def build_hermes_prompt(request: BoundedResearchRequestV1 | Mapping[str, Any]) -> str:
    """Construct the code-owned HERMES-02 prompt; callers provide no prompt text."""

    validated = (
        request if isinstance(request, BoundedResearchRequestV1)
        else BoundedResearchRequestV1.model_validate(request)
    )
    payload = validated.model_dump(mode="json")
    return (
        "HERMES-02 01A bounded research-intake handoff. This is one manually "
        "triggered, non-authoritative turn and must stop before Search Governor, "
        "Optuna, any runner/backtest, canonical write, promotion, runtime, paper/live, "
        "or capital action. Use Project-Evidence only. Read the exact evidence resource "
        "URIs below, preserve every supplied request and hypothesis identity exactly, "
        "then provide bounded causal_rationale, falsifiable_prediction, "
        "falsification_stop_conditions, proposed_parameter_bounds, "
        "proposed_objective_intent, and unresolved_assumptions to "
        "cpw_build_bounded_research_intent. Call that tool exactly once. Return exactly "
        "the tool-produced final intent JSON: no Markdown fence and no prose outside the "
        "single JSON object; no successor job is created and no tool is enabled. "
        "Fixed request JSON follows:\n"
        + json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    )


def _bounded_environment(repo_root: Path) -> dict[str, str]:
    missing = [name for name in _REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        raise HermesResearchIntakeError(
            "required Hermes deployment environment is unavailable: " + ", ".join(missing)
        )
    expected_head = _repo_head(repo_root)
    if os.environ["PROJECT_REPO_SHA"] != expected_head:
        raise HermesResearchIntakeError("PROJECT_REPO_SHA does not match worktree HEAD")
    environment = {
        name: os.environ[name]
        for name in (*_PASSTHROUGH_ENV, *_REQUIRED_ENV)
        if name in os.environ
    }
    return environment


def _parse_single_json_object(stdout: bytes) -> dict[str, Any]:
    if len(stdout) > MAX_STDOUT_BYTES:
        raise HermesResearchIntakeError("Hermes stdout exceeded the fixed byte limit")
    try:
        text = stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HermesResearchIntakeError("Hermes stdout is not valid UTF-8") from exc
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HermesResearchIntakeError("Hermes stdout is not exactly one JSON value") from exc
    if not isinstance(parsed, dict):
        raise HermesResearchIntakeError("Hermes stdout JSON root must be an object")
    return parsed


def _session_id(stderr: bytes) -> str | None:
    if len(stderr) > MAX_STDERR_BYTES:
        raise HermesResearchIntakeError("Hermes stderr exceeded the fixed byte limit")
    try:
        lines = stderr.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise HermesResearchIntakeError("Hermes stderr is not valid UTF-8") from exc
    matches = [match.group(1) for line in lines if (match := _SESSION_LINE.fullmatch(line.strip()))]
    if len(matches) > 1:
        raise HermesResearchIntakeError("Hermes returned multiple session identities")
    return matches[0] if matches else None


def _cross_check(
    raw_intent: Mapping[str, Any],
    request: BoundedResearchRequestV1,
    *,
    expected_repo_sha: str,
) -> BoundedResearchIntentV1:
    intent = BoundedResearchIntentV1.model_validate(raw_intent)
    definition = HypothesisDefinition.from_mapping(
        {
            "strategy_family": request.strategy_family,
            "mechanism": request.mechanism,
            "primary_timeframe": request.primary_timeframe,
            "required_data_features": request.required_data_features,
            "free_parameter_count": request.free_parameter_count,
            "instrument_scope": DEFAULT_INSTRUMENT_SCOPE,
        }
    )
    expected = definition.canonical_mapping()
    comparisons = {
        "request_id": (intent.request_id, request.request_id),
        "research_question": (intent.research_question, request.research_question),
        "strategy_family": (intent.strategy_family, expected["strategy_family"]),
        "mechanism": (intent.mechanism, expected["mechanism"]),
        "primary_timeframe": (intent.primary_timeframe, expected["primary_timeframe"]),
        "required_data_features": (
            intent.required_data_features, expected["required_data_features"]
        ),
        "free_parameter_count": (
            intent.free_parameter_count, expected["free_parameter_count"]
        ),
        "instrument_scope": (intent.instrument_scope, DEFAULT_INSTRUMENT_SCOPE),
        "repo_sha": (intent.repo_sha, expected_repo_sha),
        "fingerprint_sha256": (intent.fingerprint_sha256, fingerprint(definition)),
        "evidence_resource_uris": (
            [anchor.resource_uri for anchor in intent.evidence_anchors],
            request.evidence_resource_uris,
        ),
    }
    mismatches = [name for name, (actual, wanted) in comparisons.items() if actual != wanted]
    if mismatches:
        raise HermesResearchIntakeError(
            "Hermes intent changed fixed request identity: " + ", ".join(mismatches)
        )
    if intent.research_memory.fingerprint_sha256 != intent.fingerprint_sha256:
        raise HermesResearchIntakeError("Research Memory fingerprint does not match intent")
    if intent.research_memory.repo_sha != expected_repo_sha:
        raise HermesResearchIntakeError("Research Memory repo SHA does not match intent")
    if semantic_content_sha256(intent) != intent.content_sha256:
        raise HermesResearchIntakeError("Hermes intent semantic content hash mismatch")
    return intent


@task(name=TASK_NAME, retries=0, persist_result=False, cache_policy=None)
def invoke_hermes_once(request: Mapping[str, Any]) -> dict[str, Any]:
    """Invoke exactly one fixed Hermes chat command and validate its result."""

    validated = BoundedResearchRequestV1.model_validate(request)
    repo_root = _repo_root()
    environment = _bounded_environment(repo_root)
    compose_file = repo_root / "tools" / "hermes" / "compose.yaml"
    command = [
        "docker", "compose", "-f", str(compose_file), "exec", "-T", "hermes",
        "/opt/hermes/hermes", "chat", "-q", build_hermes_prompt(validated),
        "--quiet", "--source", "tool",
    ]
    process = subprocess.Popen(
        command,
        cwd=repo_root,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    try:
        stdout, stderr = process.communicate(timeout=HERMES_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        process.kill()
        process.communicate()
        raise HermesResearchIntakeError("Hermes invocation exceeded the fixed timeout") from exc
    if len(stdout) > MAX_STDOUT_BYTES or len(stderr) > MAX_STDERR_BYTES:
        raise HermesResearchIntakeError("Hermes output exceeded a fixed byte limit")
    if process.returncode != 0:
        raise HermesResearchIntakeError(
            f"Hermes invocation failed with exit code {process.returncode}"
        )
    session_id = _session_id(stderr)
    intent = _cross_check(
        _parse_single_json_object(stdout),
        validated,
        expected_repo_sha=environment["PROJECT_REPO_SHA"],
    )
    if session_id is not None:
        intent = BoundedResearchIntentV1.model_validate(
            {**intent.model_dump(mode="json"), "hermes_session_id": session_id}
        )
        if semantic_content_sha256(intent) != intent.content_sha256:
            raise HermesResearchIntakeError("operational session identity changed semantic hash")
    return intent.model_dump(mode="json")


@flow(name=FLOW_NAME, retries=0, persist_result=False)
def hermes_research_intake(request: Mapping[str, Any]) -> dict[str, Any]:
    """Run one human-triggered bounded handoff and stop after host validation."""

    validated = BoundedResearchRequestV1.model_validate(request)
    intent = invoke_hermes_once(validated.model_dump(mode="json"))
    return {
        "intent": intent,
        "non_authoritative": True,
        "creates_committed_evidence": False,
        "canonical_write": False,
    }


def register_hermes_research_intake_deployment(
    *, repo_root: str | Path, version: str
) -> Any:
    """Register the manual deployment from this exact local worktree source."""

    source_root = Path(repo_root).resolve(strict=True)
    if source_root != _repo_root().resolve(strict=True):
        raise ValueError("repo_root must be the worktree containing this installed module")
    if _FULL_GIT_SHA.fullmatch(version) is None:
        raise ValueError("version must be an exact lowercase 40-character git commit SHA")
    sourced_flow = type(hermes_research_intake).from_source(
        source=LocalStorage(str(source_root)), entrypoint=_ENTRYPOINT
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
    parser = argparse.ArgumentParser(description="Register bounded Hermes research intake")
    parser.add_argument("register", choices=("register",))
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--version", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    deployment_id = register_hermes_research_intake_deployment(
        repo_root=args.repo_root, version=args.version
    )
    print(f"registered {FLOW_NAME}/{DEPLOYMENT_NAME} ({deployment_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
