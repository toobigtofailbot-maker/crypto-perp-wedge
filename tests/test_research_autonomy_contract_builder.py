import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from tools.mcp.project_evidence.research_intent import BoundedResearchIntentV1, semantic_content_sha256
from tools.research_autonomy.contract_builder import construct_contract, validate_inputs
from tools.research_autonomy.envelope import envelope_hash, validate_envelope
from tools.research_autonomy.models import BoundedSearchRequest, DurableLineageSnapshot
from tools.research_memory.fingerprint import fingerprint

ROOT = Path(__file__).resolve().parents[1]


def fixture_inputs(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "docs").mkdir()
    (repo / "research/strategy_specs").mkdir(parents=True)
    (repo / "docs/fixture.md").write_text("Synthetic metadata only\n", encoding="utf-8")
    (repo / ".gitignore").write_text("/.cpw/\n", encoding="utf-8")
    (repo / "research/strategy_specs/STRAT-SPEC-FIXTURE.strategy_spec.json").write_text(json.dumps({"strategy_spec_id": "STRAT-SPEC-FIXTURE", "timeframe_and_data": {"primary_timeframe": "1h"}}), encoding="utf-8")
    for args in (["init", "-q"], ["config", "core.autocrlf", "false"], ["add", "."], ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "synthetic metadata"]):
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

    def evidence(path):
        return {"resource_uri": "project://fixture", "repo_path": path, "repo_sha": sha,
                "artifact_sha256": hashlib.sha256((repo / path).read_bytes()).hexdigest()}

    payload = json.loads((ROOT / "tests/fixtures/research_autonomy/bounded_research_envelope.fixture.json").read_text())
    payload["repo_sha"] = sha
    payload["search_policy"]["data_bindings"][0]["evidence"] = evidence("docs/fixture.md")
    payload["content_sha256"] = envelope_hash(payload)
    envelope = validate_envelope(payload, repo_sha=sha)
    definition = {"strategy_family": "fixture family", "mechanism": "synthetic mechanism", "primary_timeframe": "1h", "required_data_features": ["ohlcv"], "free_parameter_count": 1}
    fp = fingerprint(definition)
    intent_payload = {"schema_version": "cpw_bounded_research_intent_v1", "request_id": "INTENT-FIXTURE", "repo_sha": sha, "content_sha256": "sha256:" + "0" * 64,
        **definition, "instrument_scope": "BTCUSDT_BINANCE_USDTM_PERP", "fingerprint_version": "hypothesis-v1", "fingerprint_sha256": fp,
        "research_question": "Synthetic bounded construction?", "causal_rationale": "Fixture only", "falsifiable_prediction": "Fixture only", "falsification_stop_conditions": ["Fixture only"], "proposed_parameter_bounds": [{"name": "lookback", "minimum": 2.0, "maximum": 100.0}], "proposed_objective_intent": "Fixture only", "unresolved_assumptions": [], "evidence_anchors": [evidence("docs/fixture.md")],
        "research_memory": {"fingerprint_version": "hypothesis-v1", "fingerprint_sha256": fp, "matched": False, "index_not_truth": True, "records": [], "repo_sha": sha, "postgres_boundary": "synthetic read-only context", "authority": {"not_scientific_truth": True}}}
    intent = BoundedResearchIntentV1.model_validate(intent_payload)
    intent = intent.model_copy(update={"content_sha256": semantic_content_sha256(intent)})
    policy = payload["search_policy"]
    request_payload = {"campaign_id": "CAMPAIGN-FIXTURE", "search_id": "SEARCH-FIXTURE", "parent_search_id": None, "reason_for_change": None, "intent_sha256": intent.content_sha256, "hypothesis_id": "H-FIXTURE", "family_id": "FAMILY-FIXTURE", "strategy_spec_id": "STRAT-SPEC-FIXTURE", "strategy_spec_evidence": evidence("research/strategy_specs/STRAT-SPEC-FIXTURE.strategy_spec.json"), "data_identity": "SYNTHETIC-DATA", "data_version": "v1", "data_evidence": evidence("docs/fixture.md"), "instrument": "BTCUSDT", "venue": "Binance USDT-M", "market_type": "perpetual", "data_source_class": "synthetic", "dsl_version": "v1", "parameter_space": policy["parameter_domains"], "conditional_rules": [], "relational_constraints": [], "forbidden_regions": [], "objective": policy["objectives"][0], "scientific_protocol": payload["scientific_protocol"], "max_proposals": 6, "max_scientific_trials": 4, "compute_seconds": 30, "runtime_seconds": 60, "recovery_limit": 2, "wave_size": 2, "concurrency": 1, "split_protocol": policy["split_protocols"][0], "proposer": policy["proposers"][0], "seed": 1729, "policies": policy["policies"]}
    request = BoundedSearchRequest.model_validate_json(json.dumps(request_payload))
    return repo, intent, envelope, request


