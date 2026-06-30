"""Generate the WP-LAB factory-test synthetic population artifacts.

This helper is deliberately fixture-only: it reads the PR #583/#584/#585
contracts, writes only the package scratch directory, and never imports or
calls the research runner, backtester, candidate lifecycle writer, or any
runtime surface.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


PACKAGE = "WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01"
DEFAULT_ROWS = 600
BASELINE_ID = "known_losing_baseline"
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRATCH_DIR = REPO_ROOT / "scratch" / PACKAGE

PREREQUISITES = {
    "PR #583 artifacts": [
        Path("docs/status_entries/WP-LAB-BASELINE-PAYLOAD-DEFINE-01.md"),
        Path("scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json"),
    ],
    "PR #584 artifacts": [
        Path("docs/status_entries/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01.md"),
        Path(
            "scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/"
            "baseline_gate_expectations.json"
        ),
    ],
    "PR #585 artifacts": [
        Path("docs/status_entries/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01.md"),
        Path("scratch/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01/guard_contract.json"),
    ],
    "PR #586 artifacts": [
        Path("docs/status_entries/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01.md"),
        Path("scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/baseline_loop_result.json"),
    ],
    "PR #587 artifacts": [
        Path("docs/status_entries/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01.md"),
        Path("scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/held_boundary_map.json"),
        Path("docs/research/LAB_COMPLETION_MAP.md"),
    ],
}

STATUS_CYCLE = (
    "completed",
    "completed",
    "completed",
    "completed",
    "completed",
    "failed",
    "failed",
    "invalid",
    "blocked",
    "insufficient",
    "withheld",
    "completed",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _git_head(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def _presence(repo_root: Path) -> dict[str, bool]:
    return {
        label: all((repo_root / path).exists() for path in paths)
        for label, paths in PREREQUISITES.items()
    }


def _select_baseline(catalog: dict[str, Any]) -> dict[str, Any]:
    for baseline in catalog["baselines"]:
        if baseline["baseline_id"] == BASELINE_ID:
            return baseline
    raise ValueError(f"{BASELINE_ID} is missing from baseline payload catalog")


def _gate_for_baseline(gates: dict[str, Any]) -> dict[str, Any]:
    for baseline in gates["baselines"]:
        if baseline["baseline_id"] == BASELINE_ID:
            return baseline
    raise ValueError(f"{BASELINE_ID} is missing from baseline gate expectations")


def build_rows(row_count: int, baseline: dict[str, Any], gates: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index in range(row_count):
        ordinal = index + 1
        status = STATUS_CYCLE[index % len(STATUS_CYCLE)]
        favorable = index % 17 == 0
        parameter_scale = 1 + (index % 20)
        fast_window = 3 + (index % 9)
        slow_window = 12 + (index % 23)
        if status == "invalid":
            fast_window = slow_window

        if status == "completed":
            wfo_status = "fail_or_insufficient"
        elif status == "failed":
            wfo_status = "fail"
        elif status == "invalid":
            wfo_status = "blocked_invalid"
        elif status == "blocked":
            wfo_status = "blocked"
        else:
            wfo_status = status

        rows.append(
            {
                "row_id": f"SYN-{ordinal:04d}",
                "baseline_id": baseline["baseline_id"],
                "variant_id": f"{baseline['baseline_id']}-synthetic-{ordinal:04d}",
                "synthetic_parameters": {
                    "fast_window": fast_window,
                    "slow_window": slow_window,
                    "churn_multiplier": round(0.25 * parameter_scale, 4),
                    "synthetic_metric_bias": "favorable" if favorable else "unfavorable",
                },
                "construction_payload": True,
                "non_promotable": True,
                "candidate_eligible": False,
                "promotion_eligible": False,
                "paper_live_eligible": False,
                "canonical_crossing_allowed": False,
                "edge_claim_allowed": False,
                "synthetic_fixture_only": True,
                "status": status,
                "numerically_favorable": favorable,
                "synthetic_metrics": {
                    "synthetic_score": 1.25 if favorable else -0.75,
                    "synthetic_sharpe_like": 1.8 if favorable else -0.4,
                    "synthetic_drawdown_pct": 8.0 if favorable else 42.0,
                    "metric_authority": "none_fixture_only",
                },
                "gate_expectation": {
                    "baseline_expected_gate_result": baseline["expected_gate_result"],
                    "wfo_oos_gate_expected": gates["wfo_oos_gate_expected"],
                    "robustness_mc_gate_expected": gates["robustness_mc_gate_expected"],
                    "statistical_diagnostics_gate_expected": gates[
                        "statistical_diagnostics_gate_expected"
                    ],
                    "candidate_eligibility_expected": gates["candidate_eligibility_expected"],
                    "numeric_override_allowed": False,
                    "retuning_allowed": False,
                },
                "wfo_oos_status": wfo_status,
                "robustness_mc_status": "synthetic_status_fixture_not_run",
                "anti_overfit_status": "synthetic_status_fixture_not_run",
                "denominator_accounting_status": "retained",
                "candidate_review_expected": "no_candidate",
                "crossing_expected": "reject_by_construction",
            }
        )
    return rows


def _summaries(rows: list[dict[str, Any]], row_count: int, baseline_id: str) -> dict[str, dict[str, Any]]:
    status_counts = Counter(row["status"] for row in rows)
    favorable_count = sum(1 for row in rows if row["numerically_favorable"])
    denominator = {
        "package": PACKAGE,
        "baseline_id": baseline_id,
        "row_count_planned": row_count,
        "row_count_materialized": len(rows),
        "all_rows_accounted": row_count == len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "failed_invalid_blocked_insufficient_withheld_retained": all(
            status_counts[status] > 0
            for status in ("failed", "invalid", "blocked", "insufficient", "withheld")
        ),
        "no_winner_only_pruning": len(rows) == sum(status_counts.values()),
        "denominator_accounting_status": "preserved",
    }
    gates = {
        "package": PACKAGE,
        "baseline_id": baseline_id,
        "row_count": len(rows),
        "gate_outcome_basis": "synthetic_fixture_statuses_only",
        "real_wfo_oos_run": False,
        "real_robustness_mc_run": False,
        "real_anti_overfit_run": False,
        "numeric_override_allowed": False,
        "status_counts": dict(sorted(status_counts.items())),
        "favorable_numeric_rows": favorable_count,
        "favorable_numeric_rows_candidate_eligible": False,
        "all_rows_crossing_expected": "reject_by_construction",
    }
    assertions = {
        "package": PACKAGE,
        "baseline_id": baseline_id,
        "row_count": len(rows),
        "construction_payload_all_rows": all(row["construction_payload"] for row in rows),
        "non_promotable_all_rows": all(row["non_promotable"] for row in rows),
        "candidate_eligible_any": any(row["candidate_eligible"] for row in rows),
        "promotion_eligible_any": any(row["promotion_eligible"] for row in rows),
        "paper_live_eligible_any": any(row["paper_live_eligible"] for row in rows),
        "canonical_crossing_allowed_any": any(row["canonical_crossing_allowed"] for row in rows),
        "edge_claim_allowed_any": any(row["edge_claim_allowed"] for row in rows),
        "synthetic_fixture_only_all_rows": all(row["synthetic_fixture_only"] for row in rows),
        "all_rows_no_candidate_expected": all(
            row["candidate_review_expected"] == "no_candidate" for row in rows
        ),
        "all_rows_reject_by_construction_expected": all(
            row["crossing_expected"] == "reject_by_construction" for row in rows
        ),
        "favorable_numeric_rows": favorable_count,
        "favorable_numeric_rows_candidate_eligible": False,
        "candidate_registry_written": False,
        "canonical_result_population_written": False,
        "real_strategy_execution": False,
        "edge_search_authorized_here": False,
    }
    result = {
        "package": PACKAGE,
        "status": "completed",
        "fixture_only": True,
        "strategy_family_count": 1,
        "baseline_id": baseline_id,
        "row_count_planned": row_count,
        "row_count_materialized": len(rows),
        "all_rows_accounted": row_count == len(rows),
        "failed_rows_preserved": status_counts["failed"] > 0,
        "invalid_rows_preserved": status_counts["invalid"] > 0,
        "blocked_rows_preserved": status_counts["blocked"] > 0,
        "insufficient_or_withheld_rows_preserved": (
            status_counts["insufficient"] > 0 and status_counts["withheld"] > 0
        ),
        "favorable_numeric_rows_candidate_eligible": False,
        "construction_payload": True,
        "non_promotable": True,
        "candidate_registry_written": False,
        "canonical_result_population_written": False,
        "real_strategy_execution": False,
        "edge_search_authorized_here": False,
        "crossing_expected": "reject_by_construction",
        "lab_declared_finished": False,
        "status_counts": dict(sorted(status_counts.items())),
        "favorable_numeric_rows": favorable_count,
    }
    return {
        "denominator": denominator,
        "gates": gates,
        "assertions": assertions,
        "result": result,
    }


def _manifest_markdown(rows: list[dict[str, Any]], summaries: dict[str, dict[str, Any]]) -> str:
    status_counts = summaries["denominator"]["status_counts"]
    return f"""# {PACKAGE} Synthetic Population Manifest

