"""Fixture-only canonical crossing builder for candidate-review packets.

This module proves the crossing mechanism against fake/test inputs only. It
does not create real candidate lifecycle registry artifacts and does not grant
promotion, readiness, paper/live, runtime, capital, OMS, risk, broker, exchange,
credential, provider/API, or network authority.
"""

from __future__ import annotations

import copy
from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from tools.agent_sandbox import AuditRecord, ToolAction, ToolContext
from tools.agent_sandbox.permissions import (
    BUILD_FIXTURE_CANONICAL_CROSSING,
    READ_NON_SECRET,
    WRITE_SCRATCH,
)
from tools.registry.validate_candidate_registry import validate_candidate_registries


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-AGENT-CANONICAL-CROSSING-BUILD-01"
ROLE = "canonical_crossing_builder_fixture"
OUTPUT_ROOT = Path("scratch") / WP_ID / "outputs"
TRIAL_STATUSES = ("completed", "failed", "invalid", "pruned", "blocked")
REQUIRED_PACKET_FLAGS = {
    "not evidence",
    "not candidate authority",
    "not promotion authority",
    "not ranking authority",
    "not paper/live readiness",
    "not a trading signal",
    "human review required",
}
REQUIRED_APPROVAL_FIELDS = {
    "approval_id",
    "approved_by",
    "approval_timestamp_utc",
    "approval_scope",
    "content_reviewed",
    "content_reviewed_hash",
    "content_reviewed_at_utc",
    "canonical_crossing_allowed",
    "fixture_only",
    "source_candidate_review_packet_path",
    "source_candidate_review_packet_hash",
    "source_formalizer_artifact_path",
    "source_formalizer_artifact_hash",
    "source_bridge_artifact_path",
    "source_bridge_artifact_hash",
    "source_robustness_artifact_path",
    "source_robustness_artifact_hash",
    "source_denominator_ledger_path",
    "source_denominator_ledger_hash",
    "append_only",
    "no_promotion",
    "no_readiness",
    "operator_acknowledges_missing_diagnostics",
    "operator_acknowledges_data_availability_warnings",
    "operator_acknowledges_funding_mode",
}
REQUIRED_TRUE_APPROVAL_FLAGS = {
    "content_reviewed",
    "canonical_crossing_allowed",
    "fixture_only",
    "append_only",
    "no_promotion",
    "no_readiness",
    "operator_acknowledges_missing_diagnostics",
    "operator_acknowledges_data_availability_warnings",
    "operator_acknowledges_funding_mode",
}
FORBIDDEN_TRUE_APPROVAL_FLAGS = {
    "promotion_allowed",
    "readiness_allowed",
    "paper_live_allowed",
    "runtime_allowed",
    "candidate_registration_allowed",
    "candidate_freeze_allowed",
}


class CanonicalCrossingBuildError(ValueError):
    """Raised after the fixture crossing builder records a blocked decision."""


@dataclass(frozen=True)
class CanonicalCrossingBuildConfig:
    """Deterministic fixture crossing controls."""

    run_id: str = "fixture-crossing-run"
    timestamp_utc: str = "2026-06-23T00:00:00Z"
    event_id: str = "CLE-FIXTURE-9001"
    actor: str = "fixture crossing builder"
    gate: str = "fixture_only_canonical_crossing_build"

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} is required")


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _sha256_bytes(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _sha256_json(payload: Any) -> str:
    return _sha256_bytes(_canonical_json(payload).encode("utf-8"))


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sha256:")
        and len(value) == 71
        and all(char in "0123456789abcdef" for char in value[7:])
    )


