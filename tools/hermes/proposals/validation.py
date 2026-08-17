"""Evidence-resolution validation for Hermes H2 proposals."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from .models import TypedProposal

if TYPE_CHECKING:
    from tools.mcp.project_evidence.models import RepoIdentity
    from tools.mcp.project_evidence.query_reader import ScopedDuckDBReader
    from tools.mcp.project_evidence.resources import EvidenceResourceCatalog


class ProposalValidator:
    """Resolve every declared evidence identity before outbox persistence."""

    def __init__(
        self,
        identity: RepoIdentity,
        resources: EvidenceResourceCatalog,
        queries: ScopedDuckDBReader,
    ) -> None:
        self.identity = identity
        self.resources = resources
        self.queries = queries

    def validate(self, payload: TypedProposal | Mapping[str, Any]) -> TypedProposal:
        from tools.mcp.project_evidence.models import ResourceDeniedError

        proposal = (
            payload if isinstance(payload, TypedProposal) else TypedProposal.model_validate(payload)
        )
        if proposal.repo_sha != self.identity.repo_sha:
            raise ResourceDeniedError("proposal repo SHA does not match Project-Evidence")

        for anchor in proposal.evidence_anchors:
            expected = self._resolve_anchor(anchor.ref, anchor.query_limit)
            declared = tuple(
                (identity.path, identity.sha256) for identity in anchor.evidence_identities
            )
            if declared != expected:
                raise ResourceDeniedError(
                    f"proposal evidence identity does not match resolved evidence: {anchor.ref}"
                )
        return proposal

    def _resolve_anchor(self, ref: str, query_limit: int | None) -> tuple[tuple[str, str], ...]:
        from tools.mcp.project_evidence.models import ResourceDeniedError

        if ref.startswith(("project://", "evidence://")):
            if query_limit is not None:
                raise ResourceDeniedError("resource evidence must not declare a query limit")
            result = self.resources.read(ref)
            if result["evidence"]["repo_sha"] != self.identity.repo_sha:
                raise ResourceDeniedError("resolved resource is not bound to the service repo SHA")
            return ((result["evidence"]["path"], result["evidence"]["artifact_sha256"]),)

        if ref.startswith("query://"):
            query_name = ref.removeprefix("query://")
            if query_limit is None:
                raise ResourceDeniedError("proposal query evidence is not allowlisted")
            result = self.queries.run(query_name, limit=query_limit)
            if result["repo_sha"] != self.identity.repo_sha:
                raise ResourceDeniedError("resolved query is not bound to the service repo SHA")
            return tuple((item["path"], item["sha256"]) for item in result["evidence_inputs"])

        raise ResourceDeniedError(
            "typed proposals require exact Project-Evidence resource or query references"
        )
