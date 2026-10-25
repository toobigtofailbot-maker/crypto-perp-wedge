"""02F SOFTWARE_FIXTURE_PROOF: synthetic corpus/model cases confer no science authority."""

from __future__ import annotations

import copy
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
from test_hermes_data_evidence_resolution import synthetic
from test_hermes_intent_strategy_spec_handoff import (
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

from tools.hermes import queue_input_preparation as qp

de, hs, sr = qp.de, qp.hs, qp.sr


@pytest.fixture
def chain(tmp_path):
    native = _don_native()
    fp = fingerprint(
        HypothesisDefinition.from_mapping(
            {
                k: native[k]
                for k in (
                    "strategy_family",
                    "mechanism",
                    "primary_timeframe",
                    "required_data_features",
                    "free_parameter_count",
                )
            }
        )
    )
    batch = make_batch(
        tmp_path,
        [
            _idea("DON", native),
            _idea(
                "FLOW",
                _native(
                    primary_timeframe="4h",
                    required_data_features=[
                        "taker_buy_volume",
                        "taker_sell_volume",
                        "funding_rate",
                        "sentiment",
                    ],
                    free_parameter_count=1,
                ),
            ),
            _idea("LOB", None),
        ],
        memory=FrozenMemory(negative={fp}),
    )
    prepared = prepare(tmp_path, batch)
    responses = tmp_path / "responses"
    for i in range(2):
        respond(prepared, responses, i)
    built, _ = build(tmp_path, prepared, responses)
    readiness = sr.ScienceReadiness()
    output = tmp_path / "02d"
    hs._publish(
        readiness.build_files(built, prepared, responses),
        output,
        lambda p: readiness.verify(p, built, prepared, responses),
    )
    return output, built, prepared, responses


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    source = tmp_path / "sources"
    source.mkdir()
    path, _ = synthetic(source)
    frame = pd.read_csv(path, dtype=str)
    frame = pd.concat([frame] * 4, ignore_index=True)
    index = pd.date_range("2020-01-01", periods=16, freq="15min", tz="UTC")
    frame["open_time"] = [ts.isoformat().replace("+00:00", "Z") for ts in index]
    frame["open_time_ms"] = [ts.value // 1_000_000 for ts in index]
    frame["close_time_ms"] = frame["open_time_ms"] + 899999
    adapter = de.DataEvidenceResolution()
    catalogs = {tf: copy.deepcopy(adapter._catalog(tf)) for tf in ("15m", "4h")}
    parent = source / catalogs["15m"]["normalized"]["path"]
    parent.parent.mkdir(parents=True)
    frame.to_csv(parent, index=False, lineterminator="\n")
    for tf, rows, end in (("15m", 16, "03:45:00"), ("4h", 1, "00:00:00")):
        catalogs[tf]["range"].update(
            row_count=rows, start_utc="2020-01-01T00:00:00Z", end_utc=f"2020-01-01T{end}Z"
        )
    catalogs["15m"]["normalized"]["sha256"] = de.ft._sha256(parent)
    derived = qp._derived_bytes(parent, "4h")
    catalogs["4h"]["normalized"]["sha256"] = de.dc._sha256_bytes(derived)
    catalogs["4h"]["parent"]["normalized_sha256"] = de.ft._sha256(parent)
    original = de.DataEvidenceResolution._catalog
    monkeypatch.setattr(
        de.DataEvidenceResolution,
        "_catalog",
        lambda self, tf: copy.deepcopy(catalogs[tf]) if tf in catalogs else original(self, tf),
    )
    config = dict(qp.taker.CANONICAL_KLINE_PARENT_CONFIG["4h"])
    config.update(
        sha256=de.dc._sha256_bytes(derived),
        row_count=1,
        coverage_start="2020-01-01T00:00:00.000Z",
        coverage_end="2020-01-01T04:00:00.000Z",
    )
    monkeypatch.setattr(qp.taker, "CANONICAL_KLINE_PARENT_CONFIG", {"4h": config})
    return source, catalogs, parent


def execute(tmp_path, chain, *, local_root=None, inventory=None, materialize=False):
    adapter = qp.QueueInputPreparation()
    evidence = tmp_path / "02e"
    hs._publish(
        adapter.evidence.build_files(*chain), evidence, lambda p: adapter.evidence.verify(p, *chain)
    )
    output, workspace = tmp_path / "02f", tmp_path / "workspace"
    options = {
        "local_root": local_root,
        "inventory": inventory,
        "requests": None,
        "materialize": materialize,
    }
    result = adapter.build(output, evidence, chain, workspace, **options)
    return adapter, output, evidence, workspace, options, result


def test_mixed_batch_prepares_shared_native_source_features_and_rechecks(
    chain, corpus, tmp_path, monkeypatch
):
    source, catalogs, parent = corpus
    original = parent.read_bytes()
    inventory = tmp_path / "inventory.json"
    window = {"start": "2020-01-01T00:00:00Z", "end": "2020-01-01T04:00:00Z"}
    inventory.write_text(json.dumps({"windows": {key: window for key in ("DON", "FLOW")}}))
    writes = []
    materializer = qp.taker.materialize_canonical_kline_takerflow_features

    def counted(**kwargs):
        writes.append(kwargs["timeframe"])
        return materializer(**kwargs)

    monkeypatch.setattr(qp.taker, "materialize_canonical_kline_takerflow_features", counted)
    adapter, output, evidence, workspace, options, result = execute(
        tmp_path, chain, local_root=source, inventory=inventory, materialize=True
    )
    assert [i["idea_id"] for i in result["ideas"]] == ["DON", "FLOW", "LOB"]
    assert all((output / entry["receipt"]).is_file() for entry in result["ideas"])
    assert result["science_counts"] == {"NOT_READY": 3}
    assert result["search_contract_status"] == "NOT_ISSUABLE"
    shared = result["shared_sources"]["4h"]
    assert shared["origin"] == "NATIVE_SCRATCH_DERIVATION"
    assert shared["parent_proof"]["status"] == "PHYSICAL_PARENT_REDERIVATION_VERIFIED"
    assert shared["local"]["sha256"] == catalogs["4h"]["normalized"]["sha256"]
    assert (
        adapter.evidence.verify(
            output / "recheck",
            *chain,
            requests=workspace / "recheck.requests.json",
            local_root=workspace,
        )["content_sha256"]
        == result["recheck_content_sha256"]
    )
    before = hs._strict_json((evidence / "ideas/00.receipt.json").read_bytes())
    assert before["bases"][0]["local"]["status"] == "NOT_READY"
    for i in range(2):
        receipt = hs._strict_json((output / f"recheck/ideas/{i:02d}.receipt.json").read_bytes())
        assert receipt["bases"][0]["local"]["window_status"] == "WINDOW_VERIFIED"
        assert receipt["bases"][0]["local"]["sha256"] == shared["local"]["sha256"]
        assert (
            receipt["retained"]
            == hs._strict_json((evidence / f"ideas/{i:02d}.receipt.json").read_bytes())["retained"]
        )
    flow = hs._strict_json((output / "recheck/ideas/01.receipt.json").read_bytes())
    assert flow["bases"][0]["feature_table"]["status"] == "LOCAL_FEATURE_TABLE_VERIFIED"
    assert any(g.get("feature") == "funding_rate" for g in result["investigation_queue"])
    assert any(g.get("feature") == "sentiment" for g in result["investigation_queue"])
    assert not any(
        g["code"] == "PHYSICAL_PARENT_REDERIVATION_NOT_PERFORMED"
        for g in result["investigation_queue"]
    )
    assert parent.read_bytes() == original
    assert writes == ["4h"]
    lead = hs._strict_json((output / "recheck/ideas/02.receipt.json").read_bytes())
    assert lead["memory"]["refreshed_memory"]["state"] == "UNKNOWN"
    assert before["memory"]["refreshed_memory"]["state"] == "PRIOR_FAILED_INVESTIGATION"
    for relative in shared["features"].values():
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((workspace / relative).read_bytes())
    supplied = tmp_path / "supplied.json"
    supplied.write_text(
        json.dumps({"windows": {"FLOW": window}, "features": {"4h": shared["features"]}})
    )
    reused = adapter.build(
        tmp_path / "reuse",
        evidence,
        chain,
        tmp_path / "reuse-workspace",
        **{**options, "inventory": supplied},
    )
    reused_flow = hs._strict_json((tmp_path / "reuse/recheck/ideas/01.receipt.json").read_bytes())
    assert reused_flow["bases"][0]["feature_table"] == flow["bases"][0]["feature_table"]
    assert reused["source_bytes"][shared["features"]["feature_csv"]]
    assert writes == ["4h"]
    packet, corpus_hashes = hs._read_tree(output), qp._snapshot(workspace)
    path_open = Path.open

    def read_only(path, mode="r", *args, **kwargs):
        if any(flag in mode for flag in "wax+"):
            assert path.parent.name.startswith("cpw-02c-validate-"), (
                "replay mutated a persistent input/output"
            )
            assert not path.resolve().is_relative_to(de.ROOT)
        return path_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", read_only)
    for _ in range(2):
        assert adapter.verify(output, evidence, chain, workspace, **options) == result
    assert hs._read_tree(output) == packet and qp._snapshot(workspace) == corpus_hashes
    assert not (source / catalogs["4h"]["normalized"]["path"]).exists()
    assert writes == ["4h"]


def test_optional_corpus_absent_and_no_default_effect(chain, tmp_path):
    _, output, _, _, _, result = execute(tmp_path, chain)
    assert result["science_counts"] == {"NOT_READY": 3}
    assert all(s["local"]["status"] == "NOT_READY" for s in result["shared_sources"].values())
    assert result["next_data_investigation"]
    assert (output / "requests.json").is_file()
    run = subprocess.run(
        [sys.executable, "-B", "-m", "tools.hermes.queue_input_preparation"],
        capture_output=True,
        check=False,
    )
    assert run.returncode == 2


@pytest.mark.parametrize("kind", ["extra", "packet", "source", "upstream", "head"])
def test_replay_rejects_changed_inputs(chain, corpus, tmp_path, monkeypatch, kind):
    source, _, parent = corpus
    adapter, output, evidence, workspace, options, _ = execute(tmp_path, chain, local_root=source)
    if kind == "extra":
        (workspace / "extra").write_text("unexpected")
    elif kind == "packet":
        (output / "extra").write_text("unexpected")
    elif kind == "source":
        parent.write_bytes(parent.read_bytes() + b"\n")
    elif kind == "upstream":
        (evidence / "ideas/00.receipt.json").write_text("{}")
    else:
        monkeypatch.setattr(
            sr.RepoIdentity, "resolve", lambda root: sr.RepoIdentity("0" * 40, "drift")
        )
    with pytest.raises((hs.HandoffError, de.dc.ConsumerError)):
        adapter.verify(output, evidence, chain, workspace, **options)


@pytest.mark.parametrize("kind", ["hash", "gap", "truncated", "parent"])
def test_bad_parent_or_derived_bytes_rejected(chain, corpus, tmp_path, kind):
    source, catalogs, parent = corpus
    if kind == "parent":
        catalogs["4h"]["normalized"]["sha256"] = "0" * 64
    elif kind == "hash":
        parent.write_bytes(parent.read_bytes() + b"\n")
    else:
        frame = pd.read_csv(parent)
        frame = frame.drop(index=4) if kind == "gap" else frame.iloc[:-1]
        frame.to_csv(parent, index=False)
        catalogs["15m"]["normalized"]["sha256"] = de.ft._sha256(parent)
    with pytest.raises(hs.HandoffError):
        execute(tmp_path, chain, local_root=source, materialize=True)


@pytest.mark.parametrize(
    "window",
    [
        None,
        {},
        {"start": "2020-01-02", "end": "2020-01-01"},
        {"start": "2020-01-01T00:15:00Z", "end": "2020-01-01T04:00:00Z"},
    ],
)
def test_missing_invalid_unaligned_windows(chain, corpus, tmp_path, window):
    source, _, _ = corpus
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"windows": {"DON": window}} if window is not None else {}))
    if window is not None and window != {
        "start": "2020-01-01T00:15:00Z",
        "end": "2020-01-01T04:00:00Z",
    }:
        with pytest.raises(hs.HandoffError, match="window"):
            execute(tmp_path, chain, local_root=source, inventory=inventory, materialize=True)
    else:
        *_, result = execute(
            tmp_path, chain, local_root=source, inventory=inventory, materialize=True
        )
        assert any(
            g["code"] in {"WINDOW_MISSING", "WINDOW_OUTSIDE_OR_UNALIGNED"}
            for g in result["investigation_queue"]
        )


