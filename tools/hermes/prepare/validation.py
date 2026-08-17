"""Lineage, compatibility, and evidence validation for H2.5 PREPARE."""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import TypeAdapter

from tools.hermes.proposals.models import (
    AffectedDomain,
    AuthorityClass,
    ProposalType,
    TypedProposal,
)

from .models import (
    CodexWorkPackagePreparedPayload,
    PreparedPayload,
    PreparedPayloadBase,
    PreparedPayloadType,
    StrategyLabPreparedPayload,
)
from .serialization import canonical_sha256

if TYPE_CHECKING:
    from tools.mcp.project_evidence.models import RepoIdentity
    from tools.mcp.project_evidence.query_reader import ScopedDuckDBReader
    from tools.mcp.project_evidence.resources import EvidenceResourceCatalog


PREPARED_PAYLOAD_ADAPTER = TypeAdapter(PreparedPayload)

COMPATIBILITY_MATRIX: dict[PreparedPayloadType, frozenset[ProposalType]] = {
    PreparedPayloadType.STRATEGY_LAB: frozenset(
        {ProposalType.STRATEGY, ProposalType.STRATEGY_ADJUSTMENT}
    ),
    PreparedPayloadType.SEARCH_GOVERNOR_CAMPAIGN: frozenset(
        {
            ProposalType.STRATEGY,
            ProposalType.STRATEGY_ADJUSTMENT,
            ProposalType.INVESTIGATION,
        }
    ),
    PreparedPayloadType.CODEX_WORK_PACKAGE: frozenset(
        {
            ProposalType.BUG_FIX,
            ProposalType.LAB_IMPROVEMENT,
            ProposalType.DEPENDENCY_UPGRADE,
            ProposalType.INVESTIGATION,
            ProposalType.STRATEGY,
            ProposalType.STRATEGY_ADJUSTMENT,
        }
    ),
    PreparedPayloadType.PREFECT_WORKFLOW: frozenset(
        {
            ProposalType.LAB_IMPROVEMENT,
            ProposalType.INVESTIGATION,
            ProposalType.DATA_ACQUISITION,
        }
    ),
    PreparedPayloadType.BOUNDED_DIAGNOSTIC: frozenset(
        {
            ProposalType.BUG_FIX,
            ProposalType.LAB_IMPROVEMENT,
            ProposalType.INVESTIGATION,
            ProposalType.DEPENDENCY_UPGRADE,
        }
    ),
    PreparedPayloadType.DATA_HYDRATION: frozenset({ProposalType.DATA_ACQUISITION}),
    PreparedPayloadType.DEPENDENCY_MAINTENANCE: frozenset({ProposalType.DEPENDENCY_UPGRADE}),
}

_NON_PROTECTED_RESEARCH_DOMAINS = frozenset(
    {
        AffectedDomain.STRATEGY_RESEARCH,
        AffectedDomain.STRATEGY_ADJUSTMENT_RESEARCH,
        AffectedDomain.LAB_PROCESS,
        AffectedDomain.BOUNDED_INVESTIGATION,
        AffectedDomain.DOCUMENTATION,
        AffectedDomain.TEST_ONLY_TOOLING,
    }
)


@dataclass(frozen=True)
class SourceProposalLineage:
    path: Path
    proposal: TypedProposal
    content_sha256: str


