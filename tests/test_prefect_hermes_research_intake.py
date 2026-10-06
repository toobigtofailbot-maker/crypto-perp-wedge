from __future__ import annotations

import ast
import inspect
import json
import sqlite3
import subprocess
from pathlib import Path

import prefect
import pytest

import tools.prefect_integration.hermes_research_intake as intake_module
from tools.mcp.project_evidence.research_intent import (
    INTENT_SCHEMA_VERSION,
    REQUEST_SCHEMA_VERSION,
    BoundedResearchIntentV1,
    semantic_content_sha256,
)
from tools.prefect_integration.hermes_research_intake import (
    DEPLOYMENT_NAME,
    FLOW_NAME,
    TASK_NAME,
    WORK_POOL_NAME,
    HermesResearchIntakeError,
    _cross_check,
    _parse_single_json_object,
    build_hermes_prompt,
    hermes_research_intake,
    invoke_hermes_once,
    register_hermes_research_intake_deployment,
)
from tools.research_memory.fingerprint import (
    DEFAULT_INSTRUMENT_SCOPE,
    FINGERPRINT_VERSION,
    HypothesisDefinition,
    fingerprint,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _request(**updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "request_id": "REQ-HERMES-02-1",
        "research_question": "Can completed-bar breakout pressure persist out of sample?",
        "strategy_family": "breakout momentum",
        "mechanism": "price expansion after compressed ranges",
        "primary_timeframe": "1h",
        "required_data_features": ["ohlcv", "donchian"],
        "free_parameter_count": 2,
        "evidence_resource_uris": ["project://status"],
        "constraints": ["Use completed bars only"],
    }
    value.update(updates)
    return value


def _intent(repo_sha: str, **updates: object) -> dict[str, object]:
    definition = HypothesisDefinition.from_mapping(
        {
            "strategy_family": "breakout momentum",
            "mechanism": "price expansion after compressed ranges",
            "primary_timeframe": "1h",
            "required_data_features": ["ohlcv", "donchian"],
            "free_parameter_count": 2,
            "instrument_scope": DEFAULT_INSTRUMENT_SCOPE,
        }
    )
    value: dict[str, object] = {
        "schema_version": INTENT_SCHEMA_VERSION,
        "request_id": "REQ-HERMES-02-1",
        "repo_sha": repo_sha,
        "content_sha256": "sha256:" + "0" * 64,
        **definition.canonical_mapping(),
        "fingerprint_sha256": fingerprint(definition),
        "research_question": "Can completed-bar breakout pressure persist out of sample?",
        "causal_rationale": "Range expansion may reflect persistent information arrival.",
        "falsifiable_prediction": "OOS expectancy is positive after costs.",
        "falsification_stop_conditions": ["Stop if the preregistered OOS gate fails"],
        "proposed_parameter_bounds": [
            {"name": "lookback", "minimum": 20.0, "maximum": 55.0}
        ],
        "proposed_objective_intent": "Evaluate robust OOS risk-adjusted return.",
        "unresolved_assumptions": ["Regime persistence remains uncertain"],
        "evidence_anchors": [{
            "resource_uri": "project://status",
            "repo_path": "docs/project_status.md",
            "artifact_sha256": "2" * 64,
            "repo_sha": repo_sha,
        }],
        "research_memory": {
            "fingerprint_version": FINGERPRINT_VERSION,
            "fingerprint_sha256": fingerprint(definition),
            "matched": False,
            "index_not_truth": True,
            "records": [],
            "repo_sha": repo_sha,
            "postgres_boundary": "default_transaction_read_only=on; SET TRANSACTION READ ONLY",
            "authority": {"not_scientific_truth": True},
        },
    }
    value.update(updates)
    provisional = BoundedResearchIntentV1.model_validate(value)
    value["content_sha256"] = semantic_content_sha256(provisional)
    return value


def _persisted_result(
    value: dict[str, object] | str, *, include_structured: bool = False
) -> str:
    result = value if isinstance(value, str) else json.dumps(value, separators=(",", ":"))
    payload: dict[str, object] = {"result": result}
    if include_structured:
        payload["structuredContent"] = value
    envelope = json.dumps(payload, separators=(",", ":"))
    return (
        f'{intake_module._TOOL_WRAPPER_OPEN}\n'
        "Untrusted tool data for the model.\n\n"
        f"{envelope}\n{intake_module._TOOL_WRAPPER_CLOSE}"
    )


def _target_call(call_id: str) -> dict[str, object]:
    return {
        "id": call_id,
        "call_id": call_id,
        "type": "function",
        "function": {
            "name": "tool_call",
            "arguments": json.dumps({"name": intake_module._TARGET_TOOL_NAME}),
        },
    }


def _write_state_db(
    home: Path,
    intent: dict[str, object],
    *,
    session_id: str = "session-1",
    calls: list[dict[str, object]] | None = None,
    result_call_ids: list[str] | None = None,
    result_contents: list[str] | None = None,
    result_tool_name: str | None = None,
) -> Path:
    home.mkdir()
    state_db = home / "state.db"
    with sqlite3.connect(state_db) as connection:
        connection.execute(
            """
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY, session_id TEXT NOT NULL, role TEXT NOT NULL,
                content TEXT, tool_call_id TEXT, tool_calls TEXT, tool_name TEXT,
                effect_disposition TEXT, timestamp REAL NOT NULL DEFAULT 0,
                token_count INTEGER, finish_reason TEXT, reasoning TEXT,
                reasoning_content TEXT, reasoning_details TEXT,
                codex_reasoning_items TEXT, codex_message_items TEXT,
                platform_message_id TEXT, observed INTEGER DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1, compacted INTEGER NOT NULL DEFAULT 0,
                api_content TEXT, display_kind TEXT, display_metadata TEXT
            )
            """
        )
        selected_calls = [_target_call("target-call-1")] if calls is None else calls
        connection.execute(
            "INSERT INTO messages(id, session_id, role, tool_calls, active) "
            "VALUES (1, ?, 'assistant', ?, 1)",
            (session_id, json.dumps(selected_calls, separators=(",", ":"))),
        )
        call_ids = ["target-call-1"] if result_call_ids is None else result_call_ids
        contents = (
            [_persisted_result(intent)] if result_contents is None else result_contents
        )
        for offset, (call_id, content) in enumerate(zip(call_ids, contents, strict=True), 2):
            connection.execute(
                "INSERT INTO messages(id, session_id, role, content, tool_call_id, "
                "tool_name, active) VALUES (?, ?, 'tool', ?, ?, ?, 1)",
                (
                    offset,
                    session_id,
                    content,
                    call_id,
                    result_tool_name or intake_module._TARGET_TOOL_NAME,
                ),
            )
    return state_db


def test_prefect_static_contract_and_prompt_are_exact() -> None:
    assert prefect.__version__ == "3.8.6"
    assert FLOW_NAME == "cpw-hermes-research-intake"
    assert DEPLOYMENT_NAME == "cpw-hermes-research-intake-v1"
    assert WORK_POOL_NAME == "cpw-research-local-process"
    assert TASK_NAME == "cpw-hermes-one-shot"
    assert hermes_research_intake.name == FLOW_NAME
    assert hermes_research_intake.retries == 0
    assert hermes_research_intake.persist_result is False
    assert invoke_hermes_once.name == TASK_NAME
    assert invoke_hermes_once.retries == 0
    assert invoke_hermes_once.persist_result is False
    prompt = build_hermes_prompt(_request())
    for required in (
        "HERMES-02 01A", "REQ-HERMES-02-1", "project://status",
        "cpw_build_bounded_research_intent", "Project-Evidence only",
        "no Markdown fence", "stop before Search Governor", "no successor job",
    ):
        assert required in prompt


def test_registration_binds_source_version_pool_and_no_schedule(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class _Sourced:
        def deploy(self, **kwargs: object) -> str:
            captured.update(kwargs)
            return "deployment-id"

    class _FlowType:
        @classmethod
        def from_source(cls, **kwargs: object) -> _Sourced:
            captured.update(kwargs)
            return _Sourced()

    monkeypatch.setattr(intake_module, "_repo_root", lambda: REPO_ROOT)
    monkeypatch.setattr(intake_module, "LocalStorage", lambda path: ("local", path))
    monkeypatch.setattr(intake_module, "hermes_research_intake", object())
    monkeypatch.setattr(intake_module, "type", lambda _value: _FlowType, raising=False)
    assert register_hermes_research_intake_deployment(
        repo_root=REPO_ROOT, version="a" * 40
    ) == "deployment-id"
    assert captured["name"] == DEPLOYMENT_NAME
    assert captured["work_pool_name"] == WORK_POOL_NAME
    assert captured["version"] == "a" * 40
    assert captured["schedules"] == []
    assert captured["triggers"] == []


@pytest.mark.parametrize(
    "raw",
    [
        b"prose {}",
        b"```json\n{}\n```",
        b"{bad",
        b"[]",
        b'{} {}',
    ],
)
def test_persisted_json_requires_exactly_one_object(raw: bytes) -> None:
    with pytest.raises(HermesResearchIntakeError):
        _parse_single_json_object(raw)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update(request_id="substituted"),
        lambda value: value.update(repo_sha="3" * 40),
        lambda value: value.update(fingerprint_sha256="4" * 64),
        lambda value: value["evidence_anchors"][0].update(resource_uri="project://research-memory-index"),
        lambda value: value.update(approval_authority=True),
        lambda value: value.update(content_sha256="sha256:" + "5" * 64),
        lambda value: value.update(broker_authority=False),
    ],
)
def test_host_cross_check_rejects_substitution_and_widening(mutation: object) -> None:
    repo_sha = "1" * 40
    value = _intent(repo_sha)
    mutation(value)  # type: ignore[operator]
    with pytest.raises((HermesResearchIntakeError, ValueError)):
        _cross_check(value, intake_module.BoundedResearchRequestV1.model_validate(_request()), expected_repo_sha=repo_sha)


