"""Read-only original-source closure. Native owners remain the only approval writers."""

from __future__ import annotations

import hashlib
import json
import re
import stat
import subprocess
from pathlib import Path

from tools.agent_inbox_intake.service import original_parent_sha256
from tools.canon_intake import spec_writer as gate_c
from tools.hermes import discovery_intent as di
from tools.hermes import discovery_intent_consumer as dc
from tools.hermes import intent_strategy_spec_handoff as hs
from tools.hermes import model_origin_receipt as origin
from tools.mcp.project_evidence.models import RepoIdentity
from tools.mcp.project_evidence.research_intent import BoundedResearchIntentV1
from tools.research_memory.fingerprint import HypothesisDefinition

SEMANTICS = (
    "entry_logic",
    "exit_logic",
    "filters",
    "instruments",
    "timeframe_and_data",
    "free_parameters",
    "constraints",
    "risk_model",
    "backtest_realism_assumptions",
)
INPUTS = {
    "idea_id",
    "cycle",
    "host_receipt",
    "packet",
    "batch",
    "prepared",
    "responses",
    "built",
    "gate_c_approval",
}
ROUTE_PREFIX = "cpw_original_source_v1:"


class OriginalBlocked(ValueError):
    """No admission on an incomplete or substituted source chain."""


def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def semantic_hash(spec):
    return digest(
        json.dumps(
            {k: spec[k] for k in SEMANTICS}, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    )


def path(root, relative):
    if (
        not isinstance(relative, str)
        or any(p in {"", ".", ".."} for p in relative.split("/"))
        or "\\" in relative
        or ":" in relative
    ):
        raise OriginalBlocked("BLOCKED_ORIGINAL_SOURCE_PATH")
    cursor = root.resolve(strict=True)
    for part in relative.split("/"):
        cursor /= part
        attributes = cursor.lstat()
        if stat.S_ISLNK(attributes.st_mode) or getattr(attributes, "st_file_attributes", 0) & 0x400:
            raise OriginalBlocked("BLOCKED_ORIGINAL_SOURCE_INDIRECTION")
    return cursor


def _same(left, right, reason):
    if left != right:
        raise OriginalBlocked(reason)


def _committed(root, relative, sha):
    if not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{40}", sha) is None:
        raise OriginalBlocked("BLOCKED_REPO_SHA")
    if not relative.startswith(("research/", "docs/", "tools/registry/")):
        raise OriginalBlocked("BLOCKED_NON_METADATA_SOURCE")
    raw = path(root, relative).read_bytes()
    committed = subprocess.run(
        ["git", "show", f"{sha}:{relative}"], cwd=root, check=True, capture_output=True
    ).stdout
    _same(raw, committed, "BLOCKED_UNCOMMITTED_ORIGINAL_SOURCE")
    return raw


def verify(root, contract, evidence, *, anchor_sha256=None):
    """Reproduce native 02A/B/C and Gate C evidence; caller dictionaries grant nothing."""
    try:
        if not isinstance(evidence, dict) or set(evidence) != INPUTS:
            raise OriginalBlocked("BLOCKED_ORIGINAL_SOURCE_REQUIRED")
        if any(
            not isinstance(v, str) or not v.startswith("scratch/")
            for k, v in evidence.items()
            if k != "idea_id"
        ):
            raise OriginalBlocked("BLOCKED_ORIGINAL_CAPTURE_ROOT")
        locations = {k: path(root, v) for k, v in evidence.items() if k != "idea_id"}
        packet = dc.load_source_packet(locations["packet"])
        source_sha = packet["repo_sha"]
        if any(not isinstance(s, str) or re.fullmatch(r"[0-9a-f]{40}", s) is None for s in (source_sha, contract.repo_sha)):
            raise OriginalBlocked("BLOCKED_REPO_SHA")
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", source_sha, contract.repo_sha],
            cwd=root,
            check=True,
            capture_output=True,
        )
        observed = origin.verify_origin(
            locations["cycle"],
            locations["host_receipt"],
            anchor_sha256=anchor_sha256,
            expected_repo_sha=source_sha,
        )
        if observed.get("status") == origin.BLOCKED and observed.get("reason") not in {
            "TRUST_ANCHOR_MISSING"
        }:
            raise OriginalBlocked("BLOCKED_ORIGIN_UNVERIFIED")
        for name, sha in packet["cycle"]["inputs"].items():
            _same(
                hashlib.sha256(path(locations["cycle"], name).read_bytes()).hexdigest(),
                sha,
                "BLOCKED_CAPTURE_PACKET_MISMATCH",
            )
        matches = [i for i in packet["ideas"] if i["idea_id"] == evidence["idea_id"]]
        if len(matches) != 1 or matches[0]["typed_status"] != "TYPED_VALID":
            raise OriginalBlocked("BLOCKED_NATIVE_INTENT_REQUIRED")
        authored = matches[0]["hermes_authored"]
        index = packet["ideas"].index(matches[0])
        batch = dc.verify_batch(locations["batch"])
        _same(
            batch["source_packet"]["content_sha256"], packet["content_sha256"], "BLOCKED_02B_SOURCE"
        )
        _same(batch["source_packet"]["inputs"], packet["cycle"]["inputs"], "BLOCKED_02B_CAPTURE")
        intent_ref = batch["ideas"][index]["native_intent"]
        intent = BoundedResearchIntentV1.model_validate_json(
            path(locations["batch"], intent_ref["file"]).read_bytes()
        )
        intent_json = intent.model_dump(mode="json")
        _same(
            HypothesisDefinition.from_mapping(intent_json),
            HypothesisDefinition.from_mapping(matches[0]["validated_request"]),
            "BLOCKED_02B_SEMANTIC_SUBSTITUTION",
        )
        for key, value in matches[0]["validated_request"].items():
            if key in intent_json and key not in {
                "schema_version",
                "evidence_resource_uris",
                "mechanism",
                "strategy_family",
                "required_data_features",
            }:
                _same(intent_json[key], value, "BLOCKED_02B_SEMANTIC_SUBSTITUTION")
        fingerprint = intent.fingerprint_sha256.removeprefix("sha256:")
        _same(
            fingerprint,
            matches[0]["fingerprint"]["sha256"].removeprefix("sha256:"),
            "BLOCKED_FINGERPRINT",
        )
        _same(
            fingerprint,
            contract.hypothesis_fingerprint.removeprefix("sha256:"),
            "BLOCKED_FINGERPRINT",
        )
        if intent.primary_timeframe != "15m" or set(intent.required_data_features) - {
            "ohlcv",
            "sma",
            "stddev",
            "donchian",
        }:
            raise OriginalBlocked("BLOCKED_UNQUALIFIED_DERIVED_INPUT")
        for anchor in intent.evidence_anchors:
            raw = _committed(root, anchor.repo_path, source_sha)
            _same(hashlib.sha256(raw).hexdigest(), anchor.artifact_sha256, "BLOCKED_NATIVE_ANCHOR")
        native = hs.IntentStrategySpecHandoff(
            root, RepoIdentity(repo_sha=source_sha, branch=packet["repo_branch"])
        )
        manifest, files = native.load_prepared(locations["prepared"])
        _same(
            manifest["source_batch"]["content_sha256"],
            batch["content_sha256"],
            "BLOCKED_02C_SOURCE",
        )
        for name, file in dc._ordinary_tree(locations["batch"]).items():
            _same(files["source/" + name], file.read_bytes(), "BLOCKED_02C_INTENT")
        built = hs.verify_built(locations["built"])
        _same(
            native.build_files(locations["prepared"], locations["responses"]),
            hs._read_tree(locations["built"]),
            "BLOCKED_02C_RECONSTRUCTION",
        )
        selected = built["ideas"][index]
        if (
            selected["idea_id"] != evidence["idea_id"]
            or selected["status"] != hs.DRAFTED
            or len(selected["drafts"]) != 1
        ):
            raise OriginalBlocked("BLOCKED_02C_DSL_REQUIRED")
        receipt = json.loads(path(locations["built"], selected["receipt"]).read_bytes())
        reasoned = receipt["model_response"]["reasoned_draft"]
        # Only the native adapter's completed-bar/next-open interpretation is supported.
        # Do not infer arbitrary operator or trading-stop semantics from model prose.
        if (
            reasoned["entry_concept"]
            != "Enter at the next bar open after a completed-bar confirmation."
            or reasoned["exit_concept"] != "Exit at the declared opposite completed-bar condition."
        ):
            raise OriginalBlocked("BLOCKED_UNSUPPORTED_OPERATOR_SEMANTICS")
        family = receipt["native_formalization"]["family_id"]
        if family != contract.family_id or family.removesuffix(
            "_v1"
        ) != intent.strategy_family.removesuffix("_v1"):
            raise OriginalBlocked("BLOCKED_NATIVE_FAMILY")
        generated = json.loads(path(locations["built"], selected["drafts"][0]["file"]).read_bytes())
        bounds = {b.name: b for b in intent.proposed_parameter_bounds}
        parameters = generated["free_parameters"]["parameters"]
        if {p["name"] for p in parameters} != set(bounds) or any(
            not bounds[p["name"]].minimum <= v <= bounds[p["name"]].maximum
            for p in parameters
            for v in p["allowed_values"]
        ):
            raise OriginalBlocked("BLOCKED_NATIVE_PARAMETER_WIDENING")
        spec_relative = f"research/strategy_specs/{contract.strategy_spec_id}.strategy_spec.json"
        spec_raw = _committed(root, spec_relative, contract.repo_sha)
        spec = json.loads(spec_raw)
        _same(digest(spec_raw), contract.strategy_spec_hash, "BLOCKED_CANONICAL_SPEC_HASH")
        _same(semantic_hash(generated), semantic_hash(spec), "BLOCKED_SEMANTIC_SUBSTITUTION")
        golden = json.loads(
            _committed(
                root,
                "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json",
                contract.repo_sha,
            )
        )
        if contract.strategy_spec_id == "STRAT-SPEC-0003" or semantic_hash(spec) == semantic_hash(
            golden
        ):
            raise OriginalBlocked("BLOCKED_LEGACY_ORIGIN_ATTRIBUTION")
        hypothesis = di.canonical_sha256(authored)
        _same(
            [i for i in observed.get("ideas", []) if i["idea_id"] == evidence["idea_id"]],
            [{"idea_id": evidence["idea_id"], "original_hypothesis_sha256": hypothesis}],
            "BLOCKED_ORIGIN_IDEA",
        )
        parent = {
            "idea_id": evidence["idea_id"],
            "original_hypothesis_sha256": "sha256:" + hypothesis,
            "fingerprint_sha256": "sha256:" + fingerprint,
            "cycle_manifest_sha256": "sha256:" + observed["cycle_manifest_sha256"],
            "origin_status": observed["status"],
        }
        parent["original_parent_sha256"] = original_parent_sha256(parent)
        gate, gate_raw = gate_c._load_object(locations["gate_c_approval"], "native Gate C record")
        audit_raw = _committed(root, gate_c.AUDIT_PATH.as_posix(), contract.repo_sha)
        audits = [json.loads(line) for line in audit_raw.splitlines() if line.strip()]
        audit = [a for a in audits if a.get("canonical_target_path") == spec_relative]
        if len(audit) != 1:
            raise OriginalBlocked("BLOCKED_GATE_C_AUDIT")
        audit = audit[0]
        if (
            audit.get("schema_version") != "gate_c_strategy_spec_write_audit_v1"
            or audit.get("writer_version") != gate_c.WRITER_VERSION
            or audit.get("approved_by") != "Karl"
            or audit.get("validation_outcome") != "passed_before_write"
            or gate.get("schema_version") != "gate_c_strategy_spec_approval_v1"
            or gate.get("approval_scope") != "one_append_only_canonical_strategy_spec_write"
            or gate.get("approved_by") != "Karl"
            or gate.get("content_reviewed") is not True
            or gate.get("authorizes_execution") is not False
            or len([a for a in audits if a.get("approval_id") == gate.get("approval_id")]) != 1
        ):
            raise OriginalBlocked("BLOCKED_NATIVE_GATE_C_RECORD")
        _same(audit["approval_record_sha256"], digest(gate_raw), "BLOCKED_GATE_C_APPROVAL")
        _same(audit["approved_content_sha256"], contract.strategy_spec_hash, "BLOCKED_GATE_C_SPEC")
        _same(audit["source_hashes"], gate["source_hashes"], "BLOCKED_GATE_C_SOURCES")
        refs = {
            name: gate_c._verify_ref(root, gate[name], name)
            for name in ("source_draft", "review_trail", "eligibility_report")
        }
        for name, ref in refs.items():
            path(root, ref[0])
            _same(audit[name]["path"], ref[0], "BLOCKED_GATE_C_SOURCE_PATH")
            _same(audit[name]["sha256"], ref[1], "BLOCKED_GATE_C_SOURCE_HASH")
        draft = json.loads(refs["source_draft"][3])
        gate_c._validate_draft(
            draft, refs["source_draft"][0], gate["source_draft_id"], gate["source_hashes"]
        )
        reviews = gate_c._validate_reviews(refs["review_trail"][3], gate["source_draft_id"])
        gate_c._validate_eligibility(
            json.loads(refs["eligibility_report"][3]), gate["source_draft_id"], refs, reviews
        )
        gate_c._independent_checks(spec, spec_relative, refs, gate["approval_id"])
        recorded_status = draft["provenance"]["original_hermes_parent"]["origin_status"]
        if observed["status"] == origin.FIXTURE:
            _same(recorded_status, origin.FIXTURE, "BLOCKED_FIXTURE_ORIGIN_PROMOTION")
        elif recorded_status not in {origin.BLOCKED, origin.VERIFIED}:
            raise OriginalBlocked("BLOCKED_RECORDED_ORIGIN_STATUS")
        # Preserve the reviewed parent bytes; its quoted status never establishes B.
        # verify_native_report independently verifies the operator's receipt anchor.
        parent["origin_status"] = recorded_status
        parent["original_parent_sha256"] = original_parent_sha256(parent)
        _same(
            draft["provenance"]["original_hermes_parent"], parent, "BLOCKED_GATE_C_ORIGINAL_PARENT"
        )
        _same(
            draft["source_hashes"]["original_hermes_parent_sha256"],
            parent["original_parent_sha256"],
            "BLOCKED_GATE_C_ORIGINAL_PARENT",
        )
        return {
            "original_parent": parent,
            "semantic_sha256": semantic_hash(spec),
            "origin": observed,
            "fixture": observed["status"] == origin.FIXTURE
            or receipt["model_response"]["capture"]["capture_kind"] == hs.FIXTURE,
            "gate_c_audit_sha256": digest(audit_raw),
            "gate_c_approval_sha256": digest(gate_raw),
        }
    except OriginalBlocked:
        raise
    except (
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        AttributeError,
        OSError,
        subprocess.CalledProcessError,
    ) as exc:
        raise OriginalBlocked("BLOCKED_NATIVE_ORIGINAL_CHAIN:" + type(exc).__name__) from None


