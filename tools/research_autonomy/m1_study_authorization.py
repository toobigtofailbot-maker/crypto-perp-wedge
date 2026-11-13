"""M1 owner signature verification and single-use accounting, with no runner activation."""

import json
from pathlib import Path
from typing import Annotated, Literal

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pydantic import Field

from .envelope import canonical_json, content_hash
from .handoff import replay_handoff, validate_handoff
from .historical_source_gate import M1HistoricalRequest, Refused
from .m1_source import M1_REAL_MAPPING, M1_REAL_VERSION
from .models import Count, Identity, Positive, RepoSha, ScientificProtocol, Sha, StrictModel
from .nonholdout_qualification import HexKey, NonHoldoutQualification, _code_sha, _now, _parse, _valid
from .store import ResearchAuthorityStore

_DOMAIN = b"CPW-M1-HISTORICAL-STUDY-EXECUTE-V1\x00"


class M1TrustedOwnerKey(StrictModel):
    """Trust input for the verifier's host, never part of the signed request."""
    schema_version: Literal["cpw_m1_study_owner_key_v1"]
    key_id: Identity
    public_key_hex: HexKey
    mode: Literal["TEST_ONLY", "OWNER_CONTROLLED"]
    valid_from_ms: Count
    valid_until_ms: Positive


class M1StudyAuthorization(StrictModel):
    schema_version: Literal["cpw_m1_study_execute_v1"]
    purpose: Literal["one_historical_scientific_wave"]
    mode: Literal["TEST_ONLY", "OWNER_CONTROLLED"]
    authorization_id: Identity
    key_id: Identity
    repository: Literal["toobigtofailbot-maker/crypto-perp-wedge"]
    repo_sha: RepoSha
    campaign_id: Identity
    search_id: Identity
    contract_sha256: Sha
    custody_request_sha256: Sha
    handoff_sha256: Sha
    prepared_mapping_sha256: Sha
    trial_count: Positive
    valid_from_ms: Count
    valid_until_ms: Positive
    signature_hex: Annotated[str, Field(pattern=r"^[0-9a-f]{128}$")]


def signing_bytes(authorization: M1StudyAuthorization) -> bytes:
    return _DOMAIN + canonical_json(
        authorization.model_dump(mode="json", exclude={"signature_hex"})
    ).encode("ascii")


def _verify_signature(authorization, trusted_key, now):
    if (authorization.key_id, authorization.mode) != (trusted_key.key_id, trusted_key.mode):
        raise Refused("M1_OWNER_KEY_SCOPE")
    _valid(trusted_key, now)
    _valid(authorization, now)
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(trusted_key.public_key_hex)).verify(
            bytes.fromhex(authorization.signature_hex), signing_bytes(authorization)
        )
    except InvalidSignature:
        raise Refused("M1_OWNER_SIGNATURE_INVALID") from None


def _verify_binding(authorization, request, handoff, prepared, contract, protocol):
    source = request.source
    source.require_partition(contract.split_protocol)
    source.require_protocol(protocol)
    if ((authorization.repository, authorization.repo_sha, authorization.campaign_id,
         authorization.search_id, authorization.contract_sha256, authorization.custody_request_sha256,
         authorization.handoff_sha256, authorization.prepared_mapping_sha256)
            != (request.repository, contract.repo_sha, contract.campaign_id, contract.search_id,
                contract.contract_hash, content_hash(request.model_dump(mode="json")),
                handoff.content_sha256, content_hash(prepared))
            or (request.repo_sha, request.campaign_id, request.search_id, request.contract_hash,
                request.strategy_spec_hash, request.envelope_sha256, request.contamination_domain_id,
                request.holdout_id, request.data_identity, request.protocol_sha256)
            != (contract.repo_sha, contract.campaign_id, contract.search_id, contract.contract_hash,
                contract.strategy_spec_hash, contract.envelope_content_sha256, contract.contamination_domain_id,
                contract.split_protocol.final_holdout_ref, contract.data_identity,
                content_hash(protocol.model_dump(mode="json")))):
        raise Refused("M1_STUDY_SCOPE_MISMATCH")

    accepted = [p for p in handoff.proposal_records if p.status == "ACCEPTED_FOR_SCIENTIFIC_EXECUTION"]
    expected = [{
        "campaign_id": p.campaign_id,
        "search_id": p.search_id,
        "contract_hash": p.contract_hash,
        "proposal_id": p.proposal_id,
        "scientific_trial_id": p.scientific_trial_id,
        "params_fingerprint": p.params_fingerprint,
        "variant_id": f"VAR-{p.proposal_sequence + 1:06d}",
        "parameter_values": p.params,
    } for p in sorted(accepted, key=lambda item: item.proposal_sequence)]
    if (contract.data_version != M1_REAL_VERSION
            or prepared.get("schema_version") != M1_REAL_MAPPING
            or (prepared.get("repo_sha"), prepared.get("contract_hash"), prepared.get("handoff_sha256"),
                prepared.get("source_spec_sha256"), prepared.get("m1_source"))
            != (contract.repo_sha, contract.contract_hash, handoff.content_sha256,
                contract.strategy_spec_hash, source.model_dump(mode="json"))
            or prepared.get("scientific_denominator") != authorization.trial_count
            or not 1 <= len(accepted) == authorization.trial_count <= contract.wave_size
            or handoff.resulting_denominator > contract.max_scientific_trials
            or prepared.get("mapping") != expected
            or len({p.scientific_trial_id for p in accepted if p.scientific_trial_id}) != len(accepted)):
        raise Refused("M1_STUDY_WAVE_MISMATCH")


