"""Shared immutable contracts for the Project-Evidence MCP."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

REPO_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
NON_AUTHORITY = {
    "not_repo_truth": True,
    "not_scientific_truth": True,
    "not_canonical_evidence": True,
    "not_candidate_or_promotion_authority": True,
    "not_dispatch_or_execution_authority": True,
    "not_runtime_or_risk_authority": True,
}


class ProjectEvidenceError(RuntimeError):
    """Base error for fail-closed Project-Evidence operations."""


class ResourceDeniedError(ProjectEvidenceError, PermissionError):
    """Raised when a resource is outside the explicit allowlist."""


class EvidenceUnavailableError(ProjectEvidenceError):
    """Raised when required evidence cannot be resolved exactly."""


@dataclass(frozen=True)
class RepoIdentity:
    repo_sha: str
    branch: str

    @classmethod
    def resolve(
        cls,
        repo_root: Path,
        *,
        repo_sha: str | None = None,
        branch: str | None = None,
    ) -> RepoIdentity:
        root = repo_root.resolve()
        resolved_sha = repo_sha
        if resolved_sha is None:
            resolved_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            ).stdout.strip()
        if not REPO_SHA_RE.fullmatch(resolved_sha):
            raise EvidenceUnavailableError("repo SHA must be exactly 40 lowercase hex characters")

        resolved_branch = branch
        if resolved_branch is None:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            resolved_branch = result.stdout.strip() or "DETACHED"
        if not resolved_branch or any(ch in resolved_branch for ch in "\r\n\x00"):
            raise EvidenceUnavailableError("repo branch identity is invalid")
        return cls(repo_sha=resolved_sha, branch=resolved_branch)
