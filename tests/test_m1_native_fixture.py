"""M1 native pipeline over generated fixtures and isolated disposable PostgreSQL."""

import copy
import json
import math
import subprocess
import time
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from psycopg.conninfo import make_conninfo

import test_research_autonomy_postgres as pgtests
from test_research_autonomy_contract_builder import fixture_inputs
from tools.mcp.project_evidence.research_intent import semantic_content_sha256
from tools.research_autonomy import historical_source_gate as gate
from tools.research_autonomy.envelope import content_hash, envelope_hash, validate_envelope
from tools.research_autonomy.handoff import make_handoff
from tools.research_autonomy.m1_source import M1_ROOT, M1_SOURCE_CLASS, M1_VERSION, M1Intent, M1Source
from tools.research_autonomy.models import BoundedSearchRequest
from tools.research_autonomy.nonholdout_qualification import Custodian, NonHoldoutQualification, Revocation
from tools.research_autonomy.store import AuthorityConflict, ResearchAuthorityStore
from tools.research_factory import mapper
from tools.research_factory.evidence import EvidenceBlocked, verify_commitment, verify_m1_fixture_population
from tools.research_factory.manual_loop import manual_research_loop
from tools.research_memory.fingerprint import fingerprint

authority_db = pgtests.authority_db
ROOT = Path(__file__).resolve().parents[1]
START = 1_609_459_200_000
END = START + 10 * 86_400_000
FUNDING_STEP = 28_800_000
CREATED = "2026-10-08T00:00:00Z"
SPEC = mapper.SOURCE_SPEC
VM = mapper.SOURCE_VM
SWEEP = mapper.SOURCE_SWEEP
CELL_PATH = "research/data_slices/m1-fixture.json"


def _metadata(repo, symbol, clock):
    for name in (SPEC, VM, SWEEP):
        payload = json.loads((ROOT / name).read_text(encoding="utf-8"))
        payload = json.loads(json.dumps(payload).replace("15m", clock).replace("BTCUSDT", symbol))
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text(json.dumps(payload), encoding="utf-8")


def _objects(repo, symbol, clock):
    folder = repo / M1_ROOT / "source"
    folder.mkdir(parents=True)
    common = {"classification": "TEST_ONLY", "instrument": symbol, "epoch_id": f"TEST-EPOCH-{symbol}"}
    step = gate.CADENCE[clock]
    bars = []
    for i, ts in enumerate(range(START, END, step)):
        center = 100 + i * 0.1 + 2 * math.sin(i / 12)
        closed = center - 15 if i % 29 == 16 else center + 1
        bars.append([ts, center, max(center, closed) + 1, min(center, closed) - 1,
                     closed, 10, ts + step - 1, 0, 0, 0, 0, 0])
    events = [{"symbol": symbol, "fundingTime": ts, "fundingRate": "0.0003"}
              for ts in range(START, END, FUNDING_STEP)]
    out = []
    for role, payload in (
        ("ohlcv_input", common | {"timeframe": clock, "rows": bars}),
        ("funding_input", common | {"rows": events}),
    ):
        path = folder / f"{role}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        info = path.stat()
        out.append({"role": role, "repo_path": path.relative_to(repo).as_posix(),
                    "sha256": mapper.file_hash(path), "byte_length": info.st_size,
                    "device": info.st_dev, "inode": info.st_ino})
    return out


