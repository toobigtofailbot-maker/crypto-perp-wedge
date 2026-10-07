"""CPW-owned conversion of explicit policy and durable history, never activation."""

from __future__ import annotations

import hashlib
import json
import math
import stat
import subprocess
from pathlib import Path, PurePosixPath, PureWindowsPath

from tools.mcp.project_evidence.research_intent import BoundedResearchIntentV1, semantic_content_sha256
from tools.research_memory.fingerprint import fingerprint
from tools.research_search.contract import (
    AuthoritySemantics, ConditionalParameterRule, ForbiddenRegion, ObjectiveSpec,
    ParameterSpec, ProposerSpec, RelationalConstraint, SearchContract, SearchPolicies, SplitProtocol,
)

from .envelope import canonical_json, validate_envelope
from .models import BoundedSearchRequest, DurableLineageSnapshot, EvidenceBinding


def verify_evidence(repo_root: Path, binding: EvidenceBinding, *, repo_sha: str) -> bytes:
    if binding.repo_sha != repo_sha:
        raise ValueError("evidence repo SHA mismatch")
    raw = binding.repo_path
    path = PurePosixPath(raw)
    if path.is_absolute() or PureWindowsPath(raw).drive or "\\" in raw or any(p in {"", ".", ".."} for p in raw.split("/")):
        raise ValueError("unsafe evidence path")
    # Evidence is a repo artifact reference, never a data/holdout read path.
    if not raw.startswith(("research/strategy_specs/", "research/data_slices/", "research/data_provenance/", "research/data_feature_availability/", "docs/", "research/schemas/")):
        raise ValueError("evidence path outside metadata surface")
    root = repo_root.resolve(strict=True)
    cursor = root
    for part in path.parts:
        cursor /= part
        attrs = cursor.lstat()
        if stat.S_ISLNK(attrs.st_mode) or getattr(attrs, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise ValueError("evidence indirection denied")
    if not cursor.resolve(strict=True).is_relative_to(root) or not cursor.is_file():
        raise ValueError("unsafe evidence file")
    content = cursor.read_bytes()
    if hashlib.sha256(content).hexdigest() != binding.artifact_sha256:
        raise ValueError("evidence content hash mismatch")
    committed = subprocess.run(["git", "show", f"{repo_sha}:{raw}"], cwd=root, capture_output=True, check=False)
    if committed.returncode != 0 or committed.stdout != content:
        raise ValueError("evidence differs from exact committed repository identity")
    return content


def _subset(requested, approved):
    if (requested.name, requested.kind, requested.required) != (approved.name, approved.kind, approved.required):
        return False
    if requested.kind == "categorical":
        return {canonical_json(p) for p in requested.choices} <= {canonical_json(p) for p in approved.choices}
    if requested.low < approved.low or requested.high > approved.high:
        return False
    if approved.step is not None:
        if requested.step is None:
            return False
        offset = (requested.low - approved.low) / approved.step
        scale = requested.step / approved.step
        return math.isclose(offset, round(offset), abs_tol=1e-9) and math.isclose(scale, round(scale), abs_tol=1e-9)
    return True


def validate_inputs(intent, envelope, request, *, repo_root: Path):
    intent = BoundedResearchIntentV1.model_validate_json(intent.model_dump_json())
    request = BoundedSearchRequest.model_validate_json(request.model_dump_json())
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    envelope = validate_envelope(envelope, repo_sha=head)
    if intent.repo_sha != head or intent.content_sha256 != semantic_content_sha256(intent) or request.intent_sha256 != intent.content_sha256:
        raise ValueError("intent semantic/repository binding mismatch")
    if intent.fingerprint_sha256 != fingerprint(intent.model_dump()):
        raise ValueError("intent hypothesis fingerprint mismatch")
    for anchor in intent.evidence_anchors:
        verify_evidence(repo_root, EvidenceBinding.model_validate(anchor.model_dump()), repo_sha=head)
    surface = envelope.surface
    selections = (
        (request.instrument, surface.instruments), (request.venue, surface.venues),
        (request.market_type, surface.market_types), (intent.primary_timeframe, surface.timeframes),
        (intent.strategy_family, surface.strategy_families), (intent.mechanism, surface.mechanisms),
        (request.data_source_class, surface.data_source_classes),
        (request.strategy_spec_id, surface.strategy_spec_ids), (request.dsl_version, surface.dsl_versions),
    )
    if any(value not in allowed for value, allowed in selections) or not set(intent.required_data_features) <= set(surface.feature_families):
        raise ValueError("research request outside envelope surface")
    if (request.instrument, request.venue, request.market_type) != ("BTCUSDT", "Binance USDT-M", "perpetual"):
        raise ValueError("intent v1 instrument scope mismatch")
    domains = {p.name: p for p in envelope.search_policy.parameter_domains}
    if not request.parameter_space or len(request.parameter_space) != intent.free_parameter_count or any(p.name not in domains or not _subset(p, domains[p.name]) for p in request.parameter_space):
        raise ValueError("parameter domain outside envelope")
    if request.proposer not in envelope.search_policy.proposers or request.policies != envelope.search_policy.policies:
        raise ValueError("proposer/policy mismatch")
    policy = envelope.search_policy
    if (request.objective not in policy.objectives or
        request.conditional_rules != policy.conditional_rules or
        request.relational_constraints != policy.relational_constraints or
        request.forbidden_regions != policy.forbidden_regions or
        request.split_protocol not in policy.split_protocols or
        not any((d.data_identity, d.data_version, d.evidence) ==
                (request.data_identity, request.data_version, request.data_evidence)
                for d in policy.data_bindings)):
        raise ValueError("exact objective, constraints, split or data binding mismatch")
    if request.scientific_protocol != envelope.scientific_protocol:
        raise ValueError("scientific protocol mismatch")
    limits = envelope.budgets
    if (request.max_proposals > min(limits.job_proposals, limits.hypothesis_proposals) or
        request.max_scientific_trials > min(limits.job_trials, limits.hypothesis_trials) or
        request.wave_size > envelope.search_policy.wave_size_limit or
        request.concurrency > min(limits.concurrency, envelope.search_policy.concurrency_limit) or
        request.compute_seconds > limits.compute_seconds or request.runtime_seconds > limits.runtime_seconds or
        request.recovery_limit > limits.recoveries or request.policies.retry_limit > limits.retries):
        raise ValueError("local budget exceeds envelope")
    strategy = json.loads(verify_evidence(repo_root, request.strategy_spec_evidence, repo_sha=head))
    if strategy.get("strategy_spec_id") != request.strategy_spec_id:
        raise ValueError("strategy spec identity mismatch")
    verify_evidence(repo_root, request.data_evidence, repo_sha=head)
    return intent, envelope, request


def construct_contract(intent, envelope, request, snapshot: DurableLineageSnapshot) -> SearchContract:
    if (snapshot.envelope_id, snapshot.envelope_version, snapshot.envelope_content_sha256) != (envelope.envelope_id, envelope.envelope_version, envelope.content_sha256):
        raise ValueError("durable envelope binding mismatch")
    if snapshot.campaign_id != request.campaign_id or snapshot.holdout.holdout_id != request.split_protocol.final_holdout_ref:
        raise ValueError("durable campaign/holdout mismatch")
    if snapshot.contamination_domain_id != envelope.contamination_domain_id:
        raise ValueError("durable contamination domain outside envelope")
    # Conservatively deny continuation requiring this domain's holdout after any escape.
    if snapshot.holdout.contaminated or snapshot.holdout.state == "consumed":
        raise ValueError("contamination domain consumed; fresh holdout cannot be inferred")
    b = snapshot.budget
    if request.max_proposals > b.proposal_ceiling - b.proposals_used - b.reserved_proposals or request.max_scientific_trials > b.trial_ceiling - b.scientific_trials_used - b.reserved_trials or b.search_count >= b.search_ceiling:
        raise ValueError("durable remaining budget exhausted")
    contract = SearchContract(
        campaign_id=request.campaign_id, search_id=request.search_id,
        parent_search_id=request.parent_search_id, reason_for_change=request.reason_for_change,
        hypothesis_id=request.hypothesis_id, family_id=request.family_id,
        hypothesis_fingerprint=intent.fingerprint_sha256, data_identity=request.data_identity,
        data_version=request.data_version, repo_sha=envelope.repo_sha,
        strategy_spec_id=request.strategy_spec_id,
        strategy_spec_hash="sha256:" + request.strategy_spec_evidence.artifact_sha256,
        parameter_space=tuple(ParameterSpec(**p.model_dump()) for p in request.parameter_space),
        conditional_rules=tuple(ConditionalParameterRule(**p.model_dump()) for p in request.conditional_rules),
        relational_constraints=tuple(RelationalConstraint(**p.model_dump()) for p in request.relational_constraints),
        forbidden_regions=tuple(ForbiddenRegion(**p.model_dump()) for p in request.forbidden_regions),
        objective=ObjectiveSpec(**request.objective.model_dump()),
        scientific_constraints=request.scientific_protocol.scientific_constraints,
        max_proposals=request.max_proposals, max_scientific_trials=request.max_scientific_trials,
        wave_size=request.wave_size, concurrency=request.concurrency,
        split_protocol=SplitProtocol(**request.split_protocol.model_dump()),
        proposer=ProposerSpec(**request.proposer.model_dump()), seed=request.seed,
        policies=SearchPolicies(**request.policies.model_dump()),
        campaign_proposals_before_search=b.proposals_used,
        campaign_scientific_trials_before_search=b.scientific_trials_used,
        envelope_id=envelope.envelope_id, envelope_version=envelope.envelope_version,
        envelope_content_sha256=envelope.content_sha256,
        contamination_domain_id=snapshot.contamination_domain_id,
        authority_lineage_version=snapshot.lineage_version,
        authority_lineage_sha256=snapshot.lineage_sha256,
    )
    surface = {key: contract.to_dict()[key] for key in ("search_id", "parameter_space", "conditional_rules", "proposer", "seed")}
    surface["contract_hash"] = contract.contract_hash
    surface["objective_direction"] = contract.objective.direction
    if contract.split_protocol.final_holdout_ref in canonical_json(surface):
        raise ValueError("final-holdout identity must not enter the proposer surface")
    return contract


def contract_from_payload(payload: dict) -> SearchContract:
    """Rebuild retained exact dataclass payload; never derive new cumulative history."""
    value = dict(payload)
    for name, model in (("parameter_space", ParameterSpec), ("conditional_rules", ConditionalParameterRule), ("relational_constraints", RelationalConstraint), ("forbidden_regions", ForbiddenRegion)):
        entries = []
        for item in value[name]:
            item = dict(item)
            for key in ("choices", "when_values", "equal_values"):
                if key in item:
                    item[key] = tuple(tuple(p) if isinstance(p, list) else p for p in item[key])
            entries.append(model(**item))
        value[name] = tuple(entries)
    value["scientific_constraints"] = tuple(value["scientific_constraints"])
    value["proposer"] = dict(value["proposer"])
    value["proposer"]["config"] = tuple(tuple(p) for p in value["proposer"]["config"])
    for name, model in (("objective", ObjectiveSpec), ("split_protocol", SplitProtocol), ("proposer", ProposerSpec), ("policies", SearchPolicies), ("authority", AuthoritySemantics)):
        value[name] = model(**value[name])
    contract = SearchContract(**value)
    if contract.authority != AuthoritySemantics() or contract.split_protocol.final_holdout_access != "prohibited":
        raise ValueError("stored contract authority mismatch")
    return contract


class ContractBuilder:
    def __init__(self, store, repo_root: Path):
        self._store = store
        self._repo_root = repo_root

    def build(self, intent, envelope, request) -> SearchContract:
        return self._store.open_search(intent, envelope, request, repo_root=self._repo_root)
