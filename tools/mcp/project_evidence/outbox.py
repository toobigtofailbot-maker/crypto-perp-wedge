"""The single proposal-only project write surface available to Hermes."""

from __future__ import annotations

import json
import os
import re
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.hermes.prepare.models import PreparedPayloadBase
from tools.hermes.prepare.serialization import canonical_json_bytes, canonical_sha256
from tools.hermes.proposals.models import TypedProposal

from .models import NON_AUTHORITY, RepoIdentity, ResourceDeniedError


def _utc_now() -> datetime:
    return datetime.now(UTC)


class ProposalOutbox:
    """Create review-only proposal records under one fixed directory."""

    def __init__(
        self,
        root: Path,
        identity: RepoIdentity,
        *,
        clock: Callable[[], datetime] = _utc_now,
        id_factory: Callable[[], str] = lambda: uuid.uuid4().hex[:16],
    ) -> None:
        self.root = Path(os.path.abspath(root))
        self.identity = identity
        self._clock = clock
        self._id_factory = id_factory

    def _prepare_root(self) -> None:
        for candidate in (self.root, *self.root.parents):
            if candidate.exists() and candidate.is_symlink():
                raise ResourceDeniedError("proposal outbox path must not traverse a symlink")
        self.root.mkdir(parents=True, exist_ok=True)
        if not self.root.is_dir() or self.root.is_symlink():
            raise ResourceDeniedError("proposal outbox root is not a regular directory")

    def submit(
        self,
        *,
        proposal: TypedProposal,
    ) -> dict[str, Any]:
        if proposal.repo_sha != self.identity.repo_sha:
            raise ResourceDeniedError("proposal repo SHA does not match the outbox identity")

        self._prepare_root()
        timestamp = self._clock().astimezone(UTC)
        token = self._id_factory()
        if re.fullmatch(r"[0-9a-f]{16}", token) is None:
            raise ResourceDeniedError("proposal ID factory returned an invalid token")
        proposal_id = f"HERMES-PROP-{timestamp:%Y%m%dT%H%M%SZ}-{token}"
        payload = {
            "schema_version": "hermes_proposal_outbox_v2",
            "proposal_id": proposal_id,
            "created_at_utc": timestamp.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "source": {
                "system": "hermes",
                "session_id": proposal.source_session_id,
                "repo_sha": self.identity.repo_sha,
                "branch": self.identity.branch,
                "evidence_refs": list(proposal.evidence_refs),
            },
            "proposal_type": proposal.proposal_type.value,
            "title": proposal.title,
            "proposal": proposal.model_dump(mode="json"),
            "not_authority": True,
            "authority": dict(NON_AUTHORITY),
            "automatic_consumers": [],
            "review_required": True,
        }
        encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        final_path = self.root / f"{proposal_id}.proposal.json"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        descriptor = os.open(final_path, flags, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        return {
            "proposal_id": proposal_id,
            "outbox_file": final_path.name,
            "repo_sha": self.identity.repo_sha,
            "proposal_type": proposal.proposal_type.value,
            "authority_class": proposal.authority_class.value,
            "not_authority": True,
            "review_required": True,
            "automatic_consumers": [],
        }


class PreparedPayloadOutbox:
    """Exclusive-create inert prepared records beside their H2 parents."""

    def __init__(
        self,
        root: Path,
        identity: RepoIdentity,
        *,
        clock: Callable[[], datetime] = _utc_now,
        id_factory: Callable[[], str] = lambda: uuid.uuid4().hex[:16],
    ) -> None:
        self.root = Path(os.path.abspath(root))
        self.identity = identity
        self._clock = clock
        self._id_factory = id_factory

    def _prepare_root(self) -> None:
        for candidate in (self.root, *self.root.parents):
            if candidate.exists() and candidate.is_symlink():
                raise ResourceDeniedError("prepared outbox path must not traverse a symlink")
        if not self.root.is_dir() or self.root.is_symlink():
            raise ResourceDeniedError(
                "prepared outbox requires the existing regular proposal-outbox root"
            )

    def submit(self, *, prepared_payload: PreparedPayloadBase) -> dict[str, Any]:
        if prepared_payload.repo_sha != self.identity.repo_sha:
            raise ResourceDeniedError("prepared repo SHA does not match the outbox identity")

        self._prepare_root()
        timestamp = self._clock().astimezone(UTC)
        token = self._id_factory()
        if re.fullmatch(r"[0-9a-f]{16}", token) is None:
            raise ResourceDeniedError("prepared ID factory returned an invalid token")
        prepared_id = f"HERMES-PREP-{timestamp:%Y%m%dT%H%M%SZ}-{token}"
        payload_sha256 = canonical_sha256(prepared_payload)
        record = {
            "schema_version": "hermes_prepared_outbox_v1",
            "prepared_record_id": prepared_id,
            "created_at_utc": timestamp.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "source": {
                "system": "hermes",
                "session_id": prepared_payload.source_session_id,
                "repo_sha": self.identity.repo_sha,
                "branch": self.identity.branch,
                "source_proposal_id": prepared_payload.source_proposal_id,
                "source_proposal_content_sha256": (prepared_payload.source_proposal_content_sha256),
                "evidence_refs": list(prepared_payload.evidence_refs),
            },
            "prepared_payload_type": prepared_payload.prepared_payload_type.value,
            "prepared_payload": prepared_payload.model_dump(mode="json"),
            "prepared_payload_sha256": payload_sha256,
            "hash_scope": "canonical bytes of prepared_payload only; outer metadata excluded",
            "canonicalization": {
                "algorithm": "hermes_canonical_json_v1",
                "encoding": "UTF-8",
                "key_order": "lexicographic",
                "newline": "LF",
                "trailing_newline_count": 1,
            },
            "human_review_required": True,
            "not_authority": True,
            "automatic_consumers": [],
            "self_approval": False,
            "direct_execution": False,
            "approval_token_eligible": False,
            "broker_eligible": False,
            "dispatch_eligible": False,
            "authority": dict(NON_AUTHORITY),
        }
        encoded = canonical_json_bytes(record)
        final_path = self.root / f"{prepared_id}.prepared.json"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        descriptor = os.open(final_path, flags, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        return {
            "prepared_record_id": prepared_id,
            "outbox_file": final_path.name,
            "repo_sha": self.identity.repo_sha,
            "source_proposal_id": prepared_payload.source_proposal_id,
            "source_proposal_content_sha256": (prepared_payload.source_proposal_content_sha256),
            "prepared_payload_type": prepared_payload.prepared_payload_type.value,
            "prepared_payload_sha256": payload_sha256,
            "authority_class": prepared_payload.authority_class.value,
            "human_review_required": True,
            "not_authority": True,
            "automatic_consumers": [],
            "approval_token_eligible": False,
            "broker_eligible": False,
            "dispatch_eligible": False,
        }
