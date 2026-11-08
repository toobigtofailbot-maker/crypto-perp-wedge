"""Owner-signed M1 proof against a disposable native authority store."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import time

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from test_m1_native_fixture import _open_cell, authority_db
from tools.research_autonomy import historical_source_gate as gate
from tools.research_autonomy import m1_study_authorization as verifier
from tools.research_autonomy.envelope import content_hash
from tools.research_autonomy.nonholdout_qualification import Revocation
from tools.research_autonomy.store import AuthorityConflict
from tools.research_factory import mapper
from tools.research_factory.manual_loop import manual_research_loop

AUTH_ID = "TEST-ONLY-M1-AUTHORIZATION"
KEY_ID = "TEST-ONLY-M1-KEY"


def _signed(key, auth):
    return auth.model_copy(update={"signature_hex": key.sign(verifier.signing_bytes(auth)).hex()})


@pytest.fixture
def study(authority_db, tmp_path, monkeypatch):
    repo, store, reader, contract, handoff, request, envelope, controller, _ = _open_cell(
        authority_db, tmp_path, monkeypatch, "ETHUSDT", "1h", historical=True,
    )
    monkeypatch.setattr(verifier, "_code_sha", lambda: contract.repo_sha)
    path = repo / "scratch/m1/historical/prepared"
    when = "2026-11-08T00:00:00Z"
    prepared = mapper.prepare_wave(
        store=store, handoff=handoff, contract=contract, repo_root=repo,
        output_root=path, created_at_utc=when, m1_source=request.source,
    )
    key = Ed25519PrivateKey.generate()
    now = int(time.time() * 1000)
    trusted = verifier.M1TrustedOwnerKey(
        schema_version="cpw_m1_study_owner_key_v1", mode="TEST_ONLY", key_id=KEY_ID,
        public_key_hex=key.public_key().public_bytes_raw().hex(),
        valid_from_ms=now - 60_000, valid_until_ms=now + 600_000,
    )
    auth = _signed(key, verifier.M1StudyAuthorization(
        schema_version="cpw_m1_study_execute_v1", purpose="one_historical_scientific_wave",
        mode="TEST_ONLY", authorization_id=AUTH_ID, key_id=KEY_ID,
        repository=request.repository, repo_sha=contract.repo_sha, campaign_id=contract.campaign_id,
        search_id=contract.search_id, contract_sha256=contract.contract_hash,
        custody_request_sha256=content_hash(request.model_dump(mode="json")),
        handoff_sha256=handoff.content_sha256, prepared_mapping_sha256=content_hash(prepared),
        trial_count=len(prepared["mapping"]), valid_from_ms=now - 60_000, valid_until_ms=now + 600_000,
        signature_hex="0" * 128,
    ))
    return {"store": store, "repo_root": repo, "trusted_key": trusted, "authorization": auth,
            "request": request, "handoff": handoff, "prepared": prepared}, key, reader, contract, envelope, controller


def test_signed_scope_rejects_domain_scope_budget_and_prepared_substitution(study):
    args, key, *_ = study
    auth = args["authorization"]
    wrong_domain = key.sign(b"CPW-NONHOLDOUT-HISTORICAL-D3-2\x00" + verifier.signing_bytes(auth)).hex()
    with pytest.raises(gate.Refused, match="SIGNATURE_INVALID"):
        verifier.verify_and_consume_m1_study(**(args | {
            "authorization": auth.model_copy(update={"signature_hex": wrong_domain}),
        }))
    with pytest.raises(gate.Refused, match="TRUST_NOT_PROVISIONED"):
        verifier.verify_and_consume_m1_study(**(args | {
            "authorization": auth.model_copy(update={"mode": "OWNER_CONTROLLED"}),
            "trusted_key": args["trusted_key"].model_copy(update={"mode": "OWNER_CONTROLLED"}),
        }))
    wrong_key = Ed25519PrivateKey.generate().public_key().public_bytes_raw().hex()
    with pytest.raises(gate.Refused, match="SIGNATURE_INVALID"):
        verifier.verify_and_consume_m1_study(**(args | {
            "trusted_key": args["trusted_key"].model_copy(update={"public_key_hex": wrong_key}),
        }))
    with pytest.raises(gate.Refused, match="WAVE_MISMATCH"):
        verifier.verify_and_consume_m1_study(**(args | {
            "authorization": _signed(key, auth.model_copy(update={"trial_count": 1})),
        }))
    changed = args["request"].model_copy(update={"owner_execution_marker_sha256": "sha256:" + "1" * 64})
    with pytest.raises(gate.Refused, match="SCOPE_MISMATCH"):
        verifier.verify_and_consume_m1_study(**(args | {"request": changed}))
    mapping = args["prepared"] | {"mapping": [
        row | {"parameter_values": {"center_lookback_bars": 50}} for row in args["prepared"]["mapping"]
    ]}
    signed_mapping = _signed(key, auth.model_copy(update={"prepared_mapping_sha256": content_hash(mapping)}))
    with pytest.raises(gate.Refused, match="WAVE_MISMATCH"):
        verifier.verify_and_consume_m1_study(**(args | {"prepared": mapping, "authorization": signed_mapping}))
    with pytest.raises(AuthorityConflict, match="INACTIVE_EVIDENCE"):
        verifier.verify_and_consume_m1_study(**(args | {
            "authorization": _signed(key, auth.model_copy(update={"valid_until_ms": 1})),
        }))


@pytest.mark.parametrize("target", [AUTH_ID, KEY_ID])
def test_revoked_signature_or_key_refuses(study, target):
    args, _, _, _, _, controller = study
    controller.control("revocation", Revocation(
        record_id="TEST-ONLY-REVOCATION", approved_by="Karl", approval_reference="TEST-ONLY",
        target_id=target, action="revoke", successor_id=None,
    ))
    with pytest.raises(AuthorityConflict, match="REVOKED"):
        verifier.verify_and_consume_m1_study(**args)


def test_signed_scope_consumed_once_concurrently_and_never_opens_runner(study, monkeypatch):
    args, _, reader, contract, envelope, _ = study
    barrier = Barrier(2)

    def attempt():
        barrier.wait(timeout=15)
        try:
            return verifier.verify_and_consume_m1_study(**args)
        except AuthorityConflict:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        receipts = list(pool.map(lambda _: attempt(), range(2)))
    assert receipts.count("m1-owner-study:" + AUTH_ID) == 1
    assert receipts.count(None) == 1
    with pytest.raises(AuthorityConflict):
        verifier.verify_and_consume_m1_study(**args)

    def forbidden(*args, **kwargs):
        pytest.fail("verification must not grant source or runner access")

    monkeypatch.setattr(gate, "_lease", forbidden)
    with pytest.raises(gate.Refused, match=gate.M1_REAL_BLOCK):
        reader.authorize(attestation=None, request=args["request"], envelope=envelope,
                         contract=contract, repo_sha=contract.repo_sha)
    report = manual_research_loop(
        store=args["store"], handoff=args["handoff"], repo_root=args["repo_root"],
        preparation_root=args["repo_root"] / "scratch/m1/historical/prepared",
        output_root=args["repo_root"] / "scratch/m1/historical/output",
        created_at_utc="2026-11-08T00:00:00Z", human_invocation=True,
    )
    assert report["runner_calls"] == 0
    assert report["withholding_reasons"] == [gate.M1_REAL_BLOCK]


def test_valid_signature_cannot_consume_after_holdout_state_changes(study):
    from tools.research_autonomy.handoff import validate_handoff

    args, key, _, contract, _, _ = study
    store, handoff = args["store"], args["handoff"]
    store.record_holdout_event(contract.search_id, event_id="TEST-ONLY-HOLDOUT-STATE", informative_escape=True)
    snapshot = store.load_snapshot(contract.campaign_id)
    payload = handoff.model_dump(mode="json", exclude={"content_sha256"})
    payload.update(authority_lineage_version=snapshot.lineage_version, authority_lineage_sha256=snapshot.lineage_sha256)
    fresh = validate_handoff(payload | {"content_sha256": content_hash(payload)})
    prepared = args["prepared"] | {"handoff_sha256": fresh.content_sha256}
    auth = _signed(key, args["authorization"].model_copy(update={
        "handoff_sha256": fresh.content_sha256, "prepared_mapping_sha256": content_hash(prepared),
    }))
    with pytest.raises(gate.Refused, match="STALE_LINEAGE_OR_HOLDOUT"):
        verifier.verify_and_consume_m1_study(**(args | {
            "handoff": fresh, "prepared": prepared, "authorization": auth,
        }))
