"""02E SOFTWARE_FIXTURE_PROOF; no model invocation or historical trading evidence."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
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

from tools.data.import_binance_usdtm_15m import OUTPUT_COLUMNS
from tools.hermes import data_evidence_resolution as de
from tools.hermes import intent_strategy_spec_handoff as hs
from tools.hermes import science_readiness as sr


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
        [_idea("DON", native), _idea("FLOW", _native(free_parameter_count=1)), _idea("LOB", None)],
        memory=FrozenMemory(negative={fp}),
    )
    prepared = prepare(tmp_path, batch)
    responses = tmp_path / "responses"
    respond(prepared, responses, 0)
    respond(prepared, responses, 1)
    built, _ = build(tmp_path, prepared, responses)
    adapter = sr.ScienceReadiness()
    output = tmp_path / "02d"
    hs._publish(
        adapter.build_files(built, prepared, responses),
        output,
        lambda p: adapter.verify(p, built, prepared, responses),
    )
    return output, built, prepared, responses


def receipt(files, index=0):
    return json.loads(files[f"ideas/{index:02d}.receipt.json"])


def test_all_ideas_provenance_retention_and_queue(chain):
    files = de.DataEvidenceResolution().build_files(*chain)
    summary = json.loads(files[hs.SUMMARY_FILE])
    assert [i["idea_id"] for i in summary["ideas"]] == ["DON", "FLOW", "LOB"]
    assert (
        summary["counts"][hs.DRAFTED]
        == summary["counts"][hs.UNSUPPORTED]
        == summary["counts"][hs.LEAD]
        == 1
    )
    assert summary["science_counts"] == {"NOT_READY": 3}
    for index in range(3):
        source = json.loads((chain[0] / f"ideas/{index:02d}.receipt.json").read_bytes())
        result = receipt(files, index)
        assert result["science_status"] == "NOT_READY"
        assert result["memory"] == source["memory"]
        for key, value in result["retained"].items():
            assert value == source["source_02b"].get(key)
        assert all(v == "NOT_READY" for v in result["scientific_boundary"].values())
        assert result["next_investigations"]
    assert receipt(files)["memory"]["refreshed_memory"]["state"] == "PRIOR_FAILED_INVESTIGATION"
    assert receipt(files, 2)["memory"]["refreshed_memory"]["state"] == "UNKNOWN"
    assert receipt(files)["native_research_memory"]["records"][0]["classification"] == "NO-GO"
    result = receipt(files)
    assert result["bases"][0]["timeframe"] == "4h"
    assert result["bases"][0]["catalog"]["parent"]["data_slice_identity"].startswith(
        "binance_usdtm_btcusdt_ohlcv_15m:"
    )
    assert result["bases"][0]["metadata_status"] == "REPOSITORY_METADATA_VERIFIED_ONLY"
    assert result["bases"][0]["local"]["status"] == "NOT_READY"
    assert summary["metadata_sources"][de.AVAILABILITY]["sha256"]
    assert {g["idea_id"] for g in summary["investigation_queue"]} == {"DON", "FLOW", "LOB"}


@pytest.mark.parametrize("tf", de.TIMEFRAMES)
def test_real_committed_five_timeframe_metadata(tf):
    adapter = de.DataEvidenceResolution()
    catalog = adapter._catalog(tf)
    assert catalog["timeframe"] == tf and catalog["symbol"] == "BTCUSDT"
    assert ("parent" in catalog) == (tf in ("30m", "1h", "4h"))
    for path, identity in adapter.sources.items():
        raw = adapter.readiness.git.blob(path)
        assert de.dc._sha256_bytes(raw) == identity["sha256"]


def synthetic(tmp_path):
    # Explicit disposable D2-format engineering data, never committed market history.
    index = pd.date_range("2020-01-01", periods=4, freq="15min", tz="UTC")
    rows = []
    for ts in index:
        ms = ts.value // 1_000_000
        row = {
            "open_time_ms": ms,
            "open_time": ts.isoformat().replace("+00:00", "Z"),
            "open": "100",
            "high": "102",
            "low": "99",
            "close": "101",
            "volume": "10",
            "close_time_ms": ms + 900000 - 1,
            "quote_asset_volume": "1000",
            "num_trades": "4",
            "taker_buy_base_vol": "6",
            "taker_buy_quote_vol": "600",
            "ignore": "0",
        }
        rows.append(row)
    path = tmp_path / "synthetic.csv"
    pd.DataFrame(rows, columns=OUTPUT_COLUMNS).to_csv(path, index=False)
    catalog = {
        "timeframe": "15m",
        "normalized": {"sha256": de.ft._sha256(path)},
        "range": {
            "row_count": 4,
            "start_utc": "2020-01-01T00:00:00Z",
            "end_utc": "2020-01-01T00:45:00Z",
        },
    }
    return path, catalog


def test_native_positive_window_and_no_larger_history_claim(tmp_path):
    path, catalog = synthetic(tmp_path)
    window = {"start": "2020-01-01T00:15:00Z", "end": "2020-01-01T00:45:00Z"}
    result, frame = de.inspect_local(catalog, path, window)
    assert result["status"] == "LOCAL_BYTES_VERIFIED"
    assert result["window_status"] == "WINDOW_VERIFIED" and result["window_rows"] == 2
    assert result["native_validation"].endswith("validate_frame")
    assert len(frame) == 4
    result, _ = de.inspect_local(catalog, path, {**window, "end": "2020-01-02T00:00:00Z"})
    assert result["window_status"] == "NOT_READY"
    assert "WINDOW_OUTSIDE_OR_UNALIGNED" in result["gaps"]
    result, _ = de.inspect_local(catalog, path, None)
    assert "WINDOW_MISSING" in result["gaps"]


def test_local_digest_and_grid_tamper_fail_closed(tmp_path):
    path, catalog = synthetic(tmp_path)
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(hs.HandoffError, match="digest"):
        de.inspect_local(catalog, path, None)
    frame = pd.read_csv(path)
    frame.loc[1, "open_time_ms"] = frame.loc[0, "open_time_ms"]
    frame.to_csv(path, index=False)
    catalog["normalized"]["sha256"] = de.ft._sha256(path)
    with pytest.raises(hs.HandoffError, match="D3"):
        de.inspect_local(catalog, path, None)


@pytest.mark.parametrize(
    "relative", ["../outside.csv", "C:/private.csv", "/tmp/a", "a/../x", "a:stream", "a//b"]
)
def test_no_read_outside_admitted_root(tmp_path, relative):
    with pytest.raises(hs.HandoffError):
        de._local(tmp_path, relative)


def test_links_and_hardlinks_rejected(tmp_path):
    target = tmp_path / "target"
    target.write_text("private")
    link = tmp_path / "hardlink"
    os.link(target, link)
    with pytest.raises(hs.HandoffError, match="unlinked"):
        de._local(tmp_path, "hardlink")


def test_missing_bytes_and_source_substitution(chain, tmp_path):
    request = tmp_path / "requests.json"
    request.write_text(json.dumps({"DON": {"sources": {"4h": {"path": "diagnostic.parquet"}}}}))
    adapter = de.DataEvidenceResolution()
    with pytest.raises(hs.HandoffError, match="alternate"):
        adapter.build_files(*chain, requests=request, local_root=tmp_path)
    files = adapter.build_files(*chain, local_root=tmp_path)
    assert "LOCAL_SOURCE_MISSING" in receipt(files)["bases"][0]["local"]["gaps"]


def test_replay_tamper_and_stale(chain, tmp_path, monkeypatch):
    adapter = de.DataEvidenceResolution()
    output = tmp_path / "02e"
    hs._publish(adapter.build_files(*chain), output, lambda p: adapter.verify(p, *chain))
    assert adapter.verify(output, *chain)["schema_version"] == de.SCHEMA
    path = output / "ideas/00.receipt.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(hs.HandoffError, match="inventory"):
        adapter.verify(output, *chain)
    source = chain[0] / "ideas/00.receipt.json"
    source.write_bytes(source.read_bytes() + b" ")
    with pytest.raises(hs.HandoffError):
        adapter.build_files(*chain)


def test_stale_head_rejected(chain, monkeypatch):
    adapter = de.DataEvidenceResolution()
    identity = sr.RepoIdentity("0" * 40, "drift")
    monkeypatch.setattr(sr.RepoIdentity, "resolve", lambda root: identity)
    with pytest.raises(hs.HandoffError, match="HEAD changed"):
        adapter.build_files(*chain)


def test_no_network_or_runtime_call(chain, monkeypatch):
    def denied(*args, **kwargs):
        pytest.fail("network contact is forbidden")

    from tools.research_autonomy import contract_builder
    from tools.research_domain import preregistration

    for name in (
        "build_preregistration_packet",
        "build_approval_requirement",
        "build_approval_marker",
    ):
        monkeypatch.setattr(preregistration, name, denied)
    monkeypatch.setattr(contract_builder, "construct_contract", denied)
    monkeypatch.setattr(contract_builder.ContractBuilder, "build", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    files = de.DataEvidenceResolution().build_files(*chain)
    assert files
    # The only direct subprocess ownership is inherited exact Git blob/HEAD reads.
    import ast

    tree = ast.parse(Path(de.__file__).read_text(encoding="utf-8-sig"))
    imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert not any("runner" in name or "autonomy" in name or "runtime" in name for name in imports)


def test_cli_build_verify_replay(chain, tmp_path):
    output = tmp_path / "cli"
    args = [
        "--readiness-dir",
        str(chain[0]),
        "--built-dir",
        str(chain[1]),
        "--prepared-dir",
        str(chain[2]),
        "--responses-dir",
        str(chain[3]),
        "--output",
        str(output),
    ]
    results = []
    for command in ("build", "verify", "replay"):
        run = subprocess.run(
            [sys.executable, "-B", "-m", "tools.hermes.data_evidence_resolution", command, *args],
            cwd=de.ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert run.returncode == 0, run.stderr
        results.append(json.loads(run.stdout))
    assert results[0] == results[1] == results[2]


@pytest.mark.parametrize(
    ("feature", "kind"),
    [
        ("ohlcv", "OHLCV_BUILTIN"),
        ("donchian", "INDICATOR_CATALOG"),
        ("funding_rate", "CONDITIONAL_HISTORY"),
        ("taker_buy_volume", "CONDITIONAL_HISTORY"),
        ("open_interest", "RECENT_SNAPSHOT_VENDOR_ONLY"),
        ("liquidation_volume", "RECENT_SNAPSHOT_VENDOR_ONLY"),
        ("sentiment", "UNRECOGNIZED"),
    ],
)
def test_feature_suitability_never_invents_history(feature, kind):
    adapter = de.DataEvidenceResolution()
    result = de.assess_feature(
        feature,
        adapter._metadata(de.AVAILABILITY)["entries"],
        adapter._metadata(de.INDICATORS)["entries"],
    )
    assert result["kind"] == kind
    assert result["status"] == "NOT_READY"
    if feature == "taker_buy_volume":
        assert {r["source_class"] for r in result["availability_rows"]} >= {
            "CANONICAL_D4_KLINE_DERIVATION",
            "CANONICAL_KLINE_TAKERFLOW_DERIVATION",
        }


def test_native_feature_positive_parent_and_timing_negatives(tmp_path):
    from test_research_feature_table import _generic_fixture

    kwargs = _generic_fixture(tmp_path, "30m")
    catalog = {
        "timeframe": "30m",
        "slice_identity": {"data_slice_identity": kwargs["base_data_slice_identity"]},
    }
    local = {
        "sha256": kwargs["base_normalized_sha256"],
        "coverage_start": kwargs["base_coverage_start_utc_inclusive"],
        "coverage_end_exclusive": kwargs["base_coverage_end_utc_exclusive"],
    }
    inputs = (
        catalog,
        local,
        kwargs["base_frame"],
        kwargs["base_input_path"],
        kwargs["feature_manifest_path"],
        kwargs["feature_csv_path"],
        kwargs["requested_feature_names"],
    )
    result = de.inspect_features(*inputs)
    assert result["status"] == "LOCAL_FEATURE_TABLE_VERIFIED"
    catalog["slice_identity"]["data_slice_identity"] = (
        "binance_usdtm_btcusdt_ohlcv_30m:sha256:" + "3" * 64
    )
    with pytest.raises(de.ft.ResearchFeatureTableError, match="parent identity"):
        de.inspect_features(*inputs)
    catalog["slice_identity"]["data_slice_identity"] = kwargs["base_data_slice_identity"]
    csv = kwargs["feature_csv_path"]
    csv.write_bytes(csv.read_bytes() + b" ")
    with pytest.raises(de.ft.ResearchFeatureTableError, match="SHA-256"):
        de.inspect_features(*inputs)


def test_symlink_or_junction_refused(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "linked"
    try:
        os.symlink(real, link, target_is_directory=True)
    except OSError:
        if os.name != "nt":
            raise
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(real)], capture_output=True, check=True
        )
    with pytest.raises(hs.HandoffError, match="symlink|junction"):
        de._local(link, "nonexistent.csv")


@pytest.mark.parametrize(
    "window",
    [
        {"start": "2020-01-01", "end": "2020-01-02"},
        {"start": "2020-01-02T00:00:00Z", "end": "2020-01-01T00:00:00Z"},
    ],
)
def test_invalid_window_fails_closed(tmp_path, window):
    path, catalog = synthetic(tmp_path)
    with pytest.raises(hs.HandoffError, match="window"):
        de.inspect_local(catalog, path, window)


def test_no_default_command_has_no_effect(tmp_path):
    run = subprocess.run(
        [sys.executable, "-B", "-m", "tools.hermes.data_evidence_resolution"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(de.ROOT)},
        capture_output=True,
        check=False,
    )
    assert run.returncode == 2
    assert list(tmp_path.iterdir()) == []
