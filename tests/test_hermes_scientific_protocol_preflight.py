"""Two evidence classes: controlled native fixtures and unverified metadata review."""

from __future__ import annotations

import copy
import json
import os
import socket
import subprocess
from pathlib import Path

import pytest
import test_hermes_verified_data_signal_bridge as native

from tools.hermes import scientific_protocol_preflight as pre

hs, qp = pre.hs, pre.qp


@pytest.fixture(scope="module")
def controlled(tmp_path_factory):
    class FreshFactory:
        def mktemp(self, name):
            root = tmp_path_factory.mktemp("02h-owned-synthetic-only")
            assert not list(root.iterdir()) and not root.is_symlink()
            return root

    # The inspected 02G fixture creator writes only fixed fake bars and fixture packets.
    # No caller input, external corpus, historical file or provenance label is accepted.
    fixture = native.prepared.__wrapped__(FreshFactory())
    inputs, options = next(fixture)
    adapter = native.bridge.VerifiedDataSignalBridge()
    output = inputs[0].parent / "native-02g"
    source = adapter.build(output, *inputs, **options)
    yield inputs, options, adapter, output, source
    try:
        next(fixture)
    except StopIteration:
        pass


def proposal_for(source):
    plans = []
    for entry in source["ideas"]:
        plans.append(
            {
                "idea_id": entry["idea_id"],
                "source_idea_sha256": hs.di.canonical_sha256(entry),
                "parameters": entry["compilations"][0]["assignment"]
                if entry["compilations"]
                else {},
                "timeframe": "4h",
                "cadence_bars": 1,
                "windows": [
                    {"kind": kind, "start": start, "end": end}
                    for kind, start, end in (
                        ("construction", "2020-01-01T00:00:00Z", "2020-01-03T00:00:00Z"),
                        ("construction", "2020-01-04T00:00:00Z", "2020-01-06T00:00:00Z"),
                        ("validation", "2020-01-07T00:00:00Z", "2020-01-09T00:00:00Z"),
                        ("final_holdout", "2020-01-10T00:00:00Z", "2020-01-12T00:00:00Z"),
                    )
                ],
                "purge_bars": 1,
                "embargo_bars": 1,
                "gap_convention": "purge_plus_embargo_between_windows",
                "indicator_warmup_bars": 2,
                "warmup_bars": 2,
                "warmup_convention": "within_each_window",
                "costs": {
                    key: {"value": 1.0, "provenance": "operator proposal; review required"}
                    for key in ("fee_bps", "slippage_bps", "funding_bps", "other_cost_bps")
                },
                "budget": {
                    "trials": 1,
                    "cpu_seconds": 1.0,
                    "memory_mb": 16.0,
                    "rationale": "operator-proposed bounded software example",
                },
                "family_data_requirements": [
                    "retain upstream family, features and scientific gaps"
                ],
                "review_rationale": "proposal only; no scientific approval or data access",
            }
        )
    return {
        "schema_version": pre.PROPOSAL_SCHEMA,
        "repo_sha": source["repo_sha"],
        "source_02g": source["content_sha256"],
        "ideas": plans,
    }


@pytest.fixture
def metadata(controlled, tmp_path):
    source = copy.deepcopy(controlled[-1])
    summary, proposal = tmp_path / "supplied-summary.json", tmp_path / "proposal.json"
    summary.write_bytes(hs._json_bytes(source))
    proposal.write_bytes(hs._json_bytes(proposal_for(source)))
    return summary, proposal


