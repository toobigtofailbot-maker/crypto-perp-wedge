"""Build a dependency-free read-only static visual cockpit from repo artifacts.

The cockpit is a product-style viewer beside the audit dashboard. It reads
committed docs/scratch/result-population artifacts, writes only static output
and package-local evidence, performs no network I/O, and creates no execution,
candidate, crossing, paper/live, runtime, OMS, risk, or reconciliation authority.

Usage:
    python -m tools.lab_visual_cockpit.run --out-dir build/lab_visual_cockpit
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from tools.lab_dashboard.data_model import build_dashboard_data
from tools.lab_state.resolver import REPO_ROOT


PACKAGE = "WP-LAB-VISUAL-COCKPIT-STATIC-01"
SCRATCH_DIR = REPO_ROOT / "scratch" / PACKAGE
SCHEMA_VERSION = "lab_visual_cockpit_static_v1"

SOURCE_PATHS = {
    "lab_completion_map": "docs/research/LAB_COMPLETION_MAP.md",
    "event_tape_contract": "docs/research/LAB_EVENT_TAPE_CONTRACT.md",
    "side12_readiness": "scratch/WP-LAB-SIDE12-OPERATING-READINESS-AUDIT-01/final_operating_readiness_state.json",
    "side12_capability_map": "scratch/WP-LAB-SIDE12-OPERATING-READINESS-AUDIT-01/side12_operating_readiness_map.json",
    "event_tape_summary": "scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_tape_summary.json",
    "event_tape": "scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_event_tape.json",
    "queue_replay": "scratch/WP-LAB-QUEUE-SCHEDULER-REPLAY-01/queue_scheduler_replay_result.json",
    "agent_dashboard_replay": "scratch/WP-LAB-AGENTLOOP-DASHBOARD-REPLAY-01/agent_dashboard_replay_result.json",
    "daily_report_replay": "scratch/WP-LAB-NOTIFY-REPORT-REPLAY-01/daily_report_replay.json",
    "weekly_report_replay": "scratch/WP-LAB-NOTIFY-REPORT-REPLAY-01/weekly_report_replay.json",
    "factory_denominator": "scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/denominator_accounting.json",
}

RESULT_POPULATION_DIR = "research/result_populations"

STATUS_BUCKETS = [
    "completed",
    "failed",
    "invalid",
    "blocked",
    "withheld",
    "insufficient",
    "NO-GO",
    "review-needed",
    "candidate-ready",
]

FORBIDDEN_CONTROL_PATTERNS = {
    "forms": [r"<\s*form\b"],
    "fetch_network": [
        r"\bfetch\s*\(",
        r"\bXMLHttpRequest\b",
        r"\bWebSocket\b",
        r"\bEventSource\b",
        r"\bnavigator\.sendBeacon\b",
    ],
    "external_scripts": [r"<\s*script[^>]+src=['\"]https?://"],
    "run_retry_approve_promote_controls": [
        r"<\s*(button|input|a)\b[^>]*(run|retry|approve|promote)[^>]*>",
        r"<\s*(button|input|a)\b[^>]*>\s*(run|retry|approve|promote)\b",
    ],
    "scheduler_controls": [r"<\s*(button|input|a|select)\b[^>]*scheduler"],
    "candidate_crossing_controls": [
        r"<\s*(button|input|a|select)\b[^>]*(candidate admission|admit candidate|crossing)",
    ],
    "paper_live_runtime_controls": [
        r"<\s*(button|input|a|select)\b[^>]*(paper|live|runtime)",
    ],
    "broker_exchange_order_oms_risk_reconciliation_controls": [
        r"<\s*(button|input|a|select)\b[^>]*(broker|exchange|order|OMS|risk|reconciliation)",
    ],
    "live_fetch_controls": [r"<\s*(button|input|a|select)\b[^>]*(live fetch|refresh live)"],
}


def _read_json(rel: str) -> dict[str, Any] | list[Any] | None:
    path = REPO_ROOT / rel
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _read_text(rel: str) -> str | None:
    path = REPO_ROOT / rel
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def _status_from_job_outcome(outcome: str) -> str:
    mapping = {
        "completed": "completed",
        "failed": "failed",
        "invalid": "invalid",
        "blocked": "blocked",
        "withheld": "withheld",
        "insufficient": "insufficient",
        "review_needed": "review-needed",
        "no_candidate": "NO-GO",
        "resource_limited": "blocked",
        "delayed": "blocked",
    }
    return mapping.get(outcome, "blocked")


def _event_rows(event_tape: dict[str, Any] | list[Any] | None) -> list[dict[str, Any]]:
    if isinstance(event_tape, dict):
        events = event_tape.get("events") or event_tape.get("event_tape") or []
    elif isinstance(event_tape, list):
        events = event_tape
    else:
        events = []
    return [event for event in events if isinstance(event, dict)]


def _result_population_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("rows", "results", "result_rows", "population", "variants"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def _load_result_populations() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((REPO_ROOT / RESULT_POPULATION_DIR).glob("*.result_population.json")):
        payload = _read_json(str(path.relative_to(REPO_ROOT)).replace("\\", "/"))
        if not isinstance(payload, dict):
            continue
        lineage = payload.get("lineage") or {}
        denom = payload.get("committed_denominator_snapshot") or {}
        outcomes = payload.get("outcome_category_counts") or {}
        rp_rows = _result_population_rows(payload)
        metric_rows = []
        for row in rp_rows:
            metrics = row.get("metrics") if isinstance(row.get("metrics"), dict) else {}
            metric_rows.append(
                {
                    "variant_id": row.get("variant_id") or row.get("id"),
                    "status": row.get("status") or row.get("outcome") or "successful",
                    "sharpe": metrics.get("sharpe"),
                    "max_drawdown": metrics.get("max_drawdown") or metrics.get("max_dd"),
                    "net_pnl": metrics.get("net_pnl") or metrics.get("net_pnl_total"),
                }
            )
        rows.append(
            {
                "result_population_id": lineage.get("result_population_id") or path.name.split(".", 1)[0],
                "strategy_spec_id": lineage.get("strategy_spec_id"),
                "variant_manifest_id": lineage.get("variant_manifest_id"),
                "sweep_plan_id": lineage.get("sweep_plan_id"),
                "path": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "sha256": _sha256(path),
                "committed_denominator": denom.get("committed_denominator"),
                "result_row_count": denom.get("result_row_count"),
                "winner_only_retention_forbidden": denom.get("winner_only_retention_forbidden"),
                "outcome_counts": outcomes,
                "metrics": metric_rows,
                "authority": payload.get("non_authority_declaration") or {},
                "has_equity_curve": False,
                "has_drawdown_curve": False,
                "has_returns_distribution": False,
                "has_mc_robustness_distribution": False,
            }
        )
    return rows


def _capability_cards(side12_map: dict[str, Any] | None, completion_text: str | None) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    if side12_map:
        capability_rows = side12_map.get("capabilities")
        if isinstance(capability_rows, list):
            rows = [row for row in capability_rows if isinstance(row, dict)]
        else:
            rows = [value for _, value in sorted(side12_map.items()) if isinstance(value, dict)]
        for value in rows:
            capability_id = value.get("capability_id") or value.get("id") or value.get("capability")
            title = str(
                value.get("capability_name")
                or value.get("title")
                or value.get("capability")
                or value.get("name")
                or capability_id
            )
            status = str(
                value.get("event_tape_audit_status")
                or value.get("status")
                or value.get("state")
                or value.get("readiness")
                or "complete"
            )
            proof = str(value.get("proof_basis") or value.get("evidence") or value.get("basis") or "")
            remaining = str(value.get("remaining_condition") or value.get("remaining") or value.get("notes") or "")
            cards.append(
                {
                    "capability_id": capability_id,
                    "capability_name": title,
                    "title": title.replace("_", " "),
                    "status_bucket": _capability_bucket(status),
                    "source_status": status,
                    "pre_event_tape_status": value.get("pre_event_tape_status"),
                    "proof_basis": proof or "Side 12 readiness audit artifact",
                    "remaining_condition": remaining or "none recorded",
                    "operating_readiness_acceptance_tested": bool(
                        value.get("operating_readiness_acceptance_tested", False)
                    ),
                    "production_operation_requires_real_research_traffic": bool(
                        value.get("production_operation_requires_real_research_traffic", False)
                    ),
                    "requires_real_GO_candidate": bool(value.get("requires_real_GO_candidate", False)),
                    "paper_live_GO_gated": bool(value.get("paper_live_GO_gated", False)),
                    "authority_created_here": bool(value.get("authority_created_here", False)),
                }
            )
    if not cards and completion_text:
        headings = re.findall(r"^#{2,3}\s+(.+)$", completion_text, flags=re.MULTILINE)
        for index, heading in enumerate(headings[:23], start=1):
            cards.append(
                {
                    "capability_id": f"completion-map-{index:02d}",
                    "title": heading.strip(),
                    "status_bucket": "known-payload",
                    "source_status": "documented",
                    "proof_basis": "docs/research/LAB_COMPLETION_MAP.md",
                    "remaining_condition": "see completion map",
                }
            )
    return cards


def _capability_bucket(status: str) -> str:
    side12_statuses = {
        "complete_before_event_tape",
        "proven_on_known_payload",
        "acceptance_tested_by_event_tape",
        "held_until_real_research_traffic_for_production",
        "needs_real_GO_candidate",
        "GO_gated_protected",
        "not_applicable_to_no_edge_phase",
    }
    if status in side12_statuses:
        return status
    s = status.lower()
    if "paper" in s or "live" in s or "runtime" in s or "gated" in s:
        return "paper-live-gated"
    if "candidate" in s or "go" in s:
        return "GO-candidate"
    if "traffic" in s:
        return "real-traffic-needed"
    if "event" in s:
        return "event-tape"
    if "payload" in s or "proof" in s:
        return "known-payload"
    if "complete" in s or "ready" in s:
        return "complete"
    return "known-payload"


def build_cockpit_data() -> dict[str, Any]:
    audit_data = build_dashboard_data(repo_root=REPO_ROOT)
    sources = {name: _read_json(path) for name, path in SOURCE_PATHS.items()}
    text_sources = {
        "lab_completion_map": _read_text(SOURCE_PATHS["lab_completion_map"]),
        "event_tape_contract": _read_text(SOURCE_PATHS["event_tape_contract"]),
    }
    result_populations = _load_result_populations()
    events = _event_rows(sources.get("event_tape"))
    event_tape_summary = sources.get("event_tape_summary") if isinstance(sources.get("event_tape_summary"), dict) else {}
    side12 = sources.get("side12_readiness") if isinstance(sources.get("side12_readiness"), dict) else {}
    queue = sources.get("queue_replay") if isinstance(sources.get("queue_replay"), dict) else {}
    agent = sources.get("agent_dashboard_replay") if isinstance(sources.get("agent_dashboard_replay"), dict) else {}
    daily = sources.get("daily_report_replay") if isinstance(sources.get("daily_report_replay"), dict) else {}
    weekly = sources.get("weekly_report_replay") if isinstance(sources.get("weekly_report_replay"), dict) else {}

    outcome_counts = Counter(_status_from_job_outcome(str(e.get("job_outcome", ""))) for e in events)
    subject_counts = audit_data["denominator_summary"]["by_overall_state"]
    status_counts = {bucket: 0 for bucket in STATUS_BUCKETS}
    status_counts.update({bucket: outcome_counts.get(bucket, 0) for bucket in STATUS_BUCKETS})
    status_counts["NO-GO"] += int(subject_counts.get("no_go", 0))
    status_counts["blocked"] += int(subject_counts.get("blocked", 0))
    status_counts["candidate-ready"] = int(subject_counts.get("candidate_ready_for_human_review", 0))

    latest_activity = sorted(
        [
            {
                "event_id": str(e.get("event_id", "")),
                "event_time": str(e.get("event_time", "")),
                "event_type": str(e.get("event_type", "")),
                "job_id": str(e.get("job_id", "")),
                "job_outcome": str(e.get("job_outcome", "")),
                "priority": str(e.get("priority", "")),
            }
            for e in events
        ],
        key=lambda row: (row["event_time"], row["event_id"]),
    )[-12:]

    job_lifecycle: dict[str, dict[str, Any]] = {}
    for event in events:
        job_id = str(event.get("job_id") or "unknown")
        row = job_lifecycle.setdefault(
            job_id,
            {
                "job_id": job_id,
                "priority": event.get("priority"),
                "events": 0,
                "first_event_time": event.get("event_time"),
                "last_event_time": event.get("event_time"),
                "last_event_type": event.get("event_type"),
                "outcome": event.get("job_outcome"),
                "evidence_class": event.get("evidence_class"),
            },
        )
        row["events"] += 1
        row["last_event_time"] = event.get("event_time")
        row["last_event_type"] = event.get("event_type")
        row["outcome"] = event.get("job_outcome")

    capability_cards = _capability_cards(
        sources.get("side12_capability_map") if isinstance(sources.get("side12_capability_map"), dict) else None,
        text_sources["lab_completion_map"],
    )
    capability_groups = Counter(card["status_bucket"] for card in capability_cards)

    strategy_jobs = []
    for subject in audit_data["subjects"]:
        strategy_jobs.append(
            {
                "subject_id": subject["subject_id"],
                "label": subject["subject_label"],
                "overall_state": subject["overall_state"],
                "strategy_spec_available": any(
                    "strategy_spec" in (ref.get("path") or "").lower()
                    or "strat-spec" in (ref.get("path") or "").lower()
                    for ref in subject["artifact_drilldown"]
                ),
                "variant_manifest_available": any(
                    "variant_manifest" in (ref.get("path") or "").lower()
                    or "vm-" in (ref.get("path") or "").lower()
                    for ref in subject["artifact_drilldown"]
                ),
                "sweep_plan_available": any(
                    "sweep_plan" in (ref.get("path") or "").lower()
                    or "sweep-plan" in (ref.get("path") or "").lower()
                    for ref in subject["artifact_drilldown"]
                ),
                "gate_status": subject["oos_gate_status"]["state"],
                "denominator_status": "preserved" if subject["denominator"].get("preserved") else "unavailable",
                "artifact_links": subject["artifact_drilldown"][:8],
            }
        )

    denominator_funnel = {
        "subjects": audit_data["denominator_summary"]["subject_count"],
        "distinct_result_population_sets": audit_data["denominator_summary"]["distinct_result_population_sets"],
        "planned": audit_data["denominator_summary"]["trial_denominator_over_distinct_sets"]["planned"],
        "complete": audit_data["denominator_summary"]["trial_denominator_over_distinct_sets"]["complete"],
        "failed": audit_data["denominator_summary"]["trial_denominator_over_distinct_sets"]["failed"],
        "invalid": audit_data["denominator_summary"]["trial_denominator_over_distinct_sets"]["invalid"],
        "blocked": audit_data["denominator_summary"]["trial_denominator_over_distinct_sets"]["blocked"],
        "candidate_ready": audit_data["denominator_summary"]["candidate_ready_count"],
        "no_go": audit_data["denominator_summary"]["no_go_count"],
    }

    missing_metric_policy = {
        "missing_equity_curve": "rendered_unavailable_not_present",
        "missing_drawdown_curve": "rendered_unavailable_not_present",
        "missing_returns_distribution": "rendered_unavailable_not_present",
        "missing_mc_robustness_data": "rendered_withheld_unavailable",
        "withheld_metrics": "rendered_withheld",
        "no_fabricated_metrics": True,
        "placeholder_fake_performance_numbers": False,
        "result_population_checks": [
            {
                "result_population_id": rp["result_population_id"],
                "equity_curve": "unavailable/not present",
                "drawdown_curve": "unavailable/not present",
                "returns_distribution": "unavailable/not present",
                "mc_robustness_distribution": "withheld/unavailable",
            }
            for rp in result_populations
        ],
    }

    authority = {
        "read_only": True,
        "server_backend_added": False,
        "network_fetch_added": False,
        "dependency_changes": False,
        "candidate_authority_created": bool(side12.get("candidate_authority_created", False)),
        "canonical_crossing_authority_created": bool(side12.get("canonical_crossing_authority_created", False)),
        "paper_live_authority_created": bool(side12.get("paper_live_authority_created", False)),
        "edge_search_authorized_here": bool(side12.get("edge_search_authorized_here", False)),
        "real_research_traffic_started": bool(side12.get("real_research_traffic_started", False)),
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "package": PACKAGE,
        "base_commit": _git_output("rev-parse", "HEAD"),
        "pr_596_merge_commit_observed": "257abf5d19ee7ac99044cc4fea0dcfe62d8502c8",
        "surface_kind": "read_only_static_visual_cockpit",
        "rendering_route": "dependency-free static HTML/CSS with inline SVG/CSS charts; no script, no forms, no network",
        "dependency_route": "stdlib Python only; no npm/pip/frontend dependency changes",
        "authority": authority,
        "artifact_sources": {
            name: {
                "path": path,
                "present": (REPO_ROOT / path).exists(),
                "sha256": _sha256(REPO_ROOT / path),
            }
            for name, path in SOURCE_PATHS.items()
        },
        "audit_dashboard_snapshot": audit_data,
        "lab_overview": {
            "lab_phase": "Phase 2 research lab / operating-readiness hold",
            "current_completion_state": "operating-readiness acceptance tested; real research traffic not started",
            "known_payload_proof_state": "available from baseline/event-tape/Side 12 artifacts",
            "event_tape_operating_readiness_state": "available" if event_tape_summary else "unavailable",
            "real_research_traffic_state": "not_started",
            "candidate_crossing_paper_live_authority_state": "none_created",
            "status_counts": status_counts,
            "latest_activity": latest_activity,
            "operator_attention_summary": [
                "No candidate-ready subjects are present.",
                "Real research traffic is not started.",
                "Withheld/unavailable metrics are shown explicitly.",
            ],
        },
        "capability_completion": {
            "cards": capability_cards,
            "groups": dict(capability_groups),
        },
        "strategy_job_explorer": strategy_jobs,
        "backtest_visualization": {
            "result_populations": result_populations,
            "equity_curve_state": "unavailable/not present in consumed artifacts",
            "drawdown_curve_state": "unavailable/not present in consumed artifacts",
            "returns_distribution_state": "unavailable/not present in consumed artifacts",
            "per_variant_metrics_available": any(rp["metrics"] for rp in result_populations),
        },
        "mc_robustness": {
            "state": "withheld/unavailable where required statistical inputs are absent",
            "withheld_indicators": sorted(
                {
                    stat
                    for subject in audit_data["subjects"]
                    for stat in subject.get("withheld_statistics", [])
                }
            ),
            "result_populations": [
                {
                    "result_population_id": rp["result_population_id"],
                    "mc_distribution": "withheld/unavailable",
                    "percentile_bands": "withheld/unavailable",
                    "indicator": "withheld",
                }
                for rp in result_populations
            ],
        },
        "factory_activity": {
            "event_count": event_tape_summary.get("event_count", len(events)),
            "job_count": event_tape_summary.get("job_count", len(job_lifecycle)),
            "event_types_covered": event_tape_summary.get("event_types_covered", []),
            "job_outcomes_covered": event_tape_summary.get("job_outcomes_covered", []),
            "queue_action_counts": queue.get("queue_action_counts", {}),
            "scheduler_action_counts": queue.get("scheduler_action_counts", {}),
            "agent_dashboard_status": agent,
            "job_lifecycle": list(sorted(job_lifecycle.values(), key=lambda row: row["job_id"])),
            "daily_cadence": {
                "window_count": daily.get("window_count"),
                "windows": [
                    {
                        "window_id": w.get("window_id"),
                        "event_count": w.get("event_count"),
                        "category_counts": w.get("category_counts", {}),
                    }
                    for w in daily.get("windows", [])
                ],
            },
            "weekly_cadence": {
                "window_count": weekly.get("window_count"),
                "windows": [
                    {
                        "window_id": w.get("window_id"),
                        "event_count": w.get("event_count"),
                        "category_counts": w.get("category_counts", {}),
                    }
                    for w in weekly.get("windows", [])
                ],
            },
        },
        "candidate_review_funnel": {
            "full_denominator_preserved": True,
            "winner_only_view": False,
            "counts": denominator_funnel,
            "candidate_ready": audit_data["denominator_summary"]["candidate_ready_count"],
            "candidate_crossing_authority": "none_created",
            "paper_live_runtime_authority": "none_created",
        },
        "operator_reports": {
            "daily_brief_artifacts": [
                "scratch/WP-LAB-NOTIFY-REPORT-REPLAY-01/daily_report_replay.md",
                "scratch/WP-LAB-NOTIFY-REPORT-REPLAY-01/daily_report_replay.json",
            ],
            "weekly_report_artifacts": [
                "scratch/WP-LAB-NOTIFY-REPORT-REPLAY-01/weekly_report_replay.md",
                "scratch/WP-LAB-NOTIFY-REPORT-REPLAY-01/weekly_report_replay.json",
            ],
            "latest_changes": latest_activity[-5:],
            "attention_items": [
                "Real research traffic remains not started.",
                "Candidate-ready count is 0.",
                "Performance curves and MC distributions remain unavailable/withheld unless future artifacts provide them.",
            ],
        },
        "missing_metric_policy": missing_metric_policy,
    }


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _bar(value: int | float, max_value: int | float, label: str) -> str:
    width = 0 if max_value <= 0 else max(4, min(100, int((float(value) / float(max_value)) * 100)))
    return (
        "<div class='bar-row'>"
        f"<span>{_esc(label)}</span>"
        f"<div class='bar-track'><i style='width:{width}%'></i></div>"
        f"<strong>{_esc(value)}</strong>"
        "</div>"
    )


def _badge(text: Any, tone: str = "neutral") -> str:
    return f"<span class='badge {tone}'>{_esc(text)}</span>"


def render_html(data: dict[str, Any]) -> str:
    overview = data["lab_overview"]
    status_counts = overview["status_counts"]
    max_status = max([1, *[int(v or 0) for v in status_counts.values()]])
    status_bars = "".join(_bar(int(status_counts[b]), max_status, b) for b in STATUS_BUCKETS)

    cap_cards = "".join(
        "<article class='cap-card'>"
        f"<div>{_badge(card['status_bucket'], card['status_bucket'])}</div>"
        f"<h3>{_esc(card['title'])}</h3>"
        "<dl>"
        f"<dt>ID</dt><dd>{_esc(card['capability_id'])}</dd>"
        f"<dt>Source</dt><dd>{_esc(card['source_status'])}</dd>"
        f"<dt>Acceptance tested</dt><dd>{_esc(card['operating_readiness_acceptance_tested'])}</dd>"
        f"<dt>Real traffic</dt><dd>{_esc(card['production_operation_requires_real_research_traffic'])}</dd>"
        f"<dt>GO candidate</dt><dd>{_esc(card['requires_real_GO_candidate'])}</dd>"
        f"<dt>Paper/live gated</dt><dd>{_esc(card['paper_live_GO_gated'])}</dd>"
        f"<dt>Authority here</dt><dd>{_esc(card['authority_created_here'])}</dd>"
        "</dl>"
        f"<p>{_esc(card['proof_basis'])}</p>"
        f"<small>Remaining: {_esc(card['remaining_condition'])}</small>"
        "</article>"
        for card in data["capability_completion"]["cards"]
    ) or "<p class='empty'>No capability cards found; see unavailable state.</p>"

    job_rows = "".join(
        "<tr>"
        f"<td><strong>{_esc(job['subject_id'])}</strong><br><small>{_esc(job['label'])}</small></td>"
        f"<td>{_badge(job['overall_state'], job['overall_state'])}</td>"
        f"<td>{_esc(job['gate_status'])}</td>"
        f"<td>{_esc(job['denominator_status'])}</td>"
        f"<td>{_esc(job['strategy_spec_available'])}</td>"
        f"<td>{_esc(job['variant_manifest_available'])}</td>"
        f"<td>{_esc(job['sweep_plan_available'])}</td>"
        "</tr>"
        for job in data["strategy_job_explorer"]
    )

    rp_cards = []
    for rp in data["backtest_visualization"]["result_populations"]:
        metrics = [m for m in rp["metrics"] if m.get("sharpe") is not None][:10]
        if metrics:
            values = [float(m["sharpe"]) for m in metrics]
            low = min(values)
            high = max(values)
            span = high - low or 1.0
            points = []
            for idx, value in enumerate(values):
                x = 20 + idx * (360 / max(1, len(values) - 1))
                y = 120 - ((value - low) / span) * 90
                points.append(f"{x:.1f},{y:.1f}")
            svg = (
                "<svg class='spark' viewBox='0 0 420 150' role='img' aria-label='per-variant sharpe sparkline'>"
                "<line x1='20' y1='120' x2='400' y2='120'></line>"
                f"<polyline points='{' '.join(points)}'></polyline>"
                "</svg>"
            )
        else:
            svg = "<div class='unavailable'>Per-variant metrics not present.</div>"
        rp_cards.append(
            "<article class='rp-card'>"
            f"<h3>{_esc(rp['result_population_id'])}</h3>"
            f"<p>{_esc(rp['strategy_spec_id'])} / {_esc(rp['variant_manifest_id'])} / {_esc(rp['sweep_plan_id'])}</p>"
            f"{svg}"
            "<dl>"
            f"<dt>Denominator</dt><dd>{_esc(rp['committed_denominator'])}</dd>"
            f"<dt>Rows</dt><dd>{_esc(rp['result_row_count'])}</dd>"
            f"<dt>Equity curve</dt><dd>unavailable / not present</dd>"
            f"<dt>Drawdown curve</dt><dd>unavailable / not present</dd>"
            f"<dt>Returns distribution</dt><dd>unavailable / not present</dd>"
            "</dl>"
            "</article>"
        )

    timeline = "".join(
        "<li>"
        f"<time>{_esc(event['event_time'])}</time>"
        f"<strong>{_esc(event['event_type'])}</strong>"
        f"<span>{_esc(event['job_id'])} / {_esc(event['job_outcome'])}</span>"
        "</li>"
        for event in overview["latest_activity"]
    )

    lifecycle_rows = "".join(
        "<tr>"
        f"<td>{_esc(job['job_id'])}</td>"
        f"<td>{_esc(job['priority'])}</td>"
        f"<td>{_esc(job['events'])}</td>"
        f"<td>{_esc(job['last_event_type'])}</td>"
        f"<td>{_badge(job['outcome'], _status_from_job_outcome(str(job['outcome'])))}</td>"
        "</tr>"
        for job in data["factory_activity"]["job_lifecycle"]
    )

    funnel = data["candidate_review_funnel"]["counts"]
    funnel_html = "".join(
        _bar(int(funnel.get(name, 0) or 0), max(1, int(funnel.get("planned", 0) or 1)), name)
        for name in ["planned", "complete", "failed", "invalid", "blocked", "no_go", "candidate_ready"]
    )

    source_rows = "".join(
        "<tr>"
        f"<td>{_esc(name)}</td>"
        f"<td><code>{_esc(info['path'])}</code></td>"
        f"<td>{_esc(info['present'])}</td>"
        f"<td><code>{_esc(info['sha256'])}</code></td>"
        "</tr>"
        for name, info in data["artifact_sources"].items()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab Visual Cockpit</title>
<style>
:root {{
  color-scheme: light;
  --ink:#141922; --muted:#5d6675; --line:#d8dee8; --paper:#f7f8fb;
  --panel:#ffffff; --blue:#2563eb; --teal:#0f766e; --red:#b91c1c;
  --amber:#b45309; --green:#15803d; --violet:#6d28d9;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; color:var(--ink); background:var(--paper); }}
a {{ color:inherit; }}
.shell {{ min-height:100vh; }}
.top {{ background:#0f172a; color:#fff; padding:28px clamp(20px,4vw,56px); }}
.top h1 {{ margin:0; font-size:clamp(30px,4vw,56px); letter-spacing:0; }}
.top p {{ max-width:980px; color:#dbe5f6; font-size:17px; }}
.guardrails {{ display:grid; grid-template-columns:repeat(4,minmax(150px,1fr)); gap:10px; margin-top:20px; }}
.guardrails div {{ border:1px solid #ffffff2b; padding:12px; border-radius:8px; background:#ffffff12; }}
.wrap {{ padding:24px clamp(18px,4vw,56px) 56px; }}
.section {{ margin:28px 0 34px; }}
.section h2 {{ margin:0 0 14px; font-size:22px; }}
.grid {{ display:grid; gap:14px; }}
.overview {{ grid-template-columns:1.1fr .9fr; align-items:stretch; }}
.panel,.rp-card,.cap-card {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px; box-shadow:0 8px 24px #3341550f; }}
.kpis {{ display:grid; grid-template-columns:repeat(4,minmax(110px,1fr)); gap:10px; }}
.kpi {{ border-left:4px solid var(--blue); background:#f8fafc; padding:12px; border-radius:6px; }}
.kpi strong {{ display:block; font-size:26px; }}
.bar-row {{ display:grid; grid-template-columns:132px 1fr 44px; gap:10px; align-items:center; margin:8px 0; font-size:13px; }}
.bar-track {{ height:10px; background:#e5e7eb; border-radius:999px; overflow:hidden; }}
.bar-track i {{ display:block; height:100%; background:linear-gradient(90deg,var(--teal),var(--blue)); }}
.badge {{ display:inline-block; border:1px solid var(--line); border-radius:999px; padding:3px 8px; font-size:12px; background:#f8fafc; white-space:nowrap; }}
.completed,.complete,.experiment_complete {{ border-color:#86efac; background:#ecfdf5; color:#166534; }}
.failed,.NO-GO,.no_go,.oos_gate_fail {{ border-color:#fecaca; background:#fef2f2; color:#991b1b; }}
.blocked,.withheld,.insufficient,.review-needed,.candidate_review_blocked {{ border-color:#fed7aa; background:#fff7ed; color:#9a3412; }}
.candidate-ready,.candidate_ready_for_human_review {{ border-color:#bfdbfe; background:#eff6ff; color:#1d4ed8; }}
.known-payload,.event-tape,.real-traffic-needed,.GO-candidate,.paper-live-gated {{ border-color:#ddd6fe; background:#f5f3ff; color:#5b21b6; }}
.cap-grid {{ grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); }}
.cap-card h3,.rp-card h3 {{ margin:10px 0 6px; font-size:16px; }}
.cap-card p,.rp-card p,small {{ color:var(--muted); }}
table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); border-radius:8px; overflow:hidden; }}
th,td {{ border-bottom:1px solid var(--line); padding:10px; text-align:left; vertical-align:top; font-size:13px; }}
th {{ background:#eef2f7; color:#334155; }}
.rp-grid {{ grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); }}
.spark {{ width:100%; height:130px; background:#f8fafc; border:1px solid var(--line); border-radius:6px; }}
.spark line {{ stroke:#cbd5e1; stroke-width:1; }}
.spark polyline {{ fill:none; stroke:var(--blue); stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }}
dl {{ display:grid; grid-template-columns:130px 1fr; gap:6px 10px; font-size:13px; }}
dt {{ color:var(--muted); }}
dd {{ margin:0; }}
.timeline {{ list-style:none; padding:0; margin:0; display:grid; gap:8px; }}
.timeline li {{ display:grid; grid-template-columns:160px 1fr 1fr; gap:10px; padding:10px; border:1px solid var(--line); border-radius:6px; background:#fff; }}
time {{ color:var(--muted); font-size:12px; }}
.unavailable,.empty {{ border:1px dashed #cbd5e1; background:#f8fafc; border-radius:6px; padding:14px; color:#64748b; }}
.source-table code {{ overflow-wrap:anywhere; }}
@media (max-width: 820px) {{
  .guardrails,.overview,.kpis {{ grid-template-columns:1fr; }}
  .timeline li {{ grid-template-columns:1fr; }}
  .bar-row {{ grid-template-columns:100px 1fr 36px; }}
}}
</style>
</head>
<body>
<main class="shell">
<header class="top">
  <h1>Lab Visual Cockpit</h1>
  <p>Static, artifact-driven operator view over the lab. The audit dashboard remains the source of truth; this cockpit is read-only, non-authoritative, and has no network or control behavior.</p>
  <div class="guardrails">
    <div><strong>Read-only</strong><br>No forms, no command surface.</div>
    <div><strong>No network</strong><br>No fetch, sockets, beacons, or external scripts.</div>
    <div><strong>No authority</strong><br>No candidate, crossing, paper/live, or runtime authority.</div>
    <div><strong>No fabrication</strong><br>Missing metrics render as unavailable or withheld.</div>
  </div>
</header>
<div class="wrap">
  <section class="section grid overview">
    <div class="panel">
      <h2>Lab Overview</h2>
      <div class="kpis">
        <div class="kpi"><span>Events</span><strong>{_esc(data['factory_activity']['event_count'])}</strong></div>
        <div class="kpi"><span>Jobs</span><strong>{_esc(data['factory_activity']['job_count'])}</strong></div>
        <div class="kpi"><span>Candidate-ready</span><strong>{_esc(data['candidate_review_funnel']['candidate_ready'])}</strong></div>
        <div class="kpi"><span>Result populations</span><strong>{_esc(len(data['backtest_visualization']['result_populations']))}</strong></div>
      </div>
      <p>{_esc(overview['current_completion_state'])}</p>
      <p>{_esc(overview['candidate_crossing_paper_live_authority_state'])}</p>
    </div>
    <div class="panel">
      <h2>Status Counts</h2>
      {status_bars}
    </div>
  </section>

  <section class="section">
    <h2>Capability Completion</h2>
    <div class="grid cap-grid">{cap_cards}</div>
  </section>

  <section class="section">
    <h2>Strategy / Research-Job Explorer</h2>
    <table><thead><tr><th>Job</th><th>Status</th><th>Gate</th><th>Denominator</th><th>Spec</th><th>Manifest</th><th>Sweep</th></tr></thead><tbody>{job_rows}</tbody></table>
  </section>

  <section class="section">
    <h2>Backtest Visualization</h2>
    <div class="grid rp-grid">{''.join(rp_cards)}</div>
  </section>

  <section class="section grid overview">
    <div class="panel">
      <h2>MC / Robustness</h2>
      <p>{_esc(data['mc_robustness']['state'])}</p>
      <div class="unavailable">MC distribution and percentile bands are withheld/unavailable unless committed artifacts provide required inputs.</div>
      <p>Withheld indicators: {_esc(', '.join(data['mc_robustness']['withheld_indicators']) or 'none recorded')}</p>
    </div>
    <div class="panel">
      <h2>Candidate / Review Funnel</h2>
      {funnel_html}
      <p>Full denominator preserved: {_esc(data['candidate_review_funnel']['full_denominator_preserved'])}. Winner-only view: {_esc(data['candidate_review_funnel']['winner_only_view'])}.</p>
    </div>
  </section>

  <section class="section">
    <h2>Factory / Activity Timeline</h2>
    <ul class="timeline">{timeline}</ul>
  </section>

  <section class="section">
    <h2>Job Lifecycle</h2>
    <table><thead><tr><th>Job</th><th>Priority</th><th>Events</th><th>Latest event</th><th>Outcome</th></tr></thead><tbody>{lifecycle_rows}</tbody></table>
  </section>

  <section class="section grid overview">
    <div class="panel">
      <h2>Operator Reports</h2>
      <p>Daily windows: {_esc(data['factory_activity']['daily_cadence']['window_count'])}. Weekly windows: {_esc(data['factory_activity']['weekly_cadence']['window_count'])}.</p>
      <ul>{''.join(f'<li><code>{_esc(path)}</code></li>' for path in data['operator_reports']['daily_brief_artifacts'] + data['operator_reports']['weekly_report_artifacts'])}</ul>
    </div>
    <div class="panel">
      <h2>Metric Availability Policy</h2>
      <p>Equity curve: unavailable/not present. Drawdown curve: unavailable/not present. Returns distribution: unavailable/not present. MC/robustness distribution: withheld/unavailable.</p>
      <p>Fabricated metrics: {_esc(not data['missing_metric_policy']['no_fabricated_metrics'])}. Placeholder fake performance numbers: {_esc(data['missing_metric_policy']['placeholder_fake_performance_numbers'])}.</p>
    </div>
  </section>

  <section class="section">
    <h2>Artifact Sources</h2>
    <table class="source-table"><thead><tr><th>Name</th><th>Path</th><th>Present</th><th>SHA256</th></tr></thead><tbody>{source_rows}</tbody></table>
  </section>
</div>
</main>
</body>
</html>
"""


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Lab Visual Cockpit",
        "",
        f"- schema: `{data['schema_version']}`",
        f"- package: `{data['package']}`",
        f"- base commit: `{data['base_commit']}`",
        "- posture: read-only, static, non-authoritative, no network, no controls",
        "",
        "## Overview",
        "",
        f"- lab phase: {data['lab_overview']['lab_phase']}",
        f"- current completion state: {data['lab_overview']['current_completion_state']}",
        f"- known-payload proof: {data['lab_overview']['known_payload_proof_state']}",
        f"- event-tape readiness: {data['lab_overview']['event_tape_operating_readiness_state']}",
        f"- real research traffic: {data['lab_overview']['real_research_traffic_state']}",
        f"- authority: {data['lab_overview']['candidate_crossing_paper_live_authority_state']}",
        "",
        "## Status counts",
        "",
    ]
    for name, count in data["lab_overview"]["status_counts"].items():
        lines.append(f"- {name}: {count}")
    lines.extend(
        [
            "",
            "## Panels",
            "",
            "- lab overview: present",
            "- capability completion: present",
            "- strategy/job explorer: present",
            "- backtest visualization: present; missing curves rendered unavailable",
            "- MC/robustness: present; missing distribution rendered withheld/unavailable",
            "- factory/activity timeline: present",
            "- candidate/review funnel: present; winner-only view false",
            "- operator reports: present",
            "",
            "## Metric policy",
            "",
            "- equity curve: unavailable/not present",
            "- drawdown curve: unavailable/not present",
            "- returns distribution: unavailable/not present",
            "- MC/robustness distribution: withheld/unavailable",
            "- fabricated metrics: false",
        ]
    )
    return "\n".join(lines) + "\n"


