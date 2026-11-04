"""Read-only Stage 0->3 projection: original Hermes hypothesis -> native CPW science evidence.

Builds `origin_to_science_report.json` from evidence that already exists. It never writes Gate
C, approvals, envelopes, trials or results, and a projection is never a permission token.
Stages are hash-linked; the first missing or contradictory link stops the chain with a stable
refusal code and every later stage is reported NOT_REACHED. A/B/A+B/C are independent labels.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.agent_inbox_intake.service import original_parent_sha256
from tools.hermes import discovery_intent as di
from tools.hermes.model_origin_receipt import BLOCKED, FIXTURE

SCHEMA = "cpw_origin_to_science_report_v1"
ORIGINAL_MAPPING = "research_factory_mapping_original_v1"
EXECUTED = {"research_completed", "research_completed_no_edge", "research_failed"}
ECONOMICS = {
    "runner_route": "canonical_15m_d4_provenance",
    "funding_cost_mode": "off",
    "sizing_mode": "dynamic_equity_target_leverage",
    "target_leverage": 1.0,
    "fees": "taker 4 bps / maker 2 bps (lib/backtest.py)",
    "slippage": "fixed 1 bp",
    "fills": "complete fill at next bar open; no partial fills or queue",
    "economic_claim": "NONE: funding-off D4 cannot establish net perpetual edge; no GO",
}


def _prefixed(value: str | None) -> str | None:
    if value is None:
        return None
    return value if value.startswith("sha256:") else "sha256:" + value


def _file(path) -> tuple[bytes, str]:
    raw = Path(path).read_bytes()
    return raw, "sha256:" + hashlib.sha256(raw).hexdigest()


def original_parent(origin: dict, idea: dict, fingerprint_sha256: str) -> dict:
    """The exact closed parent reference carried by Agent Inbox and the original mapper."""
    match = [i for i in origin.get("ideas", []) if i["idea_id"] == idea["idea_id"]]
    if len(match) != 1 or match[0]["original_hypothesis_sha256"] != di.canonical_sha256(idea):
        raise ValueError("BLOCKED_ORIGIN_UNVERIFIED: idea not in verified origin cohort")
    parent = {
        "idea_id": idea["idea_id"],
        "original_hypothesis_sha256": _prefixed(match[0]["original_hypothesis_sha256"]),
        "fingerprint_sha256": _prefixed(fingerprint_sha256),
        "cycle_manifest_sha256": _prefixed(origin["cycle_manifest_sha256"]),
        "origin_status": origin["status"],
    }
    parent["original_parent_sha256"] = original_parent_sha256(parent)
    return parent


def _semantics(idea: dict, spec: dict) -> str | None:
    """Exact continuity of clock and free-parameter domain; narrowing only, never substitution."""
    draft = idea.get("native_draft")
    if not isinstance(draft, dict):
        return "BLOCKED_UNSUPPORTED_FAMILY_OR_DSL"
    if draft.get("primary_timeframe") != "15m":
        return "BLOCKED_UNSUPPORTED_TIMEFRAME_OR_DATA"
    if spec["timeframe_and_data"]["primary_timeframe"] != draft["primary_timeframe"]:
        return "BLOCKED_SEMANTIC_SUBSTITUTION"
    bounds = {b["name"]: b for b in draft.get("proposed_parameter_bounds", [])}
    params = {p["name"]: p for p in spec["free_parameters"]["parameters"]}
    if set(bounds) != set(params) or len(params) != draft.get("free_parameter_count"):
        return "BLOCKED_SEMANTIC_SUBSTITUTION"
    for name, param in params.items():
        values = param.get("allowed_values") or []
        if not values or any(not bounds[name]["minimum"] <= v <= bounds[name]["maximum"] for v in values):
            return "BLOCKED_SEMANTIC_SUBSTITUTION"
    return None


def build_report(*, origin: dict | None, idea: dict | None = None, fingerprint_sha256: str | None = None,
                 inbox_packet_path=None, gate_c_audit: dict | None = None, canonical_spec_path=None,
                 contract: dict | None = None, mapping: dict | None = None,
                 factory_report: dict | None = None) -> dict:
    stages = {}
    chain = {"origin": origin and {k: origin.get(k) for k in (
        "status", "reason", "observed_host_receipt_sha256", "observer_identity", "trust_anchor_ref",
        "cycle_manifest_sha256", "image_digest", "critic_sha256", "intent_sha256", "source_packet_sha256")}}
    blocked = None

    def stage(name, code=None, **evidence):
        nonlocal blocked
        if blocked:
            stages[name] = {"status": "NOT_REACHED"}
            return False
        stages[name] = {"status": code or "OK", **evidence}
        if code:
            blocked = code
        return code is None

    parent = None
    if origin is None or idea is None or origin.get("status") == BLOCKED and not origin.get("ideas"):
        stage("stage0_origin", "BLOCKED_ORIGIN_UNVERIFIED")
    else:
        try:
            parent = original_parent(origin, idea, fingerprint_sha256 or "")
            stage("stage0_origin", None, parent=parent)
        except (ValueError, KeyError, TypeError):
            stage("stage0_origin", "BLOCKED_ORIGIN_UNVERIFIED")
    spec = None
    if not blocked:
        if canonical_spec_path is None:
            stage("stage1_semantics", "BLOCKED_NATIVE_02B_OR_02C_MISSING")
        else:
            spec_raw, spec_hash = _file(canonical_spec_path)
            spec = json.loads(spec_raw)
            stage("stage1_semantics", _semantics(idea, spec), canonical_spec_sha256=spec_hash)
    if not blocked:
        packet_raw, packet_hash = _file(inbox_packet_path) if inbox_packet_path else (b"{}", None)
        packet = json.loads(packet_raw)
        audit = gate_c_audit or {}
        linked = (
            packet.get("source_hashes", {}).get("original_hermes_parent_sha256") == parent["original_parent_sha256"]
            and packet.get("provenance", {}).get("original_hermes_parent") == parent
            and audit.get("schema_version") == "gate_c_strategy_spec_write_audit_v1"
            and audit.get("source_hashes") == packet.get("source_hashes")
            and audit.get("source_draft", {}).get("sha256") == packet_hash
            and audit.get("approved_content_sha256") == stages["stage1_semantics"]["canonical_spec_sha256"]
        )
        stage("stage1_gate_c", None if linked else "BLOCKED_GATE_C_REVIEW_OR_APPROVAL",
              inbox_packet_sha256=packet_hash, gate_c_approval_id=audit.get("approval_id"),
              gate_c_approval_record_sha256=audit.get("approval_record_sha256"))
    if not blocked:
        contract = contract or {}
        ok = (contract.get("hypothesis_fingerprint") == parent["fingerprint_sha256"]
              and contract.get("strategy_spec_hash") == stages["stage1_semantics"]["canonical_spec_sha256"])
        stage("stage2_contract", None if ok else "BLOCKED_ENVELOPE_OR_CONTRACT",
              contract_hash=contract.get("contract_hash"), campaign_id=contract.get("campaign_id"),
              search_id=contract.get("search_id"), envelope_id=contract.get("envelope_id"))
    if not blocked:
        mapping = mapping or {}
        expected = {k: parent[k] for k in ("idea_id", "original_hypothesis_sha256", "fingerprint_sha256",
                                           "original_parent_sha256")}
        ok = (mapping.get("schema_version") == ORIGINAL_MAPPING and mapping.get("original_parent") == expected
              and mapping.get("contract_hash") == contract.get("contract_hash"))
        stage("stage2_governor_mapping", None if ok else "BLOCKED_ENVELOPE_OR_CONTRACT",
              proposal_ids=[m["proposal_id"] for m in mapping.get("mapping", [])],
              scientific_trial_ids=[m["scientific_trial_id"] for m in mapping.get("mapping", [])],
              scientific_denominator=mapping.get("scientific_denominator"),
              proposal_counts=mapping.get("proposal_counts"))
    executed = False
    if not blocked:
        report = factory_report or {}
        reasons = report.get("withholding_reasons") or []
        if not report:
            stage("stage3_physical", "NOT_EXECUTED")
        elif report.get("disposition") not in EXECUTED:
            code = next((r.split(":")[0] for r in reasons if r.startswith("BLOCKED_")), "BLOCKED_MAY_HAVE_RUN_RECONCILE")
            stage("stage3_physical", code, disposition=report.get("disposition"))
        elif (report.get("prepared") != mapping
              or len(report.get("terminal_commitments") or []) != mapping.get("scientific_denominator")):
            stage("stage3_physical", "BLOCKED_INCOMPLETE_RESULT_POPULATION")
        else:
            executed = stage("stage3_physical", None, disposition=report["disposition"],
                             approval_sha256=report.get("approval_sha256"),
                             scratch_result_sha256=report.get("scratch_result_sha256"),
                             terminal_commitments=report["terminal_commitments"],
                             runner_parity=report.get("runner_parity"))
    fixture = bool(origin and origin.get("status") == FIXTURE)
    # This dictionary-only projection has neither a host anchor nor a durable store.
    # Native origin verification and trial/custody reconciliation own physical proof.
    a = b = False
    return {
        "schema_version": SCHEMA,
        "not_authority": True,
        "permission_token": False,
        "idea_id": idea and idea.get("idea_id"),
        "original_parent": parent,
        "origin_chain": chain,
        "stages": stages,
        "first_block": blocked,
        "proof_status": {
            "A_CAPTURED_STUDY_REAL": "PROVEN" if a else "NOT_PROVEN" if executed else "NOT_EXECUTED",
            "B_MODEL_ORIGIN_VERIFIED": "PROVEN" if b else "NOT_PROVEN",
            "A_PLUS_B_HERMES_AUTHORED_STUDY": "PROVEN" if a and b else "NOT_PROVEN",
            "C_AUTONOMOUS_SELECTION_VERIFIED": "NOT_PROVEN",
        },
        "fixture_origin": fixture,
        "economics": ECONOMICS,
        "limitations": [
            "supplied dictionaries cannot establish A or B; native host and durable trial/custody verification required",
            "B is host-observed with an operator-pinned anchor, not provider-signed",
        ],
    }