def test_controlled_native_replay_dossier(controlled, metadata, tmp_path):
    inputs, options, native_adapter, native_output, source = controlled
    roots = (inputs[0], inputs[1], *inputs[2], inputs[3], options["local_root"], native_output)
    before = [qp._snapshot(p) for p in roots]
    summary, proposal = metadata
    metadata_result = pre.ScientificProtocolPreflight().build(tmp_path / "02h", summary, proposal)

    def dossier():
        assert native_adapter.verify(native_output, *inputs, **options) == source
        result = pre.review(summary.read_bytes(), proposal.read_bytes(), source["repo_sha"])
        # Only this wholly controlled test creator can attach native fixture evidence.
        result.pop("content_sha256")
        result.update(
            verification_class=pre.FIXTURE,
            status="PROPOSED_STRUCTURE_ONLY_REVIEW_REQUIRED",
            fixture_provenance="fresh empty scratch; inspected fixed_15m_v1 creator; unchanged native replay",
            native_02g_content_sha256=source["content_sha256"],
            metadata_review_sha256=metadata_result["content_sha256"],
        )
        for entry in result["ideas"]:
            entry.update(
                verification_class=pre.FIXTURE, status="PROPOSED_STRUCTURE_ONLY_REVIEW_REQUIRED"
            )
        result["integrity_scope"] = (
            "controlled synthetic software proof only; historical data NOT_VERIFIED"
        )
        return hs._render({hs.SUMMARY_FILE: hs._json_bytes(hs._hashed(result))})

    files = dossier()
    output = tmp_path / "fixture-dossier"
    hs._publish(files, output, lambda p: hs._read_tree(p) == dossier() or pytest.fail("replay"))
    assert hs._read_tree(output) == dossier()
    assert before == [qp._snapshot(p) for p in roots]
    result = hs._strict_json(files[hs.SUMMARY_FILE])
    assert [i["idea_id"] for i in result["ideas"]] == ["DON", "FLOW", "LOB"]
    assert [i["upstream_status"] for i in result["ideas"]] == [
        "PASS",
        "NOT_READY_NO_ELIGIBLE_DRAFT",
        "NOT_READY_NO_ELIGIBLE_DRAFT",
    ]
    retained = result["source_02g_metadata_unverified"]
    assert retained == source and retained["investigation_queue"]
    assert retained["ideas"][0]["source_02e_recheck"]["memory"]["refreshed_memory"]["state"] == (
        "PRIOR_FAILED_INVESTIGATION"
    )
    assert all(i["science_status"] == "NOT_READY" for i in result["ideas"])
    assert all(i["search_contract_status"] == "NOT_ISSUABLE" for i in result["ideas"])
    assert "signal_values" not in files[hs.SUMMARY_FILE].decode()
    print(
        "02H_FIXTURE_EVIDENCE="
        + json.dumps(
            {
                "content_sha256": result["content_sha256"],
                "packet_hashes": qp._snapshot(output),
                "metadata_content_sha256": metadata_result["content_sha256"],
                "native_02g_content_sha256": source["content_sha256"],
                "population": [i["idea_id"] for i in result["ideas"]],
            },
            sort_keys=True,
        )
    )


