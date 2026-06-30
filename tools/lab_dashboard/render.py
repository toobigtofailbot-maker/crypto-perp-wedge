"""Deterministic static renderers for the lab results dashboard.

Both renderers emit a pure read-only document: tables and text only, no forms,
no buttons, no ``<script>``, no network fetch, no auto-refresh. Output is a
deterministic function of the data model, so two renders are byte-identical.
"""

from __future__ import annotations

import html
from typing import Any

_CSS = """
:root { color-scheme: light dark; }
body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
       margin: 2rem; line-height: 1.45; }
h1 { font-size: 1.4rem; margin-bottom: 0.2rem; }
h2 { font-size: 1.1rem; margin-top: 1.6rem;
     border-bottom: 1px solid #8884; padding-bottom: 0.2rem; }
h3 { font-size: 1rem; margin-bottom: 0.2rem; }
table { border-collapse: collapse; margin: 0.4rem 0 1rem; width: 100%; }
th, td { border: 1px solid #8884; padding: 0.3rem 0.5rem;
         text-align: left; vertical-align: top; font-size: 0.9rem; }
th { background: #8881; }
.banner { border: 1px solid #c93; background: #fc31; padding: 0.5rem 0.75rem;
          border-radius: 6px; margin: 0.6rem 0; font-size: 0.9rem; }
.state { font-family: ui-monospace, monospace; }
.caveat { font-size: 0.9rem; }
code { font-family: ui-monospace, monospace; font-size: 0.85rem; }
""".strip()


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