def test_fixed_subprocess_vector_success_and_session_hash_exclusion(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    repo_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    hermes_home = tmp_path / "hermes-home"
    _write_state_db(hermes_home, _intent(repo_sha))
    for name, value in {
        "HERMES_PROJECT_HOME": str(hermes_home),
        "HERMES_PROPOSAL_OUTBOX_HOST": str(REPO_ROOT / "scratch/hermes_proposal_outbox"),
        "HERMES_MODEL": "test/model",
        "PROJECT_REPO_SHA": repo_sha,
        "PROJECT_REPO_BRANCH": "test",
        "RESEARCH_MEMORY_READONLY_DSN": "postgresql://redacted/test",
    }.items():
        monkeypatch.setenv(name, value)
    captured: dict[str, object] = {}
    monkeypatch.setattr(intake_module, "_repo_head", lambda _root: repo_sha)

    class _Process:
        returncode = 0

        def communicate(self, timeout: int | None = None) -> tuple[bytes, bytes]:
            captured["timeout"] = timeout
            return b"altered model-authored diagnostic prose", b"session_id: session-1\n"

        def kill(self) -> None:
            captured["killed"] = True

    def _popen(command: list[str], **kwargs: object) -> _Process:
        captured["command"] = command
        captured.update(kwargs)
        return _Process()

    monkeypatch.setattr(intake_module.subprocess, "Popen", _popen)
    result = invoke_hermes_once.fn(_request())
    command = captured["command"]
    assert command[:2] == ["docker", "compose"]
    assert command[4:9] == ["exec", "-T", "hermes", "/opt/hermes/hermes", "chat"]
    assert command[-3:] == ["--quiet", "--source", "tool"]
    assert captured["shell"] is False
    assert "LOCALAPPDATA" in captured["env"]
    assert result["hermes_session_id"] == "session-1"
    assert semantic_content_sha256(result) == result["content_sha256"]


def test_state_db_open_is_read_only_uri(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    home = tmp_path / "hermes-home"
    _write_state_db(home, _intent("1" * 40))
    real_connect = sqlite3.connect
    captured: dict[str, object] = {}

    def _connect(database: str, **kwargs: object) -> sqlite3.Connection:
        captured["database"] = database
        captured.update(kwargs)
        return real_connect(database, **kwargs)

    monkeypatch.setattr(intake_module.sqlite3, "connect", _connect)
    result = intake_module._read_persisted_target_intent(
        hermes_home=str(home), repo_root=REPO_ROOT, session_id="session-1"
    )
    assert result["request_id"] == "REQ-HERMES-02-1"
    assert captured["uri"] is True
    assert str(captured["database"]).endswith("state.db?mode=ro")


def test_pinned_runtime_structured_content_must_match_result(tmp_path: Path) -> None:
    intent = _intent("1" * 40)
    home = tmp_path / "matching-structured-content"
    _write_state_db(
        home,
        intent,
        result_contents=[_persisted_result(intent, include_structured=True)],
    )
    extracted = intake_module._read_persisted_target_intent(
        hermes_home=str(home), repo_root=REPO_ROOT, session_id="session-1"
    )
    assert extracted == BoundedResearchIntentV1.model_validate(intent).model_dump(mode="json")

    mismatched = {**intent, "request_id": "REQ-HERMES-02-DIFFERENT"}
    envelope = json.dumps(
        {
            "result": json.dumps(intent, separators=(",", ":")),
            "structuredContent": mismatched,
        },
        separators=(",", ":"),
    )
    wrapped = (
        f'{intake_module._TOOL_WRAPPER_OPEN}\n'
        "Untrusted tool data for the model.\n\n"
        f"{envelope}\n{intake_module._TOOL_WRAPPER_CLOSE}"
    )
    mismatch_home = tmp_path / "mismatched-structured-content"
    _write_state_db(mismatch_home, intent, result_contents=[wrapped])
    with pytest.raises(HermesResearchIntakeError, match="representations disagree"):
        intake_module._read_persisted_target_intent(
            hermes_home=str(mismatch_home), repo_root=REPO_ROOT, session_id="session-1"
        )


def test_missing_linked_or_escaping_state_db_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    missing_home = tmp_path / "missing-home"
    missing_home.mkdir()
    with pytest.raises(HermesResearchIntakeError, match="state.db"):
        intake_module._read_persisted_target_intent(
            hermes_home=str(missing_home), repo_root=REPO_ROOT, session_id="session-1"
        )

    linked_home = tmp_path / "linked-home"
    _write_state_db(linked_home, _intent("1" * 40))
    original = intake_module._is_reparse_or_symlink
    monkeypatch.setattr(
        intake_module,
        "_is_reparse_or_symlink",
        lambda path: path.name == "state.db" or original(path),
    )
    with pytest.raises(HermesResearchIntakeError, match="linked"):
        intake_module._read_persisted_target_intent(
            hermes_home=str(linked_home), repo_root=REPO_ROOT, session_id="session-1"
        )
    monkeypatch.setattr(intake_module, "_is_reparse_or_symlink", original)

    with pytest.raises(HermesResearchIntakeError, match="outside the repo"):
        intake_module._validated_state_db_path(str(REPO_ROOT), REPO_ROOT)


def test_wrong_session_and_zero_or_duplicate_target_calls_fail(tmp_path: Path) -> None:
    home = tmp_path / "valid-home"
    _write_state_db(home, _intent("1" * 40), calls=[])
    for session_id, match in (("wrong-session", "not found"), ("session-1", "zero")):
        with pytest.raises(HermesResearchIntakeError, match=match):
            intake_module._read_persisted_target_intent(
                hermes_home=str(home), repo_root=REPO_ROOT, session_id=session_id
            )

    duplicate_home = tmp_path / "duplicate-home"
    _write_state_db(
        duplicate_home,
        _intent("1" * 40),
        calls=[_target_call("call-1"), _target_call("call-2")],
    )
    with pytest.raises(HermesResearchIntakeError, match="multiple"):
        intake_module._read_persisted_target_intent(
            hermes_home=str(duplicate_home), repo_root=REPO_ROOT, session_id="session-1"
        )


@pytest.mark.parametrize(
    ("result_call_ids", "result_contents", "result_tool_name", "match"),
    [
        ([], [], None, "zero linked"),
        (["target-call-1", "target-call-1"], None, None, "multiple linked"),
        (["different-call"], None, None, "zero linked"),
        (["target-call-1"], None, "different-tool", "zero linked"),
        (["target-call-1"], ["not-json"], None, "wrapper"),
    ],
)
def test_linked_result_must_be_unique_exact_and_well_formed(
    tmp_path: Path,
    result_call_ids: list[str],
    result_contents: list[str] | None,
    result_tool_name: str | None,
    match: str,
) -> None:
    home = tmp_path / ("home-" + match.replace(" ", "-"))
    contents = result_contents
    if contents is None:
        contents = [_persisted_result(_intent("1" * 40)) for _ in result_call_ids]
    _write_state_db(
        home,
        _intent("1" * 40),
        result_call_ids=result_call_ids,
        result_contents=contents,
        result_tool_name=result_tool_name,
    )
    with pytest.raises(HermesResearchIntakeError, match=match):
        intake_module._read_persisted_target_intent(
            hermes_home=str(home), repo_root=REPO_ROOT, session_id="session-1"
        )


def test_invalid_intent_and_host_identity_or_hash_mismatch_fail(tmp_path: Path) -> None:
    invalid_home = tmp_path / "invalid-home"
    _write_state_db(invalid_home, _intent("1" * 40), result_contents=[_persisted_result({})])
    with pytest.raises(HermesResearchIntakeError, match="strict bounded intent"):
        intake_module._read_persisted_target_intent(
            hermes_home=str(invalid_home), repo_root=REPO_ROOT, session_id="session-1"
        )

    request = intake_module.BoundedResearchRequestV1.model_validate(_request())
    for index, mutation in enumerate(
        (
            {"content_sha256": "sha256:" + "5" * 64},
            {"repo_sha": "2" * 40},
            {"fingerprint_sha256": "3" * 64},
            {"evidence_anchors": [{
                **_intent("1" * 40)["evidence_anchors"][0],
                "resource_uri": "project://research-memory-index",
            }]},
        )
    ):
        home = tmp_path / f"mismatch-{index}"
        value = _intent("1" * 40)
        value.update(mutation)
        _write_state_db(home, value)
        extracted = intake_module._read_persisted_target_intent(
            hermes_home=str(home), repo_root=REPO_ROOT, session_id="session-1"
        )
        with pytest.raises(HermesResearchIntakeError):
            _cross_check(extracted, request, expected_repo_sha="1" * 40)


def test_final_stdout_cannot_replace_missing_persisted_result(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    repo_sha = "1" * 40
    home = tmp_path / "hermes-home"
    _write_state_db(home, _intent(repo_sha), result_call_ids=[], result_contents=[])
    monkeypatch.setattr(intake_module, "_repo_head", lambda _root: repo_sha)
    monkeypatch.setattr(intake_module, "_repo_root", lambda: REPO_ROOT)
    for name, value in {
        "HERMES_PROJECT_HOME": str(home),
        "HERMES_PROPOSAL_OUTBOX_HOST": str(tmp_path / "outbox"),
        "HERMES_MODEL": "test/model",
        "PROJECT_REPO_SHA": repo_sha,
        "PROJECT_REPO_BRANCH": "test",
        "RESEARCH_MEMORY_READONLY_DSN": "postgresql://redacted/test",
    }.items():
        monkeypatch.setenv(name, value)

    class _Process:
        returncode = 0

        def communicate(self, timeout: int | None = None) -> tuple[bytes, bytes]:
            return json.dumps(_intent(repo_sha)).encode(), b"session_id: session-1\n"

        def kill(self) -> None:
            raise AssertionError("kill should not be called")

    monkeypatch.setattr(intake_module.subprocess, "Popen", lambda *_a, **_k: _Process())
    with pytest.raises(HermesResearchIntakeError, match="zero linked"):
        invoke_hermes_once.fn(_request())


def test_extractor_is_select_only_and_adds_no_second_effect_surface() -> None:
    extractor_source = inspect.getsource(intake_module._read_persisted_target_intent)
    module_source = inspect.getsource(intake_module)
    assert "mode=ro" in extractor_source
    assert "SELECT " in extractor_source
    for forbidden_sql in ("INSERT ", "UPDATE ", "DELETE ", "CREATE ", "ALTER ", "DROP "):
        assert forbidden_sql not in extractor_source
    assert "SessionDB" not in module_source
    assert module_source.count("subprocess.Popen(") == 1
    for forbidden_surface in ("requests.", "httpx.", "urlopen(", "handoff_file", "queue.put"):
        assert forbidden_surface not in module_source


def test_timeout_kills_child(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(intake_module, "_bounded_environment", lambda _root: {"PROJECT_REPO_SHA": "1" * 40})
    killed = {"value": False}

    class _Process:
        returncode = None
        calls = 0

        def communicate(self, timeout: int | None = None) -> tuple[bytes, bytes]:
            self.calls += 1
            if self.calls == 1:
                raise subprocess.TimeoutExpired("docker", timeout)
            return b"", b""

        def kill(self) -> None:
            killed["value"] = True

    monkeypatch.setattr(intake_module.subprocess, "Popen", lambda *_args, **_kwargs: _Process())
    with pytest.raises(HermesResearchIntakeError, match="timeout"):
        invoke_hermes_once.fn(_request())
    assert killed["value"] is True


def test_forbidden_coupling_and_no_schedule_definition() -> None:
    source = (REPO_ROOT / "tools/prefect_integration/hermes_research_intake.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    forbidden = (
        "optuna", "tools.research_search", "tools.research_runner", "tools.canon_intake",
        "tools.hermes.prepare", "tools.hermes.proposals", "src.runtime", "src.execution",
    )
    assert not [name for name in imports if name.startswith(forbidden)]
    assert "shell=True" not in source
    assert "CronSchedule" not in source
    assert "HERMES-PREP" not in source
    assert ".prepared.json" not in source
    assert ".proposal.json" not in source