This is a fixture-only lab factory test. It is not market evidence, not a
backtest, not a sweep, not edge-search, not a candidate, and not a trading
recommendation.

## Population

- baseline_id: `{BASELINE_ID}`
- strategy_family_count: 1
- row_count_planned: {summaries["result"]["row_count_planned"]}
- row_count_materialized: {len(rows)}
- favorable_numeric_rows: {summaries["result"]["favorable_numeric_rows"]}

## Status Buckets

| Status | Rows |
| --- | ---: |
{chr(10).join(f"| {status} | {count} |" for status, count in status_counts.items())}

## Boundary

Every row has `construction_payload=true`, `non_promotable=true`,
`candidate_eligible=false`, `promotion_eligible=false`,
`paper_live_eligible=false`, `canonical_crossing_allowed=false`,
`edge_claim_allowed=false`, and `crossing_expected=reject_by_construction`.
Numerically favorable synthetic rows remain candidate-ineligible by
construction.
"""


def _repo_truth_markdown(
    *,
    base_commit: str,
    presence: dict[str, bool],
    row_count: int,
) -> str:
    presence_lines = "\n".join(f"- {label}: {value}" for label, value in presence.items())
    return f"""# {PACKAGE} Repo Truth Discovery

## Base

- base commit: `{base_commit}`
- pre-existing untracked worktree noise observed before package work: `build/`