def test_unknown_history_never_opens_sources_or_calls_native(metadata, tmp_path, monkeypatch):
    from tools.lab_pipeline import orchestrator, runner_adapter
    from tools.research_autonomy import contract_builder
    from tools.research_domain import preregistration

    def denied(*args, **kwargs):
        pytest.fail("forbidden source/native/scientific/network operation")

    summary, proposal = metadata
    # Even an exact fixture label and invented source paths cannot admit native replay.
    source = hs._strict_json(summary.read_bytes())
    source["label"] = "SOFTWARE_FIXTURE_PROOF"
    source["source_packet_hashes"] = {"C:/protected/holdout.parquet": "0" * 64}
    source = hs._hashed({k: v for k, v in source.items() if k != "content_sha256"})
    summary.write_bytes(hs._json_bytes(source))
    proposal.write_bytes(hs._json_bytes(proposal_for(source)))
    for cls in (
        native.bridge.VerifiedDataSignalBridge,
        qp.QueueInputPreparation,
        qp.de.DataEvidenceResolution,
        qp.sr.ScienceReadiness,
    ):
        monkeypatch.setattr(cls, "verify", denied)
    monkeypatch.setattr(hs, "verify_built", denied)
    monkeypatch.setattr(hs.dc, "verify_batch", denied)
    monkeypatch.setattr(hs.IntentStrategySpecHandoff, "build_files", denied)
    monkeypatch.setattr(native.bridge.compiler, "compile_signal", denied)
    monkeypatch.setattr(qp.sr, "compile_signal", denied)
    monkeypatch.setattr(qp.de, "inspect_local", denied)
    monkeypatch.setattr(qp, "_derived_bytes", denied)
    monkeypatch.setattr(qp.de.pd, "read_csv", denied)
    monkeypatch.setattr(qp.de.pd, "read_parquet", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(contract_builder, "construct_contract", denied)
    monkeypatch.setattr(contract_builder.ContractBuilder, "build", denied)
    monkeypatch.setattr(preregistration, "build_preregistration_packet", denied)
    monkeypatch.setattr(orchestrator, "run_pipeline", denied)
    monkeypatch.setattr(runner_adapter, "run_product_runner_adapter", denied)
    original_run = subprocess.run

    def git_identity_only(command, **kwargs):
        assert command in (["git", "rev-parse", "HEAD"], ["git", "branch", "--show-current"])
        return original_run(command, **kwargs)

    monkeypatch.setattr(subprocess, "run", git_identity_only)
    original = Path.open
    allowed = {summary.absolute(), proposal.absolute()}
    output = tmp_path / "02h-metadata"

    def bounded_open(path, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        if "r" in mode:
            assert path.absolute() in allowed or (
                path.parent.parent == output.parent
                and (
                    path.parent == output or path.parent.name.startswith(output.name + ".partial-")
                )
                and path.name in {hs.SUMMARY_FILE, "SHA256SUMS"}
            )
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", bounded_open)
    adapter = pre.ScientificProtocolPreflight()
    before = (summary.read_bytes(), proposal.read_bytes())
    result = adapter.build(output, summary, proposal)
    for _ in range(2):
        assert adapter.verify(output, summary, proposal) == result
    assert before == (summary.read_bytes(), proposal.read_bytes())
    assert result["verification_class"] == pre.METADATA
    assert result["status"] == "PROPOSED_METADATA_ONLY_UNVERIFIED"
    assert result["shared_next_inputs"] == pre.MISSING
    assert "resolve feature: sentiment" in result["ideas"][1]["next_inputs"]
    assert all(i["verification_class"] == pre.METADATA for i in result["ideas"])
    print("02H_METADATA_EVIDENCE=" + result["content_sha256"])


@pytest.mark.parametrize(
    "kind",
    [
        "unknown",
        "parameter",
        "population",
        "order",
        "cross",
        "overlap",
        "unaligned",
        "timezone",
        "negative_cost",
        "nan_cost",
        "budget",
        "infinite_budget",
        "warmup",
        "purge",
        "raw",
        "stale",
        "source_unknown",
        "idea_unknown",
        "source_cross",
        "hash",
        "bool_parameter",
        "missing_kind",
    ],
)
def test_adversarial_proposals(metadata, kind):
    source, plan = (hs._strict_json(p.read_bytes()) for p in metadata)
    idea = plan["ideas"][0]
    if kind == "unknown":
        plan["fixture_proof"] = True
    elif kind == "parameter":
        idea["parameters"]["invented"] = 3
    elif kind == "population":
        plan["ideas"].pop()
    elif kind == "order":
        plan["ideas"].reverse()
    elif kind == "cross":
        idea["source_idea_sha256"] = plan["ideas"][1]["source_idea_sha256"]
    elif kind == "overlap":
        idea["windows"][1]["start"] = idea["windows"][0]["start"]
    elif kind == "unaligned":
        idea["windows"][0]["start"] = "2020-01-01T00:01:00Z"
    elif kind == "timezone":
        idea["windows"][0]["start"] = "2020-01-01T00:00:00"
    elif kind in ("negative_cost", "nan_cost"):
        idea["costs"]["fee_bps"]["value"] = -1.0 if kind == "negative_cost" else float("nan")
    elif kind in ("budget", "infinite_budget"):
        idea["budget"]["cpu_seconds"] = -1.0 if kind == "budget" else float("inf")
    elif kind == "warmup":
        idea["warmup_bars"] = 1
    elif kind == "purge":
        idea["purge_bars"] = 1000
    elif kind == "raw":
        source["ideas"][0]["source_02c"]["signal_values"] = [1.0]
    elif kind == "stale":
        source["repo_sha"] = "0" * 40
    elif kind == "source_unknown":
        source["trusted_certificate"] = True
    elif kind == "idea_unknown":
        source["ideas"][0]["extra"] = True
    elif kind == "source_cross":
        source["ideas"][0]["source_02c"]["idea_id"] = "FLOW"
    elif kind == "bool_parameter":
        idea["parameters"]["invented"] = True
    elif kind == "missing_kind":
        idea["windows"][-1]["kind"] = "validation"
    if kind != "hash":
        source = hs._hashed({k: v for k, v in source.items() if k != "content_sha256"})
        plan["source_02g"] = source["content_sha256"]
    else:
        source["label"] = "tampered"
    with pytest.raises((ValueError, hs.HandoffError)):
        pre.review(
            hs._json_bytes(source),
            hs._json_bytes(plan),
            hs.RepoIdentity.resolve(hs.REPO_ROOT).repo_sha,
        )


def test_packet_tamper_and_paths(metadata, tmp_path):
    summary, proposal = metadata
    adapter = pre.ScientificProtocolPreflight()
    output = tmp_path / "02h"
    adapter.build(output, summary, proposal)
    packet = output / hs.SUMMARY_FILE
    packet.write_bytes(packet.read_bytes() + b" ")
    with pytest.raises(hs.HandoffError):
        adapter.verify(output, summary, proposal)
    with pytest.raises(hs.HandoffError):
        adapter.build(summary.parent, summary, proposal)
    link = tmp_path / "hardlink.json"
    os.link(summary, link)
    try:
        with pytest.raises(hs.HandoffError, match="unlinked"):
            adapter.build(tmp_path / "hard-output", link, proposal)
    finally:
        link.unlink()
    symbolic = tmp_path / "symbolic.json"
    try:
        symbolic.symlink_to(summary)
    except OSError:
        # Windows may disallow symlink creation; native reparse guard is exercised below.
        pass
    else:
        with pytest.raises(hs.HandoffError):
            adapter.build(tmp_path / "sym-output", symbolic, proposal)
        symbolic.unlink()


def test_json_bounds_default_off_and_reparse(metadata, tmp_path, monkeypatch, capsys):
    summary, proposal = metadata
    with pytest.raises(ValueError):
        pre.review(b'{"schema_version":1,"schema_version":2}', b"{}", "0" * 40)
    with pytest.raises(hs.HandoffError):
        pre.review(b" " * (pre.MAX_BYTES + 1), b"{}", "0" * 40)
    with pytest.raises(hs.HandoffError, match="external JSON"):
        pre._read_metadata(tmp_path / "protected.parquet")
    with pytest.raises(hs.HandoffError, match="external JSON"):
        pre._read_metadata(hs.REPO_ROOT / "forbidden.json")
    with pytest.raises(SystemExit) as exc:
        pre.main([])
    assert exc.value.code == 2
    args = [
        "--output",
        str(tmp_path / "cli"),
        "--summary",
        str(summary),
        "--proposal",
        str(proposal),
    ]
    outputs = []
    for command in ("build", "verify", "replay"):
        assert pre.main([command, *args]) == 0
        outputs.append(json.loads(capsys.readouterr().out))
    assert outputs[0] == outputs[1] == outputs[2]
    monkeypatch.setattr(hs.dc, "_is_link", lambda p: p == summary)
    with pytest.raises(hs.HandoffError):
        pre.ScientificProtocolPreflight().build(tmp_path / "reparse", summary, proposal)
