"""SOFTWARE_FIXTURE_PROOF: current-head chain, fixed synthetic values, no science."""

from __future__ import annotations

import copy
import json
import os
import socket
import subprocess
import sys

import pandas as pd
import pytest
import test_hermes_queue_input_preparation as fixtures

from tools.hermes import verified_data_signal_bridge as bridge

qp, de, hs = bridge.qp, bridge.de, bridge.hs


@pytest.fixture(scope="module")
def prepared(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("02g-software-fixture")
    patch = pytest.MonkeyPatch()
    chain = fixtures.chain.__wrapped__(tmp_path)
    corpus = fixtures.corpus.__wrapped__(tmp_path, patch)
    source, catalogs, parent = corpus
    frame = pd.read_csv(parent, dtype=str)
    frame = pd.concat([frame] * 64, ignore_index=True)
    index = pd.date_range("2020-01-01", periods=len(frame), freq="15min", tz="UTC")
    frame["open_time"] = [ts.isoformat().replace("+00:00", "Z") for ts in index]
    frame["open_time_ms"] = [ts.value // 1_000_000 for ts in index]
    frame["close_time_ms"] = frame["open_time_ms"] + 899999
    frame.to_csv(parent, index=False, lineterminator="\n")
    end = index[-1] + pd.Timedelta(minutes=15)
    for tf, rows, last in (
        ("15m", len(frame), index[-1]),
        ("4h", len(frame) // 16, end - pd.Timedelta(hours=4)),
    ):
        catalogs[tf]["range"].update(
            row_count=rows, end_utc=last.isoformat().replace("+00:00", "Z")
        )
    catalogs["15m"]["normalized"]["sha256"] = de.ft._sha256(parent)
    derived = qp._derived_bytes(parent, "4h")
    catalogs["4h"]["normalized"]["sha256"] = de.dc._sha256_bytes(derived)
    catalogs["4h"]["parent"]["normalized_sha256"] = de.ft._sha256(parent)
    qp.taker.CANONICAL_KLINE_PARENT_CONFIG["4h"].update(
        sha256=de.dc._sha256_bytes(derived),
        row_count=len(frame) // 16,
        coverage_end=end.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    )
    window = {"start": "2020-01-01T00:00:00Z", "end": end.isoformat().replace("+00:00", "Z")}
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"windows": {key: window for key in ("DON", "FLOW")}}))
    _, output, evidence, workspace, options, result = fixtures.execute(
        tmp_path, chain, local_root=source, inventory=inventory, materialize=True
    )
    designation = tmp_path / "designation.json"
    designation.write_bytes(
        hs._json_bytes(
            {
                "purpose": "ENGINEERING_VALIDATION_ONLY",
                "label": bridge.FIXTURE,
                "source_02f": result["content_sha256"],
                "fixture_recipe": "fixed_15m_v1",
                "windows": {
                    key: {
                        **window,
                        "timeframe": "4h",
                        "source_sha256": de.dc._sha256_bytes(derived),
                    }
                    for key in ("DON", "FLOW")
                },
            }
        )
    )
    yield (output, evidence, chain, workspace), {**options, "designation": designation}
    patch.undo()


@pytest.fixture(autouse=True)
def restore_inputs(prepared):
    root = prepared[0][0].parent
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    yield
    for path, raw in before.items():
        if path.read_bytes() != raw:
            path.write_bytes(raw)


def build(prepared, tmp_path):
    inputs, options = prepared
    adapter = bridge.VerifiedDataSignalBridge()
    output = tmp_path / "02g"
    result = adapter.build(output, *inputs, **options)
    return adapter, output, result