class PreparedPayloadValidator:
    """Validate a prepared plan without granting it any downstream authority."""

    def __init__(
        self,
        identity: RepoIdentity,
        resources: EvidenceResourceCatalog,
        queries: ScopedDuckDBReader,
        outbox_root: Path,
        *,
        max_source_bytes: int = 2_000_000,
    ) -> None:
        self.identity = identity
        self.resources = resources
        self.queries = queries
        self.outbox_root = Path(os.path.abspath(outbox_root))
        self.max_source_bytes = max_source_bytes

    def validate(self, payload: PreparedPayloadBase | Mapping[str, Any]) -> PreparedPayloadBase:
        from tools.mcp.project_evidence.models import ResourceDeniedError

        prepared = PREPARED_PAYLOAD_ADAPTER.validate_python(payload)
        if prepared.repo_sha != self.identity.repo_sha:
            raise ResourceDeniedError("prepared repo SHA does not match Project-Evidence")

        source = self.load_source_proposal(prepared.source_proposal_id)
        self._validate_lineage(prepared, source)
        self._validate_compatibility(prepared, source.proposal)
        self._validate_evidence(prepared)
        return prepared

    def load_source_proposal(self, proposal_id: str) -> SourceProposalLineage:
        from tools.mcp.project_evidence.models import (
            EvidenceUnavailableError,
            ResourceDeniedError,
        )

        for candidate in (self.outbox_root, *self.outbox_root.parents):
            if candidate.exists() and candidate.is_symlink():
                raise ResourceDeniedError("proposal outbox path must not traverse a symlink")
        if not self.outbox_root.is_dir() or self.outbox_root.is_symlink():
            raise EvidenceUnavailableError("fixed proposal outbox root is unavailable")

        source_path = self.outbox_root / f"{proposal_id}.proposal.json"
        if source_path.is_symlink():
            raise ResourceDeniedError("source proposal must be a regular non-symlink file")
        try:
            source_stat = source_path.stat(follow_symlinks=False)
        except FileNotFoundError as exc:
            raise EvidenceUnavailableError(
                "source proposal ID is absent from the fixed outbox"
            ) from exc
        if not stat.S_ISREG(source_stat.st_mode):
            raise ResourceDeniedError("source proposal must be a regular file")
        if source_stat.st_size > self.max_source_bytes:
            raise EvidenceUnavailableError("source proposal exceeds the fixed byte limit")
        try:
            source_path.resolve().relative_to(self.outbox_root.resolve())
        except ValueError as exc:
            raise ResourceDeniedError("source proposal escaped the fixed outbox root") from exc

        try:
            record = json.loads(source_path.read_bytes().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EvidenceUnavailableError("source proposal is not valid UTF-8 JSON") from exc
        if not isinstance(record, dict):
            raise EvidenceUnavailableError("source H2 outbox record must be an object")
        if record.get("schema_version") != "hermes_proposal_outbox_v2":
            raise EvidenceUnavailableError("source proposal is not an H2 outbox v2 record")
        if record.get("proposal_id") != proposal_id:
            raise ResourceDeniedError("source proposal ID does not match its fixed filename")
        try:
            proposal = TypedProposal.model_validate(record.get("proposal"))
        except Exception as exc:
            raise EvidenceUnavailableError("nested source H2 typed proposal is invalid") from exc

        expected_nested = proposal.model_dump(mode="json")
        if record.get("proposal") != expected_nested:
            raise ResourceDeniedError("source proposal object is not the validated H2 object")
        source = record.get("source")
        if not isinstance(source, dict):
            raise EvidenceUnavailableError("source H2 record has no valid source envelope")
        if (
            record.get("proposal_type") != proposal.proposal_type.value
            or record.get("title") != proposal.title
            or source.get("session_id") != proposal.source_session_id
            or source.get("repo_sha") != proposal.repo_sha
            or source.get("evidence_refs") != list(proposal.evidence_refs)
            or record.get("not_authority") is not True
            or record.get("review_required") is not True
            or record.get("automatic_consumers") != []
        ):
            raise ResourceDeniedError("source H2 outer record conflicts with its typed proposal")
        return SourceProposalLineage(
            path=source_path,
            proposal=proposal,
            content_sha256=canonical_sha256(proposal),
        )

    def _validate_lineage(
        self, prepared: PreparedPayloadBase, source: SourceProposalLineage
    ) -> None:
        from tools.mcp.project_evidence.models import ResourceDeniedError

        proposal = source.proposal
        mismatches = {
            "source_session_id": prepared.source_session_id != proposal.source_session_id,
            "source_proposal_type": prepared.source_proposal_type is not proposal.proposal_type,
            "source_proposal_content_sha256": (
                prepared.source_proposal_content_sha256 != source.content_sha256
            ),
            "source_proposal_repo_sha": prepared.source_proposal_repo_sha != proposal.repo_sha,
            "source_authority_class": (
                prepared.source_authority_class is not proposal.authority_class
            ),
            "authority_class": prepared.authority_class is not proposal.authority_class,
            "evidence_refs": tuple(prepared.evidence_refs) != tuple(proposal.evidence_refs),
        }
        failed = [field for field, mismatch in mismatches.items() if mismatch]
        if failed:
            raise ResourceDeniedError(
                "prepared source lineage mismatch: " + ", ".join(sorted(failed))
            )

    def _validate_compatibility(self, prepared: PreparedPayloadBase, source: TypedProposal) -> None:
        from tools.mcp.project_evidence.models import ResourceDeniedError

        allowed = COMPATIBILITY_MATRIX[prepared.prepared_payload_type]
        if source.proposal_type not in allowed:
            raise ResourceDeniedError("source proposal type is incompatible with prepared type")

        domains = frozenset(source.affected_domains)
        if prepared.prepared_payload_type is PreparedPayloadType.SEARCH_GOVERNOR_CAMPAIGN and (
            source.authority_class is AuthorityClass.A0
            or not domains.issubset(_NON_PROTECTED_RESEARCH_DOMAINS)
        ):
            raise ResourceDeniedError(
                "Search Governor preparation requires bounded non-protected research scope"
            )

        if (
            prepared.prepared_payload_type is PreparedPayloadType.CODEX_WORK_PACKAGE
            and source.proposal_type in {ProposalType.STRATEGY, ProposalType.STRATEGY_ADJUSTMENT}
        ):
            if not isinstance(prepared, CodexWorkPackagePreparedPayload):
                raise ResourceDeniedError("Codex work-package body is invalid")
            if (
                source.authority_class is AuthorityClass.A0
                or not domains.issubset(_NON_PROTECTED_RESEARCH_DOMAINS)
                or prepared.body.explicitly_non_protected_research_tooling is not True
            ):
                raise ResourceDeniedError(
                    "strategy-to-Codex preparation requires explicit non-protected research tooling"
                )

        if isinstance(prepared, StrategyLabPreparedPayload):
            missing = set(prepared.body.data_or_evidence_inputs) - set(prepared.evidence_refs)
            if missing:
                raise ResourceDeniedError(
                    "Strategy Lab data/evidence inputs must use prepared evidence refs"
                )

    def _validate_evidence(self, prepared: PreparedPayloadBase) -> None:
        from tools.mcp.project_evidence.models import ResourceDeniedError

        research_memory_ref = "project://research-memory-index"
        if any(research_memory_ref in fact.evidence_refs for fact in prepared.facts):
            raise ResourceDeniedError(
                "Research Memory is an index/hint and cannot directly anchor a prepared FACT"
            )
        for anchor in prepared.evidence_anchors:
            expected = self._resolve_anchor(anchor.ref, anchor.query_limit)
            declared = tuple(
                (identity.path, identity.sha256) for identity in anchor.evidence_identities
            )
            if declared != expected:
                raise ResourceDeniedError(
                    f"prepared evidence identity does not match resolved evidence: {anchor.ref}"
                )

    def _resolve_anchor(self, ref: str, query_limit: int | None) -> tuple[tuple[str, str], ...]:
        from tools.mcp.project_evidence.models import ResourceDeniedError

        if ref.startswith(("project://", "evidence://")):
            if query_limit is not None:
                raise ResourceDeniedError("resource evidence must not declare a query limit")
            result = self.resources.read(ref)
            if result["evidence"]["repo_sha"] != self.identity.repo_sha:
                raise ResourceDeniedError("resolved resource is not bound to the prepared repo SHA")
            return ((result["evidence"]["path"], result["evidence"]["artifact_sha256"]),)
        if ref.startswith("query://"):
            if query_limit is None:
                raise ResourceDeniedError("prepared query evidence is not allowlisted")
            result = self.queries.run(ref.removeprefix("query://"), limit=query_limit)
            if result["repo_sha"] != self.identity.repo_sha:
                raise ResourceDeniedError("resolved query is not bound to the prepared repo SHA")
            return tuple((item["path"], item["sha256"]) for item in result["evidence_inputs"])
        raise ResourceDeniedError(
            "prepared FACT evidence requires project://, evidence://, or query://"
        )
