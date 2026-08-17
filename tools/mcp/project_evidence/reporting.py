"""Deterministic acceptance renderers for daily and weekly evidence briefs."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class BriefFact:
    statement: str
    evidence_ref: str
    evidence_path: str
    artifact_sha256: str


def _fact_lines(facts: Sequence[BriefFact]) -> list[str]:
    if not facts:
        return ["- UNKNOWN — no resolvable evidence facts were supplied."]
    return [
        f"- FACT — {fact.statement} [{fact.evidence_ref}; {fact.evidence_path}; "
        f"sha256:{fact.artifact_sha256}]"
        for fact in facts
    ]


def render_daily_brief(
    *, repo_sha: str, report_date: str, facts: Sequence[BriefFact], blockers: Sequence[str]
) -> str:
    lines = [
        "# Daily Research / Project Brief",
        "",
        f"- Report date: {report_date}",
        f"- Repo SHA: `{repo_sha}`",
        "- Authority: non-authoritative observation only",
        "",
        "## Evidence-backed facts",
        "",
        *_fact_lines(facts),
        "",
        "## Known blockers / failures",
        "",
        *([f"- {item}" for item in blockers] or ["- UNKNOWN — no blocker evidence supplied."]),
        "",
        "## Inference",
        "",
        "- None. This deterministic sample does not infer scientific claims from missing evidence.",
        "",
        "## Open questions",
        "",
        "- Physical deployment and external-service health remain UNKNOWN unless separately observed.",
        "- No promotion, readiness, execution, or project-authority conclusion is produced.",
        "",
    ]
    return "\n".join(lines)


def render_weekly_review(
    *, repo_sha: str, week_ending: str, facts: Sequence[BriefFact], blockers: Sequence[str]
) -> str:
    lines = [
        "# Weekly Science / Project Review",
        "",
        f"- Week ending: {week_ending}",
        f"- Repo SHA: `{repo_sha}`",
        "- Authority: non-authoritative review only",
        "",
        "## FACT",
        "",
        *_fact_lines(facts),
        "",
        "## INFERENCE",
        "",
        "- None. Evidence coverage is reported without extrapolating scientific performance.",
        "",
        "## BLOCKERS / FAILURES",
        "",
        *([f"- {item}" for item in blockers] or ["- UNKNOWN — no blocker evidence supplied."]),
        "",
        "## OPEN QUESTION",
        "",
        "- Are all mutable-index claims still resolvable to exact repo evidence at this SHA?",
        "- No promotion, readiness, execution, or project-authority conclusion is produced.",
        "",
    ]
    return "\n".join(lines)
