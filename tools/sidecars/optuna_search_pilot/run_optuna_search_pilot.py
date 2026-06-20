"""Run a bounded, scratch-only Optuna search pilot.

The pilot intentionally uses a toy deterministic objective and never calls the
repo canonical runner, backtester, or artifact writers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ID = "WP-PILOT-OPTUNA-SEARCH-SIDECAR-01"
TOOL_IDENTITY = "tools.sidecars.optuna_search_pilot.run_optuna_search_pilot"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DEFAULT_TRIALS = 20
DEFAULT_SEED = 1729
OBJECTIVE_DESCRIPTION = (
    "Toy deterministic objective over a bounded synthetic parameter space; "
    "no market data, canonical runner, backtester, OOS, robustness, or "
    "candidate evidence path is invoked."
)

NON_AUTHORITY_FLAGS = [
    "scratch_only",
    "non_canonical",
    "not_full_population_evidence",
    "not_oos_evidence",
    "not_robustness_evidence",
    "not_candidate_evidence",
    "not_promotion",
    "not_readiness",
    "not_paper_live",
    "requires_repo_owned_rescreen",
]

GUARDRAIL_STATEMENTS = [
    "Optuna suggestions are not winners.",
    (
        "Any suggested params must be re-screened through the repo-owned honest "
        "full-population / OOS / robustness pipeline."
    ),
    "No winner-only reporting is allowed.",
    "Pruned/failed trials remain part of search lineage.",
]

STATE_COMPLETE = "COMPLETE"
STATE_PRUNED = "PRUNED"
STATE_FAIL = "FAIL"
VALID_STATES = {STATE_COMPLETE, STATE_PRUNED, STATE_FAIL}


class OptunaSearchPilotError(RuntimeError):
    """Raised when the pilot cannot safely produce bounded scratch output."""


@dataclass(frozen=True)
class TrialExport:
    study_id: str
    trial_number: int
    state: str
    params: dict[str, Any]
    objective_value_or_null: float | None
    failure_reason_or_null: str | None
    started_at_utc: str
    completed_at_utc: str
    seed: int
    suggested_by: str
    canonical_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "study_id": self.study_id,
            "trial_number": self.trial_number,
            "state": self.state,
            "params": self.params,
            "objective_value_or_null": self.objective_value_or_null,
            "failure_reason_or_null": self.failure_reason_or_null,
            "started_at_utc": self.started_at_utc,
            "completed_at_utc": self.completed_at_utc,
            "seed": self.seed,
            "suggested_by": self.suggested_by,
            "canonical_authority": self.canonical_authority,
        }


def default_search_space() -> dict[str, Any]:
    """Return the bounded synthetic search-space declaration."""

    return {
        "schema_version": "optuna_search_space_pilot.v1",
        "package_id": PACKAGE_ID,
        "search_space_id": "OPTUNA-SEARCH-SPACE-0001",
        "objective_direction": "maximize",
        "parameters": {
            "fast_window": {"type": "int", "low": 4, "high": 24, "step": 1},
            "slow_window": {"type": "int", "low": 25, "high": 80, "step": 1},
            "entry_threshold": {"type": "float", "low": 0.1, "high": 2.0},
            "trade_direction": {"type": "categorical", "choices": ["long", "short"]},
        },
        "objective_description": OBJECTIVE_DESCRIPTION,
        "forced_state_rules": {
            "pruned": "trial_number % 11 == 3 after parameter suggestion",
            "fail": "trial_number % 13 == 5 after parameter suggestion",
            "complete": "all other trials",
        },
        "guardrails": list(GUARDRAIL_STATEMENTS),
        "non_authority_flags": list(NON_AUTHORITY_FLAGS),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, allow_nan=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _sha256_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return f"external:{path.name}"


def _source_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
    return completed.stdout.strip()


def _source_branch() -> str:
    try:
        completed = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _assert_scratch_output_dir(output_dir: Path) -> Path:
    resolved = output_dir.resolve()
    scratch_root = (REPO_ROOT / "scratch").resolve()
    if resolved != scratch_root and scratch_root not in resolved.parents:
        raise OptunaSearchPilotError(f"output-dir must remain under {scratch_root}: {resolved}")
    return resolved


def _load_optuna_optional() -> tuple[Any | None, str | None]:
    try:
        import optuna  # type: ignore[import-not-found]
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
    return optuna, None


def _trial_base_time(seed: int) -> datetime:
    return datetime(2026, 6, 20, 0, 0, 0, tzinfo=UTC) + timedelta(seconds=seed % 60)


def _trial_timestamps(seed: int, trial_number: int) -> tuple[str, str]:
    started = _trial_base_time(seed) + timedelta(seconds=trial_number * 2)
    completed = started + timedelta(seconds=1)
    return (
        started.isoformat().replace("+00:00", "Z"),
        completed.isoformat().replace("+00:00", "Z"),
    )


def _study_id(search_space: dict[str, Any], trials: int, seed: int) -> str:
    payload = {
        "search_space_hash": _sha256_payload(search_space),
        "trials": trials,
        "seed": seed,
        "package_id": PACKAGE_ID,
    }
    return "OPTUNA-PILOT-" + _sha256_payload(payload).split(":", 1)[1][:16].upper()


def _objective_value(params: dict[str, Any]) -> float:
    fast = float(params["fast_window"])
    slow = float(params["slow_window"])
    threshold = float(params["entry_threshold"])
    direction_bonus = 0.075 if params["trade_direction"] == "long" else -0.025
    center_penalty = abs(fast - 13.0) / 30.0 + abs(slow - 55.0) / 80.0
    threshold_penalty = abs(threshold - 0.9) / 3.0
    interaction = math.sin(fast / 3.0) * 0.03 + math.cos(slow / 9.0) * 0.02
    value = 1.0 + direction_bonus + interaction - center_penalty - threshold_penalty
    return round(value, 12)


def _mock_params(trial_number: int, seed: int) -> dict[str, Any]:
    search_space = default_search_space()["parameters"]
    fast = search_space["fast_window"]["low"] + (
        (seed + trial_number * 7)
        % (search_space["fast_window"]["high"] - search_space["fast_window"]["low"] + 1)
    )
    slow = search_space["slow_window"]["low"] + (
        (seed * 3 + trial_number * 11)
        % (search_space["slow_window"]["high"] - search_space["slow_window"]["low"] + 1)
    )
    threshold_span = search_space["entry_threshold"]["high"] - search_space["entry_threshold"]["low"]
    threshold = search_space["entry_threshold"]["low"] + (
        ((seed + trial_number * 17) % 1000) / 999.0
    ) * threshold_span
    direction = search_space["trade_direction"]["choices"][(seed + trial_number) % 2]
    return {
        "fast_window": int(fast),
        "slow_window": int(slow),
        "entry_threshold": round(float(threshold), 6),
        "trade_direction": direction,
    }


def _forced_state(trial_number: int) -> tuple[str, str | None]:
    if trial_number % 11 == 3:
        return STATE_PRUNED, "deterministic_prune_guardrail"
    if trial_number % 13 == 5:
        return STATE_FAIL, "deterministic_failure_guardrail"
    return STATE_COMPLETE, None


def _mock_trials(*, study_id: str, trials: int, seed: int) -> list[TrialExport]:
    rows: list[TrialExport] = []
    for trial_number in range(trials):
        params = _mock_params(trial_number, seed)
        state, reason = _forced_state(trial_number)
        started, completed = _trial_timestamps(seed, trial_number)
        rows.append(
            TrialExport(
                study_id=study_id,
                trial_number=trial_number,
                state=state,
                params=params,
                objective_value_or_null=(
                    _objective_value(params) if state == STATE_COMPLETE else None
                ),
                failure_reason_or_null=reason,
                started_at_utc=started,
                completed_at_utc=completed,
                seed=seed,
                suggested_by="deterministic_mock_sampler",
            )
        )
    return rows


def _run_optuna_trials(
    *,
    optuna: Any,
    study_id: str,
    trials: int,
    seed: int,
) -> list[TrialExport]:
    sampler = optuna.samplers.TPESampler(seed=seed)
    study = optuna.create_study(
        direction="maximize",
        sampler=sampler,
        study_name=study_id,
    )

    def objective(trial: Any) -> float:
        params = {
            "fast_window": trial.suggest_int("fast_window", 4, 24),
            "slow_window": trial.suggest_int("slow_window", 25, 80),
            "entry_threshold": trial.suggest_float("entry_threshold", 0.1, 2.0),
            "trade_direction": trial.suggest_categorical("trade_direction", ["long", "short"]),
        }
        state, reason = _forced_state(trial.number)
        if state == STATE_PRUNED:
            trial.set_user_attr("failure_reason_or_null", reason)
            raise optuna.exceptions.TrialPruned(reason)
        if state == STATE_FAIL:
            trial.set_user_attr("failure_reason_or_null", reason)
            raise ValueError(reason)
        return _objective_value(params)

    study.optimize(objective, n_trials=trials, catch=(ValueError,))
    rows: list[TrialExport] = []
    for trial in sorted(study.trials, key=lambda item: item.number):
        state = trial.state.name
        if state not in VALID_STATES:
            state = STATE_FAIL
        reason = trial.user_attrs.get("failure_reason_or_null")
        if state == STATE_FAIL and reason is None:
            reason = "optuna_trial_failed"
        started, completed = _trial_timestamps(seed, trial.number)
        rows.append(
            TrialExport(
                study_id=study_id,
                trial_number=trial.number,
                state=state,
                params=dict(trial.params),
                objective_value_or_null=(
                    float(trial.value)
                    if state == STATE_COMPLETE and trial.value is not None
                    else None
                ),
                failure_reason_or_null=reason,
                started_at_utc=started,
                completed_at_utc=completed,
                seed=seed,
                suggested_by="optuna_tpe_sampler",
            )
        )
    return rows


def _dependency_probe(optuna: Any | None, import_error: str | None) -> dict[str, Any]:
    return {
        "package_id": PACKAGE_ID,
        "dependency": "optuna",
        "available": optuna is not None,
        "version": str(getattr(optuna, "__version__", "unknown")) if optuna is not None else None,
        "import_error": import_error,
        "dependency_file_mutation": False,
        "probe_posture": "scratch_metadata_only",
    }


def _trial_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "complete_count": sum(row["state"] == STATE_COMPLETE for row in rows),
        "pruned_count": sum(row["state"] == STATE_PRUNED for row in rows),
        "fail_count": sum(row["state"] == STATE_FAIL for row in rows),
    }


def _summary(
    *,
    rows: list[dict[str, Any]],
    search_space_hash: str,
    optuna_available: bool,
) -> dict[str, Any]:
    counts = _trial_counts(rows)
    complete_rows = [row for row in rows if row["state"] == STATE_COMPLETE]
    best = max(
        complete_rows,
        key=lambda row: row["objective_value_or_null"],
    ) if complete_rows else None
    real_optuna_exercised = optuna_available and all(
        row["suggested_by"] == "optuna_tpe_sampler" for row in rows
    )
    return {
        "execution_status": (
            "COMPLETED_REAL_OPTUNA_SIDECAR_PILOT"
            if real_optuna_exercised
            else "PARTIAL_BLOCKED_OPTIONAL_DEPENDENCY_UNAVAILABLE"
        ),
        "blocked_reason_or_null": None
        if real_optuna_exercised
        else "Optuna is not importable in the execution environment.",
        "total_trials": len(rows),
        **counts,
        "search_space_hash": search_space_hash,
        "objective_description": OBJECTIVE_DESCRIPTION,
        "best_observed_trial_id_or_null": (
            f"{rows[0]['study_id']}:{best['trial_number']}" if best else None
        ),
        "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        "guardrail_statements": list(GUARDRAIL_STATEMENTS),
        "handoff_required": (
            "repo_owned_full_population_oos_robustness_rescreen_required"
        ),
        "repo_fit_assessment": (
            "Optuna can fit only as a bounded non-canonical sidecar suggester "
            "with full trial-state export and repo-owned rescreen handoff."
            if real_optuna_exercised
            else "Real Optuna behavior was not exercised; this is partial blocked evidence "
            "covering only wrapper, export, and guardrail behavior."
        ),
        "recommendation": "sidecar" if real_optuna_exercised else "preserve",
        "real_optuna_exercised": real_optuna_exercised,
    }


def _provenance(
    *,
    search_space_path: Path,
    trial_population_path: Path,
    trial_summary_path: Path,
    dependency_probe_path: Path,
    trials: int,
    seed: int,
    optuna: Any | None,
    import_error: str | None,
) -> dict[str, Any]:
    return {
        "package_id": PACKAGE_ID,
        "tool_identity": TOOL_IDENTITY,
        "source_commit": _source_commit(),
        "source_branch": _source_branch(),
        "created_at_utc": _trial_base_time(seed).isoformat().replace("+00:00", "Z"),
        "command": (
            "python -m tools.sidecars.optuna_search_pilot.run_optuna_search_pilot "
            f"--output-dir {_repo_relative(search_space_path.parent)} --trials {trials} --seed {seed}"
        ),
        "dependency": _dependency_probe(optuna, import_error),
        "artifacts": {
            "search_space": {
                "path": _repo_relative(search_space_path),
                "sha256": _sha256_file(search_space_path),
            },
            "trial_population": {
                "path": _repo_relative(trial_population_path),
                "sha256": _sha256_file(trial_population_path),
            },
            "trial_summary": {
                "path": _repo_relative(trial_summary_path),
                "sha256": _sha256_file(trial_summary_path),
            },
            "dependency_probe": {
                "path": _repo_relative(dependency_probe_path),
                "sha256": _sha256_file(dependency_probe_path),
            },
        },
        "boundary_statement": {
            "canonical_strategy_spec_vm_sweep_mutation": False,
            "canonical_result_population_write": False,
            "canonical_trial_log_write": False,
            "canonical_runner_or_backtester_invoked": False,
            "winner_selection_authority": False,
            "candidate_readiness_or_promotion_authority": False,
            "runtime_paper_live_touched": False,
            "private_credentials_used": False,
            "dependency_files_mutated": False,
        },
    }


def _markdown_report(summary: dict[str, Any], provenance: dict[str, Any]) -> str:
    lines = [
        f"# {PACKAGE_ID} Recommendation Report",
        "",
        *[f"- {statement}" for statement in GUARDRAIL_STATEMENTS],
        "",
        f"Execution status: `{summary['execution_status']}`",
        f"Recommendation: `{summary['recommendation']}`",
        f"Real Optuna exercised: `{summary['real_optuna_exercised']}`",
        f"Blocked reason: `{summary['blocked_reason_or_null']}`",
        f"Total trials: `{summary['total_trials']}`",
        f"Complete / pruned / fail: `{summary['complete_count']} / {summary['pruned_count']} / {summary['fail_count']}`",
        f"Best observed trial: `{summary['best_observed_trial_id_or_null']}`",
        "",
        "## Non-Authority",
        "",
        *[f"- `{flag}`" for flag in NON_AUTHORITY_FLAGS],
        "",
        "## Repo Fit",
        "",
        summary["repo_fit_assessment"],
        "",
        "## Dependency",
        "",
        f"- Optuna available: `{provenance['dependency']['available']}`",
        f"- Optuna version: `{provenance['dependency']['version']}`",
        f"- Import error: `{provenance['dependency']['import_error']}`",
        "",
        "## Boundary",
        "",
    ]
    lines.extend(
        f"- {key}: `{value}`" for key, value in provenance["boundary_statement"].items()
    )
    lines.append("")
    return "\n".join(lines)


def _readme() -> str:
    return (
        f"# {PACKAGE_ID}\n\n"
        "Scratch-only Optuna sidecar pilot outputs. These files are not canonical "
        "evidence and have no winner-selection, candidate, readiness, promotion, "
        "paper/live, or runtime authority.\n\n"
        + "\n".join(f"- {statement}" for statement in GUARDRAIL_STATEMENTS)
        + "\n"
    )


def _requirements_poc() -> str:
    return (
        "# Scratch-only proof-of-concept dependency note.\n"
        "# Do not add this to repo dependency files without a later approved package.\n"
        "optuna\n"
    )


def build_payloads(*, trials: int, seed: int) -> dict[str, Any]:
    if trials <= 0:
        raise OptunaSearchPilotError(f"trials must be positive, got {trials}")
    search_space = default_search_space()
    study_id = _study_id(search_space, trials, seed)
    optuna, import_error = _load_optuna_optional()
    exports = (
        _run_optuna_trials(optuna=optuna, study_id=study_id, trials=trials, seed=seed)
        if optuna is not None
        else _mock_trials(study_id=study_id, trials=trials, seed=seed)
    )
    rows = [export.to_dict() for export in exports]
    search_space_hash = _sha256_payload(search_space)
    summary = _summary(
        rows=rows,
        search_space_hash=search_space_hash,
        optuna_available=optuna is not None,
    )
    summary["trial_population_hash"] = _sha256_payload(rows)
    summary["dependency"] = _dependency_probe(optuna, import_error)
    summary["output_checksum"] = _sha256_payload(summary)
    return {
        "search_space": search_space,
        "trial_rows": rows,
        "summary": summary,
        "dependency_probe": _dependency_probe(optuna, import_error),
        "optuna": optuna,
        "import_error": import_error,
    }


def run_pilot(*, output_dir: Path = DEFAULT_OUTPUT_DIR, trials: int = DEFAULT_TRIALS, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    output_dir = _assert_scratch_output_dir(output_dir)
    payloads = build_payloads(trials=trials, seed=seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    search_space_path = output_dir / "search_space.json"
    trial_population_path = output_dir / "trial_population.jsonl"
    trial_summary_path = output_dir / "trial_summary.json"
    dependency_probe_path = output_dir / "dependency_probe.json"

    (output_dir / "README.md").write_text(_readme(), encoding="utf-8")
    _write_json(search_space_path, payloads["search_space"])
    _write_jsonl(trial_population_path, payloads["trial_rows"])
    _write_json(trial_summary_path, payloads["summary"])
    _write_json(dependency_probe_path, payloads["dependency_probe"])
    (output_dir / "requirements.poc.txt").write_text(_requirements_poc(), encoding="utf-8")

    provenance = _provenance(
        search_space_path=search_space_path,
        trial_population_path=trial_population_path,
        trial_summary_path=trial_summary_path,
        dependency_probe_path=dependency_probe_path,
        trials=trials,
        seed=seed,
        optuna=payloads["optuna"],
        import_error=payloads["import_error"],
    )
    _write_json(output_dir / "provenance.json", provenance)
    (output_dir / "recommendation_report.md").write_text(
        _markdown_report(payloads["summary"], provenance),
        encoding="utf-8",
    )
    return payloads["summary"]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        summary = run_pilot(output_dir=args.output_dir, trials=args.trials, seed=args.seed)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "package_id": PACKAGE_ID,
                "execution_status": summary["execution_status"],
                "recommendation": summary["recommendation"],
                "real_optuna_exercised": summary["real_optuna_exercised"],
                "total_trials": summary["total_trials"],
                "complete_count": summary["complete_count"],
                "pruned_count": summary["pruned_count"],
                "fail_count": summary["fail_count"],
                "output_checksum": summary["output_checksum"],
                "output_dir": _repo_relative(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
