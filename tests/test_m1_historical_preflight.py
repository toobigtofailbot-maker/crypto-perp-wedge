"""Metadata and pre-read negatives. This suite never invokes a real trial."""

import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from test_research_factory_mapper import factory_fixture
from tools.data_ingestion.ccxt_public_funding_adapter import FUNDING_INTERVAL_MS, normalize_raw_row
from tools.lab_pipeline import runner_adapter
from tools.research_autonomy import historical_source_gate as gate
from tools.research_autonomy.m1_source import CADENCE, M1_REAL_MAPPING, M1_REAL_ROOT, M1_REAL_VERSION, M1HistoricalSource, M1Source
from tools.research_factory import mapper
from tools.research_factory.evidence import EvidenceBlocked, verify_commitment, verify_m1_historical_preparation
from tools.research_factory.manual_loop import manual_research_loop
from tools.research_runner import run_offline_sweep as runner
from tools.research_search.contract import SplitProtocol

ROOT = Path(__file__).resolve().parents[1]
START = 1577836800000
DAY = 86_400_000
END = START + 31 * DAY
WINDOW = {"start_ms": START, "end_ms": END}
HASH = "sha256:" + "a" * 64
OTHER = "sha256:" + "b" * 64
DEV_WINDOW = "2020-01-01T00:00:00Z/2020-02-01T00:00:00Z"


def source_for(symbol, clock):
    return M1HistoricalSource.model_validate({
        "schema_version": M1_REAL_VERSION, "classification": "HISTORICAL_CANDIDATE",
        "instrument": symbol, "timeframe": clock, "venue": "Binance USDT-M",
        "market_type": "perpetual", "quote_and_margin_asset": "USDT",
        "epoch_id": "FIXTURE-EPOCH", "epoch_window": WINDOW, "effective_window": WINDOW,
        "ohlcv_sha256": HASH, "funding_sha256": OTHER,
        "funding_source": "BINANCE_USDM_PUBLIC_FUNDING_HISTORY",
        "variant_manifest_sha256": mapper.file_hash(ROOT / mapper.SOURCE_VM),
        "sweep_plan_id": "SWEEP-PLAN-0003", "sweep_plan_sha256": mapper.file_hash(ROOT / mapper.SOURCE_SWEEP),
        "provenance_sha256": HASH, "epoch_evidence_sha256": HASH, "terms_evidence_sha256": HASH,
        "gate_c_approval_sha256": HASH,
        "in_sample": {"start_ms": START + 7 * DAY, "end_ms": START + 20 * DAY},
        "out_of_sample": {"start_ms": START + 22 * DAY, "end_ms": END},
        "costs": {"qualification": "HISTORICAL_EVIDENCE_REQUIRED", "fee_epoch": WINDOW,
                  "fee_schedule_sha256": HASH, "slippage_model_sha256": HASH,
                  "funding_notional_approval_sha256": HASH, "funding_notional": "entry_price",
                  "fee_bps_taker": 5.0, "fee_bps_maker": 2.0, "slippage_bps": 1.0},
    })


def public_objects(source):
    """Synthetic bytes with the public-source wire format and observed event offsets."""
    common = {"classification": source.classification, "instrument": source.instrument, "epoch_id": source.epoch_id}
    step = CADENCE[source.timeframe]
    klines = [[ts, "1", "3", "0.5", "2", "5", ts + step - 1, "7", 2, "1", "2", "0"]
              for ts in range(START, END, step)]
    events = [normalize_raw_row(
        {"symbol": source.instrument, "fundingTime": ts + 2, "fundingRate": "-0.0001"},
        page_index=0, row_index=i, expected_symbol=source.instrument,
    ) for i, ts in enumerate(range(START, END, FUNDING_INTERVAL_MS))]
    return tuple(json.dumps(payload).encode() for payload in (
        common | {"timeframe": source.timeframe, "rows": klines}, common | {"rows": events},
    ))


@pytest.mark.parametrize(("symbol", "clock"), [
    ("BTCUSDT", "15m"), ("BTCUSDT", "1h"), ("ETHUSDT", "15m"), ("ETHUSDT", "1h"), ("SOLUSDT", "1h"),
])
def test_versioned_candidate_exact_symbol_clock_and_protocol(symbol, clock):
    source = source_for(symbol, clock)
    assert source.identity.startswith("M1-HISTORICAL-")
    spec = json.loads((ROOT / mapper.SOURCE_SPEC).read_text())
    spec = json.loads(json.dumps(spec).replace("BTCUSDT", symbol).replace("15m", clock))
    source.require_spec(spec)
    source.require_protocol(SimpleNamespace(purge_bars=24, embargo_bars=24))
    with pytest.raises(ValueError, match="purge/embargo"):
        source.require_protocol(SimpleNamespace(purge_bars=1000, embargo_bars=1000))
    spec["instruments"]["symbols"] = ["OTHERUSDT"]
    with pytest.raises(ValueError, match="instrument or clock"):
        source.require_spec(spec)
    with pytest.raises(ValidationError):
        M1Source.model_validate(source.model_dump())


@pytest.mark.parametrize("field", ["epoch_window", "out_of_sample", "costs"])
def test_candidate_refuses_missing_epoch_coverage_oos_and_fee_epoch(field):
    raw = source_for("ETHUSDT", "1h").model_dump()
    if field == "costs":
        raw["costs"]["fee_epoch"] = {"start_ms": START + DAY, "end_ms": END}
    else:
        raw[field]["end_ms"] -= DAY
    with pytest.raises(ValidationError, match="frozen IS/OOS"):
        M1HistoricalSource.model_validate(raw)