def verify_and_consume_m1_study(
    *, store: ResearchAuthorityStore, repo_root: Path, trusted_key, authorization, request, handoff, prepared,
) -> str:
    """Consume an exact signed scope under the native lock. Returns an audit ID, not a lease.

    This entrypoint accepts fixture trust only. Real trust registration, historical
    reading and scientific execution are separate owner-controlled gates.
    """
    if type(store) is not ResearchAuthorityStore:
        raise Refused("M1_NATIVE_STORE_REQUIRED")
    auth = _parse(M1StudyAuthorization, authorization)
    key = _parse(M1TrustedOwnerKey, trusted_key)
    request = _parse(M1HistoricalRequest, request)
    handoff = validate_handoff(handoff)
    # Snapshot mutable metadata before either hashing or validating its contents.
    prepared = json.loads(canonical_json(prepared))
    if auth.repo_sha != _code_sha() or auth.repo_sha != handoff.repo_sha:
        raise Refused("M1_STALE_CODE")
    if auth.mode != "TEST_ONLY" or key.mode != "TEST_ONLY":
        raise Refused("M1_OWNER_TRUST_NOT_PROVISIONED")
    if not all(item.startswith("TEST-ONLY-") for item in (auth.key_id, auth.authorization_id)):
        raise Refused("M1_OWNER_KEY_SCOPE")
    waves = {proposal.wave_id for proposal in handoff.proposal_records}
    if len(waves) != 1:
        raise Refused("M1_STUDY_WAVE_MISMATCH")
    wave_id = next(iter(waves))

    # Recheck the exact lineage under the consumption lock after native replay.
    replay_handoff(handoff, store=store, repo_root=repo_root)
    protocol = _parse(ScientificProtocol, store.load_scientific_protocol(handoff.search_id))
    event_id = "m1-owner-study:" + auth.authorization_id
    payload = {
        "phase": "m1_owner_study_verification",
        "mode": auth.mode,
        "authorization_sha256": content_hash(auth.model_dump(mode="json")),
        "owner_key_sha256": content_hash(key.model_dump(mode="json")),
        "search_id": handoff.search_id,
        "wave_id": wave_id,
    }
    with store._transaction() as conn:
        _verify_signature(auth, key, _now(conn))
        for target in (key.key_id, auth.authorization_id):
            NonHoldoutQualification._unrevoked(conn, target)
        contract = store._load_contract(conn, handoff.search_id)
        store._search_active(conn, contract)
        snapshot = store._snapshot(conn, contract.campaign_id)
        if ((snapshot.lineage_version, snapshot.lineage_sha256)
                != (handoff.authority_lineage_version, handoff.authority_lineage_sha256)
                or snapshot.holdout.state != "unexposed" or snapshot.holdout.contaminated):
            raise Refused("M1_STALE_LINEAGE_OR_HOLDOUT")
        _verify_binding(auth, request, handoff, prepared, contract, protocol)
        if store._replay(conn, event_id, "nonholdout_read", payload) or conn.execute(
            """SELECT 1 FROM research_authority.authority_audit
               WHERE campaign_id=%s AND event_type='nonholdout_read'
               AND normalized_payload::jsonb->'input'->>'phase'='m1_owner_study_verification'
               AND normalized_payload::jsonb->'input'->>'search_id'=%s
               AND normalized_payload::jsonb->'input'->>'wave_id'=%s""",
            (contract.campaign_id, contract.search_id, wave_id),
        ).fetchone():
            raise Refused("M1_OWNER_STUDY_ALREADY_USED")
        store._audit(conn, event_id=event_id, event_type="nonholdout_read", payload=payload,
                     campaign=store._campaign(conn, contract.campaign_id))
    return event_id
