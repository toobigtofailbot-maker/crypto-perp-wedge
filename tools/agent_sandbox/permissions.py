"""Closed-default role, capability, and path policy for bounded research agents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


POLICY_ID = "bounded-research-agent-v1"

READ_DOCS = "read_repo_docs"
READ_NON_SECRET = "read_non_secret_files"
WRITE_SCRATCH = "write_scratch"
RUN_READ_ONLY_VALIDATION = "run_read_only_validation"
RUN_SCRATCH_TOOL = "run_scratch_tool"
RUN_NONCANONICAL_EXPERIMENT = "noncanonical_experiment_run"
RUN_NONCANONICAL_OFFLINE_SWEEP = "noncanonical_offline_sweep_run"
RUN_SCRATCH_ROBUSTNESS_DIAGNOSTIC = "run_scratch_robustness_diagnostic"


ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "research_scout": frozenset({READ_DOCS, READ_NON_SECRET}),
    "idea_formalizer": frozenset(
        {READ_DOCS, READ_NON_SECRET, WRITE_SCRATCH, RUN_READ_ONLY_VALIDATION}
    ),
    "draft_generator": frozenset({READ_DOCS, READ_NON_SECRET, WRITE_SCRATCH}),
    "non_canonical_runner": frozenset(
        {
            READ_DOCS,
            READ_NON_SECRET,
            WRITE_SCRATCH,
            RUN_READ_ONLY_VALIDATION,
            RUN_SCRATCH_TOOL,
        }
    ),
    "experiment_runner": frozenset(
        {
            READ_NON_SECRET,
            WRITE_SCRATCH,
            RUN_NONCANONICAL_EXPERIMENT,
        }
    ),
    "formalizer_runner_bridge": frozenset(
        {
            READ_NON_SECRET,
            WRITE_SCRATCH,
            RUN_READ_ONLY_VALIDATION,
            RUN_NONCANONICAL_OFFLINE_SWEEP,
        }
    ),
    "robustness_diagnostician": frozenset(
        {
            READ_DOCS,
            READ_NON_SECRET,
            WRITE_SCRATCH,
            RUN_READ_ONLY_VALIDATION,
            RUN_SCRATCH_ROBUSTNESS_DIAGNOSTIC,
        }
    ),
    "candidate_review_packet_preparer": frozenset(
        {READ_DOCS, READ_NON_SECRET, WRITE_SCRATCH}
    ),
    "notification_assistant": frozenset({READ_DOCS, WRITE_SCRATCH}),
}
SUPPORTED_ROLES = frozenset(ROLE_PERMISSIONS)


HARD_BLOCKED_ACTIONS = frozenset(
    {
        "canonical_write",
        "candidate_registration",
        "candidate_promotion",
        "candidate_readiness",
        "candidate_freeze",
        "candidate_lifecycle_transition",
        "trial_log_mutation",
        "overlay_control",
        "execution_control",
        "runtime_control",
        "paper_control",
        "live_control",
        "oms_access",
        "risk_control",
        "reconciliation_control",
        "safe_mode_control",
        "kill_switch_control",
        "broker_access",
        "exchange_access",
        "order_access",
        "capital_access",
        "credential_access",
        "private_endpoint_access",
        "dependency_mutation",
        "project_status_mutation",
        "network_access",
        "backtest_execution",
        "sweep_execution",
        "funding_mode_mutation",
        "evidence_suppression",
        "evidence_deletion",
        "toolcontext_bypass",
        "provider_memory_as_truth",
        "gate_bypass",
        "approval_gate_bypass",
        "data_availability_bypass",
        "fabricated_per_trade_data",
    }
)

PROTECTED_PREFIXES = (
    "runtime/",
    "src/runtime/",
    "paper/",
    "src/paper/",
    "live/",
    "src/live/",
    "oms/",
    "src/oms/",
    "risk/",
    "src/risk/",
    "reconciliation/",
    "src/reconciliation/",
    "safe_mode/",
    "src/safe_mode/",
    "kill_switch/",
    "src/kill_switch/",
    "broker/",
    "src/broker/",
    "exchange/",
    "src/exchange/",
    "orders/",
    "src/orders/",
    "capital/",
    "src/capital/",
    "secrets/",
)

CANONICAL_WRITE_PREFIXES = (
    "research/strategy_specs/",
    "research/variant_manifests/",
    "research/sweep_plans/",
    "research/result_populations/",
    "research/walkforward_runs/",
)

CANONICAL_WRITE_PATHS = frozenset(
    {
        "research/trial_log.jsonl",
        "research/candidate_registry.jsonl",
        "docs/project_status.md",
    }
)

DEPENDENCY_PATHS = frozenset(
    {
        "pyproject.toml",
        "requirements.txt",
        "requirements.lock.txt",
        "poetry.lock",
        "pipfile",
        "pipfile.lock",
        "environment.yml",
        "environment.yaml",
        "setup.py",
        "setup.cfg",
    }
)

DOC_READ_PREFIXES = ("docs/architecture/", "docs/status_entries/", "docs/research_pipeline/")
NON_SECRET_READ_PREFIXES = ("research/", "tests/fixtures/")
VALIDATION_TARGET_PREFIXES = ("tools/registry/", "tools/dev/")
SCRATCH_TOOL_PREFIXES = (
    "tools/research_workflow/",
    "tools/walkforward/",
    "tools/robustness/",
    "tools/candidate_lifecycle/",
)


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


def _matches_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def _is_sensitive_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return any(
        part in {".env", "credentials", "credential", "private", "secrets", "secret"}
        or part.endswith((".key", ".pem", ".p12"))
        for part in parts
    )


def decide(role: str, wp_id: str, action_type: str, target_path: str) -> PolicyDecision:
    """Return a deterministic closed-default decision for one normalized action."""

    if action_type in HARD_BLOCKED_ACTIONS:
        return PolicyDecision(False, f"hard prohibition: action_type={action_type}")

    if _is_sensitive_path(target_path):
        return PolicyDecision(False, "hard prohibition: credential/private path")

    if _matches_prefix(target_path, PROTECTED_PREFIXES):
        return PolicyDecision(False, f"hard prohibition: protected path={target_path}")

    is_write = action_type == WRITE_SCRATCH
    if is_write and (
        target_path in CANONICAL_WRITE_PATHS
        or _matches_prefix(target_path, CANONICAL_WRITE_PREFIXES)
    ):
        return PolicyDecision(False, f"hard prohibition: canonical write path={target_path}")

    if is_write and target_path in DEPENDENCY_PATHS:
        return PolicyDecision(False, f"hard prohibition: dependency path={target_path}")

    allowed_actions = ROLE_PERMISSIONS.get(role)
    if allowed_actions is None:
        return PolicyDecision(False, f"unknown role={role}")
    if action_type not in allowed_actions:
        return PolicyDecision(False, f"role={role} does not allow action_type={action_type}")

    if action_type == READ_DOCS and not _matches_prefix(target_path, DOC_READ_PREFIXES):
        return PolicyDecision(False, "path is outside the documentation read allowlist")
    if (
        action_type == READ_NON_SECRET
        and not _matches_prefix(target_path, NON_SECRET_READ_PREFIXES)
        and not (
            role in {"idea_formalizer", "experiment_runner", "formalizer_runner_bridge"}
            and target_path.startswith(f"scratch/{wp_id.casefold()}/")
        )
        and not (
            role in {"experiment_runner", "formalizer_runner_bridge"}
            and target_path.startswith("scratch/wp-agent-idea-formalizer-01/")
        )
        and not (
            role == "robustness_diagnostician"
            and (
                target_path.startswith(f"scratch/{wp_id.casefold()}/")
                or target_path.startswith(
                    "scratch/wp-agent-formalizer-runner-bridge-01/outputs/"
                )
            )
        )
    ):
        return PolicyDecision(False, "path is outside the non-sensitive read allowlist")
    if action_type == WRITE_SCRATCH:
        allowed_prefix = f"scratch/{wp_id.casefold()}/"
        if not target_path.startswith(allowed_prefix):
            return PolicyDecision(False, f"write is outside active scratch prefix={allowed_prefix}")
    if action_type == RUN_READ_ONLY_VALIDATION and not _matches_prefix(
        target_path, VALIDATION_TARGET_PREFIXES
    ):
        return PolicyDecision(False, "target is outside the read-only validation allowlist")
    if action_type == RUN_SCRATCH_TOOL and not _matches_prefix(
        target_path, SCRATCH_TOOL_PREFIXES
    ):
        return PolicyDecision(False, "target is outside the scratch-tool allowlist")
    if action_type == RUN_NONCANONICAL_EXPERIMENT:
        allowed_prefix = f"scratch/{wp_id.casefold()}/outputs/"
        if not target_path.startswith(allowed_prefix):
            return PolicyDecision(
                False,
                f"non-canonical experiment target is outside active outputs prefix={allowed_prefix}",
            )
    if action_type == RUN_NONCANONICAL_OFFLINE_SWEEP:
        allowed_prefix = f"scratch/{wp_id.casefold()}/outputs/"
        if not target_path.startswith(allowed_prefix):
            return PolicyDecision(
                False,
                f"non-canonical offline sweep target is outside active outputs prefix={allowed_prefix}",
            )
    if action_type == RUN_SCRATCH_ROBUSTNESS_DIAGNOSTIC:
        allowed_prefix = f"scratch/{wp_id.casefold()}/outputs/"
        if not target_path.startswith(allowed_prefix):
            return PolicyDecision(
                False,
                f"scratch robustness target is outside active outputs prefix={allowed_prefix}",
            )

    return PolicyDecision(True, f"allowed by role={role} under policy={POLICY_ID}")