# ---------------------------------------------------------------------------
# Markdown renderer.
# ---------------------------------------------------------------------------
def _render_baseline_proof_panel_markdown(panel: dict[str, Any]) -> list[str]:
    """Render the baseline proof panel as markdown lines."""
    lines: list[str] = []
    lines.append("## Baseline fixture proof (non-promotable, read-only)")
    lines.append("")
    lines.append(f"_{panel['non_authority_note']}_")
    lines.append("")

    # Strategy detail / baseline payloads
    bp = panel["baseline_payloads"]
    lines.append("### Strategy detail — construction payload catalog")
    lines.append("")
    if bp["available"]:
        lines.append(f"- baseline count: {bp['baseline_count']}")
        lines.append(f"- primitive family: {bp['selected_primitive_family']}")
        lines.append(f"- contract-only route: {bp['contract_only_route_used']}")
        lines.append("")
        lines.append(
            "| baseline_id | label | family | non_promotable | "
            "expected_gate | expected_crossing |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for b in bp["baselines"]:
            lines.append(
                f"| `{b['baseline_id']}` | {b['label']} | {b['strategy_family']} "
                f"| {b['non_promotable']} | {b['expected_gate_result']} "
                f"| {b['expected_crossing_result']} |"
            )
    else:
        lines.append("_Baseline payload catalog: artifact unavailable (blocker)._")
    lines.append("")

    # Sweep-grid / WFO/OOS / MC/robustness gate posture
    ge = panel["gate_expectations"]
    lines.append("### Gate posture — WFO/OOS, MC/robustness, statistical diagnostics")
    lines.append("")
    if ge["available"]:
        gr = ge["global_rule"]
        lines.append(
            f"- construction_payload_or_non_promotable_dominates_numeric: "
            f"{gr.get('construction_payload_or_non_promotable_dominates_numeric_results')}"
        )
        lines.append(f"- numeric_override_allowed: {gr.get('numeric_override_allowed')}")
        lines.append(f"- fabricated_metrics_allowed: {gr.get('fabricated_metrics_allowed')}")
        lines.append("")
        lines.append(
            "| baseline_id | WFO/OOS expected | MC/robustness expected | "
            "stat diagnostics | denominator integrity | crossing |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for b in ge["per_baseline"]:
            lines.append(
                f"| `{b['baseline_id']}` | {b['wfo_oos_gate_expected']} "
                f"| {b['robustness_mc_gate_expected']} "
                f"| {b['statistical_diagnostics_gate_expected']} "
                f"| {b['denominator_integrity_expected']} "
                f"| {b['crossing_expected']} |"
            )
    else:
        lines.append("_Gate expectations: artifact unavailable (blocker)._")
    lines.append("")

    # Guard validation
    gv = panel["guard_validation"]
    lines.append("### Non-promotable crossing guard")
    lines.append("")
    if gv["available"]:
        lines.append(f"- guard_implemented: {gv['guard_implemented']}")
        lines.append(
            f"- non_promotable_crossing_guard_hardened: "
            f"{gv['non_promotable_crossing_guard_hardened']}"
        )
        lines.append(f"- lab_declared_finished: {gv['lab_declared_finished']}")
        lines.append(f"- test_result: {gv['test_result']} ({gv['tests_observed']})")
    else:
        lines.append("_Guard validation summary: artifact unavailable (blocker)._")
    lines.append("")

    # Agent loop activity
    al = panel["agent_loop_exercise"]
    lines.append("### Agent/baseline loop activity")
    lines.append("")
    if al["available"]:
        lines.append(f"- fixture_only: {al['fixture_only']}")
        lines.append(f"- baseline_id: {al['baseline_id']}")
        lines.append(f"- status: {al['status']}")
        lines.append(f"- non_promotable: {al['non_promotable']}")
        lines.append(f"- candidate_eligible: {al['candidate_eligible']}")
        lines.append(f"- crossing_rejection_reason_code: {al['crossing_rejection_reason_code']}")
        lines.append(
            f"- canonical_result_population_written: "
            f"{al['canonical_result_population_written']}"
        )
        lines.append(f"- candidate_registry_written: {al['candidate_registry_written']}")
        nc = al["no_candidate_result"]
        lines.append(
            f"- no_candidate_result: status={nc['status']}, "
            f"outcome={nc['review_outcome']}, "
            f"completed_rows={nc['completed_rows']}/{nc['declared_rows']}, "
            f"wfo_oos={nc['wfo_oos_status']}, "
            f"fabricated={nc['missing_or_unavailable_metrics_fabricated']}"
        )
        cr = al["crossing_rejection"]
        lines.append(
            f"- crossing_rejection: status={cr['status']}, "
            f"reason={cr['reason_code']}, "
            f"action_authorized={cr['crossing_action_authorized']}, "
            f"karl_gated={cr['first_real_crossing_remains_karl_gated']}"
        )
        beh = al["agent_loop_behavior"]
        beh_flags = ", ".join(
            f"{k}={v}" for k, v in beh.items()
        )
        lines.append(f"- agent_behavior: {beh_flags}")
    else:
        lines.append("_Agent loop result: artifact unavailable (blocker)._")
    lines.append("")

    # Provenance trace
    pv = panel["provenance_trace"]
    lines.append("### Data/provenance trace (PR #583-#587)")
    lines.append("")
    if pv["available"]:
        prs = ", ".join(f"#{p}" for p in (pv["baseline_sequence_prs"] or []))
        lines.append(f"- baseline_sequence_prs: {prs}")
        lines.append(f"- core_pipe_fixture_proven: {pv['core_pipe_fixture_proven']}")
        lines.append(
            f"- no_candidate_result_observed: {pv['no_candidate_result_observed']}"
        )
        lines.append(
            f"- crossing_rejection_observed: {pv['crossing_rejection_observed']}"
        )
        lines.append(
            f"- real_candidate_crossing_completed: "
            f"{pv['real_candidate_crossing_completed']}"
        )
        lines.append(
            f"- full_always_on_factory_completed: "
            f"{pv['full_always_on_factory_completed']}"
        )
        lines.append(
            f"- lab_declared_finished_without_qualification: "
            f"{pv['lab_declared_finished_without_qualification']}"
        )
        lines.append(f"- edge_search_authorized_here: {pv['edge_search_authorized_here']}")
        lines.append(
            f"- canonical_writes_authorized_here: {pv['canonical_writes_authorized_here']}"
        )
        lines.append(
            f"- held_b_requires_real_edge_search_or_candidate_flow: "
            f"{pv['held_b_requires_real_edge_search_or_candidate_flow']}"
        )
        lines.append(
            f"- paper_live_runtime_go_gated: {pv['paper_live_runtime_go_gated']}"
        )
    else:
        lines.append("_Provenance trace: artifact unavailable (blocker)._")
    lines.append("")
    return lines


def _render_held_boundary_panel_markdown(panel: dict[str, Any]) -> list[str]:
    """Render the held-boundary / deferred-B panel as markdown lines."""
    lines: list[str] = []
    lines.append("## Held-boundary / deferred-B (not authorized in current phase)")
    lines.append("")
    lines.append(f"_{panel['non_authority_note']}_")
    lines.append("")
    if not panel["available"]:
        lines.append("_Held boundary map: artifact unavailable (blocker)._")
        lines.append("")
        return lines

    if panel["held_b_until_real_research_flow"]:
        lines.append("### Held-B until real research flow resumes")
        lines.append("")
        for item in panel["held_b_until_real_research_flow"]:
            lines.append(f"- {item}")
        lines.append("")

    if panel["requires_real_go_candidate"]:
        lines.append("### Requires first real GO candidate")
        lines.append("")
        for item in panel["requires_real_go_candidate"]:
            lines.append(f"- {item}")
        lines.append("")

    if panel["go_gated_protected"]:
        lines.append("### GO-gated protected (paper/live/runtime/OMS/exchange)")
        lines.append("")
        for item in panel["go_gated_protected"]:
            lines.append(f"- {item}")
        lines.append("")

    if panel["current_fork"]:
        lines.append("### Current fork (operator decision point)")
        lines.append("")
        for item in panel["current_fork"]:
            lines.append(f"- {item}")
        lines.append("")

    return lines


def render_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Lab Results Dashboard (read-only)")
    lines.append("")
    lines.append(f"_schema: `{data['schema_version']}` -- {data['surface_kind']}_")
    lines.append("")
    lines.append(
        "> Read-only operator visibility surface. No executable controls: no "
        "run, approve, promote, retry, scheduler, or live-fetch."
    )
    lines.append("")
    lines.append(f"> {data['edge_search_hold']}")
    lines.append("")

    summary = data["denominator_summary"]
    lines.append("## Denominator summary (full population, not winners only)")
    lines.append("")
    lines.append(f"- subjects: {summary['subject_count']}")
    lines.append(
        f"- completed experiment runs reached: "
        f"{summary['completed_experiment_run_count']}"
    )
    lines.append(f"- NO-GO: {summary['no_go_count']}")
    lines.append(f"- blocked: {summary['blocked_count']}")
    lines.append(f"- candidate ready for human review: {summary['candidate_ready_count']}")
    lines.append(
        f"- operator gate pending: {summary['operator_gate_pending_count']}"
    )
    lines.append("")
    lines.append("### Subjects by overall state")
    lines.append("")
    lines.append("| overall state | count |")
    lines.append("| --- | ---: |")
    for state, count in summary["by_overall_state"].items():
        lines.append(f"| `{state}` | {count} |")
    lines.append("")
    trials = summary["trial_denominator_over_distinct_sets"]
    lines.append(
        "### Trial denominator over "
        f"{summary['distinct_result_population_sets']} distinct Result "
        "Population set(s)"
    )
    lines.append("")
    lines.append(
        "| planned | complete | failed | invalid | blocked | pruned |"
    )
    lines.append("| ---: | ---: | ---: | ---: | ---: | ---: |")
    lines.append(
        f"| {trials['planned']} | {trials['complete']} | {trials['failed']} | "
        f"{trials['invalid']} | {trials['blocked']} | {trials['pruned']} |"
    )
    lines.append("")

    lines.append("## Caveats")
    lines.append("")
    for caveat in data["caveats"]:
        lines.append(f"- {caveat}")
    lines.append("")

    lines.extend(_render_baseline_proof_panel_markdown(data["baseline_proof_panel"]))
    lines.extend(_render_held_boundary_panel_markdown(data["held_boundary_panel"]))

    lines.append("## Subjects")
    lines.append("")
    for view in data["subjects"]:
        lines.append(f"### {view['subject_id']} -- `{view['overall_state']}`")
        lines.append("")
        lines.append(f"- label: {view['subject_label']}")
        lines.append(f"- evidence class: `{view['evidence_class']}`")
        denom = view["denominator"]
        if denom.get("available"):
            lines.append(
                f"- denominator: planned {denom['planned']}, complete "
                f"{denom['complete']}, failed {denom['failed']}, invalid "
                f"{denom['invalid']}, blocked {denom['blocked']}, pruned "
                f"{denom['pruned']} (preserved={denom['preserved']})"
            )
        else:
            lines.append("- denominator: not available")
        lines.append(
            f"- replay: `{view['replay_status']['state']}` "
            f"({view['replay_status']['reason_code']})"
        )
        oos = view["oos_gate_status"]
        lines.append(
            f"- OOS gate: `{oos['state']}` ({oos['reason_code']}); evidence "
            f"status: {oos['oos_evidence_status']}"
        )
        rob = view["robustness_status"]
        withheld = ", ".join(rob["withheld_statistics"]) or "none"
        lines.append(
            f"- robustness: `{rob['state']}` ({rob['reason_code']}); withheld "
            f"statistics: {withheld}"
        )
        review = view["candidate_review_status"]
        lines.append(
            f"- candidate review: `{review['state']}` ({review['reason_code']})"
        )
        lines.append(
            f"- reporting: `{view['reporting_status']['state']}`; operator "
            f"gate: `{view['operator_gate_status']['state']}`"
        )
        if view["result_populations"]:
            ids = ", ".join(
                f"{rp['result_population_id']} ({rp['rows']} rows)"
                for rp in view["result_populations"]
            )
            lines.append(f"- Result Populations: {ids}")
        if view["no_go_caveats"]:
            lines.append("- NO-GO caveats:")
            for caveat in view["no_go_caveats"]:
                lines.append(f"  - {caveat}")
        lines.append("- artifact drill-down:")
        for ref in view["artifact_drilldown"]:
            flag = "present" if ref["present"] else "missing"
            lines.append(f"  - `{ref['path']}` [{ref['role']}] ({flag})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Static HTML renderer.
# ---------------------------------------------------------------------------
def _state_table_rows(summary: dict[str, Any]) -> str:
    rows = []
    for state, count in summary["by_overall_state"].items():
        rows.append(
            f"<tr><td class='state'>{_esc(state)}</td>"
            f"<td>{_esc(count)}</td></tr>"
        )
    return "".join(rows)


def _subject_html(view: dict[str, Any]) -> str:
    parts: list[str] = []
    parts.append(
        f"<h3>{_esc(view['subject_id'])} "
        f"&mdash; <span class='state'>{_esc(view['overall_state'])}</span></h3>"
    )
    denom = view["denominator"]
    if denom.get("available"):
        denom_cells = (
            f"<tr><td>{_esc(denom['planned'])}</td>"
            f"<td>{_esc(denom['complete'])}</td>"
            f"<td>{_esc(denom['failed'])}</td>"
            f"<td>{_esc(denom['invalid'])}</td>"
            f"<td>{_esc(denom['blocked'])}</td>"
            f"<td>{_esc(denom['pruned'])}</td>"
            f"<td>{_esc(denom['preserved'])}</td></tr>"
        )
        denom_html = (
            "<table><thead><tr><th>planned</th><th>complete</th><th>failed</th>"
            "<th>invalid</th><th>blocked</th><th>pruned</th><th>preserved</th>"
            f"</tr></thead><tbody>{denom_cells}</tbody></table>"
        )
    else:
        denom_html = "<p>Denominator not available.</p>"

    oos = view["oos_gate_status"]
    rob = view["robustness_status"]
    review = view["candidate_review_status"]
    status_rows = [
        ("evidence class", view["evidence_class"], None),
        ("replay", view["replay_status"]["state"], view["replay_status"]["reason_code"]),
        ("OOS gate", oos["state"], oos["reason_code"]),
        ("OOS evidence status", oos["oos_evidence_status"], None),
        ("robustness", rob["state"], rob["reason_code"]),
        ("candidate review", review["state"], review["reason_code"]),
        ("reporting", view["reporting_status"]["state"], view["reporting_status"]["reason_code"]),
        ("operator gate", view["operator_gate_status"]["state"], view["operator_gate_status"]["reason_code"]),
    ]
    status_html = "".join(
        f"<tr><td>{_esc(label)}</td>"
        f"<td class='state'>{_esc(value)}</td>"
        f"<td>{_esc(reason or '')}</td></tr>"
        for label, value, reason in status_rows
    )

    rp_html = ""
    if view["result_populations"]:
        rp_rows = "".join(
            f"<tr><td>{_esc(rp['result_population_id'])}</td>"
            f"<td>{_esc(rp['exit_mode'])}</td>"
            f"<td>{_esc(rp['rows'])}</td>"
            f"<td><code>{_esc(rp['sha256'])}</code></td></tr>"
            for rp in view["result_populations"]
        )
        rp_html = (
            "<table><thead><tr><th>Result Population</th><th>exit mode</th>"
            "<th>rows</th><th>sha256</th></tr></thead><tbody>"
            f"{rp_rows}</tbody></table>"
        )

    withheld = ", ".join(rob["withheld_statistics"]) or "none"
    withheld_html = f"<p class='caveat'>Withheld statistics: {_esc(withheld)}.</p>"

    nogo_html = ""
    if view["no_go_caveats"]:
        items = "".join(
            f"<li>{_esc(c)}</li>" for c in view["no_go_caveats"]
        )
        nogo_html = f"<div class='banner'>NO-GO caveats:<ul>{items}</ul></div>"

    drill_rows = "".join(
        f"<tr><td>{_esc(ref['role'])}</td>"
        f"<td><code>{_esc(ref['path'])}</code></td>"
        f"<td>{'present' if ref['present'] else 'missing'}</td></tr>"
        for ref in view["artifact_drilldown"]
    )
    drill_html = (
        "<table><thead><tr><th>role</th><th>path</th><th>present</th></tr>"
        f"</thead><tbody>{drill_rows}</tbody></table>"
    )

    parts.append(
        "<table><thead><tr><th>field</th><th>state</th><th>reason</th></tr>"
        f"</thead><tbody>{status_html}</tbody></table>"
    )
    parts.append("<h4>Denominator (full population)</h4>")
    parts.append(denom_html)
    if rp_html:
        parts.append("<h4>Result Populations</h4>")
        parts.append(rp_html)
    parts.append(withheld_html)
    if nogo_html:
        parts.append(nogo_html)
    parts.append("<h4>Artifact drill-down</h4>")
    parts.append(drill_html)
    return "".join(parts)


def _baseline_proof_panel_html(panel: dict[str, Any]) -> str:
    """Render the baseline proof panel as static HTML."""
    parts: list[str] = []
    parts.append("<h2>Baseline fixture proof (non-promotable, read-only)</h2>")
    parts.append(
        f"<p class='caveat'><em>{_esc(panel['non_authority_note'])}</em></p>"
    )

    # Strategy detail / baseline payloads
    bp = panel["baseline_payloads"]
    parts.append("<h3>Strategy detail &mdash; construction payload catalog</h3>")
    if bp["available"]:
        parts.append(
            f"<p>baseline count: {_esc(bp['baseline_count'])}; "
            f"primitive family: {_esc(bp['selected_primitive_family'])}; "
            f"contract-only route: {_esc(bp['contract_only_route_used'])}</p>"
        )
        rows = "".join(
            f"<tr><td><code>{_esc(b['baseline_id'])}</code></td>"
            f"<td>{_esc(b['label'])}</td>"
            f"<td>{_esc(b['strategy_family'])}</td>"
            f"<td>{_esc(b['non_promotable'])}</td>"
            f"<td>{_esc(b['expected_gate_result'])}</td>"
            f"<td>{_esc(b['expected_crossing_result'])}</td></tr>"
            for b in bp["baselines"]
        )
        parts.append(
            "<table><thead><tr><th>baseline_id</th><th>label</th><th>family</th>"
            "<th>non_promotable</th><th>expected gate</th><th>expected crossing</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>"
        )
    else:
        parts.append("<p><em>Baseline payload catalog: artifact unavailable (blocker).</em></p>")

    # Gate posture (WFO/OOS + MC/robustness + statistical diagnostics)
    ge = panel["gate_expectations"]
    parts.append(
        "<h3>Gate posture &mdash; WFO/OOS, MC/robustness, statistical diagnostics</h3>"
    )
    if ge["available"]:
        gr = ge["global_rule"]
        parts.append(
            f"<p>numeric_override_allowed: {_esc(gr.get('numeric_override_allowed'))}; "
            f"fabricated_metrics_allowed: {_esc(gr.get('fabricated_metrics_allowed'))}; "
            f"dominates_numeric: {_esc(gr.get('construction_payload_or_non_promotable_dominates_numeric_results'))}</p>"
        )
        rows = "".join(
            f"<tr><td><code>{_esc(b['baseline_id'])}</code></td>"
            f"<td>{_esc(b['wfo_oos_gate_expected'])}</td>"
            f"<td>{_esc(b['robustness_mc_gate_expected'])}</td>"
            f"<td>{_esc(b['statistical_diagnostics_gate_expected'])}</td>"
            f"<td>{_esc(b['denominator_integrity_expected'])}</td>"
            f"<td>{_esc(b['crossing_expected'])}</td></tr>"
            for b in ge["per_baseline"]
        )
        parts.append(
            "<table><thead><tr><th>baseline_id</th><th>WFO/OOS expected</th>"
            "<th>MC/robustness</th><th>stat diagnostics</th>"
            "<th>denom integrity</th><th>crossing</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )
    else:
        parts.append("<p><em>Gate expectations: artifact unavailable (blocker).</em></p>")

    # Guard validation
    gv = panel["guard_validation"]
    parts.append("<h3>Non-promotable crossing guard</h3>")
    if gv["available"]:
        parts.append(
            f"<p>guard_implemented: {_esc(gv['guard_implemented'])}; "
            f"hardened: {_esc(gv['non_promotable_crossing_guard_hardened'])}; "
            f"lab_finished: {_esc(gv['lab_declared_finished'])}; "
            f"tests: {_esc(gv['test_result'])} ({_esc(gv['tests_observed'])})</p>"
        )
    else:
        parts.append("<p><em>Guard validation: artifact unavailable (blocker).</em></p>")

    # Agent loop activity
    al = panel["agent_loop_exercise"]
    parts.append("<h3>Agent/baseline loop activity</h3>")
    if al["available"]:
        nc = al["no_candidate_result"]
        cr = al["crossing_rejection"]
        beh = al["agent_loop_behavior"]
        beh_str = "; ".join(f"{k}={v}" for k, v in beh.items())
        parts.append(
            f"<p>fixture_only: {_esc(al['fixture_only'])}; "
            f"baseline: {_esc(al['baseline_id'])}; "
            f"status: {_esc(al['status'])}; "
            f"non_promotable: {_esc(al['non_promotable'])}; "
            f"candidate_eligible: {_esc(al['candidate_eligible'])}; "
            f"canonical_rp_written: {_esc(al['canonical_result_population_written'])}; "
            f"registry_written: {_esc(al['candidate_registry_written'])}</p>"
        )
        parts.append(
            f"<p>no_candidate: status={_esc(nc['status'])}, "
            f"outcome={_esc(nc['review_outcome'])}, "
            f"rows={_esc(nc['completed_rows'])}/{_esc(nc['declared_rows'])}, "
            f"wfo_oos={_esc(nc['wfo_oos_status'])}, "
            f"fabricated={_esc(nc['missing_or_unavailable_metrics_fabricated'])}</p>"
        )
        parts.append(
            f"<p>crossing_rejection: status={_esc(cr['status'])}, "
            f"reason={_esc(cr['reason_code'])}, "
            f"action_authorized={_esc(cr['crossing_action_authorized'])}, "
            f"karl_gated={_esc(cr['first_real_crossing_remains_karl_gated'])}</p>"
        )
        parts.append(f"<p class='caveat'>agent_behavior: {_esc(beh_str)}</p>")
    else:
        parts.append("<p><em>Agent loop result: artifact unavailable (blocker).</em></p>")

    # Provenance trace
    pv = panel["provenance_trace"]
    parts.append("<h3>Data/provenance trace (PR #583-#587)</h3>")
    if pv["available"]:
        prs = ", ".join(f"#{p}" for p in (pv["baseline_sequence_prs"] or []))
        parts.append(
            f"<p>PRs: {_esc(prs)}; "
            f"core_pipe_proven: {_esc(pv['core_pipe_fixture_proven'])}; "
            f"no_candidate_observed: {_esc(pv['no_candidate_result_observed'])}; "
            f"crossing_rejection_observed: {_esc(pv['crossing_rejection_observed'])}</p>"
        )
        parts.append(
            "<div class='banner'>"
            f"NOT proven: real_candidate_crossing={_esc(pv['real_candidate_crossing_completed'])}, "
            f"always_on_factory={_esc(pv['full_always_on_factory_completed'])}, "
            f"lab_finished={_esc(pv['lab_declared_finished_without_qualification'])}; "
            f"edge_search_authorized={_esc(pv['edge_search_authorized_here'])}, "
            f"canonical_writes_authorized={_esc(pv['canonical_writes_authorized_here'])}, "
            f"paper_live_go_gated={_esc(pv['paper_live_runtime_go_gated'])}"
            "</div>"
        )
    else:
        parts.append("<p><em>Provenance trace: artifact unavailable (blocker).</em></p>")

    return "".join(parts)


def _held_boundary_panel_html(panel: dict[str, Any]) -> str:
    """Render the held-boundary / deferred-B panel as static HTML."""
    parts: list[str] = []
    parts.append(
        "<h2>Held-boundary / deferred-B (not authorized in current phase)</h2>"
    )
    parts.append(
        f"<p class='caveat'><em>{_esc(panel['non_authority_note'])}</em></p>"
    )
    if not panel["available"]:
        parts.append("<p><em>Held boundary map: artifact unavailable (blocker).</em></p>")
        return "".join(parts)

    def _ul(items: list[str]) -> str:
        return "<ul>" + "".join(f"<li>{_esc(i)}</li>" for i in items) + "</ul>"

    if panel["held_b_until_real_research_flow"]:
        parts.append("<h3>Held-B until real research flow resumes</h3>")
        parts.append(_ul(panel["held_b_until_real_research_flow"]))

    if panel["requires_real_go_candidate"]:
        parts.append("<h3>Requires first real GO candidate</h3>")
        parts.append(_ul(panel["requires_real_go_candidate"]))

    if panel["go_gated_protected"]:
        parts.append(
            "<h3>GO-gated protected (paper/live/runtime/OMS/exchange)</h3>"
        )
        parts.append(_ul(panel["go_gated_protected"]))

    if panel["current_fork"]:
        parts.append("<h3>Current fork (operator decision point)</h3>")
        parts.append(_ul(panel["current_fork"]))

    return "".join(parts)


def render_html(data: dict[str, Any]) -> str:
    summary = data["denominator_summary"]
    trials = summary["trial_denominator_over_distinct_sets"]
    caveats = "".join(f"<li>{_esc(c)}</li>" for c in data["caveats"])
    subjects = "".join(_subject_html(v) for v in data["subjects"])
    baseline_proof_html = _baseline_proof_panel_html(data["baseline_proof_panel"])
    held_boundary_html = _held_boundary_panel_html(data["held_boundary_panel"])

    return (
        "<!DOCTYPE html>\n"
        "<html lang='en'>\n<head>\n<meta charset='utf-8'>\n"
        "<title>Lab Results Dashboard (read-only)</title>\n"
        f"<style>{_CSS}</style>\n</head>\n<body>\n"
        "<h1>Lab Results Dashboard</h1>\n"
        f"<p>schema <code>{_esc(data['schema_version'])}</code> &mdash; "
        f"{_esc(data['surface_kind'])}</p>\n"
        "<div class='banner'>Read-only operator visibility surface. No "
        "executable controls: no run, approve, promote, retry, scheduler, or "
        "live-fetch.</div>\n"
        f"<div class='banner'>{_esc(data['edge_search_hold'])}</div>\n"
        "<h2>Denominator summary (full population, not winners only)</h2>\n"
        "<table><thead><tr><th>metric</th><th>count</th></tr></thead><tbody>"
        f"<tr><td>subjects</td><td>{_esc(summary['subject_count'])}</td></tr>"
        "<tr><td>completed experiment runs reached</td>"
        f"<td>{_esc(summary['completed_experiment_run_count'])}</td></tr>"
        f"<tr><td>NO-GO</td><td>{_esc(summary['no_go_count'])}</td></tr>"
        f"<tr><td>blocked</td><td>{_esc(summary['blocked_count'])}</td></tr>"
        "<tr><td>candidate ready for human review</td>"
        f"<td>{_esc(summary['candidate_ready_count'])}</td></tr>"
        "<tr><td>operator gate pending</td>"
        f"<td>{_esc(summary['operator_gate_pending_count'])}</td></tr>"
        "</tbody></table>\n"
        "<h2>Subjects by overall state</h2>\n"
        "<table><thead><tr><th>overall state</th><th>count</th></tr></thead>"
        f"<tbody>{_state_table_rows(summary)}</tbody></table>\n"
        "<h2>Trial denominator over "
        f"{_esc(summary['distinct_result_population_sets'])} distinct Result "
        "Population set(s)</h2>\n"
        "<table><thead><tr><th>planned</th><th>complete</th><th>failed</th>"
        "<th>invalid</th><th>blocked</th><th>pruned</th></tr></thead><tbody>"
        f"<tr><td>{_esc(trials['planned'])}</td>"
        f"<td>{_esc(trials['complete'])}</td>"
        f"<td>{_esc(trials['failed'])}</td>"
        f"<td>{_esc(trials['invalid'])}</td>"
        f"<td>{_esc(trials['blocked'])}</td>"
        f"<td>{_esc(trials['pruned'])}</td></tr>"
        "</tbody></table>\n"
        f"<h2>Caveats</h2>\n<ul>{caveats}</ul>\n"
        f"{baseline_proof_html}\n"
        f"{held_boundary_html}\n"
        f"<h2>Subjects</h2>\n{subjects}\n"
        "</body>\n</html>\n"
    )
