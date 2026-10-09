"""Non-authoritative active-wave persistence and exact Governor recovery."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from tools.research_search.governor import SearchGovernor
from tools.research_storage.workspace import resolve_workspace_path

from .contract_builder import contract_from_payload
from .envelope import canonical_json, content_hash
from .models import ProposalWaveHandoff


def validate_handoff(value):
    raw = value.model_dump(mode="json") if isinstance(value, ProposalWaveHandoff) else value
    handoff = ProposalWaveHandoff.model_validate_json(canonical_json(raw))
    if content_hash({k: v for k, v in raw.items() if k != "content_sha256"}) != handoff.content_sha256:
        raise ValueError("handoff content hash mismatch")
    contract = contract_from_payload(handoff.frozen_contract.model_dump(mode="json"))
    if (contract.contract_hash, contract.search_id, contract.campaign_id, contract.parent_search_id,
        contract.repo_sha, contract.envelope_id, contract.envelope_version, contract.envelope_content_sha256) != (
        handoff.contract_hash, handoff.search_id, handoff.campaign_id, handoff.parent_search_id,
        handoff.repo_sha, handoff.envelope_id, handoff.envelope_version, handoff.envelope_content_sha256):
        raise ValueError("handoff contract/envelope identity mismatch")
    return handoff


def make_handoff(*, store, contract, intent_sha256, pre_wave_snapshot, requested_wave_count, proposal_records, resulting_denominator, repo_root: Path):
    snapshot = store.load_snapshot(contract.campaign_id)
    payload = {
        "schema_version": "cpw_proposal_wave_handoff_v1", "repo_sha": contract.repo_sha,
        "intent_sha256": intent_sha256, "envelope_id": contract.envelope_id,
        "envelope_version": contract.envelope_version, "envelope_content_sha256": contract.envelope_content_sha256,
        "campaign_id": contract.campaign_id, "search_id": contract.search_id,
        "parent_search_id": contract.parent_search_id,
        "authority_lineage_version": snapshot.lineage_version,
        "authority_lineage_sha256": snapshot.lineage_sha256,
        "frozen_contract": contract.to_dict(), "contract_hash": contract.contract_hash,
        "pre_wave_snapshot": pre_wave_snapshot, "requested_wave_count": requested_wave_count,
        "proposal_records": [r.to_dict() for r in proposal_records],
        "resulting_denominator": resulting_denominator, "noncanonical": True,
        "runner_authority": False, "approval_authority": False,
        "authority": {k: False for k in ("candidate_promotion", "canonical_result_population", "protected_runtime", "risk_changes", "paper_live", "exchange_order", "capital")},
    }
    payload = json.loads(canonical_json(payload))
    payload["content_sha256"] = content_hash(payload)
    handoff = validate_handoff(payload)
    replay_handoff(handoff, store=store, repo_root=repo_root)
    return handoff


def _path(repo_root: Path, handoff, *, create_parent=False):
    return resolve_workspace_path(repo_root=repo_root, storage_class="active",
        namespace="research-autonomy", artifact_path=f"{handoff.search_id}/{handoff.content_sha256.split(':')[1]}.json",
        create_parent=create_parent)


def write_handoff(handoff, *, repo_root: Path) -> Path:
    handoff = validate_handoff(handoff)
    _verify_repo(repo_root, handoff.repo_sha)
    candidate = _path(repo_root, handoff)
    if not candidate.is_relative_to(repo_root.resolve() / ".cpw/active"):
        raise ValueError("active workspace redirected")
    ignored = subprocess.run(["git", "check-ignore", "-q", candidate.relative_to(repo_root.resolve()).as_posix()], cwd=repo_root, check=False)
    if ignored.returncode != 0:
        raise ValueError("active handoff must be gitignored")
    path = _path(repo_root, handoff, create_parent=True)
    encoded = (canonical_json(handoff.model_dump(mode="json")) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() != encoded:
            raise ValueError("existing handoff bytes conflict")
        return path
    fd, temp = tempfile.mkstemp(prefix="wave-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        # Link publishes without overwriting a racing handoff.
        try:
            os.link(temp, path)
        except FileExistsError:
            if path.read_bytes() != encoded:
                raise ValueError("concurrent handoff bytes conflict")
    finally:
        os.unlink(temp)
    return path


def load_handoff(path: Path, *, repo_root: Path):
    relative = path.absolute().relative_to(repo_root.resolve() / ".cpw/active/research-autonomy")
    safe = resolve_workspace_path(repo_root=repo_root, storage_class="active", namespace="research-autonomy", artifact_path=relative.as_posix())
    if not safe.is_relative_to(repo_root.resolve() / ".cpw/active") or path.resolve(strict=True) != safe:
        raise ValueError("unsafe active handoff path")
    handoff = validate_handoff(json.loads(path.read_text(encoding="utf-8")))
    _verify_repo(repo_root, handoff.repo_sha)
    if path.resolve(strict=True) != _path(repo_root, handoff):
        raise ValueError("handoff path outside exact active namespace")
    return handoff


def _verify_repo(repo_root, repo_sha):
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    if head != repo_sha:
        raise ValueError("handoff repository SHA mismatch")


def replay_handoff(handoff, *, store, repo_root: Path):
    handoff = validate_handoff(handoff)
    _verify_repo(repo_root, handoff.repo_sha)
    snapshot, contract = store.verify_recovery_binding(handoff, repo_root=repo_root)
    if (snapshot.lineage_version, snapshot.lineage_sha256, snapshot.envelope_id, snapshot.envelope_version, snapshot.envelope_content_sha256) != (
        handoff.authority_lineage_version, handoff.authority_lineage_sha256, handoff.envelope_id, handoff.envelope_version, handoff.envelope_content_sha256):
        raise ValueError("handoff durable lineage binding mismatch")
    if contract.contract_hash != handoff.contract_hash:
        raise ValueError("handoff durable contract binding mismatch")
    governor = SearchGovernor.restore(contract, handoff.pre_wave_snapshot.model_dump(mode="json"))
    before = governor.proposal_count
    governor.propose_wave(handoff.requested_wave_count)
    actual = json.loads(canonical_json([p.to_dict() for p in governor.proposal_records[before:]]))
    expected = [p.model_dump(mode="json") for p in handoff.proposal_records]
    if canonical_json(actual) != canonical_json(expected) or governor.scientific_denominator != handoff.resulting_denominator:
        raise ValueError("exact proposal-wave replay divergence")
    return governor
