"""SOFTWARE_FIXTURE_PROOF: current-HEAD labeled fixtures, never physical Hermes output."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest
from test_hermes_intent_strategy_spec_handoff import (
    ROOT,
    FrozenMemory,
    HypothesisDefinition,
    _don_native,
    _idea,
    _native,
    build,
    fingerprint,
    make_batch,
    prepare,
    respond,
)

from tools.hermes import discovery_intent_consumer as dc
from tools.hermes import intent_strategy_spec_handoff as hs
from tools.hermes import science_readiness as sr


@pytest.fixture
def chain(tmp_path):
    batch = make_batch(tmp_path, [_idea("DON", _don_native()),
                                  _idea("FLOW", _native(free_parameter_count=1)), _idea("LOB", None)])
    prepared = prepare(tmp_path, batch)
    responses = tmp_path / "responses"
    respond(prepared, responses, 0)
    respond(prepared, responses, 1)
    built, _ = build(tmp_path, prepared, responses)
    return built, prepared, responses


def _summary(files):
    return json.loads(files[hs.SUMMARY_FILE])


def test_population_parameters_memory_and_honest_science(chain):
    files = sr.ScienceReadiness().build_files(*chain)
    summary = _summary(files)
    assert [i["idea_id"] for i in summary["ideas"]] == ["DON", "FLOW", "LOB"]
    assert summary["counts"][hs.DRAFTED] == summary["counts"][hs.UNSUPPORTED] == summary["counts"][hs.LEAD] == 1
    assert summary["science_counts"] == {"NOT_READY": 3, "NOT_ISSUABLE": 3}
    result = json.loads(files["ideas/00.receipt.json"])
    check = result["technical_checks"][0]
    review = check["parameter_review"]
    assert review["intent_bounds"][0]["minimum"] == 10
    assert review["formalized_bounds"][0]["minimum"] == 20
    assert review["model_to_formalized_changed"] is True
    assert review["status"] == "REQUIRES_REVIEW_NO_SEMANTIC_EQUIVALENCE_ASSERTED"
    assert check["compiler"]["status"] == "PASSED"
    assert check["compiler"]["label"] == "SYNTHETIC_TECHNICAL_ONLY"
    assert result["preregistration"]["missing_inputs"] == sr.PREREG_MISSING
    assert set(result["search_contract"]["reasons"]) == set(sr.CONTRACT_REASONS)
    for index in range(3):
        receipt = json.loads(files[f"ideas/{index:02d}.receipt.json"])
        assert receipt["source_02c"]["critic_assessment"] == receipt["source_02b"]["critic_assessment"]
        assert receipt["source_02b"]["original_memory"] == receipt["memory"]["original_memory"]["record"]
        assert receipt["science_status"] == "NOT_READY"
        assert receipt["next_legal_investigation"]
    assert result["source_02c"]["model_response"]["authorship"] == "NOT_MODEL_OUTPUT_LABELED_FIXTURE"


@pytest.mark.parametrize("summary_changed", [False, True])
def test_matching_parameter_bounds_do_not_claim_a_change(tmp_path, monkeypatch, summary_changed):
    if summary_changed:
        formalize = hs.CpwDomainTools.formalize_strategy_draft

        def with_summary_change(self, request):
            result = formalize(self, request)
            result["domain_semantics"]["research_object"]["summary"] = "Labeled fixture: unrelated summary edit."
            return result

        monkeypatch.setattr(hs.CpwDomainTools, "formalize_strategy_draft", with_summary_change)
    native = _don_native(proposed_parameter_bounds=[
        {"name": "channel_lookback_bars", "minimum": 20.0, "maximum": 55.0}])
    batch = make_batch(tmp_path, [_idea("DON", native)])
    prepared = prepare(tmp_path, batch)
    responses = tmp_path / "responses"
    respond(prepared, responses, 0)
    built, _ = build(tmp_path, prepared, responses)
    files = sr.ScienceReadiness().build_files(built, prepared, responses)
    result = json.loads(files["ideas/00.receipt.json"])
    review = result["technical_checks"][0]["parameter_review"]
    assert review["model_bounds"] == review["formalized_bounds"]
    assert (result["source_02c"]["model_response"]["reasoned_draft"] !=
            result["source_02c"]["native_formalization"]["research_object"]) is summary_changed
    assert review["model_to_formalized_changed"] is False
    assert review["status"] == "REQUIRES_REVIEW_NO_SEMANTIC_EQUIVALENCE_ASSERTED"


def test_cli_build_verify_replay_identical_bytes_and_no_repo_writes(chain, tmp_path):
    before = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)
    outputs = []
    for name in ("packet-a", "packet-b"):
        output = tmp_path / name
        inputs = ["--built-dir", str(chain[0]), "--prepared-dir", str(chain[1]),
                  "--responses-dir", str(chain[2]), "--output", str(output)]
        for command in ("build", "verify", "replay"):
            run = subprocess.run([sys.executable, "-m", "tools.hermes.science_readiness", command, *inputs],
                                 cwd=ROOT, capture_output=True, text=True, check=False)
            assert run.returncode == 0, run.stderr
        outputs.append(hs._read_tree(output))
    assert outputs[0] == outputs[1]
    assert subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT) == before
    print("SOFTWARE_FIXTURE_PROOF", _summary(outputs[0])["content_sha256"], _summary(outputs[0])["counts"])


@pytest.mark.parametrize("target", ["built", "prepared", "responses"])
def test_tampered_chain_rejected(chain, target):
    directory = chain[["built", "prepared", "responses"].index(target)]
    pattern = "*.response.json" if target == "responses" else "*.json"
    file = next(p for p in directory.rglob(pattern) if p.is_file())
    file.write_bytes(file.read_bytes() + b" ")
    with pytest.raises((dc.ConsumerError, ValueError)):
        sr.ScienceReadiness().build_files(*chain)


def test_rehashed_built_population_substitution_rejected(chain):
    files = hs._read_tree(chain[0])
    summary = _summary(files)
    summary["ideas"] = summary["ideas"][::-1]
    summary.pop("content_sha256")
    files[hs.SUMMARY_FILE] = hs._json_bytes(hs._hashed(summary))
    for name, raw in hs._render({n: r for n, r in files.items() if n != "SHA256SUMS"}).items():
        (chain[0] / name).write_bytes(raw)
    with pytest.raises(dc.ConsumerError, match="replay"):
        sr.ScienceReadiness().build_files(*chain)


def test_stale_head_and_midrun_drift_fail_closed(chain, monkeypatch):
    adapter = sr.ScienceReadiness()
    monkeypatch.setattr(sr.RepoIdentity, "resolve", lambda root: sr.RepoIdentity("b" * 40, "drift"))
    with pytest.raises(dc.ConsumerError, match="HEAD changed"):
        adapter.build_files(*chain)
    with pytest.raises(dc.ConsumerError, match="stale"):
        sr.ScienceReadiness().build_files(*chain)


def test_collision_traversal_inventory_and_link_refusal(chain, tmp_path):
    adapter = sr.ScienceReadiness()
    files = adapter.build_files(*chain)
    output = tmp_path / "packet"
    hs._publish(files, output, lambda p: adapter.verify(p, *chain))
    with pytest.raises(dc.ConsumerError, match="overwrite"):
        hs._publish(files, output, lambda p: None)
    (output / "extra.json").write_text("{}")
    with pytest.raises(dc.ConsumerError, match="inventory"):
        adapter.verify(output, *chain)
    summary = json.loads((chain[0] / "summary.json").read_bytes())
    summary["ideas"][0]["receipt"] = "../../escape.json"
    summary.pop("content_sha256")
    (chain[0] / "summary.json").write_bytes(hs._json_bytes(hs._hashed(summary)))
    with pytest.raises(dc.ConsumerError):
        adapter.build_files(*chain)
    link = tmp_path / "linked"
    try:
        os.symlink(output, link, target_is_directory=True)
    except OSError:
        if os.name != "nt":
            raise
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(output)], check=True, capture_output=True)
    with pytest.raises(dc.ConsumerError):
        hs._read_tree(link)
    with pytest.raises(dc.ConsumerError, match="symlink|junction"):
        hs._publish(files, link / "new", lambda p: None)
    with pytest.raises(dc.ConsumerError, match="symlink|junction"):
        adapter.verify(link, *chain)
    with pytest.raises(dc.ConsumerError, match="traversal"):
        sr._check_paths(output / ".." / "other")


def test_unknown_memory_retained_without_novelty(chain):
    files = sr.ScienceReadiness().build_files(*chain)
    for index in range(3):
        result = json.loads(files[f"ideas/{index:02d}.receipt.json"])
        assert "not novelty" in result["memory"]["original_memory"]["interpretation"]
    assert json.loads(files["ideas/02.receipt.json"])["memory"]["refreshed_memory"]["state"] == "UNKNOWN"


def test_raw_capture_bytes_bound_by_readiness_hash(chain, tmp_path):
    adapter = sr.ScienceReadiness()
    files = adapter.build_files(*chain)
    output = tmp_path / "packet"
    hs._publish(files, output, lambda p: adapter.verify(p, *chain))
    capture = next(chain[2].glob("*.capture.json"))
    capture.write_bytes(capture.read_bytes() + b" ")
    with pytest.raises(dc.ConsumerError, match="identical bytes"):
        adapter.verify(output, *chain)


def test_no_science_authority_or_network_calls(chain, monkeypatch):
    import socket

    from tools.research_autonomy import contract_builder
    from tools.research_domain import preregistration

    def forbidden(*args, **kwargs):
        pytest.fail("unauthorized scientific or network operation")

    for name in ("build_preregistration_packet", "build_approval_requirement", "build_approval_marker"):
        monkeypatch.setattr(preregistration, name, forbidden)
    monkeypatch.setattr(contract_builder, "construct_contract", forbidden)
    monkeypatch.setattr(contract_builder.ContractBuilder, "build", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    assert _summary(sr.ScienceReadiness().build_files(*chain))["authority"] == hs.AUTHORITY


def test_no_default_command_has_no_effect(tmp_path):
    run = subprocess.run([sys.executable, "-m", "tools.hermes.science_readiness"], cwd=tmp_path,
                         env={**os.environ, "PYTHONPATH": str(ROOT)}, capture_output=True, check=False)
    assert run.returncode == 2
    assert list(tmp_path.iterdir()) == []


def test_negative_memory_and_critic_agreement_retained(tmp_path):
    native = _don_native()
    fp = fingerprint(HypothesisDefinition.from_mapping({k: native[k] for k in (
        "strategy_family", "mechanism", "primary_timeframe", "required_data_features", "free_parameter_count")}))
    idea = _idea("DON", native, critic_assessment={
        "stance": "AGREE", "critic_excerpt": "taker archive alignment to 1h bars is unverified",
        "evidence_gaps": [], "failure_modes": [], "counterarguments": []})
    batch = make_batch(tmp_path, [idea], memory=FrozenMemory(negative={fp}))
    prepared = prepare(tmp_path, batch)
    responses = tmp_path / "responses"
    respond(prepared, responses, 0)
    built, _ = build(tmp_path, prepared, responses)
    files = sr.ScienceReadiness().build_files(built, prepared, responses)
    result = json.loads(files["ideas/00.receipt.json"])
    assert result["source_02c"]["critic_assessment"]["stance"] == "AGREE"
    assert result["memory"]["refreshed_memory"]["state"] == "PRIOR_FAILED_INVESTIGATION"
    assert result["source_native_intent"]["research_memory"]["records"][0]["classification"] == "NO-GO"
    assert any("PRIOR_NEGATIVE_MEMORY" in r for r in result["source_02c"]["review_requirements"])