def test_mixed_fixture_real_native_compiler_and_immutable_replay(prepared, tmp_path, monkeypatch):
    inputs, options = prepared
    before = [
        qp._snapshot(p)
        for p in (inputs[0], inputs[1], *inputs[2], inputs[3], options["local_root"])
    ]
    calls = []
    native = bridge.compiler.compile_signal

    def observed(spec, assignment, frame):
        calls.append(frame.copy())
        assert list(frame.columns) == list(bridge.OHLCV)
        assert len(frame) == 64 and frame.index.tz is not None
        return native(spec, assignment, frame)

    monkeypatch.setattr(bridge.compiler, "compile_signal", observed)
    adapter, output, result = build(prepared, tmp_path)
    assert [i["idea_id"] for i in result["ideas"]] == ["DON", "FLOW", "LOB"]
    assert [i["status"] for i in result["ideas"]] == [
        "PASS",
        "NOT_READY_NO_ELIGIBLE_DRAFT",
        "NOT_READY_NO_ELIGIBLE_DRAFT",
    ]
    check = result["ideas"][0]["compilations"][0]
    assert check["rows"] == 64 and len(check["signal_sha256"]) == 64
    assert result["label"] == bridge.FIXTURE
    assert (
        result["science_status"] == "NOT_READY"
        and result["search_contract_status"] == "NOT_ISSUABLE"
    )
    retained = result["ideas"][0]["source_02e_recheck"]
    assert retained["memory"]["refreshed_memory"]["state"] == "PRIOR_FAILED_INVESTIGATION"
    assert retained["scientific_boundary"] and result["investigation_queue"]
    flow = result["ideas"][1]["source_02e_recheck"]
    assert any(f["feature"] == "sentiment" and f["status"] == "NOT_READY" for f in flow["features"])
    assert (
        result["ideas"][2]["source_02e_recheck"]["memory"]["refreshed_memory"]["state"] == "UNKNOWN"
    )
    hashes = qp._snapshot(output)
    for _ in range(2):
        assert adapter.verify(output, *inputs, **options) == result
        assert qp._snapshot(output) == hashes
    assert calls and len(calls) == 4  # build, publication verification, two replays
    assert before == [
        qp._snapshot(p)
        for p in (inputs[0], inputs[1], *inputs[2], inputs[3], options["local_root"])
    ]
    assert "signal_values" not in (output / hs.SUMMARY_FILE).read_text()
    print(
        "FIXTURE_EVIDENCE="
        + json.dumps(
            {
                "content_sha256": result["content_sha256"],
                "source_02f": result["source_02f"],
                "signal_sha256": check["signal_sha256"],
                "rows": check["rows"],
                "population": [i["idea_id"] for i in result["ideas"]],
                "packet_hashes": hashes,
            },
            sort_keys=True,
        )
    )


@pytest.mark.parametrize(
    "kind", ["absent", "historical", "unbound", "wrong_window", "extra", "fake_recipe"]
)
def test_designation_refusal_before_compiler(prepared, tmp_path, monkeypatch, kind):
    inputs, options = prepared
    options = dict(options)
    path = options["designation"]
    value = hs._strict_json(path.read_bytes())
    if kind == "absent":
        options["designation"] = None
    elif kind == "historical":
        value.update(label="HISTORICAL", fixture_recipe=None)
    elif kind == "unbound":
        value["source_02f"] = "0" * 64
    elif kind == "wrong_window":
        value["windows"]["DON"]["start"] = "2020-01-02T00:00:00Z"
    elif kind == "extra":
        value["holdout_approved"] = True
    else:
        value["fixture_recipe"] = "self_label"
    path.write_bytes(hs._json_bytes(value))
    monkeypatch.setattr(
        bridge.compiler,
        "compile_signal",
        lambda *a: pytest.fail("02G compiler called across refused window"),
    )
    if kind in ("absent", "historical"):
        result = bridge.VerifiedDataSignalBridge().build(tmp_path / "02g", *inputs, **options)
        assert result["ideas"][0]["status"] == "NOT_READY_NON_HOLDOUT_WINDOW_UNVERIFIED"
    else:
        with pytest.raises(hs.HandoffError):
            bridge.VerifiedDataSignalBridge().build(tmp_path / "02g", *inputs, **options)


