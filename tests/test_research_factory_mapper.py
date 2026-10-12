"""Synthetic authority fixtures; no real approval or physical acceptance claims."""

import json
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.research_search.test_search_governor import make_contract
from tools.research_autonomy.handoff import make_handoff
from tools.research_factory import mapper
from tools.research_search.contract import ParameterSpec, SplitProtocol
from tools.research_search.governor import SearchGovernor

ROOT = Path(__file__).resolve().parents[1]
CATALOG = "research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json"
IMPORT = "research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json"


def factory_fixture(tmp_path, **contract_changes):
    root = tmp_path / "repo"
    root.mkdir()
    for name in (mapper.SOURCE_SPEC, mapper.SOURCE_VM, mapper.SOURCE_SWEEP, CATALOG, IMPORT):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, path)
    (root / ".gitignore").write_text("/scratch/\n/.cpw/\n")
    for args in (
        ["init", "-q"],
        ["config", "core.autocrlf", "false"],
        ["add", "."],
        [
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "metadata fixture",
        ],
    ):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    catalog = json.loads((root / CATALOG).read_text())
    data = catalog["slice_identity"]["data_slice_identity"]
    contract = replace(
        make_contract(backend="random", max_proposals=6, max_trials=4, wave_size=2),
        repo_sha=sha,
        strategy_spec_id="STRAT-SPEC-0003",
        strategy_spec_hash=mapper.file_hash(root / mapper.SOURCE_SPEC),
        family_id="sma_stddev_mean_reversion_v1",
        data_identity=data,
        data_version=catalog["catalog_version"],
        parameter_space=(
            ParameterSpec("center_lookback_bars", "int", 50, 100, 50),
            ParameterSpec("vol_lookback_bars", "int", 30, 50, 20),
            ParameterSpec("trend_lookback_bars", "int", 100, 200, 100),
        ),
        conditional_rules=(),
        relational_constraints=(),
        forbidden_regions=(),
        split_protocol=SplitProtocol(
            "FIXTURE-SPLIT",
            data,
            "2020-01-01T00:00:00Z/2026-04-12T00:00:00Z",
            "HOLDOUT-UNOPENED-FIXTURE",
        ),
    )
    contract = replace(contract, **contract_changes)
    governor = SearchGovernor(contract)
    pre = governor.snapshot()
    governor.propose_wave(2)
    snapshot = SimpleNamespace(
        lineage_version=2,
        lineage_sha256="sha256:" + "d" * 64,
        envelope_id=contract.envelope_id,
        envelope_version=contract.envelope_version,
        envelope_content_sha256=contract.envelope_content_sha256,
    )

    class FixtureStore:
        def load_snapshot(self, *args):
            return snapshot

        def verify_recovery_binding(self, *args, **kwargs):
            return snapshot, contract

        def load_trial_result(self, *args, **kwargs):
            return None

    store = FixtureStore()
    handoff = make_handoff(
        store=store,
        contract=contract,
        intent_sha256="sha256:" + "f" * 64,
        pre_wave_snapshot=pre,
        requested_wave_count=2,
        proposal_records=governor.proposal_records,
        resulting_denominator=governor.scientific_denominator,
        repo_root=root,
    )
    return root, store, contract, handoff


def test_supported_mapping_is_exact_deterministic_and_schema_valid(tmp_path):
    root, store, contract, handoff = factory_fixture(tmp_path)
    args = dict(
        store=store,
        handoff=handoff,
        contract=contract,
        repo_root=root,
        output_root=root / "scratch/prepared",
        created_at_utc="2026-10-08T00:00:00Z",
    )
    result = mapper.prepare_wave(**args)
    assert mapper.prepare_wave(**args) == result
    expected = [
        p for p in handoff.proposal_records if p.status == "ACCEPTED_FOR_SCIENTIFIC_EXECUTION"
    ]
    assert len(result["mapping"]) == len(expected) == 2
    assert result["proposal_counts"]["total"] == len(handoff.proposal_records)
    for row, proposal in zip(result["mapping"], expected):
        assert row["parameter_values"] == proposal.params
        assert row["params_fingerprint"] == proposal.params_fingerprint
        assert row["scientific_trial_id"] == proposal.scientific_trial_id
    mapper.runner._validate_parent_inputs(
        *[root / result["paths"][k] for k in ("spec", "vm", "sweep")]
    )
    vm = json.loads((root / result["paths"]["vm"]).read_text())
    assert {r["variant_id"] for r in vm["variant_assignments"]} == {
        m["variant_id"] for m in result["mapping"]
    }
    assert result["runner_authority"] is False and result["approval_authority"] is False
    sweep = json.loads((root / result["paths"]["sweep"]).read_text())
    assert sweep["trial_accounting"]["not_attempted_variant_count"] == len(expected)


