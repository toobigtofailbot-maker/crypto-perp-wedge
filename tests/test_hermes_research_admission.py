"""All model receipts here are SYNTHETIC FIXTURES, never actual research."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from tools.hermes import research_admission as admission
from tools.mcp.project_evidence.domain_tools import CpwDomainTools, FormalizeStrategyDraftInput
from tools.mcp.project_evidence.models import RepoIdentity
from tools.mcp.project_evidence.resources import EvidenceResourceCatalog

REPO = Path(__file__).resolve().parents[1]
URIS = [
    "project://feature-availability",
    "project://indicator-catalog",
    "project://strategy-spec-template",
    "evidence://decision/DEC-0001",
    "evidence://decision/DEC-0002",
]


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _dump(value: object) -> bytes:
    return json.dumps(value).encode()


def _reasoned(features=None, timeframe="4h") -> dict:
    draft = {
        "summary": "SYNTHETIC FIXTURE: price trend test, not actual research",
        "causal_rationale": "Persistence is an unproven possibility.",
        "falsifiable_prediction": "A future held-out test may reject persistence.",
        "symbols": ["BTCUSDT"],
        "timeframe": timeframe,
        "features": features or ["sma", "ohlcv"],
        "entry_concept": "Completed close above/below trailing SMA(50); next open only.",
        "exit_concept": "Persist until relationship changes; flat warmup or invalid input.",
        "parameter_bounds": [{"name": "lookback", "minimum": 50.0, "maximum": 50.0}],
        "stop_conditions": ["No execution; uncertain costs, funding, holdout and prior history."],
    }
    if features == ["donchian", "ohlcv"]:
        draft["entry_concept"] = (
            "Completed close confirms Donchian channel breakout; next open only."
        )
        draft["exit_concept"] = "Exit on the declared channel-exit or maximum-hold condition."
        draft["parameter_bounds"] = [
            {"name": "channel_lookback_bars", "minimum": 20.0, "maximum": 55.0}
        ]
    return draft


def _request(
    idea="BTCUSDT 4h price SMA trend persistence", features=None
) -> FormalizeStrategyDraftInput:
    return FormalizeStrategyDraftInput.model_validate(
        {
            "idea": idea,
            "symbol": "BTCUSDT",
            "timeframe": "4h",
            "constraints": [],
            "reasoned_draft": _reasoned(features),
            "evidence_resource_uris": URIS,
        }
    )


@pytest.fixture(scope="module")
def repo(tmp_path_factory):
    root = tmp_path_factory.mktemp("fixture-repo")
    original = EvidenceResourceCatalog(REPO, RepoIdentity.resolve(REPO))
    for uri in [*URIS, "project://strategy-spec-schema"]:
        relative = original.spec_for_uri(uri).relative_path
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((REPO / relative).read_bytes())
    for args in [
        ("init", "-q"),
        ("add", "."),
        (
            "-c",
            "user.name=fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "Synthetic test repository",
        ),
    ]:
        subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True)
    return root


@pytest.fixture()
def setup(repo, tmp_path, monkeypatch):
    identity = RepoIdentity.resolve(repo)
    catalog = EvidenceResourceCatalog(repo, identity)
    package = tmp_path / "fixture-package"
    (package / "inputs").mkdir(parents=True)
    sources = [{"id": "R0", "kind": "repo"}]
    for index, uri in enumerate(URIS, 1):
        anchor = catalog.read(uri)["evidence"]
        sources.append(
            {
                "id": f"R{index}",
                "kind": "repo",
                "url_or_uri": uri,
                "evidence_path_or_unknown": anchor["path"],
                "sha256_or_unknown": anchor["artifact_sha256"],
                "repo_sha_or_unknown": admission.HISTORIC_SHA,
            }
        )
    sources.append({"id": "P1", "kind": "public", "url_or_uri": "https://example.invalid/fixture"})
    contents = {
        "research_opportunity_brief.md": b"SYNTHETIC FIXTURE brief; no actual agent research.",
        "source_index.json": _dump(sources),
        "scout_result.md": b"SYNTHETIC scout",
        "critic_result.md": b"SYNTHETIC critic",
        "run_manifest.json": _dump(
            {"repo_sha": admission.HISTORIC_SHA, "not_authority": True, "state": "COMPLETED"}
        ),
    }
    manifest = {"contents": {}}
    wp = b"SYNTHETIC FIXTURE package document."
    (package / admission.WP_NAME).write_bytes(wp)
    manifest["contents"][admission.WP_NAME] = {"bytes": len(wp), "sha256": _hash(wp)}
    for name, raw in contents.items():
        (package / "inputs" / name).write_bytes(raw)
        manifest["contents"]["inputs/" + name] = {"bytes": len(raw), "sha256": _hash(raw)}
    raw_manifest = _dump(manifest)
    (package / "SHA256SUMS.json").write_bytes(raw_manifest)
    monkeypatch.setattr(admission, "PACKAGE_MANIFEST_SHA256", _hash(raw_manifest))
    monkeypatch.setattr(admission, "BRIEF_SHA256", _hash(contents["research_opportunity_brief.md"]))
    draft = {
        "schema_version": "cpw_hermes_admission_draft_v1",
        "repo_sha": identity.repo_sha,
        "brief_sha256": admission.BRIEF_SHA256,
        "not_authority": True,
        "source_ids": ["R1", "R2", "R3", "R5", "P1"],
        "reasoned_draft": _reasoned(),
    }
    events = [
        {"type": "system", "fixture": True},
        {
            "type": "result",
            "session_id": "fixture-session",
            "exit_code": 0,
            "text": json.dumps(draft),
        },
    ]
    receipt = tmp_path / "fixture-result.jsonl"
    receipt.write_bytes(b"\n".join(_dump(e) for e in events))
    return {
        "root": repo,
        "package": package,
        "expected_repo_sha": identity.repo_sha,
        "output": tmp_path / "output",
        "agent_output": receipt,
    }


def test_pinned_inputs_and_current_sources(setup):
    inputs, sources = admission.load_inputs(setup["package"])
    assert len(inputs) == 5
    root = setup["root"]
    catalog = EvidenceResourceCatalog(root, RepoIdentity.resolve(root))
    refreshed = admission.refresh_sources(root, catalog, sources)
    assert [s["status"] for s in refreshed] == [
        "REFERENCE_ONLY",
        *["CURRENT"] * 5,
        "REFERENCE_ONLY",
        "CURRENT",
    ]
    assert "current" not in refreshed[-2]  # no fabricated public-content hash


@pytest.mark.parametrize(
    "name",
    [
        "SHA256SUMS.json",
        "inputs/source_index.json",
        "inputs/research_opportunity_brief.md",
        "inputs/run_manifest.json",
    ],
)
def test_tampered_input_has_no_native_success(setup, name, monkeypatch):
    path = setup["package"] / name
    path.write_bytes(path.read_bytes() + b" ")
    monkeypatch.setattr(
        CpwDomainTools, "formalize_strategy_draft", lambda *_: pytest.fail("native call")
    )
    report = admission.run_admission(**setup)
    assert report["status"] == "FAILED"
    assert report["failure_phase"] == "package_inputs"


def test_stale_source_blocks_before_formalization(setup, monkeypatch):
    original = EvidenceResourceCatalog.read

    def changed(self, uri):
        result = original(self, uri)
        if uri == URIS[1]:
            result["evidence"]["artifact_sha256"] = "f" * 64
        return result

    monkeypatch.setattr(EvidenceResourceCatalog, "read", changed)
    monkeypatch.setattr(
        CpwDomainTools, "formalize_strategy_draft", lambda *_: pytest.fail("native call")
    )
    report = admission.run_admission(**setup)
    assert report["status"] == "BLOCKED_ADMISSION"
    assert report["reason"] == "STALE_OR_CHANGED_SOURCES"
    assert report["sources"][2]["current"]["artifact_sha256"] == "f" * 64


def test_unknown_source_is_denied(setup):
    _, sources = admission.load_inputs(setup["package"])
    sources[2]["url_or_uri"] = "project://secret"
    catalog = EvidenceResourceCatalog(setup["root"], RepoIdentity.resolve(setup["root"]))
    with pytest.raises(PermissionError):
        admission.refresh_sources(setup["root"], catalog, sources)


def test_real_native_trend_limitation_with_synthetic_receipt(setup):
    report = admission.run_admission(**setup)
    assert report["status"] == "BLOCKED_ADMISSION"
    assert report["native_status"] == "accepted"
    assert report["admission_disposition"] == "unsupported"
    native = json.loads((setup["output"] / "artifacts/native_results.json").read_bytes())
    assert native["formalization"]["domain_semantics"]["draft_strategy_specs"] == []
    assert report["blockers"] == [
        "no validated draft adapter exists for this exact primitive family"
    ]
    assert native["preregistration"] is native["approval_requirement"] is None
    assert report["scientific_execution_authorized"] is False


def test_accepted_compatible_fixture_gets_native_description_only(repo):
    identity = RepoIdentity.resolve(repo)
    tools = CpwDomainTools(EvidenceResourceCatalog(repo, identity), identity)
    request = _request("BTCUSDT 4h price donchian breakout", ["donchian", "ohlcv"]).model_copy(
        update={"evidence_resource_uris": ["evidence://decision/DEC-0002"]}
    )
    first = admission.native_admission(tools, request)
    assert first == admission.native_admission(tools, request)
    assert first["admission_disposition"] == "accepted"
    assert first["formalization"]["domain_semantics"]["draft_strategy_specs"]
    packet = first["preregistration"]["domain_semantics"]
    requirement = first["approval_requirement"]["domain_semantics"]
    assert packet["frozen_content"]["canonical_write_allowed"] is False
    assert requirement["required_fields"]["approved_by"] == "Karl"
    assert "approval_timestamp_utc" not in requirement


def test_native_missing_data_and_rejection_are_preserved(repo):
    identity = RepoIdentity.resolve(repo)
    tools = CpwDomainTools(EvidenceResourceCatalog(repo, identity), identity)
    missing = admission.native_admission(
        tools, _request("BTCUSDT price liquidation pressure", ["liquidation_volume", "ohlcv"])
    )
    assert missing["admission_disposition"] == missing["native_status"] == "needs_data"
    assert missing["preregistration"] is None
    rejected = admission.native_admission(tools, _request("BTCUSDT price ema", ["sma", "ohlcv"]))
    assert rejected["admission_disposition"] == rejected["native_status"] == "rejected"
    assert rejected["preregistration"] is None


@pytest.mark.parametrize(
    "mutation",
    [
        "repo",
        "source",
        "authority",
        "draft_authority",
        "timeframe",
        "features",
        "brief",
        "tool",
        "failed",
        "two_results",
        "no_session",
        "bad_json",
        "duplicate_key",
    ],
)
def test_untrusted_receipt_fails_closed(setup, mutation):
    events = [json.loads(line) for line in setup["agent_output"].read_bytes().splitlines()]
    result = events[-1]
    draft = json.loads(result["text"])
    if mutation == "repo":
        draft["repo_sha"] = "f" * 40
    elif mutation == "source":
        draft["source_ids"].append("R99")
    elif mutation == "authority":
        draft["approved_by"] = "Karl"
    elif mutation == "draft_authority":
        draft["reasoned_draft"]["execute"] = True
    elif mutation == "timeframe":
        draft["reasoned_draft"]["timeframe"] = "15m"
    elif mutation == "features":
        draft["reasoned_draft"]["features"].append("stddev")
    elif mutation == "brief":
        draft["brief_sha256"] = "f" * 64
    elif mutation == "tool":
        events.insert(0, {"type": "tool_use", "name": "terminal"})
    elif mutation == "failed":
        result["exit_code"] = 1
    elif mutation == "two_results":
        events.append(copy.deepcopy(result))
    elif mutation == "no_session":
        result.pop("session_id")
    result["text"] = json.dumps(draft)
    if mutation == "bad_json":
        result["text"] = "{"
    if mutation == "duplicate_key":
        result["text"] = '{"repo_sha":"' + draft["repo_sha"] + '",' + result["text"][1:]
    setup["agent_output"].write_bytes(b"\n".join(_dump(e) for e in events))
    report = admission.run_admission(**setup)
    assert report["status"] == "FAILED"
    assert report["failure_phase"] == "agent_input"
    assert not (setup["output"] / "artifacts/native_results.json").exists()


def test_missing_agent_input_is_pending_with_assessment_only(setup):
    setup["agent_output"] = None
    report = admission.run_admission(**setup)
    assert report["reason"] == "PENDING_MODEL_INPUT"
    assert report["formalization"] == "NOT_CALLED"
    assert (setup["output"] / "artifacts/assessment.json").is_file()
    assert (setup["output"] / "artifacts/draft_prompt.txt").is_file()
    assert not (setup["output"] / "artifacts/native_results.json").exists()


def test_immutable_outputs_and_exact_manifest(setup):
    admission.run_admission(**setup)
    published = setup["output"] / "artifacts"
    before = {p.name: p.read_bytes() for p in published.iterdir()}
    with pytest.raises(FileExistsError):
        admission.run_admission(**setup)
    assert before == {p.name: p.read_bytes() for p in published.iterdir()}
    assert not (setup["output"] / ".partial").exists()
    for name, entry in json.loads(before["manifest.json"])["files"].items():
        assert entry == {"sha256": _hash(before[name]), "bytes": len(before[name])}


def test_repo_sha_mismatch_fails_before_native_calls(setup, monkeypatch):
    setup["expected_repo_sha"] = "f" * 40
    monkeypatch.setattr(
        CpwDomainTools, "assess_research_capabilities", lambda *_: pytest.fail("native call")
    )
    report = admission.run_admission(**setup)
    assert report["status"] == "FAILED"
    assert report["failure_phase"] == "repository"


def test_uncommitted_native_schema_blocks(setup, monkeypatch):
    original = admission._git

    def dirty(root, *args):
        raw = original(root, *args)
        return (
            raw + b" "
            if args[0] == "show" and args[1].endswith("strategy_spec.schema.json")
            else raw
        )

    monkeypatch.setattr(admission, "_git", dirty)
    report = admission.run_admission(**setup)
    assert report["reason"] == "STALE_OR_CHANGED_SOURCES"
    assert report["sources"][-1]["id"] == "CPW_SCHEMA"
    assert report["sources"][-1]["status"] == "STALE_OR_CHANGED"


def test_input_change_during_native_call_discards_success(setup, monkeypatch):
    original = CpwDomainTools.formalize_strategy_draft

    def change_input(self, request):
        result = original(self, request)
        path = setup["package"] / "inputs/critic_result.md"
        path.write_bytes(path.read_bytes() + b"changed")
        return result

    monkeypatch.setattr(CpwDomainTools, "formalize_strategy_draft", change_input)
    report = admission.run_admission(**setup)
    assert report["status"] == "FAILED"
    assert not (setup["output"] / "artifacts/native_results.json").exists()


@pytest.mark.parametrize("target", ["repo", "package", "parent", "agent_input"])
def test_unowned_outputs_denied(setup, target):
    setup["output"] = {
        "repo": setup["root"] / "forbidden-output",
        "package": setup["package"] / "forbidden-output",
        "parent": setup["package"].parent.parent / "absent-parent" / "out",
        "agent_input": setup["agent_output"].parent,
    }[target]
    with pytest.raises(ValueError):
        admission.run_admission(**setup)


def test_path_traversal_and_indirection_denied(setup, monkeypatch):
    with pytest.raises(ValueError, match="traversal"):
        admission._ordinary(setup["output"] / ".." / "other")
    ordinary_lstat = Path.lstat

    class Reparse:
        st_mode = 0o100644
        st_file_attributes = 0x400

    monkeypatch.setattr(
        Path,
        "lstat",
        lambda path: Reparse() if path == setup["agent_output"] else ordinary_lstat(path),
    )
    with pytest.raises(ValueError, match="indirection"):
        admission._read(setup["agent_output"])


@pytest.mark.parametrize(
    "raw",
    [
        b"Bearer " + b"a" * 30,
        b"sk-" + b"a" * 30,
        b'{"refresh_token":"secret"}',
        b"postgresql://u:p@host/db",
        b"x" * (admission.MAX_BYTES + 1),
    ],
    ids=["bearer", "key", "oauth", "dsn", "oversize"],
)
def test_secret_and_oversized_receipts_never_persist(setup, raw):
    setup["agent_output"].write_bytes(raw)
    report = admission.run_admission(**setup)
    assert report["status"] == "FAILED"
    assert raw not in (setup["output"] / "artifacts/admission.json").read_bytes()
    assert not (setup["output"] / "artifacts/agent_result.jsonl").exists()


def test_malformed_native_result_never_publishes_success(setup, monkeypatch):
    original = CpwDomainTools.formalize_strategy_draft

    def malformed(self, request):
        result = original(self, request)
        result["domain_semantics"]["draft_strategy_spec"]["produced"] = True
        return result

    monkeypatch.setattr(CpwDomainTools, "formalize_strategy_draft", malformed)
    report = admission.run_admission(**setup)
    assert report["status"] == "FAILED"
    assert report["failure_phase"] == "native_admission"


def test_no_protected_imports_or_state_writes():
    import ast

    tree = ast.parse(Path(admission.__file__).read_text())
    imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert not any(
        name
        and name.startswith(
            (
                "prefect",
                "src",
                "lib",
                "tools.research_factory",
                "tools.research_autonomy",
                "tools.research_runner",
                "tools.canon_intake",
            )
        )
        for name in imports
    )
    assert not any(
        isinstance(node, ast.Attribute) and node.attr in {"shell", "system", "eval", "exec"}
        for node in ast.walk(tree)
    )