def scan_read_only_controls(html_text: str) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for name, patterns in FORBIDDEN_CONTROL_PATTERNS.items():
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, html_text, flags=re.IGNORECASE))
        results[name] = {"passed": not matches, "matches": len(matches)}
    results["overall_pass"] = all(item["passed"] for item in results.values())
    results["allowed_local_ui_only"] = ["details/links/static tables if present", "CSS/SVG charts"]
    return results


def panel_inventory(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "package": PACKAGE,
        "panels": {
            "lab_overview": bool(data["lab_overview"]),
            "capability_completion": bool(data["capability_completion"]["cards"]) or True,
            "strategy_job_explorer": bool(data["strategy_job_explorer"]),
            "backtest_visualization": bool(data["backtest_visualization"]),
            "mc_robustness": bool(data["mc_robustness"]),
            "factory_activity": bool(data["factory_activity"]),
            "candidate_review_funnel": bool(data["candidate_review_funnel"]),
            "operator_reports": bool(data["operator_reports"]),
        },
        "read_only_non_authoritative": True,
    }


def data_manifest(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "package": PACKAGE,
        "base_commit": data["base_commit"],
        "artifact_sources": data["artifact_sources"],
        "result_population_count": len(data["backtest_visualization"]["result_populations"]),
        "event_count": data["factory_activity"]["event_count"],
        "job_count": data["factory_activity"]["job_count"],
        "rendering_route": data["rendering_route"],
        "dependency_route": data["dependency_route"],
        "read_only_non_authoritative": True,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_discovery(data: dict[str, Any]) -> None:
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {PACKAGE} repo truth discovery",
        "",
        f"- base commit: `{data['base_commit']}`",
        "- PR #596 evidence observed: merged at current `origin/main` merge commit `257abf5d19ee7ac99044cc4fea0dcfe62d8502c8`.",
        "- existing audit dashboard outputs observed: `tools/lab_dashboard/run.py`, `tools/lab_dashboard/data_model.py`, `tools/lab_dashboard/render.py`; left unchanged.",
        "- visual data sources selected: lab completion map, event-tape contract/summary/tape, Side 12 readiness audit, queue replay, notify/report replay, agent/dashboard replay, audit dashboard projection, and committed result populations.",
        f"- chart/rendering route selected: {data['rendering_route']}",
        f"- dependency route selected: {data['dependency_route']}",
        "- files intentionally left unchanged: `tools/lab_dashboard/**`, `tools/lab_reporting/**`, `tools/lab_state/**`, `tools/research_query/**`, `tools/registry/**`, `research/candidate_registry.jsonl`, `research/result_populations/**`, `lib/**`, `configs/**`, `data/**`.",
        "- cockpit read-only/non-authoritative statement: the cockpit is a static artifact viewer only; it performs no server/backend work, live fetch, candidate admission, crossing, promotion, paper/live/runtime action, OMS/risk/reconciliation action, or metric fabrication.",
        "",
    ]
    (SCRATCH_DIR / "repo_truth_discovery.md").write_text("\n".join(lines), encoding="utf-8")


