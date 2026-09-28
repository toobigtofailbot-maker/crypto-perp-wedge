"""Composition root for the Project-Evidence MCP capability boundary."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from tools.hermes.prepare.models import PreparedPayloadBase, PreparedPayloadType
from tools.hermes.prepare.validation import COMPATIBILITY_MATRIX, PreparedPayloadValidator
from tools.hermes.proposals.models import AuthorityClass, ProposalType, TypedProposal
from tools.hermes.proposals.validation import ProposalValidator

from .domain_tools import CPW_DOMAIN_TOOL_NAMES, CPW_DOMAIN_TOOLS_SCHEMA_VERSION, CpwDomainTools
from .memory_reader import ReadOnlyResearchMemoryReader
from .models import RepoIdentity
from .outbox import PreparedPayloadOutbox, ProposalOutbox
from .query_reader import QUERY_NAMES, ScopedDuckDBReader
from .resources import EvidenceResourceCatalog
from .watch import DependencySecurityWatch


class ProjectEvidenceService:
    """Maximum scoped visibility with one proposal-only write capability."""

    def __init__(
        self,
        repo_root: Path,
        *,
        repo_sha: str | None = None,
        branch: str | None = None,
        outbox_root: Path | None = None,
        research_memory_readonly_dsn: str | None = None,
        watch_manifest_path: Path | None = None,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.identity = RepoIdentity.resolve(self.repo_root, repo_sha=repo_sha, branch=branch)
        self.resources = EvidenceResourceCatalog(self.repo_root, self.identity)
        self.queries = ScopedDuckDBReader(self.repo_root, self.identity)
        self.memory = ReadOnlyResearchMemoryReader(research_memory_readonly_dsn, self.resources)
        fixed_outbox_root = outbox_root or self.repo_root / "scratch" / "hermes_proposal_outbox"
        self.outbox = ProposalOutbox(fixed_outbox_root, self.identity)
        self.prepared_outbox = PreparedPayloadOutbox(fixed_outbox_root, self.identity)
        self.watch = DependencySecurityWatch(
            watch_manifest_path or self.repo_root / "tools" / "hermes" / "upstream_watch.json",
            self.identity,
        )
        self.proposals = ProposalValidator(self.identity, self.resources, self.queries)
        self.prepared_payloads = PreparedPayloadValidator(
            self.identity,
            self.resources,
            self.queries,
            fixed_outbox_root,
        )
        self.domain_tools = CpwDomainTools(self.resources, self.identity)

    @classmethod
    def from_environment(cls) -> ProjectEvidenceService:
        repo_root = Path(os.environ.get("PROJECT_EVIDENCE_ROOT", Path.cwd()))
        return cls(
            repo_root,
            repo_sha=os.environ.get("PROJECT_REPO_SHA"),
            branch=os.environ.get("PROJECT_REPO_BRANCH"),
            outbox_root=Path(
                os.environ.get(
                    "HERMES_PROPOSAL_OUTBOX",
                    repo_root / "scratch" / "hermes_proposal_outbox",
                )
            ),
            research_memory_readonly_dsn=os.environ.get("RESEARCH_MEMORY_READONLY_DSN"),
            watch_manifest_path=Path(
                os.environ.get(
                    "HERMES_UPSTREAM_WATCH_MANIFEST",
                    repo_root / "tools" / "hermes" / "upstream_watch.json",
                )
            ),
        )

    def manifest(self) -> dict[str, Any]:
        return {
            "service": "project-evidence",
            "schema_version": "project_evidence_mcp_v3",
            "repo_sha": self.identity.repo_sha,
            "branch": self.identity.branch,
            "read_resource_count": len(self.resources.list_resources()),
            "query_names": sorted(QUERY_NAMES),
            "research_memory_configured": self.memory.configured,
            "write_surfaces": ["proposal_outbox"],
            "proposal_contract": {
                "schema_version": "hermes_typed_proposal_v1",
                "proposal_types": [proposal_type.value for proposal_type in ProposalType],
                "authority_classes": [authority_class.value for authority_class in AuthorityClass],
                "proposal_only": True,
                "execution_authority": False,
                "standing_authority": False,
                "automatic_consumers": [],
            },
            "prepared_payload_contract": {
                "schema_version": "hermes_prepared_payload_v1",
                "prepared_payload_types": [
                    prepared_type.value for prepared_type in PreparedPayloadType
                ],
                "compatibility_matrix": {
                    prepared_type.value: sorted(
                        proposal_type.value for proposal_type in COMPATIBILITY_MATRIX[prepared_type]
                    )
                    for prepared_type in PreparedPayloadType
                },
                "source_proposal_required": True,
                "human_review_required": True,
                "prepared_only": True,
                "execution_authority": False,
                "approval_token_eligible": False,
                "broker_eligible": False,
                "dispatch_eligible": False,
                "standing_authority": False,
                "automatic_consumers": [],
            },
            "cpw_domain_tools": {
                "schema_version": CPW_DOMAIN_TOOLS_SCHEMA_VERSION,
                "semantic_owner": "CPW",
                "tool_names": list(CPW_DOMAIN_TOOL_NAMES),
                "compute_only": True,
                "canonical_write": False,
                "execution_authority": False,
                "approval_authority": False,
                "promotion_authority": False,
                "runtime_authority": False,
                "standing_authority": False,
                "automatic_consumers": [],
            },
            "default_policy": "deny",
            "ambient_filesystem": False,
            "arbitrary_sql": False,
            "shell": False,
            "credentials_or_tokens_returned": False,
            "project_authority": False,
        }

    def submit_proposal(
        self,
        *,
        proposal: TypedProposal | Mapping[str, Any],
    ) -> dict[str, Any]:
        validated = self.proposals.validate(proposal)
        return self.outbox.submit(proposal=validated)

    def submit_prepared_payload(
        self,
        *,
        prepared_payload: PreparedPayloadBase | Mapping[str, Any],
    ) -> dict[str, Any]:
        validated = self.prepared_payloads.validate(prepared_payload)
        return self.prepared_outbox.submit(prepared_payload=validated)
