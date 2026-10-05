from __future__ import annotations

import ast
import json
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
def test_stdout_requires_exactly_one_json_object(raw: bytes) -> None:
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
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    for name, value in {
        "HERMES_PROJECT_HOME": str(REPO_ROOT.parent / "hermes-home"),
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
            return json.dumps(_intent(repo_sha), separators=(",", ":")).encode(), b"session_id: session-1\n"

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