def test_historical_candidate_reaches_mapper_and_stops_at_all_native_entrypoints(tmp_path, monkeypatch):
    source = source_for("BTCUSDT", "15m")
    objects = public_objects(source)
    price_hash, funding_hash = ("sha256:" + hashlib.sha256(raw).hexdigest() for raw in objects)
    source = M1HistoricalSource.model_validate(source.model_dump() | {
        "ohlcv_sha256": price_hash, "funding_sha256": funding_hash,
    })
    root, store, contract, handoff = factory_fixture(
        tmp_path, data_identity=source.identity, data_version=M1_REAL_VERSION,
        split_protocol=SplitProtocol("M1-PLAN", source.identity, DEV_WINDOW, "UNOPENED-HOLDOUT"),
    )
    args = dict(store=store, handoff=handoff, contract=contract, repo_root=root,
                output_root=root / M1_REAL_ROOT / "prepared", created_at_utc="2026-11-08T00:00:00Z")
    prepared = mapper.prepare_wave(**args, m1_source=source)
    assert prepared["schema_version"] == M1_REAL_MAPPING
    assert prepared["runner_authority"] is False
    assert len(prepared["mapping"]) == prepared["scientific_denominator"] == 2

    def forbidden(*args, **kwargs):
        pytest.fail("unapproved M1 entered source/runner or durable terminal path")

    monkeypatch.setattr(runner, "_load_ohlcv_input", forbidden)
    monkeypatch.setattr(runner, "_build_result_population", forbidden)
    monkeypatch.setattr(store, "load_trial_result", forbidden)
    monkeypatch.setattr(runner_adapter, "REPO_ROOT", root)
    monkeypatch.setattr(runner_adapter, "_ordinary_input", forbidden)
    spec, vm, sweep = (root / prepared["paths"][name] for name in ("spec", "vm", "sweep"))
    with pytest.raises(runner_adapter.RunnerAdapterError, match=gate.M1_REAL_BLOCK):
        runner_adapter._route_before_read(spec)
    with pytest.raises(runner.OfflineSweepError, match=gate.M1_REAL_BLOCK):
        runner.run_offline_sweep(spec, vm, sweep, canonical_15m=True)
    result = manual_research_loop(
        store=store, handoff=handoff, repo_root=root, preparation_root=args["output_root"],
        output_root=root / M1_REAL_ROOT / "output", created_at_utc=args["created_at_utc"], human_invocation=True,
    )
    assert result["withholding_reasons"] == [gate.M1_REAL_BLOCK]
    assert result["runner_calls"] == 0
    with pytest.raises(EvidenceBlocked, match="requires an approved"):
        verify_commitment(root, {}, contract)

    request = {
        "schema_version": gate.M1_REAL_SCHEMA, "purpose": "m1_historical_study_read",
        "repository": "toobigtofailbot-maker/crypto-perp-wedge", "repo_sha": contract.repo_sha,
        "campaign_id": contract.campaign_id, "search_id": contract.search_id,
        "contract_hash": contract.contract_hash, "strategy_spec_hash": contract.strategy_spec_hash,
        "original_parent_sha256": contract.strategy_spec_hash, "contamination_domain_id": "DOMAIN",
        "holdout_id": "UNOPENED-HOLDOUT", "envelope_sha256": contract.envelope_content_sha256,
        "protocol_sha256": HASH, "data_identity": source.identity, "data_version": M1_REAL_VERSION,
        "instrument": source.instrument, "venue": source.venue, "market": source.market_type,
        "timeframe": source.timeframe, "effective_window": WINDOW, "label_horizon_bars": 0,
        "fitting": "none", "storage": "windows_share_deny_write_v1", "source": source.model_dump(mode="json"),
        "owner_execution_marker_sha256": HASH,
        "objects": [{"byte_length": len(raw), "device": 1, "inode": 1, "role": role,
                     "sha256": digest, "repo_path": f"{M1_REAL_ROOT}sources/cell/{role}.json"}
                    for role, digest, raw in zip(gate.M1_ROLES, (price_hash, funding_hash), objects, strict=True)],
    }
    bound = gate.M1HistoricalRequest.model_validate_json(json.dumps(request))
    replayed, coverage = runner_adapter.preflight_m1_historical_adapter(
        store=store, handoff=handoff, contract=contract, repo_root=root,
        preparation_root=args["output_root"], created_at_utc=args["created_at_utc"],
        request=bound, public_objects=objects,
    )
    assert replayed == prepared
    assert coverage == {"bars": 31 * 96, "funding_events": 31 * 3,
                        "missing_settlement_marks": 31 * 3, "nonzero_settlement_offsets": 31 * 3}
    with pytest.raises(runner.OfflineSweepError, match="bytes differ"):
        verify_m1_historical_preparation(root, prepared, contract, bound, objects[::-1])
    with pytest.raises(EvidenceBlocked, match="candidate preparation required"):
        verify_m1_historical_preparation(root, prepared | {"runner_authority": True}, contract, bound, objects)
    with pytest.raises(runner.OfflineSweepError, match="TEST_ONLY source required"):
        runner._m1_fixture_execution_input(source, objects)
    monkeypatch.setattr(gate, "_lease", forbidden)
    reader = gate.HistoricalSourceGate(store, root)
    kwargs = dict(attestation=None, envelope=None, contract=contract, repo_sha=contract.repo_sha)
    with pytest.raises(gate.Refused, match=gate.M1_REAL_BLOCK):
        reader.authorize(request=request, **kwargs)
    swapped = copy.deepcopy(request)
    swapped["objects"][0]["sha256"] = OTHER
    with pytest.raises(gate.Refused, match=gate.REFUSAL):
        reader.authorize(request=swapped, **kwargs)