def _open_cell(authority_db, tmp_path, monkeypatch, symbol, clock, *, protected_start=END + 10 * 86_400_000):
    repo, intent, envelope, request = fixture_inputs(tmp_path)
    _metadata(repo, symbol, clock)
    (repo / ".gitignore").write_text("/.cpw/\n/scratch/\n", encoding="utf-8")
    objects = _objects(repo, symbol, clock)
    window = {"start_ms": START, "end_ms": END}
    source = M1Source.model_validate_json(json.dumps({
        "schema_version": M1_VERSION, "classification": "TEST_ONLY", "instrument": symbol,
        "timeframe": clock, "venue": "Binance USDT-M", "market_type": "perpetual",
        "quote_and_margin_asset": "USDT", "epoch_id": f"TEST-EPOCH-{symbol}",
        "epoch_window": window, "effective_window": window,
        "ohlcv_sha256": objects[0]["sha256"], "funding_sha256": objects[1]["sha256"],
        "funding_source": "TEST_ONLY_SYNTHETIC_8H", "variant_manifest_sha256": mapper.file_hash(repo / VM),
        "sweep_plan_id": "SWEEP-PLAN-0003", "sweep_plan_sha256": mapper.file_hash(repo / SWEEP),
        "costs": {"qualification": "TEST_ONLY", "fee_bps_taker": 5, "fee_bps_maker": 2,
                  "slippage_bps": 3, "funding_notional": "entry_price"},
    }))
    (repo / CELL_PATH).parent.mkdir(parents=True)
    (repo / CELL_PATH).write_text(source.model_dump_json(), encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                    "commit", "-qm", "M1 TEST_ONLY metadata"], cwd=repo, check=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    monkeypatch.setattr(gate, "_code_sha", lambda: head)

    def binding(path):
        return {"resource_uri": "project://fixture", "repo_path": path, "repo_sha": head,
                "artifact_sha256": mapper.file_hash(repo / path).split(":")[1]}

    domains = [dict(name=name, kind="int", required=True, low=low, high=high, step=step, choices=[])
               for name, low, high, step in (
                   ("center_lookback_bars", 50, 100, 50), ("vol_lookback_bars", 30, 50, 20),
                   ("trend_lookback_bars", 100, 200, 100),
               )]
    env = envelope.model_dump(mode="json")
    env["repo_sha"] = head
    env["surface"].update(instruments=[symbol], timeframes=[clock], strategy_spec_ids=["STRAT-SPEC-0003"],
                          data_source_classes=[M1_SOURCE_CLASS])
    policy = env["search_policy"]
    policy["parameter_domains"] = domains
    policy["data_bindings"] = [{"data_identity": source.identity, "data_version": M1_VERSION,
                                "evidence": binding(CELL_PATH)}]
    split = policy["split_protocols"][0]
    split.update(development_data_ref=source.identity, development_window="2021-01-01T00:00:00Z/2021-01-11T00:00:00Z")
    env["content_sha256"] = envelope_hash(env)
    envelope = validate_envelope(env, repo_sha=head)
    intent_raw = intent.model_dump(mode="json")
    intent_raw.update(schema_version="cpw_m1_fixture_intent_v1", repo_sha=head, primary_timeframe=clock,
                      instrument_scope=f"{symbol}_BINANCE_USDTM_PERP", free_parameter_count=3,
                      evidence_anchors=[binding("docs/fixture.md")])
    intent_raw["fingerprint_sha256"] = fingerprint(intent_raw)
    intent_raw["research_memory"]["fingerprint_sha256"] = intent_raw["fingerprint_sha256"]
    intent = M1Intent.model_validate_json(json.dumps(intent_raw))
    intent = intent.model_copy(update={"content_sha256": semantic_content_sha256(intent)})
    payload = request.model_dump(mode="json")
    payload.update(campaign_id="TEST-ONLY-CAMPAIGN", search_id="TEST-ONLY-SEARCH",
                   intent_sha256=intent.content_sha256, strategy_spec_id="STRAT-SPEC-0003",
                   strategy_spec_evidence=binding(SPEC), data_identity=source.identity,
                   data_version=M1_VERSION, data_evidence=binding(CELL_PATH), instrument=symbol,
                   data_source_class=M1_SOURCE_CLASS, parameter_space=domains, split_protocol=split)
    request = BoundedSearchRequest.model_validate_json(json.dumps(payload))
    store = ResearchAuthorityStore(make_conninfo(authority_db[0], options="-c role=cpw_research_authority_writer"))
    store.register_envelope(envelope)
    store.open_campaign(envelope, campaign_id=request.campaign_id,
                        contamination_domain_id=envelope.contamination_domain_id,
                        holdout_id=split["final_holdout_ref"], hypothesis_fingerprint=intent.fingerprint_sha256)
    contract = store.open_search(intent, envelope, request, repo_root=repo)
    governor, pre, _ = pgtests.wave(store, contract)
    handoff = make_handoff(store=store, contract=contract, intent_sha256=intent.content_sha256,
                           pre_wave_snapshot=pre, requested_wave_count=2,
                           proposal_records=governor.proposal_records,
                           resulting_denominator=governor.scientific_denominator, repo_root=repo)
    reader = gate.HistoricalSourceGate(store, repo)
    owner_store = ResearchAuthorityStore(make_conninfo(authority_db[0], options="-c role=cpw_nonholdout_owner"))
    controller = NonHoldoutQualification(owner_store)
    now = int(time.time() * 1000)
    key = Ed25519PrivateKey.generate()
    custodian = Custodian(record_id="TEST-ONLY-CUSTODIAN", approved_by="Karl", approval_reference="TEST-ONLY",
                          public_key_hex=key.public_key().public_bytes_raw().hex(),
                          valid_from_ms=now - 60_000, valid_until_ms=now + 600_000)
    controller.control("custodian", custodian)
    raw = {
        "schema_version": gate.M1_SCHEMA, "purpose": "m1_fixture_read", "repository": "toobigtofailbot-maker/crypto-perp-wedge",
        "repo_sha": head, "campaign_id": contract.campaign_id, "search_id": contract.search_id,
        "contract_hash": contract.contract_hash, "strategy_spec_hash": contract.strategy_spec_hash,
        "original_parent_sha256": contract.strategy_spec_hash, "contamination_domain_id": envelope.contamination_domain_id,
        "holdout_id": split["final_holdout_ref"], "envelope_sha256": envelope.content_sha256,
        "protocol_sha256": content_hash(envelope.scientific_protocol.model_dump(mode="json")),
        "data_identity": source.identity, "data_version": M1_VERSION, "instrument": symbol,
        "venue": source.venue, "market": source.market_type, "timeframe": clock,
        "effective_window": window, "label_horizon_bars": 0, "fitting": "none",
        "storage": gate.STORAGE.get(gate.sys.platform, "linux_immutable_flag_v1"), "objects": objects,
        "source": source.model_dump(mode="json"),
    }
    custody_request = gate.M1Request.model_validate_json(json.dumps(raw))
    designation = gate.M1Designation(
        record_id="TEST-ONLY-DESIGNATION", approved_by="Karl", approval_reference="TEST-ONLY",
        custodian_id=custodian.record_id, valid_from_ms=now - 60_000, valid_until_ms=now + 600_000,
        request=custody_request, protected_mapping_complete=True,
        protected_intervals=(gate.Interval(start_ms=protected_start, end_ms=protected_start + 86_400_000),),
    )
    gate.HistoricalSourceGate(owner_store, repo).designate(designation)
    attestation = gate.HistoricalAttestation(
        attestation_id="TEST-ONLY-ATTESTATION", custodian_id=custodian.record_id, designation_id=designation.record_id,
        designation_sha256=content_hash(designation.model_dump(mode="json")),
        request_sha256=content_hash(custody_request.model_dump(mode="json")),
        valid_from_ms=now - 60_000, valid_until_ms=now + 600_000, signature_hex="0" * 128,
    )
    # Disposable fixture key only. The separate domain cannot sign a historical grant.
    attestation = attestation.model_copy(update={"signature_hex": key.sign(
        gate.signing_bytes(attestation, m1_fixture=True)).hex()})
    return repo, store, reader, contract, handoff, custody_request, envelope, controller, attestation