## Prerequisite Artifacts

{presence_lines}

## Existing Helper Surfaces

- `tools/lab_state/**`: read-only coordinator state model and resolver.
- `tools/lab_dashboard/**`: read-only dashboard projection.
- `tools/lab_reporting/**`: read-only operator report shaping.
- `tools/candidate_lifecycle/canonical_crossing_build.py`: existing crossing
  guard surface, inspected but not called by this package.
- `tools/registry/**`: existing validators, used only through validation
  commands.
- `tools/dev/diff_scope_summary.py`: diff-scope validation utility.

## External Adoption Runway

- workflow-gen: repo has `tools/external_pilots/workflow_hyperopt_pilot.py` and
  historical scratch outputs; not used here.
- vectorbt: repo has non-canonical sidecar surfaces; not used here.
- robustness MC: repo has advisory robustness helpers, but this package runs no
  MC and uses synthetic status fixtures only.
- analytics metrics: repo has advisory analytics helpers; not used here.
- CCXT: repo has public-data adapter surfaces; not used here.
- Nautilus: repo has a mapping spike surface; not used here.

## Selected Route

Decision: create a package-local fixture generator under
`tools/lab_factorytest/**` plus focused tests, then materialize {row_count}
scratch-only rows under `scratch/{PACKAGE}/`.

The selected baseline is `{BASELINE_ID}`, from the PR #583 payload catalog.
This package uses exactly one non-promotable baseline family and performs no
edge-search.

