"""Composition root for the Project-Evidence MCP capability boundary."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .memory_reader import ReadOnlyResearchMemoryReader
from .models import RepoIdentity
from .outbox import ProposalOutbox
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
        self.outbox = ProposalOutbox(
            outbox_root or self.repo_root / "scratch" / "hermes_proposal_outbox",
            self.identity,
        )
        self.watch = DependencySecurityWatch(
            watch_manifest_path or self.repo_root / "tools" / "hermes" / "upstream_watch.json",
            self.identity,
        )

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
            "schema_version": "project_evidence_mcp_v1",
            "repo_sha": self.identity.repo_sha,
            "branch": self.identity.branch,
            "read_resource_count": len(self.resources.list_resources()),
            "query_names": sorted(QUERY_NAMES),
            "research_memory_configured": self.memory.configured,
            "write_surfaces": ["proposal_outbox"],
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
        title: str,
        proposal_type: str,
        body: str,
        source_session_id: str,
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        for ref in evidence_refs:
            if ref.startswith(("project://", "evidence://")):
                self.resources.spec_for_uri(ref)
            elif ref.startswith("query://"):
                if ref.removeprefix("query://") not in QUERY_NAMES:
                    from .models import ResourceDeniedError

                    raise ResourceDeniedError("proposal query evidence is not allowlisted")
            elif not ref.startswith("memory://"):
                from .models import ResourceDeniedError

                raise ResourceDeniedError("proposal evidence reference is not allowlisted")
        return self.outbox.submit(
            title=title,
            proposal_type=proposal_type,
            body=body,
            source_session_id=source_session_id,
            evidence_refs=evidence_refs,
        )