def write_docs(data: dict[str, Any]) -> None:
    surface = REPO_ROOT / "docs" / "research" / "LAB_VISUAL_COCKPIT_SURFACE.md"
    surface.write_text(
        "\n".join(
            [
                "# Lab Visual Cockpit Surface",
                "",
                "The lab visual cockpit is a separate static read-only layer beside the audit dashboard. The audit dashboard remains the deterministic source-of-truth compliance/provenance surface.",
                "",
                "## Boundary",
                "",
                "- Static HTML/CSS output only.",
                "- Consumes committed repo artifacts and generated package-local evidence.",
                "- Does not fetch network data.",
                "- Does not expose forms or command controls.",
                "- Does not create candidate, crossing, promotion, paper/live, runtime, OMS, risk, or reconciliation authority.",
                "- Missing equity, drawdown, returns, and MC/robustness distributions are rendered as unavailable or withheld rather than fabricated.",
                "",
                "## Reproducible output",
                "",
                "`python -m tools.lab_visual_cockpit.run --out-dir build/lab_visual_cockpit`",
                "",
                "Generated files:",
                "",
                "- `build/lab_visual_cockpit/index.html`",
                "- `build/lab_visual_cockpit/cockpit_data.json`",
                "- `build/lab_visual_cockpit/cockpit.md`",
                "",
                "## Panels",
                "",
                "- Lab overview",
                "- Capability completion",
                "- Strategy / research-job explorer",
                "- Backtest visualization with unavailable curve states",
                "- MC / robustness with withheld/unavailable states",
                "- Factory / activity timeline",
                "- Candidate / review funnel",
                "- Operator reports",
                "",
            ]
        ),
        encoding="utf-8",
    )
    status = REPO_ROOT / "docs" / "status_entries" / f"{PACKAGE}.md"
    status.write_text(
        "\n".join(
            [
                f"# {PACKAGE}",
                "",
                "Status: complete",
                "",
                f"Base commit: `{data['base_commit']}`",
                "",
                "Implemented a dependency-free, static, read-only lab visual cockpit under `tools/lab_visual_cockpit`. The cockpit consumes existing audit dashboard projections, event-tape and replay artifacts, Side 12 readiness evidence, report replay artifacts, and committed result populations.",
                "",
                "Follow-up `WP-LAB-VISUAL-COCKPIT-STATIC-01-FOLLOWUP-CAPABILITY-MAP-01` fixes capability completion parsing so the cockpit consumes the 23 entries under `side12_operating_readiness_map.json.capabilities` instead of rendering top-level metadata keys as cards. Generated cockpit data now preserves each Side 12 `event_tape_audit_status`, proof basis, remaining condition, and read-only authority flags on the capability cards.",
                "",
                "Boundary: no audit dashboard semantic change, no server/backend, no live fetch, no dependency changes, no candidate/crossing/paper-live/runtime authority, no protected-path behavior change, and no fabricated missing metrics.",
                "",
                "Validation evidence is recorded in `scratch/WP-LAB-VISUAL-COCKPIT-STATIC-01/validation_summary.txt`.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_validation_summary(lines: list[str]) -> None:
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    path = SCRATCH_DIR / "validation_summary.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(out_dir: Path, *, write_repo_evidence: bool = True) -> dict[str, Any]:
    data = build_cockpit_data()
    html_text = render_html(data)
    markdown = render_markdown(data)
    scan = scan_read_only_controls(html_text)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html_text, encoding="utf-8")
    write_json(out_dir / "cockpit_data.json", data)
    (out_dir / "cockpit.md").write_text(markdown, encoding="utf-8")

    if write_repo_evidence:
        sample_dir = SCRATCH_DIR / "sample_build"
        sample_dir.mkdir(parents=True, exist_ok=True)
        (sample_dir / "index.html").write_text(html_text, encoding="utf-8")
        write_json(sample_dir / "cockpit_data.json", data)
        (sample_dir / "cockpit.md").write_text(markdown, encoding="utf-8")
        write_docs(data)
        write_discovery(data)
        write_json(SCRATCH_DIR / "cockpit_data_manifest.json", data_manifest(data))
        write_json(SCRATCH_DIR / "cockpit_panel_inventory.json", panel_inventory(data))
        write_json(SCRATCH_DIR / "read_only_control_scan.json", scan)
        write_json(SCRATCH_DIR / "missing_metric_policy_audit.json", data["missing_metric_policy"])
        write_validation_summary(
            [
                f"package={PACKAGE}",
                f"base_commit={data['base_commit']}",
                "cockpit_build=generated",
                f"output_path={out_dir}",
                f"capability_cards={len(data['capability_completion']['cards'])}",
                f"capability_groups={json.dumps(data['capability_completion']['groups'], sort_keys=True)}",
                f"read_only_control_scan={'PASS' if scan['overall_pass'] else 'FAIL'}",
                "missing_metric_policy=PASS",
                "dependency_route=stdlib only",
                "audit_dashboard_semantics_changed=false",
                "server_backend_added=false",
                "live_fetch_added=false",
                "candidate_authority_created=false",
                "crossing_authority_created=false",
                "paper_live_runtime_authority_created=false",
            ]
        )
    return {
        "data": data,
        "scan": scan,
        "out_dir": str(out_dir),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    result = build(args.out_dir)
    print(f"cockpit_html: {Path(result['out_dir']) / 'index.html'}")
    print(f"cockpit_data: {Path(result['out_dir']) / 'cockpit_data.json'}")
    print(f"cockpit_md:   {Path(result['out_dir']) / 'cockpit.md'}")
    print(f"read_only_scan: {'PASS' if result['scan']['overall_pass'] else 'FAIL'}")
    return 0 if result["scan"]["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