@pytest.mark.parametrize("kind", ["02f", "02e", "draft", "response", "csv", "feature", "head"])
def test_exact_upstream_integrity(prepared, tmp_path, monkeypatch, kind):
    inputs, options = prepared
    if kind == "head":
        monkeypatch.setattr(
            bridge.sr.RepoIdentity,
            "resolve",
            lambda root: bridge.sr.RepoIdentity("0" * 40, "drift"),
        )
    else:
        paths = {
            "02f": inputs[0] / hs.SUMMARY_FILE,
            "02e": inputs[1] / hs.SUMMARY_FILE,
            "draft": next((inputs[2][1] / "drafts").rglob("*.json")),
            "response": inputs[2][3] / "00.response.json",
            "csv": de._local(
                inputs[3],
                hs._strict_json((inputs[0] / hs.SUMMARY_FILE).read_bytes())["shared_sources"]["4h"][
                    "path"
                ],
            ),
            "feature": inputs[3] / "features/4h.csv",
        }
        path = paths[kind]
        path.write_bytes(path.read_bytes() + b" ")
    monkeypatch.setattr(
        bridge.compiler,
        "compile_signal",
        lambda *a: pytest.fail("compiler before integrity verification"),
    )
    with pytest.raises((hs.HandoffError, de.dc.ConsumerError)):
        bridge.VerifiedDataSignalBridge().build(tmp_path / "02g", *inputs, **options)


def test_native_warmup_and_no_padding(prepared, tmp_path):
    inputs, options = prepared
    adapter = bridge.VerifiedDataSignalBridge()
    upstream = hs._strict_json((inputs[0] / hs.SUMMARY_FILE).read_bytes())
    retained = hs._strict_json((inputs[0] / upstream["ideas"][0]["receipt"]).read_bytes())
    built = hs._strict_json((inputs[2][1] / hs.SUMMARY_FILE).read_bytes())
    draft = built["ideas"][0]["drafts"][0]
    spec = hs._strict_json((inputs[2][1] / draft["file"]).read_bytes())
    # A valid but insufficient explicit window, without modifying the admitted source.
    retained = copy.deepcopy(retained)
    retained["requested_window"]["end"] = "2020-01-01T08:00:00Z"
    selected = hs._strict_json(options["designation"].read_bytes())
    selected["windows"]["DON"]["end"] = "2020-01-01T08:00:00Z"
    result = adapter._compile(spec, draft, retained, upstream, inputs[3], selected, True, {})
    assert result["status"] == "NOT_READY_GENUINE_WARMUP_REQUIRED"
    assert "signal_sha256" not in result


def test_fabricated_host_feature_not_backfilled(prepared):
    inputs, _options = prepared
    upstream = hs._strict_json((inputs[0] / hs.SUMMARY_FILE).read_bytes())
    retained = hs._strict_json((inputs[0] / upstream["ideas"][0]["receipt"]).read_bytes())
    retained["features"].append({"feature": "sentiment", "status": "NOT_READY"})
    built = hs._strict_json((inputs[2][1] / hs.SUMMARY_FILE).read_bytes())
    draft = built["ideas"][0]["drafts"][0]
    spec = hs._strict_json((inputs[2][1] / draft["file"]).read_bytes())
    result = bridge.VerifiedDataSignalBridge()._compile(
        spec, draft, retained, upstream, inputs[3], {}, False, {}
    )
    assert result["status"] == "NOT_READY_REQUIRED_FEATURE_EVIDENCE"


