"""SOFTWARE_FIXTURE_PROOF: structural study-plan preflight over a current-head 02G batch."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys

import pytest
from test_hermes_verified_data_signal_bridge import prepared  # noqa: F401

from tools.hermes import scientific_protocol_preflight as preflight

bridge, qp, de, hs = preflight.bridge, preflight.qp, preflight.de, preflight.hs
SOURCE = "7ad31cdd866e7ed0470ba1b1904a772c0f2d7f77abca6e27634e53f54c78f0e8"


@pytest.fixture(scope="module")
def signal(prepared, tmp_path_factory):  # noqa: F811
    inputs, options = prepared
    output = tmp_path_factory.mktemp("02h") / "02g"
    result = bridge.VerifiedDataSignalBridge().build(output, *inputs, **options)
    return output, inputs, options, result


def _plan() -> dict:
    return {
        "source_sha256": SOURCE,
        "primary_timeframe": "4h",
        "windows": {
            "construction": {"start": "2020-01-04T08:00:00Z", "end": "2020-01-07T00:00:00Z"},
            "validation": {"start": "2020-01-07T08:00:00Z", "end": "2020-01-09T00:00:00Z"},
            "final_holdout": {"start": "2020-01-09T08:00:00Z", "end": "2020-01-11T16:00:00Z"},
        },
        "purge_bars": 1,
        "embargo_bars": 1,
        "warmup_bars": 20,
        "leakage_considerations": "completed-bar features only; operator assumption",
        "costs": {
            "fee_bps": 4.5,
            "slippage_bps": 2,
            "funding_source": "operator assumption, not a verified funding series",
            "cost_source": "operator assumption",
        },
        "budget": {"max_trials": 2, "max_compute_minutes": 30},
        "robustness_plan": "parameter-neighbour stability review",
        "multiple_testing_plan": "count every proposed trial; human decides correction",
        "lineage_refs": ["fixture 02F/02G chain"],
        "parameters": ["channel_lookback_bars"],
    }


def _proposal(result: dict, **ideas) -> dict:
    return {
        "schema_version": preflight.PROPOSAL_SCHEMA,
        "source_02g": result["content_sha256"],
        "provenance": bridge.FIXTURE,
        "non_holdout_certificate": "NOT_AVAILABLE",
        "operator": "karl",
        "rationale": "software fixture study-plan structure only",
        "ideas": ideas or {"DON": _plan()},
    }


def _write(tmp_path, value) -> object:
    path = tmp_path / "proposal.json"
    path.write_bytes(value if isinstance(value, bytes) else hs._json_bytes(value))
    return path


@pytest.fixture
def offline(signal, monkeypatch):
    """Upstream already verified once; 02H itself must read no bars and call no native runner."""
    output, inputs, options, result = signal
    monkeypatch.setattr(bridge.VerifiedDataSignalBridge, "verify", lambda *a, **k: result)

    def denied(*args, **kwargs):
        pytest.fail("bar access or native execution from 02H")

    monkeypatch.setattr(de, "inspect_local", denied)
    monkeypatch.setattr(de.pd, "read_csv", denied)
    monkeypatch.setattr(bridge.compiler, "compile_signal", denied)

    def run(tmp_path, proposal):
        path = None if proposal is None else _write(tmp_path, proposal)
        files = preflight.ScientificProtocolPreflight().build_files(
            output, *inputs, proposal=path, **options
        )
        return hs._strict_json(files[hs.SUMMARY_FILE])

    return run, result


def _forbid_native(monkeypatch):
    from tools.lab_pipeline import orchestrator
    from tools.research_autonomy import contract_builder
    from tools.research_domain import preregistration

    def denied(*args, **kwargs):
        pytest.fail("forbidden network/preregistration/dispatch operation")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(contract_builder, "construct_contract", denied)
    monkeypatch.setattr(preregistration, "build_preregistration_packet", denied)
    monkeypatch.setattr(preregistration, "build_approval_marker", denied)
    monkeypatch.setattr(orchestrator, "_formalized_idea", denied)


def test_software_fixture_structural_proposal_and_replay(signal, tmp_path, monkeypatch):
    signal_dir, inputs, options, upstream = signal
    _forbid_native(monkeypatch)
    proposal = _write(tmp_path, _proposal(upstream, DON=_plan(), FLOW={"features": ["sentiment"]}))
    before = [qp._snapshot(p) for p in (signal_dir, inputs[0], inputs[1], *inputs[2], inputs[3])]
    adapter = preflight.ScientificProtocolPreflight()
    output = tmp_path / "02h"
    result = adapter.build(output, signal_dir, *inputs, proposal=proposal, **options)
    assert [i["idea_id"] for i in result["ideas"]] == ["DON", "FLOW", "LOB"]
    assert [i["status"] for i in result["ideas"]] == [
        preflight.STRUCTURED,
        "NOT_READY_UPSTREAM_NOT_COMPILED",
        "NOT_READY_PROPOSAL_MISSING",
    ]
    don, flow, lob = result["ideas"]
    assert don["structural_findings"] == [] and don["missing_inputs"] == []
    assert "feature_evidence:sentiment" in flow["missing_inputs"]
    assert flow["source_02g_idea"] == upstream["ideas"][1]
    assert (
        lob["source_02g_idea"]["source_02e_recheck"]["memory"]
        == (upstream["ideas"][2]["source_02e_recheck"]["memory"])
    )
    assert all(i["science_status"] == "NOT_READY" for i in result["ideas"])
    assert result["science_status"] == "NOT_READY"
    assert result["search_contract_status"] == "NOT_ISSUABLE"
    assert result["stage_5b_active"] is False and result["canonical_write_allowed"] is False
    assert result["non_holdout_certificate"] == "NOT_AVAILABLE"
    assert result["selection"] == "NONE_ALL_IDEAS_RETAINED"
    assert result["shared_source_requirements"] == {
        f"4h:{SOURCE}": {"timeframe": "4h", "ideas": ["DON", "FLOW"]}
    }
    assert don["input_map"]["pipeline_request"] == "NOT_EMITTED"
    text = json.dumps(result)
    assert "pipeline_run_id" not in text and "approval_marker" not in text
    review = (output / preflight.REVIEW_FILE).read_text()
    assert preflight.STRUCTURED in review and "NOT_ISSUABLE" in review
    hashes = qp._snapshot(output)
    assert adapter.verify(output, signal_dir, *inputs, proposal=proposal, **options) == result
    assert qp._snapshot(output) == hashes
    assert before == [
        qp._snapshot(p) for p in (signal_dir, inputs[0], inputs[1], *inputs[2], inputs[3])
    ]
    print(
        "FIXTURE_EVIDENCE="
        + json.dumps(
            {
                "content_sha256": result["content_sha256"],
                "source_02g": result["source_02g"],
                "proposal_sha256": result["proposal_sha256"],
                "population": [[i["idea_id"], i["status"]] for i in result["ideas"]],
                "packet_hashes": hashes,
            },
            sort_keys=True,
        )
    )
    # A changed declared cost changes identity and invalidates the published replay.
    changed = _proposal(upstream, DON=_plan(), FLOW={"features": ["sentiment"]})
    changed["ideas"]["DON"]["costs"]["fee_bps"] = 5.0
    _write(tmp_path, changed)
    with pytest.raises(hs.HandoffError, match="replay"):
        adapter.verify(output, signal_dir, *inputs, proposal=proposal, **options)


def test_identity_changes_with_window_source_or_cost(offline, tmp_path):
    run, upstream = offline
    base = run(tmp_path, _proposal(upstream))["content_sha256"]
    for change in ("window", "cost", "embargo"):
        plan = _plan()
        if change == "window":
            plan["windows"]["final_holdout"]["start"] = "2020-01-09T12:00:00Z"
        elif change == "cost":
            plan["costs"]["slippage_bps"] = 3
        else:
            plan["embargo_bars"] = 0
        assert run(tmp_path, _proposal(upstream, DON=plan))["content_sha256"] != base


def test_absent_and_incomplete_proposals_are_gaps_not_defaults(offline, tmp_path):
    run, upstream = offline
    absent = run(tmp_path, None)
    assert {i["status"] for i in absent["ideas"]} == {"NOT_READY_PROPOSAL_MISSING"}
    assert absent["proposal_sha256"] is None and len(absent["ideas"]) == 3
    plan = _plan()
    plan["costs"] = None
    del plan["windows"]
    result = run(tmp_path, _proposal(upstream, DON=plan))
    don = result["ideas"][0]
    assert don["status"] == "NOT_READY_PROPOSAL_INCOMPLETE"
    assert don["missing_inputs"] == ["windows", "costs"]
    assert don["plan"]["windows"] is None and don["structural_findings"] == []


@pytest.mark.parametrize(
    "kind,finding",
    [
        ("overlap", "overlap"),
        ("order", "overlap"),
        ("misaligned", "aligned"),
        ("naive", "timezone"),
        ("garbage", "validation"),
        ("purge", "purge+embargo"),
        ("warmup", "warmup"),
        ("coverage", "coverage metadata"),
    ],
)
def test_structural_findings(offline, tmp_path, kind, finding):
    run, upstream = offline
    plan = _plan()
    w = plan["windows"]
    if kind == "overlap":
        w["validation"]["start"] = "2020-01-06T00:00:00Z"
    elif kind == "order":
        w["validation"], w["final_holdout"] = w["final_holdout"], w["validation"]
    elif kind == "misaligned":
        w["validation"]["start"] = "2020-01-07T09:00:00Z"
    elif kind == "naive":
        w["construction"]["end"] = "2020-01-07T00:00:00"
    elif kind == "garbage":
        w["validation"]["end"] = "not-a-time"
    elif kind == "purge":
        plan["embargo_bars"] = 2
    elif kind == "warmup":
        plan["warmup_bars"] = 21
    else:
        w["final_holdout"]["end"] = "2020-01-11T20:00:00Z"
    don = run(tmp_path, _proposal(upstream, DON=plan))["ideas"][0]
    assert don["status"] == "NOT_READY_STRUCTURE_INVALID"
    assert any(finding in f for f in don["structural_findings"]), don["structural_findings"]


@pytest.mark.parametrize(
    "kind",
    [
        "unknown_field",
        "unknown_idea",
        "unknown_parameter",
        "invented_feature",
        "stale_02g",
        "source_substitution",
        "timeframe",
        "fake_certificate",
        "historical_label",
        "negative_cost",
        "nonfinite_cost",
        "zero_budget",
        "bool_bars",
        "flow_parameter",
        "lob_source",
    ],
)
def test_proposal_refusals(offline, tmp_path, kind):
    run, upstream = offline
    proposal = _proposal(upstream)
    don = proposal["ideas"]["DON"]
    raw = None
    if kind == "unknown_field":
        don["holdout_certified"] = True
    elif kind == "unknown_idea":
        proposal["ideas"]["NEW"] = _plan()
    elif kind == "unknown_parameter":
        don["parameters"] = ["stop_bars"]
    elif kind == "invented_feature":
        don["features"] = ["funding_rate"]
    elif kind == "stale_02g":
        proposal["source_02g"] = "0" * 64
    elif kind == "source_substitution":
        don["source_sha256"] = "1" * 64
    elif kind == "timeframe":
        don["primary_timeframe"] = "1h"
    elif kind == "fake_certificate":
        proposal["non_holdout_certificate"] = {"status": "CERTIFIED", "sha256": "2" * 64}
    elif kind == "historical_label":
        proposal["provenance"] = "OPERATOR_PROPOSED_HISTORICAL"
    elif kind == "negative_cost":
        don["costs"]["fee_bps"] = -1
    elif kind == "nonfinite_cost":
        raw = hs._json_bytes(proposal).replace(b'"fee_bps": 4.5', b'"fee_bps": NaN')
    elif kind == "zero_budget":
        don["budget"]["max_trials"] = 0
    elif kind == "bool_bars":
        don["warmup_bars"] = True
    elif kind == "flow_parameter":
        proposal["ideas"]["FLOW"] = {"parameters": ["channel_lookback_bars"]}
    else:  # LOB has no verified source at all; naming one is a substitution
        proposal["ideas"]["LOB"] = {"source_sha256": SOURCE}
    with pytest.raises((hs.HandoffError, ValueError)):
        run(tmp_path, raw or proposal)


def test_synthetic_label_cannot_pass_as_history(offline, tmp_path, monkeypatch):
    run, upstream = offline
    historical = {**upstream, "label": "TECHNICAL_COMPILATION_ONLY"}
    monkeypatch.setattr(bridge.VerifiedDataSignalBridge, "verify", lambda *a, **k: historical)
    with pytest.raises(hs.HandoffError, match="provenance"):
        run(tmp_path, _proposal(historical))


@pytest.mark.parametrize("kind", ["summary", "sums", "head"])
def test_tampered_or_stale_02g_refused(signal, tmp_path, monkeypatch, kind):
    signal_dir, inputs, options, _ = signal
    copied = tmp_path / "02g-copy"
    copied.mkdir()
    for name, raw in hs._read_tree(signal_dir).items():
        (copied / name).write_bytes(raw)
    if kind == "summary":
        path = copied / hs.SUMMARY_FILE
        path.write_bytes(path.read_bytes().replace(b'"PASS"', b'"FAIL"', 1))
    elif kind == "sums":
        (copied / "extra.json").write_bytes(b"{}")
    else:
        monkeypatch.setattr(
            bridge.sr.RepoIdentity,
            "resolve",
            lambda root: bridge.sr.RepoIdentity("0" * 40, "drift"),
        )
    with pytest.raises((hs.HandoffError, de.dc.ConsumerError)):
        preflight.ScientificProtocolPreflight().build_files(copied, *inputs, **options)


def test_unsafe_paths_and_packet_tamper(signal, offline, tmp_path):
    signal_dir, inputs, options, upstream = signal
    _ = offline  # stubbed upstream verification keeps publication checks fast
    adapter = preflight.ScientificProtocolPreflight()
    proposal = _write(tmp_path, _proposal(upstream))
    with pytest.raises(hs.HandoffError, match="disjoint"):
        adapter.build(signal_dir / "nested", signal_dir, *inputs, proposal=proposal, **options)
    output = tmp_path / "02h"
    adapter.build(output, signal_dir, *inputs, proposal=proposal, **options)
    path = output / hs.SUMMARY_FILE
    path.write_bytes(path.read_bytes().replace(b'"NOT_READY"', b'"READY"', 1))
    with pytest.raises(hs.HandoffError):
        adapter.verify(output, signal_dir, *inputs, proposal=proposal, **options)
    link = tmp_path / "proposal-link"
    os.link(proposal, link)
    try:
        with pytest.raises(hs.HandoffError, match="unlinked"):
            adapter.build(tmp_path / "other", signal_dir, *inputs, proposal=proposal, **options)
    finally:
        link.unlink()


def test_cli_default_off():
    run = subprocess.run(
        [sys.executable, "-B", "-m", "tools.hermes.scientific_protocol_preflight"],
        capture_output=True,
        check=False,
    )
    assert run.returncode == 2