def test_changed_frozen_spec_rejects_before_prepared_outputs(tmp_path):
    root, store, contract, handoff = factory_fixture(tmp_path)
    (root / mapper.SOURCE_SPEC).write_text("{}")
    with pytest.raises(ValueError):
        mapper.prepare_wave(
            store=store,
            handoff=handoff,
            contract=contract,
            repo_root=root,
            output_root=root / "scratch/prepared",
            created_at_utc="2026-10-08T00:00:00Z",
        )
    assert not (root / "scratch").exists()


def test_different_contract_or_handoff_hash_rejects(tmp_path):
    root, store, contract, handoff = factory_fixture(tmp_path)
    with pytest.raises(ValueError):
        mapper.prepare_wave(
            store=store,
            handoff=handoff,
            contract=replace(contract, strategy_spec_id="STRAT-SPEC-0004"),
            repo_root=root,
            output_root=root / "scratch/prepared",
            created_at_utc="2026-10-08T00:00:00Z",
        )
    assert not (root / "scratch").exists()


@pytest.mark.parametrize(
    "changes",
    [
        {"family_id": "unsupported_family"},
        {"data_version": "unverified_catalog_version"},
        {"parameter_space": (ParameterSpec("new_parameter", "int", 1, 2, 1),)},
    ],
)
def test_unsupported_frozen_mapping_never_publishes(tmp_path, changes):
    root, store, contract, handoff = factory_fixture(tmp_path, **changes)
    with pytest.raises(mapper.MappingBlocked, match="unsupported_mapping"):
        mapper.prepare_wave(
            store=store,
            handoff=handoff,
            contract=contract,
            repo_root=root,
            output_root=root / "scratch/prepared",
            created_at_utc="2026-10-08T00:00:00Z",
        )
    assert not (root / "scratch").exists()


def test_duplicate_governor_records_are_counted_without_extra_variants(tmp_path):
    root, store, contract, handoff = factory_fixture(
        tmp_path,
        parameter_space=(
            ParameterSpec("center_lookback_bars", "int", 50, 50, 50),
            ParameterSpec("vol_lookback_bars", "int", 30, 30, 20),
            ParameterSpec("trend_lookback_bars", "int", 100, 100, 100),
        ),
    )
    prepared = mapper.prepare_wave(
        store=store,
        handoff=handoff,
        contract=contract,
        repo_root=root,
        output_root=root / "scratch/prepared",
        created_at_utc="2026-10-08T00:00:00Z",
    )
    assert prepared["scientific_denominator"] == len(prepared["mapping"]) == 1
    assert prepared["proposal_counts"]["duplicate"] > 0
    assert prepared["proposal_counts"]["total"] == 1 + prepared["proposal_counts"]["duplicate"]
    vm = json.loads((root / prepared["paths"]["vm"]).read_text())
    assert all(
        len(axis["allowed_values"]) == 1 and axis["range"]["min"] == axis["range"]["max"]
        for axis in vm["parameter_axes"]
    )


