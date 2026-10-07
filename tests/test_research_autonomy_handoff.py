import copy
import json

import pytest

from test_research_autonomy_contract_builder import fixture_inputs, fixture_snapshot
from tools.research_autonomy.contract_builder import construct_contract
from tools.research_autonomy.envelope import content_hash
from tools.research_autonomy.handoff import load_handoff, make_handoff, replay_handoff, validate_handoff, write_handoff
from tools.research_search.governor import SearchGovernor


class StaticStore:
    """A unit-test double; physical durable binding is tested in PostgreSQL."""
    def __init__(self, snapshot, contract):
        self.snapshot = snapshot
        self.contract = contract

    def load_snapshot(self, campaign_id):
        assert campaign_id == self.contract.campaign_id
        return self.snapshot

    def verify_recovery_binding(self, handoff, *, repo_root):
        return self.snapshot, self.contract


def handoff_fixture(tmp_path):
    repo, intent, envelope, request = fixture_inputs(tmp_path)
    snapshot = fixture_snapshot(envelope)
    contract = construct_contract(intent, envelope, request, snapshot)
    store = StaticStore(snapshot, contract)
    governor = SearchGovernor(contract)
    pre = governor.snapshot()
    governor.propose_wave(2)
    handoff = make_handoff(store=store, contract=contract, intent_sha256=intent.content_sha256,
        pre_wave_snapshot=pre, requested_wave_count=2, proposal_records=governor.proposal_records,
        resulting_denominator=governor.scientific_denominator, repo_root=repo)
    return repo, store, governor, handoff


def test_active_wave_roundtrip_and_exact_replay(tmp_path):
    repo, store, original, handoff = handoff_fixture(tmp_path)
    path = write_handoff(handoff, repo_root=repo)
    assert path.is_relative_to(repo / ".cpw/active")
    assert write_handoff(handoff, repo_root=repo) == path
    loaded = load_handoff(path, repo_root=repo)
    replayed = replay_handoff(loaded, store=store, repo_root=repo)
    assert json.dumps([p.to_dict() for p in replayed.proposal_records], sort_keys=True) == json.dumps([p.to_dict() for p in original.proposal_records], sort_keys=True)
    assert replayed.scientific_denominator == original.scientific_denominator
    assert loaded.noncanonical and not loaded.runner_authority


@pytest.mark.parametrize("field", ["authority_lineage_sha256", "contract_hash", "resulting_denominator", "proposal_records"])
def test_tampered_hash_and_rehashed_binding_fail(tmp_path, field):
    repo, store, _, handoff = handoff_fixture(tmp_path)
    raw = handoff.model_dump(mode="json")
    if field == "proposal_records":
        raw[field][0]["params"]["lookback"] += 1
    elif field == "resulting_denominator":
        raw[field] += 1
    else:
        raw[field] = "sha256:" + "f" * 64
    with pytest.raises(ValueError):
        validate_handoff(raw)
    raw["content_sha256"] = content_hash({k:v for k,v in raw.items() if k != "content_sha256"})
    with pytest.raises(ValueError):
        replay_handoff(raw, store=store, repo_root=repo)


def test_performance_payload_unknown_fields_and_authority_fail(tmp_path):
    _, _, _, handoff = handoff_fixture(tmp_path)
    for mutate in (
        lambda r: r.update(objective_value=1.0),
        lambda r: r["authority"].update(capital=True),
        lambda r: r["pre_wave_snapshot"]["objective_by_fingerprint"].update({"sha256:" + "a"*64: 1.0}),
        lambda r: r["proposal_records"][0].update(winner=True),
    ):
        raw = copy.deepcopy(handoff.model_dump(mode="json"))
        mutate(raw)
        raw["content_sha256"] = content_hash({k:v for k,v in raw.items() if k != "content_sha256"})
        with pytest.raises(ValueError):
            validate_handoff(raw)