def route(root, spec_path, *, custody=None):
    """Intrinsic prepared source hash, never an optional sibling mapping or caller flag."""
    from tools.research_autonomy.historical_source_gate import HistoricalLease, HistoricalSourceGate
    from tools.research_autonomy.store import ResearchAuthorityStore

    spec = json.loads(Path(spec_path).read_bytes())
    refs = [
        r for r in spec.get("provenance", {}).get("source_refs", []) if r.startswith(ROUTE_PREFIX)
    ]
    if not refs:
        source_root = Path(__file__).resolve().parents[2]
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source_root, text=True).strip()
        golden = json.loads(_committed(source_root, "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json", sha))
        if semantic_hash(spec) != semantic_hash(golden):
            raise OriginalBlocked("BLOCKED_UNKNOWN_EXECUTION_ROUTE")
        return None
    if (
        len(refs) != 1
        or type(custody) is not HistoricalLease
        or custody._root != root.resolve()
        or type(custody._gate) is not HistoricalSourceGate
        or type(custody._gate.store) is not ResearchAuthorityStore
    ):
        raise OriginalBlocked("BLOCKED_NONHOLDOUT_CUSTODY")
    custody.require_preread([o.repo_path for o in custody.request.objects])
    relative, expected = refs[0][len(ROUTE_PREFIX) :].split("#")
    if not relative.startswith("scratch/") or not relative.endswith("/original_source.json"):
        raise OriginalBlocked("BLOCKED_ORIGINAL_ROUTE_SOURCE_PATH")
    raw = path(root, relative).read_bytes()
    _same(digest(raw), expected, "BLOCKED_ORIGINAL_ROUTE_HASH")
    source = json.loads(raw)
    contract = custody._gate.store.load_contract(custody.request.search_id)
    proof = verify(root, contract, source["evidence"])
    _same(source["contract_hash"], contract.contract_hash, "BLOCKED_ORIGINAL_ROUTE_CONTRACT")
    _same(source["parent"], proof["original_parent"], "BLOCKED_ORIGINAL_ROUTE_PARENT")
    _same(
        custody.request.original_parent_sha256,
        source["parent"]["original_parent_sha256"],
        "BLOCKED_ORIGINAL_ROUTE_CUSTODY",
    )
    _same(semantic_hash(spec), proof["semantic_sha256"], "BLOCKED_PREPARED_SEMANTIC_SUBSTITUTION")
    return {
        "schema_version": "cpw_original_runner_route_v1",
        "source_proof_sha256": expected,
        "contract_hash": contract.contract_hash,
        "original_parent_sha256": source["parent"]["original_parent_sha256"],
    }
