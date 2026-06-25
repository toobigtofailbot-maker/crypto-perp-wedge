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


def render_html(data: dict[str, Any]) -> str:
    summary = data["denominator_summary"]
    trials = summary["trial_denominator_over_distinct_sets"]
    caveats = "".join(f"<li>{_esc(c)}</li>" for c in data["caveats"])
    subjects = "".join(_subject_html(v) for v in data["subjects"])

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
        f"<h2>Subjects</h2>\n{subjects}\n"
        "</body>\n</html>\n"
    )
