"""Manual Prefect handoff for one fixed-command bounded Hermes research turn."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import stat
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
MAX_TOOL_RESULT_BYTES: Final = 1_000_000
_ENTRYPOINT: Final = (
    "tools/prefect_integration/hermes_research_intake.py:hermes_research_intake"
)
_FULL_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_SESSION_LINE = re.compile(r"^session_id: ([A-Za-z0-9][A-Za-z0-9._:-]{0,127})$")
_TARGET_TOOL_NAME: Final = (
    "mcp__project_evidence__cpw_build_bounded_research_intent"
)
_TOOL_WRAPPER_OPEN: Final = (
    f'<untrusted_tool_result source="{_TARGET_TOOL_NAME}">'
)
_TOOL_WRAPPER_CLOSE: Final = "</untrusted_tool_result>"
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
    "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "ProgramData",
    "ProgramFiles", "ProgramFiles(x86)", "ProgramW6432", "CommonProgramFiles",
    "CommonProgramFiles(x86)", "CommonProgramW6432", "DOCKER_HOST",
    "DOCKER_CONTEXT", "DOCKER_CONFIG", "DOCKER_CLI_PLUGIN_EXTRA_DIRS",
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


def _parse_single_json_object(raw: bytes) -> dict[str, Any]:
    if len(raw) > MAX_TOOL_RESULT_BYTES:
        raise HermesResearchIntakeError("JSON payload exceeded the fixed byte limit")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HermesResearchIntakeError("JSON payload is not valid UTF-8") from exc
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HermesResearchIntakeError("payload is not exactly one JSON value") from exc
    if not isinstance(parsed, dict):
        raise HermesResearchIntakeError("JSON payload root must be an object")
    return parsed


def _is_reparse_or_symlink(path: Path) -> bool:
    metadata = path.lstat()
    file_attributes = getattr(metadata, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(file_attributes & reparse_flag)


def _validated_state_db_path(hermes_home_value: str, repo_root: Path) -> Path:
    raw_home = Path(hermes_home_value)
    try:
        if _is_reparse_or_symlink(raw_home):
            raise HermesResearchIntakeError("HERMES_PROJECT_HOME must not be linked")
        hermes_home = raw_home.resolve(strict=True)
        resolved_repo = repo_root.resolve(strict=True)
    except OSError as exc:
        raise HermesResearchIntakeError("HERMES_PROJECT_HOME is unavailable") from exc
    if hermes_home == resolved_repo or resolved_repo in hermes_home.parents:
        raise HermesResearchIntakeError("HERMES_PROJECT_HOME must remain outside the repo")

    state_db = raw_home / "state.db"
    try:
        if _is_reparse_or_symlink(state_db):
            raise HermesResearchIntakeError("Hermes state.db must not be linked")
        metadata = state_db.lstat()
        resolved_state_db = state_db.resolve(strict=True)
    except OSError as exc:
        raise HermesResearchIntakeError("Hermes state.db is unavailable") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise HermesResearchIntakeError("Hermes state.db must be a regular file")
    if resolved_state_db.parent != hermes_home:
        raise HermesResearchIntakeError("Hermes state.db escapes HERMES_PROJECT_HOME")
    return resolved_state_db


def _target_call_id(tool_calls_text: str) -> str | None:
    try:
        tool_calls = json.loads(tool_calls_text)
    except json.JSONDecodeError as exc:
        raise HermesResearchIntakeError("Hermes tool-call metadata is malformed") from exc
    if not isinstance(tool_calls, list):
        raise HermesResearchIntakeError("Hermes tool-call metadata must be a list")
    matches: list[str] = []
    for tool_call in tool_calls:
        if not isinstance(tool_call, dict):
            raise HermesResearchIntakeError("Hermes tool-call entry is malformed")
        function = tool_call.get("function")
        if not isinstance(function, dict):
            raise HermesResearchIntakeError("Hermes tool-call function is malformed")
        function_name = function.get("name")
        target_name: object = function_name
        if function_name == "tool_call":
            arguments_text = function.get("arguments")
            if not isinstance(arguments_text, str):
                raise HermesResearchIntakeError("Hermes tool-call arguments are malformed")
            try:
                arguments = json.loads(arguments_text)
            except json.JSONDecodeError as exc:
                raise HermesResearchIntakeError(
                    "Hermes tool-call arguments are malformed"
                ) from exc
            if not isinstance(arguments, dict):
                raise HermesResearchIntakeError("Hermes tool-call arguments are malformed")
            target_name = arguments.get("name")
        if target_name != _TARGET_TOOL_NAME:
            continue
        call_id = tool_call.get("call_id")
        legacy_id = tool_call.get("id")
        if not isinstance(call_id, str) or not call_id:
            raise HermesResearchIntakeError("target tool call has no exact call ID")
        if legacy_id is not None and legacy_id != call_id:
            raise HermesResearchIntakeError("target tool call IDs disagree")
        matches.append(call_id)
    if len(matches) > 1:
        raise HermesResearchIntakeError("target builder tool was called multiple times")
    return matches[0] if matches else None


def _intent_from_persisted_tool_content(content: str) -> dict[str, Any]:
    if not content or len(content.encode("utf-8")) > MAX_TOOL_RESULT_BYTES:
        raise HermesResearchIntakeError("persisted target tool result is empty or oversized")
    if not content.startswith(_TOOL_WRAPPER_OPEN + "\n") or not content.endswith(
        "\n" + _TOOL_WRAPPER_CLOSE
    ):
        raise HermesResearchIntakeError("persisted target tool result wrapper is invalid")
    body = content[len(_TOOL_WRAPPER_OPEN) + 1 : -len(_TOOL_WRAPPER_CLOSE) - 1]
    parts = body.split("\n\n", 1)
    if len(parts) != 2 or not parts[0]:
        raise HermesResearchIntakeError("persisted target tool result wrapper is invalid")
    envelope = _parse_single_json_object(parts[1].encode("utf-8"))
    if set(envelope) not in ({"result"}, {"result", "structuredContent"}):
        raise HermesResearchIntakeError("persisted target tool result envelope is invalid")
    if not isinstance(envelope["result"], str):
        raise HermesResearchIntakeError("persisted target tool result envelope is invalid")
    intent = _parse_single_json_object(envelope["result"].encode("utf-8"))
    if "structuredContent" in envelope and envelope["structuredContent"] != intent:
        raise HermesResearchIntakeError(
            "persisted target tool result representations disagree"
        )
    return intent


def _read_persisted_target_intent(
    *, hermes_home: str, repo_root: Path, session_id: str
) -> dict[str, Any]:
    state_db = _validated_state_db_path(hermes_home, repo_root)
    uri = state_db.as_uri() + "?mode=ro"
    try:
        with sqlite3.connect(uri, uri=True) as connection:
            rows = connection.execute(
                "SELECT id, role, content, tool_call_id, tool_calls, tool_name "
                "FROM messages WHERE session_id = ? AND active = 1 ORDER BY id",
                (session_id,),
            ).fetchall()
    except sqlite3.Error as exc:
        raise HermesResearchIntakeError("Hermes session state is unavailable") from exc
    if not rows:
        raise HermesResearchIntakeError("Hermes session was not found in read-only state")

    target_call_ids = [
        call_id
        for _id, role, _content, _tool_call_id, tool_calls, _tool_name in rows
        if role == "assistant" and isinstance(tool_calls, str)
        for call_id in [_target_call_id(tool_calls)]
        if call_id is not None
    ]
    if len(target_call_ids) != 1:
        qualifier = "multiple" if target_call_ids else "zero"
        raise HermesResearchIntakeError(
            f"Hermes session has {qualifier} target builder tool calls"
        )
    call_id = target_call_ids[0]
    results = [
        content
        for _id, role, content, result_call_id, _tool_calls, tool_name in rows
        if role == "tool"
        and result_call_id == call_id
        and tool_name == _TARGET_TOOL_NAME
    ]
    if len(results) != 1:
        qualifier = "multiple" if results else "zero"
        raise HermesResearchIntakeError(
            f"Hermes session has {qualifier} linked target tool results"
        )
    if not isinstance(results[0], str):
        raise HermesResearchIntakeError("persisted target tool result has no content")
    raw_intent = _intent_from_persisted_tool_content(results[0])
    try:
        return BoundedResearchIntentV1.model_validate(raw_intent).model_dump(mode="json")
    except ValueError as exc:
        raise HermesResearchIntakeError(
            "persisted target tool result is not a strict bounded intent"
        ) from exc


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
    if session_id is None:
        raise HermesResearchIntakeError("Hermes did not return one session identity")
    raw_intent = _read_persisted_target_intent(
        hermes_home=environment["HERMES_PROJECT_HOME"],
        repo_root=repo_root,
        session_id=session_id,
    )
    intent = _cross_check(
        raw_intent,
        validated,
        expected_repo_sha=environment["PROJECT_REPO_SHA"],
    )
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
