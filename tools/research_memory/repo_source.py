"""Deterministic, read-only bootstrap input derived from committed repo truth."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.research_memory.fingerprint import HypothesisDefinition

NEGATIVE_CLASSIFICATIONS = frozenset(
    {"NO-GO", "BLOCKED", "INVALID", "INCOMPLETE", "SUPERSEDED", "REJECTED"}
)


@dataclass(frozen=True)
class EvidenceSeed:
    artifact_path: str
    artifact_id: str | None
    evidence_role: str
    artifact_content_sha256: str
    source_record_sha256: str | None
    supports_conclusion: bool


@dataclass(frozen=True)
class MemorySeed:
    definition: HypothesisDefinition
    source_key: str
    title: str
    status: str
    classification: str
    negative_reason: str | None
    source_created_at: str | None
    source_updated_at: str | None
    source_metadata: dict[str, Any]
    aliases: tuple[tuple[str, str], ...]
    evidence: tuple[EvidenceSeed, ...]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return _sha256_bytes(payload.encode("utf-8"))


def _safe_repo_file(repo_root: Path, relative_path: str, *, label: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"{label} must be a safe repo-relative path: {relative_path}")
    unresolved = repo_root / candidate
    cursor = repo_root
    for part in candidate.parts:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError(f"{label} must not traverse a symlink: {relative_path}")
    resolved = unresolved.resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} escapes repo root: {relative_path}") from exc
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} is not an ordinary repo file: {relative_path}")
    return resolved


def _evidence(
    repo_root: Path,
    relative_path: str,
    *,
    artifact_id: str | None,
    evidence_role: str,
    supports_conclusion: bool,
    source_record_sha256: str | None = None,
) -> EvidenceSeed:
    path = _safe_repo_file(repo_root, relative_path, label=evidence_role)
    return EvidenceSeed(
        artifact_path=Path(relative_path).as_posix(),
        artifact_id=artifact_id,
        evidence_role=evidence_role,
        artifact_content_sha256=_sha256_bytes(path.read_bytes()),
        source_record_sha256=source_record_sha256,
        supports_conclusion=supports_conclusion,
    )


def _experiment_artifacts(repo_root: Path) -> dict[str, list[tuple[str, dict[str, Any]]]]:
    experiments_dir = repo_root / "research" / "experiments"
    by_candidate: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    if not experiments_dir.exists():
        return by_candidate
    artifact_paths = sorted(
        {*experiments_dir.glob("EXP-*.plan.json"), *experiments_dir.glob("REP-*.report.json")}
    )
    for path in artifact_paths:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"experiment artifact must be an ordinary file: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        candidate_id = payload.get("candidate_id")
        if isinstance(candidate_id, str):
            relative = path.relative_to(repo_root).as_posix()
            by_candidate.setdefault(candidate_id, []).append((relative, payload))
    return by_candidate


def load_repo_memory_seeds(repo_root: Path) -> tuple[MemorySeed, ...]:
    """Build stable memory seeds without writing to repo artifacts or PostgreSQL."""

    repo_root = repo_root.resolve()
    registry_path = _safe_repo_file(
        repo_root, "research/candidate_registry.jsonl", label="candidate registry"
    )
    registry_bytes = registry_path.read_bytes()
    registry_sha256 = _sha256_bytes(registry_bytes)
    experiments = _experiment_artifacts(repo_root)
    seeds: list[MemorySeed] = []

    for line_number, line in enumerate(registry_bytes.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        candidate_id = row["candidate_id"]
        classification = row["overall_verdict"]
        mechanism = row.get("differentiation_summary") or row["name"]
        definition = HypothesisDefinition.from_mapping(
            {
                "strategy_family": row["strategy_family"],
                "mechanism": mechanism,
                "primary_timeframe": row["timeframe"],
                "required_data_features": row["information_inputs"],
                "free_parameter_count": row["free_parameter_count"],
            }
        )
        row_sha256 = _canonical_json_sha256(row)
        refs = [
            EvidenceSeed(
                artifact_path="research/candidate_registry.jsonl",
                artifact_id=candidate_id,
                evidence_role="candidate_registry_record",
                artifact_content_sha256=registry_sha256,
                source_record_sha256=row_sha256,
                supports_conclusion=False,
            )
        ]

        hypothesis_path = row.get("hypothesis_md_path")
        if hypothesis_path:
            refs.append(
                _evidence(
                    repo_root,
                    hypothesis_path,
                    artifact_id=candidate_id,
                    evidence_role="hypothesis",
                    supports_conclusion=False,
                )
            )

        decision_path = row.get("decision_record_path")
        if decision_path:
            refs.append(
                _evidence(
                    repo_root,
                    decision_path,
                    artifact_id=Path(decision_path).stem,
                    evidence_role="decision_record",
                    supports_conclusion=classification != "PENDING",
                )
            )

        experiment_ids: list[str] = []
        for relative_path, artifact in experiments.get(candidate_id, []):
            if "report_id" in artifact:
                artifact_id = artifact["report_id"]
                role = "experiment_report"
            else:
                artifact_id = artifact.get("plan_id")
                role = "experiment_plan"
            supports = role == "experiment_report" and classification != "PENDING"
            refs.append(
                _evidence(
                    repo_root,
                    relative_path,
                    artifact_id=artifact_id,
                    evidence_role=role,
                    supports_conclusion=supports,
                    source_record_sha256=_canonical_json_sha256(artifact),
                )
            )
            if isinstance(artifact_id, str):
                experiment_ids.append(artifact_id)

        negative_reason = None
        if classification in NEGATIVE_CLASSIFICATIONS:
            negative_reason = (
                f"{classification} is indexed for {candidate_id}; canonical rationale remains "
                "only in the content-addressed repo evidence references."
            )

        seeds.append(
            MemorySeed(
                definition=definition,
                source_key=candidate_id,
                title=row["name"],
                status=row["status"],
                classification=classification,
                negative_reason=negative_reason,
                source_created_at=row.get("created_at"),
                source_updated_at=row.get("updated_at"),
                source_metadata={
                    "candidate_registry_line": line_number,
                    "candidate_registry_record_sha256": row_sha256,
                    "experiment_artifact_ids": sorted(experiment_ids),
                    "pipeline_stage": row["pipeline_stage"],
                    "trial_ids": row["trial_ids"],
                },
                aliases=(("candidate_id", candidate_id.lower()), ("name", row["name"])),
                evidence=tuple(
                    sorted(refs, key=lambda ref: (ref.evidence_role, ref.artifact_path))
                ),
            )
        )

    source_keys = [seed.source_key for seed in seeds]
    if len(source_keys) != len(set(source_keys)):
        raise ValueError("candidate registry contains duplicate candidate_id values")
    return tuple(sorted(seeds, key=lambda seed: seed.source_key))