## Files Intentionally Left Unchanged

- `research/candidate_registry.jsonl`
- `research/result_populations/**`
- `tools/research_runner/**`
- `lib/**`
- `configs/**`
- `data/**`
- paper/live/runtime, OMS, risk, reconciliation, broker, exchange, and order
  paths
"""


def _external_runway_markdown() -> str:
    return f"""# {PACKAGE} External Runway Usage

No external adoption runway tool was invoked.

| Surface | Repo truth | Used here |
| --- | --- | --- |
| workflow-gen | Historical/non-authoritative pilot surfaces exist. | No; future integration only. |
| vectorbt | Non-canonical sidecar surfaces exist. | No; no import or computation. |
| robustness MC | Advisory helpers exist. | No; synthetic gate statuses only. |
| analytics metrics | Advisory metrics helpers exist. | No; dashboard/reporting metric work deferred. |
| CCXT | Public-data adapter surfaces exist. | No use in this package. |
| Nautilus | Mapping spike surface exists. | No use in this package. |
"""


def _validation_summary_text(row_count: int, summaries: dict[str, dict[str, Any]]) -> str:
    return f"""package={PACKAGE}
status=completed
fixture_only=true
baseline_id={BASELINE_ID}
row_count_planned={row_count}
row_count_materialized={summaries["result"]["row_count_materialized"]}
all_rows_accounted={str(summaries["result"]["all_rows_accounted"]).lower()}
status_counts={json.dumps(summaries["result"]["status_counts"], sort_keys=True)}
favorable_numeric_rows={summaries["result"]["favorable_numeric_rows"]}
candidate_registry_written=false
canonical_result_population_written=false
real_strategy_execution=false
edge_search_authorized_here=false
crossing_expected=reject_by_construction
"""


def generate(*, repo_root: Path = REPO_ROOT, scratch_dir: Path = SCRATCH_DIR, row_count: int = DEFAULT_ROWS) -> dict[str, Any]:
    if row_count < 500:
        raise ValueError("row_count must be at least 500")

    presence = _presence(repo_root)
    missing = [label for label, is_present in presence.items() if not is_present]
    if missing:
        raise FileNotFoundError(f"missing prerequisite groups: {', '.join(missing)}")

    catalog = _read_json(repo_root / "scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json")
    gate_catalog = _read_json(
        repo_root
        / "scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/baseline_gate_expectations.json"
    )
    baseline = _select_baseline(catalog)
    gate = _gate_for_baseline(gate_catalog)
    rows = build_rows(row_count, baseline, gate)
    summaries = _summaries(rows, row_count, baseline["baseline_id"])

    scratch_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "package": PACKAGE,
        "fixture_only": True,
        "strategy_family_count": 1,
        "baseline": baseline,
        "row_count_planned": row_count,
        "row_count_materialized": len(rows),
        "rows": rows,
    }
    _write_json(scratch_dir / "synthetic_population_manifest.json", manifest)
    _write_text(scratch_dir / "synthetic_population_manifest.md", _manifest_markdown(rows, summaries))
    _write_json(scratch_dir / "denominator_accounting.json", summaries["denominator"])
    _write_json(scratch_dir / "gate_outcome_summary.json", summaries["gates"])
    _write_json(scratch_dir / "non_promotable_assertions.json", summaries["assertions"])
    _write_json(scratch_dir / "factorytest_result.json", summaries["result"])
    _write_text(
        scratch_dir / "repo_truth_discovery.md",
        _repo_truth_markdown(
            base_commit=_git_head(repo_root),
            presence=presence,
            row_count=row_count,
        ),
    )
    _write_text(scratch_dir / "external_runway_usage.md", _external_runway_markdown())
    _write_text(scratch_dir / "validation_summary.txt", _validation_summary_text(row_count, summaries))
    return summaries["result"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--scratch-dir", type=Path, default=SCRATCH_DIR)
    args = parser.parse_args()
    result = generate(repo_root=args.repo_root, scratch_dir=args.scratch_dir, row_count=args.rows)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

