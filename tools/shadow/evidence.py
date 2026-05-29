"""Non-canonical local shadow evidence and disclosure records.

This module combines shadow adapter and parity observations for local
decision support only. It creates no files, canonical artifacts, schemas,
registry/query exposure, readiness authority, transition authority, approval
authority, ranking/scoring/recommendation authority, or human-gate execution.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Literal, Mapping, Sequence

from tools.shadow.adapter import ShadowSignalObservation
from tools.shadow.parity import ShadowParityObservation

DisclosureType = Literal[
    "interruption",
    "invalid_observation",
    "missing_data",
    "observation_reset",
]

NO_READINESS_TRANSITION_APPROVAL_STATEMENT = (
    "Local shadow evidence is decision-support only and has no readiness, "
    "transition, approval, promotion, recommendation, scoring, ranking, or "
    "human-gate execution authority."
)
DISCLOSURE_COMPLETENESS_STATEMENT = (
    "Disclosure completeness is descriptive local context only; it is not "
    "readiness, transition, approval, ranking, scoring, or recommendation "
    "authority."
)


def _freeze_mapping(metadata: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(deepcopy(dict(metadata or {})))


@dataclass(frozen=True)
class ShadowDisclosure:
    """Local descriptive disclosure for human review context only."""

    disclosure_type: DisclosureType
    description: str
    observed_at_utc: str | None = None
    reference_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    def to_local_dict(self) -> dict[str, Any]:
        """Return a local non-canonical dictionary representation."""

        return {
            "disclosure_type": self.disclosure_type,
            "description": self.description,
            "observed_at_utc": self.observed_at_utc,
            "reference_id": self.reference_id,
            "metadata": deepcopy(dict(self.metadata)),
        }


@dataclass(frozen=True)
class ShadowEvidenceRecord:
    """Local non-canonical evidence combining shadow observations."""

    signal_observation: ShadowSignalObservation
    parity_observation: ShadowParityObservation
    lineage_references: tuple[str, ...] = ()
    disclosures: tuple[ShadowDisclosure, ...] = ()
    evidence_id: str | None = None
    candidate_id: str | None = None
    generated_at_utc: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    no_readiness_transition_approval_statement: str = (
        NO_READINESS_TRANSITION_APPROVAL_STATEMENT
    )
    disclosure_completeness_statement: str = DISCLOSURE_COMPLETENESS_STATEMENT
    decision_support_only: bool = True
    canonical: bool = False
    readiness_authority: bool = False
    transition_authority: bool = False
    approval_authority: bool = False
    human_gate_execution: bool = False
    ranking_authority: bool = False
    scoring_authority: bool = False
    recommendation_authority: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "lineage_references", tuple(self.lineage_references))
        object.__setattr__(self, "disclosures", tuple(self.disclosures))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @property
    def disclosure_complete(self) -> bool:
        """Descriptive-only coverage flag for all required disclosure types."""

        counts = disclosure_counts(self)
        return all(count > 0 for count in counts.values())

    def to_local_dict(self) -> dict[str, Any]:
        """Return a local non-canonical dictionary representation."""

        return {
            "evidence_id": self.evidence_id,
            "candidate_id": self.candidate_id,
            "generated_at_utc": self.generated_at_utc,
            "lineage_references": list(self.lineage_references),
            "disclosures": [item.to_local_dict() for item in self.disclosures],
            "disclosure_counts": disclosure_counts(self),
            "disclosure_complete": self.disclosure_complete,
            "disclosure_completeness_statement": self.disclosure_completeness_statement,
            "metadata": deepcopy(dict(self.metadata)),
            "no_readiness_transition_approval_statement": (
                self.no_readiness_transition_approval_statement
            ),
            "decision_support_only": self.decision_support_only,
            "canonical": self.canonical,
            "readiness_authority": self.readiness_authority,
            "transition_authority": self.transition_authority,
            "approval_authority": self.approval_authority,
            "human_gate_execution": self.human_gate_execution,
            "ranking_authority": self.ranking_authority,
            "scoring_authority": self.scoring_authority,
            "recommendation_authority": self.recommendation_authority,
            "signal_observation_id": self.signal_observation.observation_id,
            "parity_observation_id": self.parity_observation.observation_id,
        }


DisclosureInput = str | ShadowDisclosure


def _build_disclosures(
    disclosure_type: DisclosureType,
    entries: Sequence[DisclosureInput] | None,
) -> tuple[ShadowDisclosure, ...]:
    if entries is None:
        return ()

    disclosures: list[ShadowDisclosure] = []
    for entry in entries:
        if isinstance(entry, ShadowDisclosure):
            if entry.disclosure_type != disclosure_type:
                raise ValueError(
                    "disclosure list contains a disclosure with the wrong type"
                )
            disclosures.append(
                ShadowDisclosure(
                    disclosure_type=entry.disclosure_type,
                    description=entry.description,
                    observed_at_utc=entry.observed_at_utc,
                    reference_id=entry.reference_id,
                    metadata=entry.metadata,
                )
            )
            continue

        disclosures.append(
            ShadowDisclosure(
                disclosure_type=disclosure_type,
                description=str(entry),
            )
        )

    return tuple(disclosures)


def build_shadow_evidence(
    *,
    signal_observation: ShadowSignalObservation,
    parity_observation: ShadowParityObservation,
    lineage_references: Sequence[str] | None = None,
    interruptions: Sequence[DisclosureInput] | None = None,
    invalid_observations: Sequence[DisclosureInput] | None = None,
    missing_data: Sequence[DisclosureInput] | None = None,
    observation_resets: Sequence[DisclosureInput] | None = None,
    evidence_id: str | None = None,
    candidate_id: str | None = None,
    generated_at_utc: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> ShadowEvidenceRecord:
    """Build local decision-support evidence without writing output files."""

    disclosures = (
        _build_disclosures("interruption", interruptions)
        + _build_disclosures("invalid_observation", invalid_observations)
        + _build_disclosures("missing_data", missing_data)
        + _build_disclosures("observation_reset", observation_resets)
    )

    return ShadowEvidenceRecord(
        signal_observation=signal_observation,
        parity_observation=parity_observation,
        lineage_references=tuple(lineage_references or ()),
        disclosures=disclosures,
        evidence_id=evidence_id,
        candidate_id=candidate_id,
        generated_at_utc=generated_at_utc,
        metadata=metadata or {},
    )


def has_any_disclosure(record: ShadowEvidenceRecord) -> bool:
    return bool(record.disclosures)


def disclosure_counts(record: ShadowEvidenceRecord) -> dict[str, int]:
    counts = {
        "interruption": 0,
        "invalid_observation": 0,
        "missing_data": 0,
        "observation_reset": 0,
    }
    for disclosure in record.disclosures:
        counts[disclosure.disclosure_type] += 1
    return counts


__all__ = [
    "DISCLOSURE_COMPLETENESS_STATEMENT",
    "NO_READINESS_TRANSITION_APPROVAL_STATEMENT",
    "DisclosureType",
    "ShadowDisclosure",
    "ShadowEvidenceRecord",
    "build_shadow_evidence",
    "disclosure_counts",
    "has_any_disclosure",
]
