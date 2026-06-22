"""Bridge approved formalizer drafts into scratch-only real offline sweeps."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.agent_sandbox import BlockedActionError, ToolAction, ToolContext
from tools.agent_sandbox.permissions import (
    READ_NON_SECRET,
    RUN_NONCANONICAL_OFFLINE_SWEEP,
    RUN_READ_ONLY_VALIDATION,
    WRITE_SCRATCH,
)
from tools.registry.validate_strategy_specs import validate_strategy_specs
from tools.registry.validate_variant_sweep_artifacts import validate_variant_sweep_artifacts
from tools.research_runner.run_offline_sweep import run_offline_sweep


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01"
ROLE = "formalizer_runner_bridge"
OUTPUT_ROOT = Path("scratch") / WP_ID / "outputs"
FORMALIZER_OUTPUT_PREFIX = "scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/"
APPROVAL_SCOPE = "noncanonical_scratch_runner_bridge_only"
BRIDGE_VERSION = "formalizer-runner-bridge-v1"
VARIANT_TEMPLATE_PATH = Path("research/variant_manifests/VM-0003.variant_manifest.json")
SWEEP_TEMPLATE_PATH = Path("research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json")
STRATEGY_VALIDATOR_PATH = "tools/registry/validate_strategy_specs.py"
VARIANT_SWEEP_VALIDATOR_PATH = "tools/registry/validate_variant_sweep_artifacts.py"
TRIAL_STATUSES = ("completed", "failed", "invalid", "pruned", "blocked")
NON_AUTHORITY_FLAGS = (
    "not canonical",
    "not evidence",
    "not candidate authority",
    "not promotion authority",
    "not paper/live readiness",
    "human review required",
)
RUNNER_OUTCOME_TO_TRIAL_STATUS = {
    "successful": "completed",
    "failed": "failed",
    "invalid": "invalid",
    "excluded": "pruned",
    "filtered": "pruned",
    "errored": "blocked",
    "aborted": "blocked",
    "data_unavailable": "blocked",
    "not_attempted": "blocked",
}


class FormalizerRunnerBridgeError(ValueError):
    """Raised when bridge inputs cannot safely satisfy the bounded contract."""


@dataclass(frozen=True)
class FormalizerRunnerBridgeConfig:
    ohlcv_input_path: str
    funding_cost_mode: str = "off"
    experiment_scope: str = "full_history_public"
    deterministic_seed: int = 0
    timestamp_utc: str = "2026-06-22T00:00:00Z"

    def __post_init__(self) -> None:
        if self.funding_cost_mode not in {"off", "on"}:
            raise ValueError("funding_cost_mode must be 'off' or 'on'")
        if self.experiment_scope not in {"full_history_public", "limited_noncanonical"}:
            raise ValueError(
                "experiment_scope must be 'full_history_public' or 'limited_noncanonical'"
            )
        if not self.ohlcv_input_path:
            raise ValueError("ohlcv_input_path is required")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _get_path(payload: Mapping[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise FormalizerRunnerBridgeError(f"manifest hash scope is missing {dotted_path}")
        current = current[part]
    return current


def _refresh_manifest_hash(manifest: dict[str, Any]) -> str:
    pinning = manifest["manifest_hash_pinning"]
    scoped = {path: _get_path(manifest, path) for path in pinning["hash_scope"]}
    digest = _sha256(scoped)
    pinning["manifest_hash"] = digest
    return digest


class FormalizerRunnerBridge:
    """ToolContext-routed bridge for one approved SMA/stddev formalizer family."""

    def __init__(
        self,
        *,
        config: FormalizerRunnerBridgeConfig,
        tool_context: ToolContext,
        repo_root: Path = REPO_ROOT,
    ) -> None:
        if tool_context.role != ROLE or tool_context.wp_id != WP_ID:
            raise ValueError("FormalizerRunnerBridge requires its exact ToolContext role and WP")
        self.config = config
        self.tool_context = tool_context
        self.repo_root = repo_root.resolve()

    def _repo_relative(self, path: Path | str) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                candidate = candidate.resolve().relative_to(self.repo_root)
            except ValueError as exc:
                raise FormalizerRunnerBridgeError("path must remain inside the repo") from exc
        normalized = candidate.as_posix()
        if normalized == ".." or normalized.startswith("../"):
            raise FormalizerRunnerBridgeError("path must remain inside the repo")
        return normalized

    def _read_bytes(self, path: Path | str) -> bytes:
        relative = self._repo_relative(path)
        return self.tool_context.run_allowed(
            ToolAction(READ_NON_SECRET, relative),
            lambda: (self.repo_root / relative).read_bytes(),
        )

    def _read_json(self, path: Path | str) -> dict[str, Any]:
        relative = self._repo_relative(path)
        try:
            payload = json.loads(self._read_bytes(relative))
        except (json.JSONDecodeError, OSError) as exc:
            raise FormalizerRunnerBridgeError(f"cannot read JSON object: {relative}") from exc
        if not isinstance(payload, dict):
            raise FormalizerRunnerBridgeError(f"JSON root must be an object: {relative}")
        return payload

    def _write_json(self, path: Path | str, payload: Mapping[str, Any]) -> str:
        relative = self._repo_relative(path)

        def operation() -> None:
            target = self.repo_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )

        self.tool_context.run_allowed(ToolAction(WRITE_SCRATCH, relative), operation)
        return relative

    @staticmethod
    def _validate_formalizer_contract(path: str, payload: Mapping[str, Any]) -> None:
        if not path.startswith(FORMALIZER_OUTPUT_PREFIX) or not path.endswith(
            "/formalized_idea.json"
        ):
            raise FormalizerRunnerBridgeError(
                "formalizer output must be the scoped scratch artifact"
            )
        if payload.get("schema_version") != "agent_formalized_idea_v1":
            raise FormalizerRunnerBridgeError("unsupported formalizer output schema")
        if payload.get("status") != "accepted":
            raise FormalizerRunnerBridgeError("formalizer output must be accepted")
        if not isinstance(payload.get("run_id"), str) or not payload["run_id"]:
            raise FormalizerRunnerBridgeError("formalizer run_id is required")
        research_object = payload.get("research_object")
        if not isinstance(research_object, Mapping):
            raise FormalizerRunnerBridgeError("formalizer research_object is required")
        if research_object.get("symbols") != ["BTCUSDT"] or research_object.get(
            "timeframe"
        ) != "15m":
            raise FormalizerRunnerBridgeError("bridge supports only BTCUSDT 15m")
        if not {"sma", "stddev"}.issubset(set(research_object.get("features", []))):
            raise FormalizerRunnerBridgeError(
                "bridge supports only the formalizer SMA/stddev mean-reversion family"
            )
        draft = payload.get("draft_strategy_spec")
        if not isinstance(draft, Mapping) or draft.get("produced") is not True or not draft.get(
            "path"
        ):
            raise FormalizerRunnerBridgeError(
                "validated formalizer draft Strategy Spec is required"
            )
        non_authority = payload.get("non_authority")
        if not isinstance(non_authority, Mapping) or not non_authority.get("scratch_only"):
            raise FormalizerRunnerBridgeError("formalizer non-authority contract is missing")

    def _require_approval(
        self,
        approval: Mapping[str, Any],
        *,
        source_run_id: str,
        approval_path: str,
        formalizer_path: str,
    ) -> None:
        expected_prefix = formalizer_path.rsplit("/", 1)[0] + "/"
        valid = (
            approval_path.startswith(expected_prefix)
            and approval.get("approved_for_noncanonical_runner_bridge") is True
            and approval.get("approved_by") == "operator"
            and approval.get("approval_scope") == APPROVAL_SCOPE
            and isinstance(approval.get("approval_timestamp_utc"), str)
            and bool(approval.get("approval_timestamp_utc"))
            and approval.get("source_formalizer_run_id") == source_run_id
        )
        if self.config.funding_cost_mode == "on":
            valid = valid and approval.get("approved_funding_cost_mode") == "on"
        if valid:
            return
        try:
            self.tool_context.require_allowed(ToolAction("approval_gate_bypass", approval_path))
        except BlockedActionError:
            raise
        raise AssertionError("unapproved bridge was unexpectedly allowed")

    def _validate_draft(self, draft_path: str) -> dict[str, Any]:
        if not draft_path.startswith(FORMALIZER_OUTPUT_PREFIX):
            raise FormalizerRunnerBridgeError(
                "draft Strategy Spec must remain in formalizer scratch"
            )
        draft = self._read_json(draft_path)
        errors = self.tool_context.run_allowed(
            ToolAction(RUN_READ_ONLY_VALIDATION, STRATEGY_VALIDATOR_PATH),
            lambda: validate_strategy_specs(
                strategy_specs_dir=(self.repo_root / draft_path).parent,
                repo_root=self.repo_root,
            ),
        )
        if errors:
            raise FormalizerRunnerBridgeError(
                "draft Strategy Spec validation failed: " + "; ".join(errors)
            )
        constraints = draft.get("provenance", {}).get("source_constraints", [])
        if not any("STRAT-SPEC-0003 capability family" in str(item) for item in constraints):
            raise FormalizerRunnerBridgeError(
                "draft does not declare the supported STRAT-SPEC-0003 adapter"
            )
        return draft

    def _availability_blockers(self, formalized: Mapping[str, Any]) -> list[str]:
        assessment = formalized.get("capability_assessment")
        rows = assessment.get("feature_assessments", []) if isinstance(assessment, Mapping) else []
        blockers: list[str] = []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            feature = str(row.get("feature", "unknown"))
            coverage = str(row.get("coverage_class", ""))
            source = str(row.get("source_class", ""))
            testability = str(row.get("historical_testability", ""))
            if feature not in {"sma", "stddev"}:
                blockers.append(
                    f"{feature} is not encoded by the supported STRAT-SPEC-0003 draft adapter"
                )
            if feature == "taker_buy_sell_ratio" and source == "PUBLIC_TRADE_ARCHIVE_DERIVATION":
                blockers.append(
                    "taker flow requires a distinct referenced archive-derived fixture/source; "
                    "the OHLCV runner fixture is insufficient"
                )
                continue
            constrained = coverage in {
                "PUBLIC_SNAPSHOT_ONLY",
                "RECENT_ONLY_PUBLIC_REST",
                "STREAMING_ONLY_PUBLIC_CAPTURE",
                "STREAMING_ONLY_PUBLIC_WS",
                "VENDOR_ONLY_FOR_HISTORY",
                "UNKNOWN_OR_BLOCKED",
            } or testability in {"vendor_or_capture_constrained", "blocked_unknown"}
            if self.config.experiment_scope == "full_history_public" and constrained:
                blockers.append(
                    f"{feature} cannot run as full-history public data ({coverage or testability})"
                )
            if feature in {"open_interest", "open_interest_value"}:
                blockers.append("open interest cannot be reconstructed from trades")
            if feature == "liquidation_volume":
                blockers.append("liquidation history requires vendor/captured data")
        if self.config.funding_cost_mode == "on":
            blockers.append(
                "real offline runner has no explicit funding-on input; "
                "zero-funding execution cannot be mislabeled"
            )
        return list(dict.fromkeys(blockers))

    def _derive_inputs(
        self,
        *,
        run_id: str,
        run_dir: Path,
        formalized: Mapping[str, Any],
        formalizer_path: str,
        formalizer_hash: str,
        approval_path: str,
        approval_hash: str,
        draft: Mapping[str, Any],
    ) -> dict[str, str]:
        inputs_dir = run_dir / "inputs"
        spec = copy.deepcopy(dict(draft))
        spec_id = str(spec["strategy_spec_id"])
        spec_path = (inputs_dir / f"{spec_id}.strategy_spec.json").as_posix()
        spec_hash = _sha256(spec)

        manifest = copy.deepcopy(self._read_json(VARIANT_TEMPLATE_PATH))
        numeric_id = 9000 + (int(run_id[:8], 16) % 1000)
        manifest_id = f"VM-{numeric_id:04d}"
        manifest_path = (inputs_dir / f"{manifest_id}.variant_manifest.json").as_posix()
        manifest["variant_manifest_id"] = manifest_id
        manifest["parent_strategy_spec"].update(
            {
                "strategy_spec_id": spec_id,
                "strategy_spec_hash": spec_hash,
                "strategy_spec_ref": spec_path,
            }
        )
        manifest["manifest_hash_pinning"]["frozen_at"] = self.config.timestamp_utc
        manifest["lineage"].update(
            {
                "parent_refs": [
                    {
                        "ref_type": "strategy_spec",
                        "ref_id": spec_id,
                        "ref_path": spec_path,
                        "ref_hash": spec_hash,
                    }
                ],
                "source_refs": [
                    {
                        "ref_type": "concept",
                        "ref_id": f"FORMALIZER-{formalized['run_id']}",
                        "ref_path": formalizer_path,
                        "ref_hash": formalizer_hash,
                    },
                    {
                        "ref_type": "manual_review",
                        "ref_id": "OPERATOR-BRIDGE-APPROVAL",
                        "ref_path": approval_path,
                        "ref_hash": approval_hash,
                    },
                ],
                "created_at": self.config.timestamp_utc,
                "updated_at": self.config.timestamp_utc,
                "audit_notes": [
                    "Scratch-only compatibility copy of merged VM-0003 semantics.",
                    "frozen_for_sweep_planning is required by the runner contract "
                    "and grants no canonical freeze authority.",
                    "Human approval is scoped only to this non-canonical scratch bridge run.",
                ],
                "hash_refs": [spec_hash, formalizer_hash, approval_hash],
            }
        )
        manifest["review"].update(
            {
                "reviewer": None,
                "reviewed_at": None,
                "review_notes": [
                    "Scratch-only runner compatibility artifact; not canonical approval or freeze.",
                    "Human review remains required after execution.",
                ],
                "approval_scope": "sweep_planning_only",
            }
        )
        manifest_hash = _refresh_manifest_hash(manifest)

        sweep = copy.deepcopy(self._read_json(SWEEP_TEMPLATE_PATH))
        sweep_id = f"SWEEP-PLAN-{numeric_id:04d}"
        sweep_path = (inputs_dir / f"{sweep_id}.sweep_plan.json").as_posix()
        sweep["sweep_plan_id"] = sweep_id
        sweep["parent_variant_manifest"].update(
            {"variant_manifest_id": manifest_id, "manifest_hash": manifest_hash}
        )
        sweep["lineage"].update(
            {
                "parent_manifest_ref": {
                    "ref_type": "variant_manifest",
                    "ref_id": manifest_id,
                    "ref_path": manifest_path,
                    "ref_hash": manifest_hash,
                },
                "parent_strategy_spec_ref": {
                    "ref_type": "strategy_spec",
                    "ref_id": spec_id,
                    "ref_path": spec_path,
                    "ref_hash": spec_hash,
                },
                "source_refs": [
                    {
                        "ref_type": "other",
                        "ref_id": f"FORMALIZER-{formalized['run_id']}",
                        "ref_path": formalizer_path,
                        "ref_hash": formalizer_hash,
                    },
                    {
                        "ref_type": "manual_review",
                        "ref_id": "OPERATOR-BRIDGE-APPROVAL",
                        "ref_path": approval_path,
                        "ref_hash": approval_hash,
                    },
                ],
                "created_at": self.config.timestamp_utc,
                "updated_at": self.config.timestamp_utc,
                "audit_notes": [
                    "Scratch-only compatibility copy of merged SWEEP-PLAN-0003 semantics.",
                    "This artifact grants no canonical sweep, evidence, or execution authority.",
                ],
            }
        )
        sweep["review"].update(
            {
                "reviewer": None,
                "reviewed_at": None,
                "review_notes": [
                    "Scratch-only runner compatibility artifact; not canonical approval.",
                    "Human review remains required after execution.",
                ],
                "approval_scope": "offline_run_planning_only",
            }
        )

        written = {
            "strategy_spec": self._write_json(spec_path, spec),
            "variant_manifest": self._write_json(manifest_path, manifest),
            "sweep_plan": self._write_json(sweep_path, sweep),
        }
        metadata = {
            "schema_version": "formalizer_runner_bridge_input_metadata_v1",
            "source_formalizer_run_id": formalized["run_id"],
            "source_formalized_idea_path": formalizer_path,
            "source_draft_strategy_spec_path": formalized["draft_strategy_spec"]["path"],
            "approval_marker_path": approval_path,
            "approval_marker_hash": approval_hash,
            "bridge_tool_version": BRIDGE_VERSION,
            "created_at_utc": self.config.timestamp_utc,
            "funding_cost_mode": self.config.funding_cost_mode,
            "data_assumptions": {
                "experiment_scope": self.config.experiment_scope,
                "ohlcv_input_path": self.config.ohlcv_input_path,
                "runner_mode": "canonical_15m_fixture_offline",
            },
            "compatibility_status_not_authority": True,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        written["bridge_metadata"] = self._write_json(inputs_dir / "bridge_metadata.json", metadata)
        return written

    def _validate_derived_inputs(self, paths: Mapping[str, str]) -> None:
        inputs_dir = (self.repo_root / paths["strategy_spec"]).parent
        strategy_errors = self.tool_context.run_allowed(
            ToolAction(RUN_READ_ONLY_VALIDATION, STRATEGY_VALIDATOR_PATH),
            lambda: validate_strategy_specs(
                strategy_specs_dir=inputs_dir,
                repo_root=self.repo_root,
            ),
        )
        variant_errors = self.tool_context.run_allowed(
            ToolAction(RUN_READ_ONLY_VALIDATION, VARIANT_SWEEP_VALIDATOR_PATH),
            lambda: validate_variant_sweep_artifacts(
                variant_manifests_dir=inputs_dir,
                sweep_plans_dir=inputs_dir,
                strategy_specs_dir=inputs_dir,
            ),
        )
        errors = [*strategy_errors, *variant_errors]
        if errors:
            raise FormalizerRunnerBridgeError(
                "derived input validation failed: " + "; ".join(errors)
            )

    def _invoke_runner(
        self,
        *,
        run_dir: Path,
        input_paths: Mapping[str, str],
        ohlcv_path: str,
        write_result_population: bool,
        invocation_name: str,
    ) -> dict[str, Any]:
        target = (run_dir / "runner_artifacts" / invocation_name).as_posix()

        def operation() -> dict[str, Any]:
            return run_offline_sweep(
                self.repo_root / input_paths["strategy_spec"],
                self.repo_root / input_paths["variant_manifest"],
                self.repo_root / input_paths["sweep_plan"],
                self.repo_root / run_dir / "runner_artifacts",
                write_result_population=write_result_population,
                run_label=invocation_name,
                deterministic_seed=self.config.deterministic_seed,
                canonical_15m=True,
                ohlcv_input_path=self.repo_root / ohlcv_path,
            )

        return self.tool_context.run_allowed(
            ToolAction(
                RUN_NONCANONICAL_OFFLINE_SWEEP,
                target,
                metadata={"network": False, "scratch_only": True},
            ),
            operation,
        )

    @staticmethod
    def _reconcile(bridged: Mapping[str, Any], direct: Mapping[str, Any]) -> dict[str, Any]:
        bridged_rows = bridged["result_population"]["variant_result_rows"]
        direct_rows = direct["result_population"]["variant_result_rows"]
        comparisons = {
            "trial_count": len(bridged_rows) == len(direct_rows),
            "variant_ids": [row["variant_id"] for row in bridged_rows]
            == [row["variant_id"] for row in direct_rows],
            "outcomes": [row["outcome_category"] for row in bridged_rows]
            == [row["outcome_category"] for row in direct_rows],
            "core_metrics": [row["metrics"] for row in bridged_rows]
            == [row["metrics"] for row in direct_rows],
            "status_counts": bridged["outcome_category_counts"]
            == direct["outcome_category_counts"],
            "committed_denominator": bridged["committed_denominator"]
            == direct["committed_denominator"],
            "result_identity": bridged["result_population"]["result_population_identity_hash"]
            == direct["result_population"]["result_population_identity_hash"],
        }
        return {"passed": all(comparisons.values()), "comparisons": comparisons}

    @staticmethod
    def _ledger_rows(
        *,
        run_id: str,
        runner_invocation_id: str,
        formalizer_run_id: str,
        formalizer_path: str,
        approval_scope: str,
        input_paths: Mapping[str, str],
        manifest: Mapping[str, Any],
        runner_result: Mapping[str, Any] | None,
        runner_artifact_path: str | None,
        blockers: Sequence[str],
        funding_cost_mode: str,
        timestamp_utc: str,
    ) -> list[dict[str, Any]]:
        variants = {row["variant_id"]: row for row in manifest["variant_assignments"]}
        if runner_result is None:
            source_rows = [
                {
                    "variant_id": variant_id,
                    "outcome_category": "not_attempted",
                    "non_success": {"reason": "; ".join(blockers)},
                    "metrics": None,
                    "row_identity_hash": None,
                }
                for variant_id in sorted(variants)
            ]
        else:
            source_rows = runner_result["result_population"]["variant_result_rows"]
        rows: list[dict[str, Any]] = []
        for index, runner_row in enumerate(source_rows, start=1):
            variant = variants[runner_row["variant_id"]]
            outcome = runner_row["outcome_category"]
            trial_status = RUNNER_OUTCOME_TO_TRIAL_STATUS[outcome]
            metrics = runner_row.get("metrics") if trial_status == "completed" else None
            reason = runner_row.get("non_success", {}).get("reason") or f"runner {outcome}"
            rows.append(
                {
                    "run_id": run_id,
                    "source_formalizer_run_id": formalizer_run_id,
                    "source_formalizer_artifact_path": formalizer_path,
                    "approval_scope": approval_scope,
                    "bridge_input_paths": dict(input_paths),
                    "runner_invocation_id": runner_invocation_id,
                    "strategy_family": "strat-spec-0003-sma-stddev-mean-reversion",
                    "variant_id": runner_row["variant_id"],
                    "trial_id": f"{run_id}-TRIAL-{index:03d}",
                    "trial_status": trial_status,
                    "status_reason": reason,
                    "runner_outcome_category": outcome,
                    "params": copy.deepcopy(variant["parameter_values"]),
                    "funding_cost_mode": funding_cost_mode,
                    "input_hash": _sha256(variant),
                    "output_hash": runner_row.get("row_identity_hash"),
                    "metrics_summary": metrics,
                    "runner_artifact_path": runner_artifact_path,
                    "started_at_utc": timestamp_utc,
                    "finished_at_utc": timestamp_utc,
                    "non_authority_flags": list(NON_AUTHORITY_FLAGS),
                }
            )
        return rows

    def _assert_denominator(
        self,
        rows: Sequence[Mapping[str, Any]],
        manifest: Mapping[str, Any],
        *,
        target_path: str,
    ) -> None:
        expected = {row["variant_id"] for row in manifest["variant_assignments"]}
        actual = {row.get("variant_id") for row in rows}
        if actual != expected or len(rows) != len(expected):
            self.tool_context.require_allowed(ToolAction("evidence_suppression", target_path))
            raise AssertionError("denominator suppression was unexpectedly allowed")
        if any(row.get("trial_status") not in TRIAL_STATUSES for row in rows):
            raise FormalizerRunnerBridgeError("denominator ledger contains an unsupported status")

    def run(
        self,
        *,
        formalizer_output_path: Path | str,
        approval_path: Path | str,
    ) -> dict[str, Any]:
        formalizer_path = self._repo_relative(formalizer_output_path)
        approval_relative = self._repo_relative(approval_path)
        formalizer_bytes = self._read_bytes(formalizer_path)
        formalized = json.loads(formalizer_bytes)
        self._validate_formalizer_contract(formalizer_path, formalized)
        approval_bytes = self._read_bytes(approval_relative)
        approval = json.loads(approval_bytes)
        if not isinstance(approval, dict):
            raise FormalizerRunnerBridgeError("approval marker must be a JSON object")
        self._require_approval(
            approval,
            source_run_id=formalized["run_id"],
            approval_path=approval_relative,
            formalizer_path=formalizer_path,
        )
        draft = self._validate_draft(str(formalized["draft_strategy_spec"]["path"]))
        ohlcv_path = self._repo_relative(self.config.ohlcv_input_path)
        ohlcv_hash = _sha256_bytes(self._read_bytes(ohlcv_path))

        run_identity = {
            "formalizer_hash": _sha256_bytes(formalizer_bytes),
            "approval_hash": _sha256_bytes(approval_bytes),
            "draft_hash": _sha256(draft),
            "ohlcv_hash": ohlcv_hash,
            "config": self.config.__dict__,
            "bridge_version": BRIDGE_VERSION,
        }
        run_id = hashlib.sha256(_canonical_bytes(run_identity)).hexdigest()[:16]
        run_dir = OUTPUT_ROOT / run_id
        input_paths = self._derive_inputs(
            run_id=run_id,
            run_dir=run_dir,
            formalized=formalized,
            formalizer_path=formalizer_path,
            formalizer_hash=run_identity["formalizer_hash"],
            approval_path=approval_relative,
            approval_hash=run_identity["approval_hash"],
            draft=draft,
        )
        self._validate_derived_inputs(input_paths)
        manifest = self._read_json(input_paths["variant_manifest"])
        blockers = self._availability_blockers(formalized)
        if blockers:
            record = self.tool_context.authorize(
                ToolAction("data_availability_bypass", formalizer_path)
            )
            if record.decision != "blocked":
                raise AssertionError("data-availability bypass was unexpectedly allowed")
        runner_invocation_id = hashlib.sha256(
            _canonical_bytes(
                {
                    "run_id": run_id,
                    "inputs": input_paths,
                    "seed": self.config.deterministic_seed,
                }
            )
        ).hexdigest()[:16]
        runner_result: dict[str, Any] | None = None
        reconciliation = {"passed": False, "not_run_reasons": blockers}
        runner_artifact_path = None
        if not blockers:
            runner_result = self._invoke_runner(
                run_dir=run_dir,
                input_paths=input_paths,
                ohlcv_path=ohlcv_path,
                write_result_population=True,
                invocation_name="bridged",
            )
            direct_result = self._invoke_runner(
                run_dir=run_dir,
                input_paths=input_paths,
                ohlcv_path=ohlcv_path,
                write_result_population=False,
                invocation_name="direct-manual-equivalent",
            )
            reconciliation = self._reconcile(runner_result, direct_result)
            if not reconciliation["passed"]:
                raise FormalizerRunnerBridgeError("manual runner reconciliation failed")
            runner_artifact_path = self._repo_relative(str(runner_result["output_path"]))

        ledger_rows = self._ledger_rows(
            run_id=run_id,
            runner_invocation_id=runner_invocation_id,
            formalizer_run_id=formalized["run_id"],
            formalizer_path=formalizer_path,
            approval_scope=approval["approval_scope"],
            input_paths=input_paths,
            manifest=manifest,
            runner_result=runner_result,
            runner_artifact_path=runner_artifact_path,
            blockers=blockers,
            funding_cost_mode=self.config.funding_cost_mode,
            timestamp_utc=self.config.timestamp_utc,
        )
        self._assert_denominator(
            ledger_rows,
            manifest,
            target_path=(run_dir / "denominator_ledger.json").as_posix(),
        )
        counts = Counter(row["trial_status"] for row in ledger_rows)
        count_packet = {status: counts.get(status, 0) for status in TRIAL_STATUSES}
        ledger = {
            "schema_version": "formalizer_runner_bridge_denominator_ledger_v1",
            "run_id": run_id,
            "declared_trial_count": len(ledger_rows),
            "denominator_preserved": True,
            "trial_status_counts": count_packet,
            "rows": ledger_rows,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        ledger_path = self._write_json(run_dir / "denominator_ledger.json", ledger)
        completed = [row for row in ledger_rows if row["trial_status"] == "completed"]
        review = {
            "schema_version": "formalizer_runner_bridge_human_review_packet_v1",
            "run_id": run_id,
            "source_idea_formalizer_summary": copy.deepcopy(formalized["research_object"]),
            "approval_metadata": copy.deepcopy(approval),
            "derived_input_artifact_paths": input_paths,
            "runner_invocation_metadata": {
                "runner": "tools.research_runner.run_offline_sweep",
                "runner_invocation_id": runner_invocation_id,
                "mode": "canonical_15m_fixture_offline",
                "deterministic_seed": self.config.deterministic_seed,
                "ohlcv_input_path": ohlcv_path,
                "ohlcv_input_hash": ohlcv_hash,
                "network": False,
            },
            "denominator_counts": count_packet,
            "completed_trial_count": count_packet["completed"],
            "failed_trial_count": count_packet["failed"],
            "invalid_trial_count": count_packet["invalid"],
            "pruned_trial_count": count_packet["pruned"],
            "blocked_trial_count": count_packet["blocked"],
            "manual_reconciliation_result": reconciliation,
            "top_metrics": completed[0]["metrics_summary"] if completed else None,
            "full_ledger_path": ledger_path,
            "runner_artifact_paths": [runner_artifact_path] if runner_artifact_path else [],
            "validation_status": "blocked" if blockers else "passed",
            "data_availability_blockers": blockers,
            "data_availability_warnings": [],
            "funding_mode": {
                "requested": self.config.funding_cost_mode,
                "effective": "off" if not blockers else "not_run",
                "default_off": True,
                "global_mode_mutated": False,
            },
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        review_path = self._write_json(run_dir / "human_review_packet.json", review)
        return {
            "run_id": run_id,
            "status": "blocked" if blockers else "completed",
            "trial_status_counts": count_packet,
            "manual_reconciliation_result": reconciliation,
            "artifact_paths": {
                "denominator_ledger": ledger_path,
                "human_review_packet": review_path,
                "runner_result": runner_artifact_path,
                **input_paths,
            },
            "blockers": blockers,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