def test_native_feature_join_uses_fixture_parent_and_completed_bars(prepared, monkeypatch):
    inputs, options = prepared
    upstream = hs._strict_json((inputs[0] / hs.SUMMARY_FILE).read_bytes())
    retained = hs._strict_json((inputs[0] / upstream["ideas"][0]["receipt"]).read_bytes())
    flow = hs._strict_json((inputs[0] / upstream["ideas"][1]["receipt"]).read_bytes())
    retained["features"].extend(f for f in flow["features"] if f["feature"] in qp.TAKER)
    built = hs._strict_json((inputs[2][1] / hs.SUMMARY_FILE).read_bytes())
    draft = built["ideas"][0]["drafts"][0]
    spec = hs._strict_json((inputs[2][1] / draft["file"]).read_bytes())
    selected = hs._strict_json(options["designation"].read_bytes())
    native = de.ft.resolve_research_feature_table
    observed = []

    def resolve(**kwargs):
        result = native(**kwargs)
        assert result.joined_frame["taker_buy_volume"].eq(96.0).all()
        assert result.joined_frame["taker_sell_volume"].eq(64.0).all()
        observed.append(result.feature_table_identity)
        return result

    monkeypatch.setattr(de.ft, "resolve_research_feature_table", resolve)
    result = bridge.VerifiedDataSignalBridge()._compile(
        spec, draft, retained, upstream, inputs[3], selected, True, {}
    )
    assert observed and result["status"] == "PASS"


def test_fixture_label_requires_actual_fixed_values(prepared, tmp_path):
    inputs, _options = prepared
    shared = hs._strict_json((inputs[0] / hs.SUMMARY_FILE).read_bytes())["shared_sources"]
    parent = de._local(inputs[3], shared["15m"]["path"])
    altered = pd.read_csv(parent, dtype=str)
    altered.loc[0, "close"] = "100.5"
    fake = tmp_path / "parent.csv"
    altered.to_csv(fake, index=False)
    shared["15m"]["path"] = fake.name
    assert not bridge._fixture_parent(shared, tmp_path)


def test_packet_byte_tamper_and_output_overlap(prepared, tmp_path):
    inputs, options = prepared
    adapter, output, _ = build(prepared, tmp_path)
    path = output / hs.SUMMARY_FILE
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(hs.HandoffError):
        adapter.verify(output, *inputs, **options)
    with pytest.raises(hs.HandoffError, match="disjoint"):
        adapter.build(inputs[3] / "nested", *inputs, **options)
    link = tmp_path / "designation-link"
    os.link(options["designation"], link)
    try:
        with pytest.raises(hs.HandoffError, match="unlinked"):
            adapter.build(tmp_path / "other", *inputs, **options)
    finally:
        link.unlink()


def test_no_network_science_model_or_trading(prepared, tmp_path, monkeypatch):
    from tools.research_autonomy import contract_builder
    from tools.research_domain import preregistration

    def denied(*args, **kwargs):
        pytest.fail("forbidden network/scientific operation")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(contract_builder, "construct_contract", denied)
    monkeypatch.setattr(contract_builder.ContractBuilder, "build", denied)
    monkeypatch.setattr(preregistration, "build_preregistration_packet", denied)
    _, _, result = build(prepared, tmp_path)
    assert result["ideas"][0]["status"] == "PASS"


def test_cli_default_off_and_missing_corpus(tmp_path, capsys):
    chain = fixtures.chain.__wrapped__(tmp_path)
    run = subprocess.run(
        [sys.executable, "-B", "-m", "tools.hermes.verified_data_signal_bridge"],
        capture_output=True,
        check=False,
    )
    assert run.returncode == 2
    _, preparation, evidence, workspace, _, _ = fixtures.execute(tmp_path, chain)
    args = [
        "--output",
        str(tmp_path / "02g"),
        "--preparation-dir",
        str(preparation),
        "--evidence-dir",
        str(evidence),
        "--workspace",
        str(workspace),
    ]
    for name, path in zip(("readiness-dir", "built-dir", "prepared-dir", "responses-dir"), chain):
        args.extend(["--" + name, str(path)])
    results = []
    for command in ("build", "verify", "replay"):
        # Fixture catalogs are process-local; exercise CLI parsing in that same process.
        assert bridge.main([command, *args]) == 0
        results.append(json.loads(capsys.readouterr().out))
    assert results[0] == results[1] == results[2]