@pytest.mark.skipif(gate.sys.platform != "win32", reason="exercise Windows immutable file and parent leases")
@pytest.mark.parametrize(("symbol", "clock"), [
    ("BTCUSDT", "15m"), ("BTCUSDT", "1h"), ("ETHUSDT", "15m"), ("ETHUSDT", "1h"), ("SOLUSDT", "1h"),
])
def test_native_m1_fixture_cell(authority_db, tmp_path, monkeypatch, symbol, clock):
    repo, store, reader, contract, handoff, request, envelope, controller, attestation = _open_cell(
        authority_db, tmp_path, monkeypatch, symbol, clock,
    )
    grant = dict(attestation=attestation, request=request, envelope=envelope,
                 contract=contract, repo_sha=contract.repo_sha)
    if (symbol, clock) == ("ETHUSDT", "15m"):
        with monkeypatch.context() as patch:
            def forbidden_lease(*args):
                pytest.fail("invalid authority touched a source handle")

            patch.setattr(gate, "_lease", forbidden_lease)
            for field, value in (
                ("instrument", "BTCUSDT"), ("timeframe", "1h"),
                ("holdout_id", "UNAPPROVED-HOLDOUT"),
            ):
                with pytest.raises(gate.Refused):
                    reader.authorize(**(grant | {"request": request.model_copy(update={field: value})}))
            with pytest.raises(gate.Refused):
                reader.authorize(**(grant | {"attestation": attestation.model_copy(update={"signature_hex": "0" * 128})}))
    with reader.authorize(**grant) as custody:
        arguments = dict(store=store, handoff=handoff, repo_root=repo,
                         preparation_root=repo / M1_ROOT / "prepared", output_root=repo / M1_ROOT / "outputs",
                         created_at_utc=CREATED, human_invocation=True, custody=custody)
        report = manual_research_loop(**arguments)
        observation = report["fixture_observation"]
        assert report["disposition"] == "research_insufficient_evidence"
        assert observation["real_scientific_trials"] == 0
        assert report["runner_calls"] == 1
        assert observation["execution"]["source"]["instrument"] == symbol
        population = observation["population"]
        assert len(population["variant_result_rows"]) == handoff.resulting_denominator == 2
        with pytest.raises(EvidenceBlocked, match="cannot create a terminal"):
            verify_commitment(repo, {}, contract)
        for row in population["variant_result_rows"]:
            assert row["data_coverage"]["timeframe"] == clock
            assert row["outcome_category"] in {"successful", "failed"}, row["error"]
            if row["metrics"]["trade_count"]:
                assert row["metrics"]["fees"] == pytest.approx(row["metrics"]["slippage"] * 5 / 3)
        print("M1_FIXTURE", json.dumps({
            "symbol": symbol, "clock": clock, "classification": "TEST_ONLY", "contract_hash": contract.contract_hash,
            "source": observation["execution"]["source"], "population_sha256": observation["population_sha256"],
            "proposal_counts": report["prepared"]["proposal_counts"],
            "rows": [{"outcome": row["outcome_category"], "metrics": row["metrics"]}
                     for row in population["variant_result_rows"]],
        }, sort_keys=True))
        if (symbol, clock) == ("ETHUSDT", "15m"):
            prepared = report["prepared"]
            reopened = gate.HistoricalSourceGate(ResearchAuthorityStore(
                make_conninfo(authority_db[0], options="-c role=cpw_research_authority_writer")
            ), repo)
            assert verify_m1_fixture_population(reopened, contract, prepared, observation) == 2
            changed = copy.deepcopy(observation)
            changed["population_sha256"] = "sha256:" + "0" * 64
            with pytest.raises(EvidenceBlocked):
                verify_m1_fixture_population(reader, contract, prepared, changed)
            with pytest.raises(gate.Refused, match="ALREADY_USED"):
                manual_research_loop(**arguments)
            controller.control("revocation", Revocation(
                record_id="TEST-ONLY-REVOCATION", target_id=attestation.attestation_id, approved_by="Karl",
                approval_reference="TEST-ONLY", action="revoke", successor_id=None,
            ))
            with pytest.raises(AuthorityConflict):
                verify_m1_fixture_population(reader, contract, prepared, observation)
    assert not (repo / "research/result_populations").exists()
    for row in handoff.proposal_records:
        if row.scientific_trial_id:
            assert store.load_trial_result(row.scientific_trial_id, repo_root=repo) is None
    if (symbol, clock) != ("ETHUSDT", "15m"):
        with pytest.raises(gate.Refused, match="ALREADY_USED"):
            reader.authorize(**grant)


