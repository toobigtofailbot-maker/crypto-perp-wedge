"""Read-only origin->science projection. All inputs are labeled TEST_ONLY software fixtures."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from tools.hermes import discovery_intent as di
from tools.hermes import model_origin_receipt as mor
from tools.research_factory import original_study_bridge as bridge

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json"
FINGERPRINT = "sha256:" + "5" * 64
IDEA = {
    "idea_id": "IDEA-TEST-ONLY",
    "title": "TEST_ONLY labeled hypothesis",
    "native_draft": {
        "primary_timeframe": "15m",
        "free_parameter_count": 3,
        "proposed_parameter_bounds": [
            {"name": "center_lookback_bars", "minimum": 20, "maximum": 200},
            {"name": "vol_lookback_bars", "minimum": 10, "maximum": 100},
            {"name": "trend_lookback_bars", "minimum": 50, "maximum": 400},
        ],
    },
}


def _origin(idea=IDEA, status=mor.FIXTURE):
    return {"status": status, "reason": None, "cycle_manifest_sha256": "a" * 64,
            "ideas": [{"idea_id": idea["idea_id"], "original_hypothesis_sha256": di.canonical_sha256(idea)}]}


def chain(tmp_path, idea=IDEA, origin=None):
    origin = origin or _origin(idea)
    parent = bridge.original_parent(origin, idea, FINGERPRINT)
    spec_hash = "sha256:" + hashlib.sha256(SPEC.read_bytes()).hexdigest()
    packet = {"source_hashes": {"source_request_sha256": "sha256:" + "1" * 64,
                                "original_hermes_parent_sha256": parent["original_parent_sha256"]},
              "provenance": {"original_hermes_parent": parent}}
    packet_path = tmp_path / "AIDRAFT-TEST.draft_packet.json"
    packet_path.write_text(json.dumps(packet))
    audit = {"schema_version": "gate_c_strategy_spec_write_audit_v1", "approval_id": "GATE-C-TEST-ONLY",
             "approval_record_sha256": "sha256:" + "2" * 64, "source_hashes": packet["source_hashes"],
             "source_draft": {"sha256": "sha256:" + hashlib.sha256(packet_path.read_bytes()).hexdigest()},
             "approved_content_sha256": spec_hash}
    contract = {"hypothesis_fingerprint": FINGERPRINT, "strategy_spec_hash": spec_hash,
                "contract_hash": "sha256:" + "3" * 64, "campaign_id": "C", "search_id": "S", "envelope_id": "E"}
    mapping = {"schema_version": bridge.ORIGINAL_MAPPING, "contract_hash": contract["contract_hash"],
               "original_parent": {k: parent[k] for k in ("idea_id", "original_hypothesis_sha256",
                                                          "fingerprint_sha256", "original_parent_sha256")},
               "mapping": [{"proposal_id": f"P{i}", "scientific_trial_id": f"T{i}"} for i in range(2)],
               "scientific_denominator": 2, "proposal_counts": {"accepted": 2}}
    report = {"disposition": "research_completed_no_edge", "prepared": mapping,
              "terminal_commitments": ["E1", "E2"], "withholding_reasons": []}
    return {"origin": origin, "idea": idea, "fingerprint_sha256": FINGERPRINT, "inbox_packet_path": packet_path,
                "gate_c_audit": audit, "canonical_spec_path": SPEC, "contract": contract, "mapping": mapping,
                "factory_report": report}


def test_complete_fixture_chain_links_every_stage_but_proves_nothing(tmp_path):
    report = bridge.build_report(**chain(tmp_path))
    assert report["first_block"] is None
    assert all(s["status"] == "OK" for s in report["stages"].values())
    assert report["stages"]["stage2_governor_mapping"]["scientific_trial_ids"] == ["T0", "T1"]
    assert report["proof_status"] == {
        "A_CAPTURED_STUDY_REAL": "NOT_PROVEN", "B_MODEL_ORIGIN_VERIFIED": "NOT_PROVEN",
        "A_PLUS_B_HERMES_AUTHORED_STUDY": "NOT_PROVEN", "C_AUTONOMOUS_SELECTION_VERIFIED": "NOT_PROVEN"}
    assert report["fixture_origin"] is True and report["not_authority"] is True
    assert report["permission_token"] is False and report["economics"]["funding_cost_mode"] == "off"


def test_unanchored_origin_is_never_b(tmp_path):
    report = bridge.build_report(**chain(tmp_path, origin=_origin(status=mor.BLOCKED)))
    assert report["proof_status"]["B_MODEL_ORIGIN_VERIFIED"] == "NOT_PROVEN"
    assert report["proof_status"]["A_PLUS_B_HERMES_AUTHORED_STUDY"] == "NOT_PROVEN"


def test_caller_declared_verified_origin_and_completed_factory_cannot_promote_proof(tmp_path):
    report = bridge.build_report(**chain(tmp_path, origin=_origin(status=mor.VERIFIED)))
    assert all(value == "NOT_PROVEN" for value in report["proof_status"].values())


def _idea(**draft):
    idea = copy.deepcopy(IDEA)
    idea["native_draft"].update(draft)
    return idea


@pytest.mark.parametrize("mutate,code", [
    (lambda c: c.update(origin=None), "BLOCKED_ORIGIN_UNVERIFIED"),
    (lambda c: c["origin"]["ideas"][0].update(original_hypothesis_sha256="f" * 64), "BLOCKED_ORIGIN_UNVERIFIED"),
    (lambda c: c.update(canonical_spec_path=None), "BLOCKED_NATIVE_02B_OR_02C_MISSING"),
    (lambda c: c["gate_c_audit"].update(approved_content_sha256="sha256:" + "0" * 64), "BLOCKED_GATE_C_REVIEW_OR_APPROVAL"),
    (lambda c: c["gate_c_audit"]["source_hashes"].pop("original_hermes_parent_sha256"), "BLOCKED_GATE_C_REVIEW_OR_APPROVAL"),
    (lambda c: c["contract"].update(hypothesis_fingerprint="sha256:" + "9" * 64), "BLOCKED_ENVELOPE_OR_CONTRACT"),
    (lambda c: c["mapping"].update(schema_version="research_factory_mapping_v1"), "BLOCKED_ENVELOPE_OR_CONTRACT"),
    (lambda c: c.update(factory_report=None), "NOT_EXECUTED"),
    (lambda c: c["factory_report"].update(disposition="research_blocked", withholding_reasons=[
        "BLOCKED_NONHOLDOUT_CUSTODY: exact study custody lease required"]), "BLOCKED_NONHOLDOUT_CUSTODY"),
    (lambda c: c["factory_report"].update(terminal_commitments=["E1"]), "BLOCKED_INCOMPLETE_RESULT_POPULATION"),
])
def test_each_broken_link_stops_with_stable_code(tmp_path, mutate, code):
    args = chain(tmp_path)
    mutate(args)
    report = bridge.build_report(**args)
    assert report["first_block"] == code
    assert report["proof_status"]["A_CAPTURED_STUDY_REAL"] != "PROVEN"
    statuses = [s["status"] for s in report["stages"].values()]
    assert statuses[statuses.index(code) + 1:] == ["NOT_REACHED"] * (len(statuses) - statuses.index(code) - 1)


@pytest.mark.parametrize("idea,code", [
    (dict(IDEA, native_draft=None), "BLOCKED_UNSUPPORTED_FAMILY_OR_DSL"),
    (_idea(primary_timeframe="4h"), "BLOCKED_UNSUPPORTED_TIMEFRAME_OR_DATA"),
    (_idea(free_parameter_count=2), "BLOCKED_SEMANTIC_SUBSTITUTION"),
    (_idea(proposed_parameter_bounds=[{"name": "center_lookback_bars", "minimum": 60, "maximum": 70},
                                      {"name": "vol_lookback_bars", "minimum": 10, "maximum": 100},
                                      {"name": "trend_lookback_bars", "minimum": 50, "maximum": 400}]),
     "BLOCKED_SEMANTIC_SUBSTITUTION"),
])
def test_original_mechanism_is_never_substituted_with_template(tmp_path, idea, code):
    report = bridge.build_report(**chain(tmp_path, idea=idea))
    assert report["first_block"] == code