class CanonicalCrossingFixtureBuilder:
    """Build one fake append-only crossing event after strict preflight checks."""

    def __init__(
        self,
        *,
        config: CanonicalCrossingBuildConfig,
        tool_context: ToolContext,
        repo_root: Path = REPO_ROOT,
    ) -> None:
        if tool_context.role != ROLE or tool_context.wp_id != WP_ID:
            raise ValueError("CanonicalCrossingFixtureBuilder requires its exact role and WP")
        self.config = config
        self.tool_context = tool_context
        self.repo_root = repo_root.resolve()
        self.decisions: list[dict[str, Any]] = []
        self.tool_audit_records: list[AuditRecord] = []

    def _record_decision(self, *, decision: str, check: str, reason: str) -> None:
        self.decisions.append({"decision": decision, "check": check, "reason": reason})

    def _block(self, check: str, reason: str) -> None:
        self._record_decision(decision="blocked", check=check, reason=reason)
        raise CanonicalCrossingBuildError(reason)

    def _repo_relative(self, path: Path | str) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                candidate = candidate.resolve().relative_to(self.repo_root)
            except ValueError as exc:
                raise CanonicalCrossingBuildError("path must remain inside the repo") from exc
        normalized = candidate.as_posix()
        if normalized == ".." or normalized.startswith("../") or "\x00" in normalized:
            raise CanonicalCrossingBuildError("path must remain inside the repo")
        return normalized

    def _is_allowed_fixture_input(self, relative: str) -> bool:
        active_scratch_prefix = f"scratch/{WP_ID}/"
        return relative.startswith("tests/fixtures/") or relative.startswith(active_scratch_prefix)

    def _is_allowed_output(self, relative: str) -> bool:
        return relative.startswith(f"scratch/{WP_ID}/outputs/")

    def _authorize(self, action_type: str, relative: str) -> AuditRecord:
        record = self.tool_context.require_allowed(ToolAction(action_type, relative))
        self.tool_audit_records.append(record)
        return record

    def _read_bytes(self, path: Path | str) -> tuple[str, bytes, str]:
        relative = self._repo_relative(path)
        if not self._is_allowed_fixture_input(relative):
            self._block("input_path_allowlist", f"fixture input path is outside allowed prefixes: {relative}")
        self._authorize(READ_NON_SECRET, relative)
        if not (self.repo_root / relative).is_file():
            self._block("input_exists", f"fixture input file not found: {relative}")
        content = (self.repo_root / relative).read_bytes()
        return relative, content, _sha256_bytes(content)

    def _read_json(self, path: Path | str) -> tuple[str, dict[str, Any], str]:
        relative, content, digest = self._read_bytes(path)
        try:
            payload = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._block("json_parse", f"invalid JSON: {relative}")
            raise AssertionError("unreachable") from exc
        if not isinstance(payload, dict):
            self._block("json_root", f"JSON root must be an object: {relative}")
        return relative, payload, digest

    def _write_json(self, path: Path | str, payload: Mapping[str, Any]) -> str:
        relative = self._repo_relative(path)
        if not self._is_allowed_output(relative):
            self._block("output_path_allowlist", f"fixture output path is outside active WP outputs: {relative}")
        self._authorize(WRITE_SCRATCH, relative)
        target = self.repo_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_canonical_json(payload), encoding="utf-8", newline="\n")
        return relative

    def _authorize_crossing_action(self, output_registry_path: str) -> None:
        relative = self._repo_relative(output_registry_path)
        if not self._is_allowed_output(relative):
            self._block("crossing_action_output", f"crossing output is outside active WP outputs: {relative}")
        self._authorize(BUILD_FIXTURE_CANONICAL_CROSSING, relative)

    def _required_mapping(self, value: Any, check: str) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            self._block(check, f"{check} must be an object")
        return value

    def _validate_approval(
        self,
        *,
        approval: Mapping[str, Any],
        approval_path: str,
        approval_hash: str,
        packet_path: str,
        packet_hash: str,
        packet: Mapping[str, Any],
    ) -> dict[str, Any]:
        missing = sorted(REQUIRED_APPROVAL_FIELDS - set(approval))
        if missing:
            self._block("approval_contract", f"approval artifact missing fields: {missing}")
        for field in sorted(REQUIRED_TRUE_APPROVAL_FLAGS):
            if approval.get(field) is not True:
                self._block("approval_contract", f"approval field must be true: {field}")
        for field in sorted(FORBIDDEN_TRUE_APPROVAL_FLAGS):
            if approval.get(field) is True:
                self._block("approval_forbidden_implication", f"approval implies forbidden authority: {field}")
        if approval.get("approval_scope") != "fixture_only_canonical_crossing_build":
            self._block("approval_scope", "approval_scope must be fixture_only_canonical_crossing_build")
        if approval.get("content_reviewed_hash") != packet_hash:
            self._block("content_before_lock", "content_reviewed_hash does not match candidate-review packet")
        if approval.get("source_candidate_review_packet_path") != packet_path:
            self._block("approval_packet_path", "approval packet path does not match loaded packet")
        if approval.get("source_candidate_review_packet_hash") != packet_hash:
            self._block("approval_packet_hash", "approval packet hash does not match loaded packet")

        source_formalizer = self._required_mapping(packet.get("source_formalizer"), "source_formalizer")
        source_bridge = self._required_mapping(packet.get("source_bridge"), "source_bridge")
        source_robustness = self._required_mapping(packet.get("source_robustness"), "source_robustness")
        denominator = self._required_mapping(packet.get("denominator_snapshot"), "denominator_snapshot")
        expected_sources = {
            "source_formalizer_artifact": (
                source_formalizer.get("path"),
                source_formalizer.get("sha256"),
            ),
            "source_bridge_artifact": (
                source_bridge.get("review_packet_path"),
                source_bridge.get("review_packet_sha256"),
            ),
            "source_robustness_artifact": (
                source_robustness.get("diagnostics_path"),
                source_robustness.get("diagnostics_sha256"),
            ),
            "source_denominator_ledger": (
                denominator.get("ledger_path"),
                denominator.get("ledger_sha256"),
            ),
        }
        source_checks: dict[str, dict[str, Any]] = {}
        for prefix, (expected_path, expected_hash) in expected_sources.items():
            path_field = f"{prefix}_path"
            hash_field = f"{prefix}_hash"
            if approval.get(path_field) != expected_path:
                self._block("source_lineage_path", f"{path_field} does not match packet lineage")
            if approval.get(hash_field) != expected_hash:
                self._block("source_lineage_hash", f"{hash_field} does not match packet lineage")
            if not isinstance(expected_path, str) or not _is_sha256(expected_hash):
                self._block("source_lineage_shape", f"{prefix} source path/hash are invalid")
            _source_path, _source_payload, actual_hash = self._read_json(expected_path)
            if actual_hash != expected_hash:
                self._block("source_lineage_hash", f"actual source hash mismatch: {expected_path}")
            source_checks[prefix] = {
                "path": expected_path,
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
                "status": "passed",
            }

        return {
            "status": "passed",
            "approval_path": approval_path,
            "approval_hash": approval_hash,
            "packet_path": packet_path,
            "packet_hash": packet_hash,
            "source_checks": source_checks,
        }

    def _validate_packet_contract(self, packet: Mapping[str, Any]) -> dict[str, Any]:
        if packet.get("schema_version") != "candidate_review_packet_v1":
            self._block("packet_schema", "candidate-review packet schema_version is invalid")
        flags = set(packet.get("non_authority_flags", []))
        if not REQUIRED_PACKET_FLAGS.issubset(flags):
            self._block("non_authority_flags", "candidate-review packet lacks required non-authority flags")

        denominator = self._required_mapping(packet.get("denominator_snapshot"), "denominator_snapshot")
        counts = self._required_mapping(denominator.get("counts"), "denominator_counts")
        normalized_counts: dict[str, int] = {}
        for status in TRIAL_STATUSES:
            value = counts.get(status)
            if not isinstance(value, int) or value < 0:
                self._block("denominator_counts", f"denominator count missing or invalid: {status}")
            normalized_counts[status] = value
        rows = denominator.get("row_disposition")
        if not isinstance(rows, list) or not rows:
            self._block("row_disposition", "row_disposition must be a non-empty list")
        for row in rows:
            if not isinstance(row, Mapping):
                self._block("row_disposition", "row_disposition rows must be objects")
            if not row.get("variant_id") or row.get("trial_status") not in TRIAL_STATUSES or not row.get("status_reason"):
                self._block("row_disposition", "row_disposition row is incomplete")
        computed_counts = Counter(row.get("trial_status") for row in rows)
        if any(computed_counts[status] != normalized_counts[status] for status in TRIAL_STATUSES):
            self._block("denominator_counts", "row_disposition counts do not match denominator counts")
        declared_trial_count = denominator.get("declared_trial_count")
        if declared_trial_count != len(rows) or sum(normalized_counts.values()) != len(rows):
            self._block("denominator_counts", "declared trial count does not match denominator rows")
        if denominator.get("all_source_rows_preserved") is not True:
            self._block("denominator_preservation", "all_source_rows_preserved must be true")

        robustness = self._required_mapping(packet.get("robustness_summary"), "robustness_summary")
        skipped = robustness.get("diagnostics_skipped")
        if not isinstance(skipped, list) or not skipped:
            self._block("skipped_diagnostics", "skipped diagnostics must remain visible")
        missing = self._required_mapping(packet.get("missing_data_limitations"), "missing_data_limitations")
        for key in ("per_trade", "oos_walkforward", "funding_stress"):
            if not isinstance(missing.get(key), Mapping):
                self._block("missing_diagnostics", f"missing diagnostic state hidden: {key}")

        data_funding = self._required_mapping(packet.get("data_and_funding_summary"), "data_and_funding_summary")
        for key in ("data_availability_warnings", "data_availability_blockers"):
            if not isinstance(data_funding.get(key), list):
                self._block("data_availability", f"{key} must be present as a list")
        funding_mode = self._required_mapping(data_funding.get("funding_mode"), "funding_mode")
        effective_funding = funding_mode.get("effective")
        if effective_funding not in {"off", "on", "not_run", "unknown"}:
            self._block("funding_mode", "funding mode effective value is missing or invalid")
        if not isinstance(data_funding.get("funding_stress_status"), Mapping):
            self._block("funding_mode", "funding stress status must be preserved")

        return {
            "status": "passed",
            "denominator_counts": normalized_counts,
            "row_count": len(rows),
            "skipped_diagnostics_count": len(skipped),
            "data_warning_count": len(data_funding["data_availability_warnings"]),
            "data_blocker_count": len(data_funding["data_availability_blockers"]),
            "funding_cost_mode": effective_funding,
        }

    def _crossing_evidence(
        self,
        *,
        packet: Mapping[str, Any],
        packet_path: str,
        packet_hash: str,
        approval_path: str,
        approval_hash: str,
    ) -> dict[str, Any]:
        formalizer = self._required_mapping(packet["source_formalizer"], "source_formalizer")
        bridge = self._required_mapping(packet["source_bridge"], "source_bridge")
        robustness = self._required_mapping(packet["source_robustness"], "source_robustness")
        denominator = self._required_mapping(packet["denominator_snapshot"], "denominator_snapshot")
        robustness_summary = self._required_mapping(packet["robustness_summary"], "robustness_summary")
        data_funding = self._required_mapping(packet["data_and_funding_summary"], "data_and_funding_summary")
        funding_stress = self._required_mapping(data_funding["funding_stress_status"], "funding_stress_status")
        funding_mode = self._required_mapping(data_funding["funding_mode"], "funding_mode")
        missing = self._required_mapping(packet["missing_data_limitations"], "missing_data_limitations")
        def missing_state(name: str) -> dict[str, Any]:
            state = self._required_mapping(missing[name], f"missing_{name}")
            normalized: dict[str, Any] = {
                "status": state["status"],
                "performed": state["performed"],
            }
            if "reason" in state:
                normalized["reason"] = state["reason"]
            if "queued_follow_up" in state:
                normalized["queued_follow_up"] = state["queued_follow_up"]
            if "fabricated_per_trade_data" in state:
                normalized["fabricated_per_trade_data"] = state["fabricated_per_trade_data"]
            return normalized

        skipped = [
            {"diagnostic": item["diagnostic"], "reason": item["reason"]}
            for item in robustness_summary["diagnostics_skipped"]
        ]
        source_lineage = {
            "candidate_review_packet_path": packet_path,
            "candidate_review_packet_hash": packet_hash,
            "formalizer_artifact_path": formalizer["path"],
            "formalizer_artifact_hash": formalizer["sha256"],
            "formalizer_draft_strategy_spec_path": formalizer.get("draft_strategy_spec_path"),
            "formalizer_draft_strategy_spec_hash": formalizer.get("draft_strategy_spec_sha256"),
            "bridge_artifact_path": bridge["review_packet_path"],
            "bridge_artifact_hash": bridge["review_packet_sha256"],
            "bridge_runner_artifact_path": bridge.get("runner_artifact_path"),
            "bridge_runner_artifact_hash": bridge.get("runner_artifact_sha256"),
            "robustness_artifact_path": robustness["diagnostics_path"],
            "robustness_artifact_hash": robustness["diagnostics_sha256"],
            "robustness_review_packet_path": robustness.get("review_packet_path"),
            "robustness_review_packet_hash": robustness.get("review_packet_sha256"),
            "denominator_ledger_path": denominator["ledger_path"],
            "denominator_ledger_hash": denominator["ledger_sha256"],
            "operator_approval_path": packet.get("operator_approval", {}).get("path")
            if isinstance(packet.get("operator_approval"), Mapping)
            else None,
            "operator_approval_hash": packet.get("operator_approval", {}).get("sha256")
            if isinstance(packet.get("operator_approval"), Mapping)
            else None,
            "crossing_approval_path": approval_path,
            "crossing_approval_hash": approval_hash,
        }
        warnings = list(data_funding.get("data_availability_warnings", []))
        blockers = list(data_funding.get("data_availability_blockers", []))
        return {
            "source_lineage": source_lineage,
            "denominator_snapshot": {
                "completed_count": denominator["counts"]["completed"],
                "failed_count": denominator["counts"]["failed"],
                "invalid_count": denominator["counts"]["invalid"],
                "pruned_count": denominator["counts"]["pruned"],
                "blocked_count": denominator["counts"]["blocked"],
                "declared_trial_count": denominator["declared_trial_count"],
                "all_source_rows_preserved": True,
                "full_ledger_path": denominator["ledger_path"],
                "full_ledger_hash": denominator["ledger_sha256"],
                "row_disposition": [
                    {
                        "variant_id": row["variant_id"],
                        "trial_status": row["trial_status"],
                        "status_reason": row["status_reason"],
                    }
                    for row in denominator["row_disposition"]
                ],
            },
            "diagnostics_summary": {
                "completed_diagnostics": list(robustness_summary.get("diagnostics_completed", [])),
                "skipped_diagnostics": skipped,
                "skipped_reasons": sorted({item["reason"] for item in skipped}),
                "missing_diagnostics": {
                    "per_trade": missing_state("per_trade"),
                    "oos_walkforward": missing_state("oos_walkforward"),
                    "funding_stress": missing_state("funding_stress"),
                },
                "unsupported_diagnostics": list(packet.get("unsupported_diagnostics", [])),
            },
            "data_availability": {
                "warnings": warnings,
                "blockers": blockers,
                "coverage_classes": list(packet.get("data_availability_coverage_classes", [])),
                "constraint_classes": list(packet.get("data_availability_constraint_classes", [])),
                "caveats": list(packet.get("data_availability_caveats", warnings + blockers)),
            },
            "funding": {
                "funding_cost_mode": funding_mode["effective"],
                "funding_stress_status": {
                    "status": funding_stress["status"],
                    "performed": funding_stress["performed"],
                    "skipped_reason": funding_stress.get("skipped_reason") or funding_stress.get("reason"),
                },
            },
            "non_authority_flags": {
                "not_evidence": True,
                "not_candidate_authority": True,
                "not_promotion_authority": True,
                "not_ranking_authority": True,
                "not_paper_live_readiness": True,
                "not_trading_signal": True,
                "human_review_required": True,
            },
            "append_only_semantics": {
                "append_only": True,
                "new_event_only": True,
                "no_overwrite": True,
                "correction_requires_supersession_event": True,
                "source_hashes_preserved": True,
                "denominator_snapshot_preserved": True,
                "caveats_preserved": True,
                "missing_diagnostics_preserved": True,
            },
        }

    def _append_event(
        self,
        *,
        registry: Mapping[str, Any],
        packet: Mapping[str, Any],
        crossing_evidence: Mapping[str, Any],
    ) -> dict[str, Any]:
        output = copy.deepcopy(dict(registry))
        candidates = output.get("candidates")
        ledger = output.get("append_only_ledger")
        if not isinstance(candidates, list) or len(candidates) != 1 or not isinstance(candidates[0], dict):
            self._block("fake_registry_shape", "fixture registry must contain exactly one candidate")
        if not isinstance(ledger, list):
            self._block("fake_registry_shape", "fixture registry append_only_ledger must be a list")
        candidate = candidates[0]
        candidate_id = candidate.get("candidate_id")
        if not isinstance(candidate_id, str):
            self._block("fake_registry_shape", "fixture candidate_id is invalid")
        if any(event.get("event_id") == self.config.event_id for event in ledger if isinstance(event, Mapping)):
            self._block("append_only", "event_id collision would overwrite an existing event")
        if any(event.get("candidate_id") == candidate_id for event in ledger if isinstance(event, Mapping)):
            self._block("append_only", "candidate already has lifecycle events; crossing must be first-entry-shaped")
        if candidate.get("lifecycle_event_refs"):
            self._block("append_only", "candidate lifecycle_event_refs are not empty before first crossing")

        source_ref = {
            "artifact_type": "candidate_review_packet",
            "artifact_id": "CANDIDATE-REVIEW-PACKET-FIXTURE",
            "artifact_ref": crossing_evidence["source_lineage"]["candidate_review_packet_path"],
            "relationship": "source_lineage",
            "authority_boundary": "review_reference_only",
            "identity_hash": crossing_evidence["source_lineage"]["candidate_review_packet_hash"],
            "notes": "Fixture source packet only; not canonical evidence.",
        }
        event = {
            "event_id": self.config.event_id,
            "event_sequence": 1,
            "candidate_id": candidate_id,
            "event_type": "candidate_review_packet_crossed",
            "timestamp_utc": self.config.timestamp_utc,
            "actor": self.config.actor,
            "gate": self.config.gate,
            "from_status": None,
            "to_status": "proposed",
            "reason": "Fixture-only append-only crossing event preserving reviewed packet content.",
            "related_evidence_links": [source_ref],
            "blocking_or_exception_refs": [],
            "crossing_evidence": copy.deepcopy(dict(crossing_evidence)),
            "non_authority_declaration": {
                "not_candidate_approval": True,
                "not_paper_live_authority": True,
                "not_runtime_authority": True,
                "not_promotion_authority": True,
                "not_trading_recommendation": True,
                "not_broker_exchange_authority": True,
                "not_capital_authority": True,
                "notes": "Fixture crossing event creates no evidence, ranking, readiness, promotion, paper/live, runtime, or execution authority.",
            },
        }
        candidate["candidate_status"] = "proposed"
        candidate["lifecycle_event_refs"] = [self.config.event_id]
        candidate["required_next_review"] = (
            "first real crossing remains separately Karl-gated; full content must be surfaced"
        )
        candidate["evidence_links"] = [source_ref]
        output["append_only_ledger"] = [*ledger, event]
        output["validation_summary"]["fixture_only"] = True
        output["validation_summary"]["real_candidate_registered"] = False
        output["validation_summary"]["notes"] = (
            "Fixture-only registry copy after canonical crossing build proof; no real canonical evidence written."
        )
        return output

    def _write_failure_audit(self, run_dir: Path, error: Exception) -> None:
        failure_packet = {
            "status": "blocked",
            "error": str(error),
            "fixture_only": True,
            "real_canonical_evidence_written": False,
            "first_real_crossing_remains_karl_gated": True,
        }
        audit_log = {
            "status": "blocked",
            "decisions": self.decisions,
            "tool_context_records": [record.to_dict() for record in self.tool_audit_records],
        }
        self._write_json(run_dir / "crossing_audit_log.json", audit_log)
        self._write_json(run_dir / "crossing_result_packet.json", failure_packet)

    def run(
        self,
        *,
        candidate_review_packet_path: Path | str,
        crossing_approval_path: Path | str,
        fake_registry_input_path: Path | str,
    ) -> dict[str, Any]:
        run_dir = OUTPUT_ROOT / self.config.run_id
        output_registry = run_dir / "fake_registry_after.candidate_lifecycle_registry.json"
        self._authorize_crossing_action(output_registry.as_posix())
        try:
            packet_path, packet, packet_hash = self._read_json(candidate_review_packet_path)
            approval_path, approval, approval_hash = self._read_json(crossing_approval_path)
            registry_path, registry, registry_hash = self._read_json(fake_registry_input_path)
            before_hash = _sha256_json(registry)
            self._write_json(
                run_dir / "crossing_input_manifest.json",
                {
                    "candidate_review_packet_path": packet_path,
                    "candidate_review_packet_hash": packet_hash,
                    "crossing_approval_path": approval_path,
                    "crossing_approval_hash": approval_hash,
                    "fake_registry_input_path": registry_path,
                    "fake_registry_input_file_hash": registry_hash,
                    "fixture_only": True,
                },
            )
            approval_report = self._validate_approval(
                approval=approval,
                approval_path=approval_path,
                approval_hash=approval_hash,
                packet_path=packet_path,
                packet_hash=packet_hash,
                packet=packet,
            )
            packet_report = self._validate_packet_contract(packet)
            self._record_decision(
                decision="allowed",
                check="preflight",
                reason="approval, content, source hash, denominator, caveat, and non-authority checks passed",
            )
            crossing_evidence = self._crossing_evidence(
                packet=packet,
                packet_path=packet_path,
                packet_hash=packet_hash,
                approval_path=approval_path,
                approval_hash=approval_hash,
            )
            output_registry_payload = self._append_event(
                registry=registry,
                packet=packet,
                crossing_evidence=crossing_evidence,
            )
            after_hash = _sha256_json(output_registry_payload)
            output_registry_path = self._write_json(output_registry, output_registry_payload)
            post_write_errors = validate_candidate_registries(registry_dir=self.repo_root / run_dir)
            post_write_status = "passed" if not post_write_errors else "failed"
            if post_write_errors:
                self._block("post_write_validation", "candidate registry validator failed after fake write")
            result_packet = {
                "status": "completed",
                "fixture_only": True,
                "no_real_canonical_evidence_written": True,
                "first_real_crossing_remains_separately_karl_gated": True,
                "output_registry_path": output_registry_path,
                "output_registry_hash": after_hash,
                "event_id": self.config.event_id,
                "event_type": "candidate_review_packet_crossed",
            }
            audit_log = {
                "status": "completed",
                "decisions": self.decisions,
                "tool_context_records": [record.to_dict() for record in self.tool_audit_records],
            }
            outputs = {
                "crossing_input_manifest": self._write_json(
                    run_dir / "crossing_input_manifest.json",
                    {
                        "candidate_review_packet_path": packet_path,
                        "candidate_review_packet_hash": packet_hash,
                        "crossing_approval_path": approval_path,
                        "crossing_approval_hash": approval_hash,
                        "fake_registry_input_path": registry_path,
                        "fake_registry_input_file_hash": registry_hash,
                        "fixture_only": True,
                    },
                ),
                "crossing_approval_validation": self._write_json(
                    run_dir / "crossing_approval_validation.json", approval_report
                ),
                "crossing_preflight_report": self._write_json(
                    run_dir / "crossing_preflight_report.json",
                    {"status": "passed", "packet_contract": packet_report},
                ),
                "fake_registry_before_hash": self._write_json(
                    run_dir / "fake_registry_before_hash.json",
                    {"path": registry_path, "payload_hash": before_hash, "file_hash": registry_hash},
                ),
                "fake_registry_after_hash": self._write_json(
                    run_dir / "fake_registry_after_hash.json",
                    {"path": output_registry_path, "payload_hash": after_hash},
                ),
                "post_write_validation_report": self._write_json(
                    run_dir / "post_write_validation_report.json",
                    {"status": post_write_status, "errors": post_write_errors},
                ),
                "crossing_audit_log": self._write_json(
                    run_dir / "crossing_audit_log.json", audit_log
                ),
                "crossing_result_packet": self._write_json(
                    run_dir / "crossing_result_packet.json", result_packet
                ),
                "fake_registry_after": output_registry_path,
            }
            return {"status": "completed", "outputs": outputs, "result_packet": result_packet}
        except Exception as exc:
            if not isinstance(exc, CanonicalCrossingBuildError):
                self._record_decision(decision="blocked", check="unexpected_error", reason=str(exc))
            self._write_failure_audit(run_dir, exc)
            raise
