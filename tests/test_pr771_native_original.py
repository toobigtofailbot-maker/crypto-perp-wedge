"""Native 02A/B/C + Agent Inbox + Gate C software fixtures. Never model/science proof."""

import copy
import json
import subprocess
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.agent_inbox_intake.models import IntakeDraftRequest
from tools.agent_inbox_intake.service import create_intake_draft
from tools.canon_intake import spec_writer
from tools.hermes import discovery_intent as di
from tools.hermes import discovery_intent_consumer as dc
from tools.hermes import model_origin_receipt as mor
from tools.mcp.project_evidence.models import RepoIdentity
from tools.research_autonomy.handoff import make_handoff
from tools.research_factory import mapper, original_source
from tools.research_search.contract import ParameterSpec
from tools.research_search.governor import SearchGovernor

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
    return path


@pytest.fixture
def native_chain(tmp_path, monkeypatch):
    import test_hermes_model_origin_receipt as host_fixture
    from test_canon_intake_spec_writer import _fixture_repo
    from test_hermes_discovery_intent_consumer import (
        CRITIC,
        FrozenMemory,
        _idea,
        _sources,
        consumer,
    )
    from test_hermes_intent_strategy_spec_handoff import (
        _don_native,
        build,
        prepare,
        respond,
    )
    from test_hermes_model_origin_receipt import build as build_host
    from test_research_factory_mapper import factory_fixture

    repo = tmp_path / "repo"
    subprocess.run(
        ["git", "clone", "--shared", "--quiet", str(ROOT), str(repo)],
        check=True,
        capture_output=True,
    )
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    scratch = repo / "scratch/PR771-TEST-ONLY"
    scratch.mkdir(parents=True)
    idea = _idea(
        "DON",
        _don_native(
            primary_timeframe="15m",
            mechanism="BTCUSDT 15m Donchian breakouts persist because slow information diffusion follows completed-bar channel breaks.",
        ),
    )
    monkeypatch.setattr(host_fixture, "SHA", sha)
    monkeypatch.setattr(host_fixture, "IDEA", idea)
    monkeypatch.setattr(host_fixture, "SOURCES", _sources(sha))
    monkeypatch.setattr(host_fixture, "CRITIC", CRITIC)

    def manifest_fields(cycle, manifest, receipt):
        manifest.update(not_authority=True, repo_branch="test", package="TEST_ONLY")

    cycle, host = build_host(scratch, mutate=manifest_fields)
    identity = RepoIdentity(repo_sha=sha, branch="test")
    packet = di.DiscoveryIntentAdapter(ROOT, identity).build(cycle)
    packet_dir = scratch / "cycle.discovery-intent"
    di.write_packet_directory(packet, cycle, packet_dir)
    batch, intents = consumer(FrozenMemory()).build_batch(packet_dir)
    batch_dir = scratch / "batch"
    dc.write_batch(batch, intents, batch_dir)
    prepared_dir = prepare(scratch, batch_dir)
    responses = scratch / "responses"
    respond(prepared_dir, responses, 0)
    built_dir, built = build(scratch, prepared_dir, responses)
    generated = json.loads((built_dir / built["ideas"][0]["drafts"][0]["file"]).read_text())
    intent = json.loads((batch_dir / "intents/00.native_intent.json").read_text())
    observed = mor.verify_origin(cycle, host, anchor_sha256=None, expected_repo_sha=sha)
    assert observed["status"] == mor.FIXTURE
    parent = {
        "idea_id": "DON",
        "original_hypothesis_sha256": "sha256:" + di.canonical_sha256(idea),
        "fingerprint_sha256": "sha256:" + intent["fingerprint_sha256"].removeprefix("sha256:"),
        "cycle_manifest_sha256": "sha256:" + observed["cycle_manifest_sha256"],
        "origin_status": observed["status"],
    }
    from tools.agent_inbox_intake.service import original_parent_sha256

    parent["original_parent_sha256"] = original_parent_sha256(parent)
    packet = create_intake_draft(
        IntakeDraftRequest(
            title="TEST_ONLY Donchian",
            hypothesis_text=idea["native_draft"]["mechanism"],
            timeframe_hint="15m",
        ),
        repo_root=repo,
        original_parent=parent,
    )
    staging = tmp_path / "writer-template"
    staging.mkdir()
    _, _, gate = _fixture_repo(staging, ROOT)
    draft_id = packet["draft_id"]
    refs = {
        "source_draft": {
            "path": packet["provenance"]["output_path"],
            "sha256": mapper.file_hash(repo / packet["provenance"]["output_path"]),
        }
    }
    review = json.loads((staging / gate["review_trail"]["path"]).read_text())
    review["draft_id"] = draft_id
    review_path = (
        repo / f"scratch/WP-DASH-AGENT-INBOX-WRITE-01A/reviews/{draft_id}.review_events.jsonl"
    )
    write(review_path, review)
    # Native reviews are JSONL, one complete object per line.
    review_path.write_text(json.dumps(review) + "\n")
    refs["review_trail"] = {
        "path": review_path.relative_to(repo).as_posix(),
        "sha256": mapper.file_hash(review_path),
    }
    eligibility = json.loads((staging / gate["eligibility_report"]["path"]).read_text())
    eligibility.update(
        draft_id=draft_id,
        source_draft_path=refs["source_draft"]["path"],
        source_draft_hash=refs["source_draft"]["sha256"],
        review_trail_path=refs["review_trail"]["path"],
        review_trail_hash=refs["review_trail"]["sha256"],
    )
    eligible_path = (
        repo
        / f"scratch/WP-CANON-ELIGIBILITY-VALIDATOR-01/reports/{draft_id}.eligibility_report.json"
    )
    write(eligible_path, eligibility)
    refs["eligibility_report"] = {
        "path": eligible_path.relative_to(repo).as_posix(),
        "sha256": mapper.file_hash(eligible_path),
    }
    canonical = copy.deepcopy(generated)
    canonical["strategy_spec_id"] = "STRAT-SPEC-9999"
    canonical["pre_registration_support"]["variant_manifest_ref"] = "VM-9999"
    canonical["provenance"]["source_refs"] = [
        f"{k}:{refs[k]['path']}#{refs[k]['sha256']}" for k in refs
    ] + ["gate_c_approval:GATE-C-TEST-0001"]
    proposed = write(scratch / "proposed.json", canonical)
    gate.update(
        source_draft_id=draft_id,
        source_hashes=packet["source_hashes"],
        approved_content_sha256=mapper.file_hash(proposed),
        **refs,
    )
    gate_path = write(scratch / "gate.json", gate)
    spec_writer.write_approved_strategy_spec(
        repo_root=repo, proposed_content_path=proposed, gate_c_path=gate_path
    )
    vm = json.loads((ROOT / mapper.SOURCE_VM).read_text())
    values = canonical["free_parameters"]["parameters"][0]["allowed_values"]
    vm["variant_manifest_id"] = "VM-9999"
    vm["parent_strategy_spec"].update(
        strategy_spec_id="STRAT-SPEC-9999",
        strategy_spec_ref="research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json",
        strategy_spec_hash=mapper.runner._sha256_prefixed(canonical),
    )
    axis = vm["parameter_axes"][0]
    axis.update(parameter_name="channel_lookback_bars", allowed_values=values)
    vm["parameter_axes"] = [axis]
    for assignment in vm["variant_assignments"]:
        assignment["parameter_values"] = {"channel_lookback_bars": values[0]}
        assignment["axis_refs"] = [axis["axis_id"]]
    vm["manifest_hash_pinning"]["manifest_hash"] = mapper.runner._sha256_prefixed(
        {k: mapper._get(vm, k) for k in vm["manifest_hash_pinning"]["hash_scope"]}
    )
    write(repo / "research/variant_manifests/VM-9999.variant_manifest.json", vm)
    sweep = json.loads((ROOT / mapper.SOURCE_SWEEP).read_text())
    sweep["sweep_plan_id"] = "SWEEP-PLAN-9999"
    sweep["parent_variant_manifest"].update(
        variant_manifest_id="VM-9999", manifest_hash=vm["manifest_hash_pinning"]["manifest_hash"]
    )
    write(repo / "research/sweep_plans/SWEEP-PLAN-9999.sweep_plan.json", sweep)
    subprocess.run(["git", "add", "research"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=TEST_ONLY",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "TEST_ONLY native canonical fixture",
        ],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    frozen_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    base = tmp_path / "base"
    base.mkdir()
    _, _, old_contract, _ = factory_fixture(base)
    contract = replace(
        old_contract,
        repo_sha=frozen_sha,
        strategy_spec_id="STRAT-SPEC-9999",
        strategy_spec_hash=mapper.file_hash(
            repo / "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json"
        ),
        family_id="donchian_channel_breakout_v1",
        hypothesis_fingerprint=intent["fingerprint_sha256"],
        parameter_space=(
            ParameterSpec(
                "channel_lookback_bars", "int", values[0], values[-1], values[1] - values[0]
            ),
        ),
    )
    evidence = {
        "idea_id": "DON",
        **{
            k: v.relative_to(repo).as_posix()
            for k, v in {
                "cycle": cycle,
                "host_receipt": host,
                "packet": packet_dir,
                "batch": batch_dir,
                "prepared": prepared_dir,
                "responses": responses,
                "built": built_dir,
                "gate_c_approval": gate_path,
            }.items()
        },
    }
    return repo, contract, evidence


def test_native_02abc_gate_c_chain_verifies_without_proof_promotion(native_chain):
    repo, contract, evidence = native_chain
    proof = original_source.verify(repo, contract, evidence)
    assert proof["fixture"] and proof["origin"]["B_verified"] is False
    assert proof["original_parent"]["fingerprint_sha256"].removeprefix(
        "sha256:"
    ) == contract.hypothesis_fingerprint.removeprefix("sha256:")


def test_hash_only_parent_is_not_original_admission(tmp_path):
    with pytest.raises(original_source.OriginalBlocked, match="SOURCE_REQUIRED"):
        original_source.verify(tmp_path, SimpleNamespace(), {"idea_id": "invented"})


def prepare_native(native_chain):
    repo, contract, evidence = native_chain
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
    store = SimpleNamespace(
        load_snapshot=lambda *a: snapshot,
        verify_recovery_binding=lambda *a, **k: (snapshot, contract),
    )
    wave = make_handoff(
        store=store,
        contract=contract,
        intent_sha256="sha256:" + "f" * 64,
        pre_wave_snapshot=pre,
        requested_wave_count=2,
        proposal_records=governor.proposal_records,
        resulting_denominator=governor.scientific_denominator,
        repo_root=repo,
    )
    return mapper.prepare_wave(
        store=store,
        handoff=wave,
        contract=contract,
        repo_root=repo,
        output_root=repo / "scratch/native-prepared",
        created_at_utc="2026-11-04T12:00:00Z",
        original=evidence,
    )


def test_native_source_positive_reaches_governor_prepared_artifacts(native_chain):
    import pandas as pd

    from tools.research_runner.spec_signal_compiler import compile_signal

    repo, contract, evidence = native_chain
    prepared = prepare_native(native_chain)
    assert prepared["original_parent"]["idea_id"] == evidence["idea_id"]
    assert prepared["scientific_denominator"] == len(prepared["mapping"]) == 2
    assert all(row["contract_hash"] == contract.contract_hash for row in prepared["mapping"])
    spec = json.loads((repo / prepared["paths"]["spec"]).read_text())
    assert (
        len(
            [
                ref
                for ref in spec["provenance"]["source_refs"]
                if ref.startswith(original_source.ROUTE_PREFIX)
            ]
        )
        == 1
    )
    assert prepared["approval_authority"] is False
    # Pure software compilation for the full fixture denominator; no backtest or trial.
    bars = pd.DataFrame({"open": [100.0 + i for i in range(128)],
                         "high": [102.0 + i for i in range(128)],
                         "low": [99.0 + i for i in range(128)],
                         "close": [101.0 + i for i in range(128)], "volume": [1.0] * 128},
                        index=pd.date_range("2020-01-01", periods=128, freq="15min", tz="UTC"))
    vm = json.loads((repo / prepared["paths"]["vm"]).read_bytes())
    for assignment in vm["variant_assignments"]:
        assert len(compile_signal(spec, assignment, bars)) == len(bars)


def test_native_source_refuses_critic_host_missing02c_and_wrong_contract(native_chain):
    repo, contract, evidence = native_chain
    for key in ("host_receipt", "built", "packet"):
        altered = dict(evidence, **{key: "scratch/does-not-exist"})
        with pytest.raises(original_source.OriginalBlocked):
            original_source.verify(repo, contract, altered)
    with pytest.raises(original_source.OriginalBlocked, match="FINGERPRINT"):
        original_source.verify(
            repo, replace(contract, hypothesis_fingerprint="sha256:" + "0" * 64), evidence
        )
    critic = repo / evidence["cycle"] / "critic_result.md"
    critic.write_bytes(b"TEST_ONLY forged critic")
    with pytest.raises(original_source.OriginalBlocked):
        original_source.verify(repo, contract, evidence)


def test_same_parameter_bounds_cannot_replace_entry_exit_filters_risk_or_clock(native_chain):
    repo, contract, evidence = native_chain
    target = repo / "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json"
    source = json.loads(target.read_bytes())
    for field in ("entry_logic", "exit_logic", "filters", "risk_model", "timeframe_and_data"):
        replacement = copy.deepcopy(source)
        replacement[field] = {"TEST_ONLY_SUBSTITUTION": True}
        write(target, replacement)
        subprocess.run(["git", "add", str(target)], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=TEST_ONLY",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-qm",
                "TEST_ONLY tampered semantics",
            ],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        with pytest.raises(original_source.OriginalBlocked, match="SEMANTIC_SUBSTITUTION"):
            original_source.verify(
                repo,
                replace(contract, repo_sha=sha, strategy_spec_hash=mapper.file_hash(target)),
                evidence,
            )


def test_original_route_sidecar_cannot_grant_pre_read_access(native_chain, monkeypatch):
    from tools.lab_pipeline import runner_adapter as adapter

    repo, _, _ = native_chain
    prepared = prepare_native(native_chain)
    spec = repo / prepared["paths"]["spec"]
    mapping = spec.parent / "mapping.json"
    monkeypatch.setattr(adapter, "REPO_ROOT", repo)
    monkeypatch.setattr(
        adapter, "_execution_binding", lambda **k: pytest.fail("unauthorized historical read")
    )
    for content in (
        None,
        {"schema_version": "research_factory_mapping_v1"},
        {"schema_version": mapper.ORIGINAL_SCHEMA},
    ):
        if content is None:
            mapping.unlink()
        else:
            write(mapping, content)
        with pytest.raises(adapter.RunnerAdapterError, match="BLOCKED_NONHOLDOUT_CUSTODY"):
            adapter._route_before_read(spec)
    relocated = repo / "scratch/relocated.strategy_spec.json"
    relocated.write_bytes(spec.read_bytes())
    with pytest.raises(adapter.RunnerAdapterError, match="BLOCKED_NONHOLDOUT_CUSTODY"):
        adapter._route_before_read(relocated)
    value = json.loads(spec.read_bytes())
    value["provenance"]["source_refs"] = []
    write(relocated, value)
    with pytest.raises(adapter.RunnerAdapterError, match="UNKNOWN_EXECUTION_ROUTE"):
        adapter._route_before_read(relocated)


def test_native_proof_api_never_trusts_a_supplied_store_or_dict(tmp_path):
    from tools.research_factory.original_study_bridge import verify_native_report

    report = verify_native_report(
        store=SimpleNamespace(),
        repo_root=tmp_path,
        mapping_binding={"PROVEN": True},
        summary_binding={"PROVEN": True},
    )
    assert report["status"] == "BLOCKED_NATIVE_PROOF"
    assert not any(v == "PROVEN" for v in report["proof_status"].values())


def test_same_bounds_with_changed_model_operator_prose_is_not_reinterpreted(native_chain):
    from tools.hermes import intent_strategy_spec_handoff as native

    repo, contract, evidence = native_chain
    response = repo / evidence["responses"] / "00.response.json"
    content = json.loads(response.read_bytes())
    content["reasoned_draft"]["entry_concept"] = "Enter intrabar at the channel boundary."
    write(response, content)
    source_sha = json.loads((repo / evidence["packet"] / "packet.json").read_bytes())["repo_sha"]
    producer = native.IntentStrategySpecHandoff(
        repo, RepoIdentity(repo_sha=source_sha, branch="test")
    )
    output = repo / "scratch/rebuilt-substituted"
    native._publish(
        producer.build_files(repo / evidence["prepared"], repo / evidence["responses"]),
        output,
        native.verify_built,
    )
    with pytest.raises(original_source.OriginalBlocked, match="UNSUPPORTED_OPERATOR_SEMANTICS"):
        original_source.verify(
            repo, contract, dict(evidence, built=output.relative_to(repo).as_posix())
        )


def test_direct_kernel_verifier_cannot_bypass_atomic_custody_boundary(tmp_path):
    from tools.research_factory.evidence import EvidenceBlocked, verify_commitment

    payload = {
        k: None
        for k in (
            "campaign_id",
            "search_id",
            "contract_hash",
            "proposal_id",
            "scientific_trial_id",
            "variant_id",
            "params_fingerprint",
            "attempt_number",
            "idempotency_id",
            "classification",
            "approval_id",
            "approval_sha256",
            "prepared_hashes",
            "runner_result_sha256",
            "authority_lineage_version",
            "authority_lineage_sha256",
            "mapping_binding",
            "summary_binding",
            "fold_binding",
            "fold_manifest_binding",
            "fold_sha256",
            "robustness_binding",
            "robustness_sha256",
            "purge_bars",
            "embargo_bars",
        )
    }
    mapping = write(tmp_path / "scratch/mapping.json", {"schema_version": mapper.ORIGINAL_SCHEMA})
    payload["mapping_binding"] = {
        "path": "scratch/mapping.json",
        "sha256": mapper.file_hash(mapping),
    }
    with pytest.raises(EvidenceBlocked, match="BLOCKED_ATOMIC_CUSTODY_COMMIT"):
        verify_commitment(tmp_path, payload, SimpleNamespace())


def test_historical_payload_cannot_be_read_as_prepared_metadata(monkeypatch):
    from tools.lab_pipeline import runner_adapter as adapter

    monkeypatch.setattr(adapter, "read_json", lambda *a: pytest.fail("historical byte read"))
    with pytest.raises(adapter.RunnerAdapterError, match="prepared metadata role"):
        adapter._route_before_read("data/processed/d4a/TEST_ONLY.csv")


@pytest.mark.parametrize("entrypoint", ["approval_template", "run_product_runner_adapter"])
def test_metadata_role_guard_also_applies_to_synthetic_entrypoints(monkeypatch, entrypoint):
    from tools.lab_pipeline import runner_adapter as adapter

    monkeypatch.setattr(adapter, "read_json", lambda *a: pytest.fail("historical byte read"))
    args = dict(prepared_strategy_spec_path="data/processed/d4a/TEST_ONLY.csv",
                prepared_variant_manifest_path="scratch/x.variant_manifest.json",
                prepared_sweep_plan_path="scratch/x.sweep_plan.json",
                bridge_preparation_run_id="TEST", product_pipeline_run_id="TEST", canonical_15m=False)
    if entrypoint == "run_product_runner_adapter":
        args["execute_approval_path"] = "scratch/TEST_ONLY.json"
    with pytest.raises(adapter.RunnerAdapterError, match="BLOCKED_PREPARED_METADATA_ROLE"):
        getattr(adapter, entrypoint)(**args)


@pytest.mark.parametrize("tamper", [{"approved_by": "model"},
    {"prepared_strategy_spec_sha256": "sha256:" + "0" * 64},
    {"original_route": {"contract_hash": "invented"}}])
def test_legacy_lookalike_still_requires_exact_owner_marker_before_source_read(tmp_path, monkeypatch, tamper):
    from tests.test_lab_pipeline_runner_adapter import _configure_temp_repo, _prepared_bridge_packet, _real_route_fixture
    from tools.lab_pipeline import runner_adapter as adapter
    from tools.lab_pipeline.state import write_json

    output = _configure_temp_repo(monkeypatch, tmp_path)
    bridge, review = _prepared_bridge_packet(tmp_path)
    source_paths = _real_route_fixture(monkeypatch, tmp_path, output)
    kwargs = dict(prepared_strategy_spec_path=bridge["artifact_paths"]["strategy_spec"],
                  prepared_variant_manifest_path=bridge["artifact_paths"]["variant_manifest"],
                  prepared_sweep_plan_path=bridge["artifact_paths"]["sweep_plan"],
                  bridge_preparation_run_id=bridge["run_id"],
                  product_pipeline_run_id=review["product_bridge_preparation_metadata"]["product_pipeline_run_id"],
                  output_root=output, **source_paths)
    marker = adapter.approval_template(**kwargs)
    marker.update(tamper)
    marker_path = write_json(output / "TEST_ONLY-marker.json", marker)
    monkeypatch.setattr(adapter, "_execution_binding", lambda **k: pytest.fail("source read before owner validation"))
    monkeypatch.setattr(adapter, "_invoke_existing_runner", lambda **k: pytest.fail("unauthorized runner"))
    with pytest.raises(adapter.RunnerAdapterError, match="BLOCKED"):
        adapter.run_product_runner_adapter(**kwargs, execute_approval_path=marker_path)