def authority_inputs(root):
    """Explicit engineering-test envelope/intent, never an operational Karl envelope."""
    import hashlib

    from tools.mcp.project_evidence.research_intent import (
        BoundedResearchIntentV1,
        semantic_content_sha256,
    )
    from tools.research_autonomy.envelope import envelope_hash, validate_envelope
    from tools.research_autonomy.models import BoundedSearchRequest
    from tools.research_memory.fingerprint import fingerprint

    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    catalog = json.loads((root / CATALOG).read_text())

    def evidence(name):
        return {
            "resource_uri": "project://engineering-test-fixture/" + name,
            "repo_path": name,
            "repo_sha": sha,
            "artifact_sha256": hashlib.sha256((root / name).read_bytes()).hexdigest(),
        }

    envelope = json.loads(
        (
            ROOT / "tests/fixtures/research_autonomy/bounded_research_envelope.fixture.json"
        ).read_text()
    )
    envelope["repo_sha"] = sha
    envelope["envelope_id"] = "ENVELOPE-FACTORY-ENGINEERING-FIXTURE"
    envelope["contamination_domain_id"] = "DOMAIN-FACTORY-ENGINEERING-FIXTURE"
    surface = envelope["surface"]
    surface.update(
        timeframes=["15m"],
        strategy_families=["sma_stddev_mean_reversion_v1"],
        mechanisms=["engineering fixture only"],
        data_source_classes=["offline_local"],
        feature_families=["ohlcv", "sma", "stddev"],
        strategy_spec_ids=["STRAT-SPEC-0003"],
    )
    spec = json.loads((root / mapper.SOURCE_SPEC).read_text())
    domains = [
        {
            "name": p["name"],
            "kind": "int",
            "low": p["range"]["min"],
            "high": p["range"]["max"],
            "step": p["range"]["step"],
            "choices": [],
            "required": True,
        }
        for p in spec["free_parameters"]["parameters"]
    ]
    data_id = catalog["slice_identity"]["data_slice_identity"]
    policy = envelope["search_policy"]
    policy["parameter_domains"] = domains
    policy["proposers"] = [{"backend": "random", "version": "4.9.0", "config": []}]
    policy["data_bindings"] = [
        {
            "data_identity": data_id,
            "data_version": catalog["catalog_version"],
            "evidence": evidence(CATALOG),
        }
    ]
    policy["split_protocols"] = [
        {
            "protocol_id": "FACTORY-ENGINEERING-FIXTURE-SPLIT",
            "development_data_ref": data_id,
            "development_window": "2020-01-01T00:00:00Z/2026-04-12T00:00:00Z",
            "final_holdout_ref": "HOLDOUT-UNOPENED-ENGINEERING-FIXTURE",
            "final_holdout_access": "prohibited",
        }
    ]
    envelope["scientific_protocol"].update(purge_bars=96, embargo_bars=32)
    envelope["content_sha256"] = envelope_hash(envelope)
    frozen = validate_envelope(envelope, repo_sha=sha)
    definition = {
        "strategy_family": "sma_stddev_mean_reversion_v1",
        "mechanism": "engineering fixture only",
        "primary_timeframe": "15m",
        "required_data_features": ["ohlcv", "sma", "stddev"],
        "free_parameter_count": 3,
    }
    fp = fingerprint(definition)
    intent_payload = {
        "schema_version": "cpw_bounded_research_intent_v1",
        "request_id": "INTENT-FACTORY-ENGINEERING-FIXTURE",
        "repo_sha": sha,
        "content_sha256": "sha256:" + "0" * 64,
        **definition,
        "instrument_scope": "BTCUSDT_BINANCE_USDTM_PERP",
        "fingerprint_version": "hypothesis-v1",
        "fingerprint_sha256": fp,
        "research_question": "Bounded integration engineering proof only?",
        "causal_rationale": "Fixture only",
        "falsifiable_prediction": "No strategy or edge claim",
        "falsification_stop_conditions": ["Identity or gate mismatch"],
        "proposed_parameter_bounds": [
            {"name": p["name"], "minimum": float(p["low"]), "maximum": float(p["high"])}
            for p in domains
        ],
        "proposed_objective_intent": "Existing row sharpe only; engineering fixture",
        "unresolved_assumptions": [],
        "evidence_anchors": [evidence(mapper.SOURCE_SPEC), evidence(CATALOG)],
        "research_memory": {
            "fingerprint_version": "hypothesis-v1",
            "fingerprint_sha256": fp,
            "matched": False,
            "index_not_truth": True,
            "records": [],
            "repo_sha": sha,
            "postgres_boundary": "isolated engineering test",
            "authority": {"not_scientific_truth": True},
        },
    }
    intent = BoundedResearchIntentV1.model_validate_json(json.dumps(intent_payload))
    intent = intent.model_copy(update={"content_sha256": semantic_content_sha256(intent)})
    request = {
        "campaign_id": "CAMPAIGN-FACTORY-ENGINEERING-FIXTURE",
        "search_id": "SEARCH-FACTORY-ENGINEERING-FIXTURE",
        "parent_search_id": None,
        "reason_for_change": None,
        "intent_sha256": intent.content_sha256,
        "hypothesis_id": "H-ENGINEERING-FIXTURE",
        "family_id": "sma_stddev_mean_reversion_v1",
        "strategy_spec_id": "STRAT-SPEC-0003",
        "strategy_spec_evidence": evidence(mapper.SOURCE_SPEC),
        "data_identity": data_id,
        "data_version": catalog["catalog_version"],
        "data_evidence": evidence(CATALOG),
        "instrument": "BTCUSDT",
        "venue": "Binance USDT-M",
        "market_type": "perpetual",
        "data_source_class": "offline_local",
        "dsl_version": "v1",
        "parameter_space": domains,
        "conditional_rules": [],
        "relational_constraints": [],
        "forbidden_regions": [],
        "objective": policy["objectives"][0],
        "scientific_protocol": envelope["scientific_protocol"],
        "max_proposals": 6,
        "max_scientific_trials": 4,
        "compute_seconds": 30,
        "runtime_seconds": 60,
        "recovery_limit": 2,
        "wave_size": 2,
        "concurrency": 1,
        "split_protocol": policy["split_protocols"][0],
        "proposer": policy["proposers"][0],
        "seed": 1729,
        "policies": policy["policies"],
    }
    return intent, frozen, BoundedSearchRequest.model_validate_json(json.dumps(request))