def test_m1_hourly_protected_embargo_refuses_before_lease(authority_db, tmp_path, monkeypatch):
    _, _, reader, contract, _, request, envelope, _, attestation = _open_cell(
        authority_db, tmp_path, monkeypatch, "ETHUSDT", "1h", protected_start=END + 3_600_000,
    )

    def forbidden_lease(*args):
        pytest.fail("protected window touched source handles")

    monkeypatch.setattr(gate, "_lease", forbidden_lease)
    with pytest.raises(gate.Refused, match="PROTECTED_OVERLAP"):
        reader.authorize(attestation=attestation, request=request, envelope=envelope,
                         contract=contract, repo_sha=contract.repo_sha)


def test_m1_metadata_rejects_ambiguous_json():
    from tools.research_autonomy.m1_source import exact_json

    with pytest.raises(ValueError, match="duplicate"):
        exact_json('{"symbol":"ETHUSDT","symbol":"BTCUSDT"}')
    with pytest.raises(ValueError, match="nonfinite"):
        exact_json('{"funding":NaN}')


@pytest.mark.parametrize("side", [1, -1])
def test_m1_fee_slippage_and_event_funding_reconcile(side, monkeypatch):
    import pandas as pd
    from test_backtest import _make_ohlcv
    from tools.research_runner import run_offline_sweep as runner

    prices = _make_ohlcv([100.0] * 16)
    events = pd.DataFrame({"funding_rate": [0.0003]}, index=[prices.index[8]])
    signal = pd.Series([side] * 11 + [0] * 5, index=prices.index)

    def compile_test_signal(*args, funding):
        assert funding is None  # Settlement rates are unavailable to signals.
        return signal

    monkeypatch.setattr(runner, "compile_signal", compile_test_signal)
    execution = runner._ExecutionInput(
        mode="m1_test_only", execution_provenance_class="fixture_offline",
        ohlcv=prices, funding=events, timeframe="1h", data_catalog_ref="TEST_ONLY",
        data_slice_identity="TEST_ONLY", environment_summary=[], data_coverage_notes=[],
        funding_input_identity={"funding_mode": "on", "m1_fixture_costs": {
            "fee_bps_taker": 5.0, "fee_bps_maker": 2.0, "slippage_bps": 3.0,
            "funding_notional": "entry_price",
        }},
    )
    sizing = runner._sizing_context(execution, runner.SIZING_MODE_FIXED_ORDER_SIZE, 0.01)
    result = runner._run_canonical_15m_backtest({}, {}, execution, sizing, sizing.exact_resolution)
    assert result.fees_paid == pytest.approx(0.10)
    assert result.slippage_paid == pytest.approx(0.06)
    assert result.funding_paid == pytest.approx(side * 0.03)
    assert result.equity_curve.iloc[-1] == pytest.approx(runner.INITIAL_EQUITY - 0.16 - side * 0.03)