def fixture_snapshot(envelope, *, proposals=0, trials=0):
    return DurableLineageSnapshot.model_validate_json(json.dumps({"campaign_id": "CAMPAIGN-FIXTURE", "envelope_id": envelope.envelope_id, "envelope_version": 1, "envelope_content_sha256": envelope.content_sha256, "contamination_domain_id": "DOMAIN-FIXTURE", "lineage_version": 1, "lineage_sha256": "sha256:" + "1" * 64, "budget": {"proposals_used": proposals, "scientific_trials_used": trials, "reserved_proposals": 0, "reserved_trials": 0, "proposal_ceiling": 12, "trial_ceiling": 8, "search_ceiling": 3, "search_count": 0}, "holdout": {"contamination_domain_id": "DOMAIN-FIXTURE", "holdout_id": "HOLDOUT-FIXTURE", "state": "unexposed", "contaminated": False}}))


def test_contract_is_deterministic_and_uses_durable_history(tmp_path):
    repo, intent, envelope, request = fixture_inputs(tmp_path)
    args = validate_inputs(intent, envelope, request, repo_root=repo)
    snapshot = fixture_snapshot(envelope, proposals=3, trials=2)
    first = construct_contract(*args, snapshot)
    assert first == construct_contract(*args, snapshot)
    assert first.campaign_proposals_before_search == 3
    assert first.campaign_scientific_trials_before_search == 2
    assert first.authority_lineage_sha256 == snapshot.lineage_sha256
    from tools.research_search.governor import SearchGovernor
    governor = SearchGovernor(first)
    assert request.split_protocol.final_holdout_ref not in json.dumps(governor.adapter_surface)


@pytest.mark.parametrize("field,value", [("max_proposals", 7), ("venue", "other"), ("data_version", "unapproved"), ("intent_sha256", "sha256:" + "0" * 64)])
def test_request_policy_mismatches_fail(tmp_path, field, value):
    repo, intent, envelope, request = fixture_inputs(tmp_path)
    with pytest.raises(ValueError):
        validate_inputs(intent, envelope, request.model_copy(update={field: value}), repo_root=repo)


def test_parameter_widening_evidence_tamper_and_missing_authority_fail(tmp_path):
    repo, intent, envelope, request = fixture_inputs(tmp_path)
    payload = request.model_dump(mode="json")
    payload["parameter_space"][0]["high"] = 101
    with pytest.raises(ValueError, match="parameter"):
        validate_inputs(intent, envelope, BoundedSearchRequest.model_validate_json(json.dumps(payload)), repo_root=repo)
    for field in ("campaign_proposals_before_search", "remaining_campaign_budget", "authority_lineage_version", "holdout_fresh"):
        payload = request.model_dump(mode="json")
        payload[field] = 0
        with pytest.raises(ValueError):
            BoundedSearchRequest.model_validate_json(json.dumps(payload))
    (repo / "docs/fixture.md").write_text("tampered")
    with pytest.raises(ValueError, match="hash mismatch"):
        validate_inputs(intent, envelope, request, repo_root=repo)


def test_consumed_domain_and_durable_budget_fail_closed(tmp_path):
    _, intent, envelope, request = fixture_inputs(tmp_path)
    s = fixture_snapshot(envelope, proposals=10)
    with pytest.raises(ValueError, match="budget"):
        construct_contract(intent, envelope, request, s)
    s = fixture_snapshot(envelope)
    s = s.model_copy(update={"holdout": s.holdout.model_copy(update={"contaminated": True})})
    with pytest.raises(ValueError, match="contamination"):
        construct_contract(intent, envelope, request, s)


def test_autonomy_never_calls_historical_successor_or_execution_owners():
    import ast
    forbidden = ("tools.hermes", "tools.prefect_integration", "tools.research_runner", "lib.backtest", "tools.canon_intake", "src.runtime")
    for path in (ROOT / "tools/research_autonomy").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(forbidden)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr != "successor"
