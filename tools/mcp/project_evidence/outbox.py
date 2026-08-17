"""The single proposal-only project write surface available to Hermes."""

from __future__ import annotations

import json
import os
import re
import uuid
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import NON_AUTHORITY, RepoIdentity, ResourceDeniedError

_TYPE_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_SESSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


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
        title: str,
        proposal_type: str,
        body: str,
        source_session_id: str,
        evidence_refs: Sequence[str],
    ) -> dict[str, Any]:
        if not isinstance(title, str) or not title.strip() or len(title) > 200:
            raise ResourceDeniedError("proposal title must be 1..200 characters")
        if not isinstance(body, str) or not body.strip() or len(body) > 50_000:
            raise ResourceDeniedError("proposal body must be 1..50000 characters")
        if _TYPE_RE.fullmatch(proposal_type) is None:
            raise ResourceDeniedError("proposal type is invalid")
        if _SESSION_RE.fullmatch(source_session_id) is None:
            raise ResourceDeniedError("proposal source session identity is invalid")
        refs = list(evidence_refs)
        if (
            not refs
            or len(refs) > 50
            or any(
                not isinstance(ref, str)
                or len(ref) > 300
                or not ref.startswith(("project://", "evidence://", "query://", "memory://"))
                for ref in refs
            )
        ):
            raise ResourceDeniedError("proposal evidence references are missing or invalid")

        self._prepare_root()
        timestamp = self._clock().astimezone(UTC)
        token = self._id_factory()
        if re.fullmatch(r"[0-9a-f]{16}", token) is None:
            raise ResourceDeniedError("proposal ID factory returned an invalid token")
        proposal_id = f"HERMES-PROP-{timestamp:%Y%m%dT%H%M%SZ}-{token}"
        payload = {
            "schema_version": "hermes_proposal_outbox_v1",
            "proposal_id": proposal_id,
            "created_at_utc": timestamp.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "source": {
                "system": "hermes",
                "session_id": source_session_id,
                "repo_sha": self.identity.repo_sha,
                "branch": self.identity.branch,
                "evidence_refs": refs,
            },
            "proposal_type": proposal_type,
            "title": title.strip(),
            "body": body.strip(),
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
            "not_authority": True,
            "review_required": True,
            "automatic_consumers": [],
        }