def test_no_network_science_or_unsafe_native_writer(chain, corpus, tmp_path, monkeypatch):
    from tools.research_autonomy import contract_builder
    from tools.research_domain import preregistration

    def denied(*args, **kwargs):
        pytest.fail("forbidden network/scientific/native CLI writer invocation")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(contract_builder, "construct_contract", denied)
    monkeypatch.setattr(contract_builder.ContractBuilder, "build", denied)
    for name in (
        "build_preregistration_packet",
        "build_approval_requirement",
        "build_approval_marker",
    ):
        monkeypatch.setattr(preregistration, name, denied)
    monkeypatch.setattr(qp.four, "derive_slice", denied)
    monkeypatch.setattr(qp.short, "derive_slice", denied)
    *_, result = execute(tmp_path, chain, local_root=corpus[0], materialize=True)
    assert result["science_status"] == "NOT_READY"


def test_paths_hardlinks_and_repo_writes_refused(tmp_path):
    for relative in ("../escape", "a/../b", "C:/private", "/etc/passwd", "a//b"):
        with pytest.raises(hs.HandoffError):
            de._local(tmp_path, relative)
    real = tmp_path / "real"
    real.write_text("input")
    os.link(real, tmp_path / "hardlink")
    with pytest.raises(hs.HandoffError):
        qp._snapshot(tmp_path)
    with pytest.raises(de.dc.ConsumerError, match="external"):
        de.dc._check_output_target(de.ROOT / "forbidden-02f-output")
    with pytest.raises(hs.HandoffError, match="disjoint"):
        qp._separate(tmp_path, tmp_path / "nested")
    checkout = tmp_path / "another-checkout"
    checkout.mkdir()
    (checkout / ".git").write_text("gitdir: other")
    with pytest.raises(hs.HandoffError, match="Git checkout"):
        qp._external_target(checkout / "forbidden")


def test_cli_build_verify_replay(chain, tmp_path):
    evidence = tmp_path / "02e"
    adapter = de.DataEvidenceResolution()
    hs._publish(adapter.build_files(*chain), evidence, lambda p: adapter.verify(p, *chain))
    args = [
        "--evidence-dir",
        str(evidence),
        "--workspace",
        str(tmp_path / "workspace"),
        "--output",
        str(tmp_path / "02f"),
    ]
    for name, path in zip(("readiness-dir", "built-dir", "prepared-dir", "responses-dir"), chain):
        args.extend(["--" + name, str(path)])
    results = []
    for command in ("build", "verify", "replay"):
        run = subprocess.run(
            [sys.executable, "-B", "-m", "tools.hermes.queue_input_preparation", command, *args],
            capture_output=True,
            text=True,
            check=False,
        )
        assert run.returncode == 0, run.stderr
        results.append(json.loads(run.stdout))
    assert results[0] == results[1] == results[2]
