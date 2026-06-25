"""Deterministic static renderers for the operator brief / weekly report.

Three renderers emit pure read-only documents — tables and text only, no forms,
no buttons, no ``<script>``, no network fetch, no auto-refresh, and no
recommendation / promotion / decision label. Each output is a deterministic
function of the data model, so two renders are byte-identical.

- ``render_daily_brief_markdown`` — a compact operator daily brief.
- ``render_weekly_report_markdown`` — a fuller weekly research-lab report.
- ``render_weekly_report_html`` — the weekly report as table-based static HTML.
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

_DESCRIPTIVE_BANNER = (
    "Read-only operator surface. Descriptive only: no recommendation, ranking, "
    "promotion/decision label, readiness verdict, edge-search suggestion, "
    "auto-send, notification, or scheduler."
)


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _reason(code: str | None) -> str:
    return f" ({code})" if code else ""


# ---------------------------------------------------------------------------
# Shared markdown fragments.
# ---------------------------------------------------------------------------
def _subject_md_line(line: dict[str, Any]) -> str:
    return (
        f"- `{line['subject_id']}` -- overall `{line['overall_state']}` "
        f"(evidence {line['evidence_class']})"
    )


def _counts_md(data: dict[str, Any]) -> list[str]:
    counts = data["counts"]
    return [
        f"- subjects: {counts['subjects']}",
        f"- completed runs: {counts['completed_runs']}",
        f"- blocked runs: {counts['blocked_runs']}",
        f"- NO-GOs: {counts['no_gos']}",
        f"- open decision surfaces: {counts['open_decision_surfaces']}",
        f"- candidate-review evidence: {counts['candidate_review_evidence']}",
    ]


def _section_md(title: str, lines: list[dict[str, Any]]) -> list[str]:
    out = [f"## {title}", ""]
    if not lines:
        out.append("- none")
    else:
        out.extend(_subject_md_line(line) for line in lines)
    out.append("")
    return out


# ---------------------------------------------------------------------------
# Daily brief (markdown).
# ---------------------------------------------------------------------------
def render_daily_brief_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Lab Operator Daily Brief (read-only)")
    lines.append("")
    lines.append(
        f"_schema: `{data['schema_version']}` -- as of {data['as_of']}_"
    )
    lines.append("")
    lines.append(f"> {_DESCRIPTIVE_BANNER}")
    lines.append("")
    lines.append(f"> {data['edge_search_hold']}")
    lines.append("")

    lines.append("## At a glance")
    lines.append("")
    lines.extend(_counts_md(data))
    lines.append("")

    lines.extend(_section_md("Completed runs", data["completed_runs"]))
    lines.extend(_section_md("Blocked runs", data["blocked_runs"]))
    lines.extend(_section_md("NO-GOs", data["no_gos"]))
    lines.extend(
        _section_md("Open decision surfaces", data["open_decision_surfaces"])
    )

    lines.append("## Validation status")
    lines.append("")
    for v in data["validation_status"]:
        lines.append(
            f"- `{v['subject_id']}` -- replay `{v['replay_state']}`; OOS gate "
            f"`{v['oos_gate_state']}`{_reason(v['oos_gate_reason_code'])} "
            f"(evidence {v['oos_evidence_status']}); robustness "
            f"`{v['robustness_state']}`"
        )
    lines.append("")

    lines.append("## Candidate-review readiness")
    lines.append("")
    lines.append(
        "_Surfaced only when packet evidence exists; never a readiness "
        "verdict or promotion._"
    )
    lines.append("")
    for c in data["candidate_review_readiness"]:
        if c["has_candidate_review_evidence"]:
            lines.append(f"- `{c['subject_id']}` -- {c['detail']}")
    if not any(
        c["has_candidate_review_evidence"]
        for c in data["candidate_review_readiness"]
    ):
        lines.append("- none (no candidate-review packet evidence)")
    lines.append("")

    lines.append("## Withheld statistics and caveats")
    lines.append("")
    withheld = ", ".join(data["withheld_statistics"]) or "none"
    lines.append(f"- withheld statistics: {withheld}")
    for caveat in data["caveats"]:
        lines.append(f"- {caveat}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Weekly report (markdown).
# ---------------------------------------------------------------------------
def render_weekly_report_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Lab Weekly Research Report (read-only)")
    lines.append("")
    lines.append(
        f"_schema: `{data['schema_version']}` -- period {data['period']}_"
    )
    lines.append("")
    lines.append(f"> {_DESCRIPTIVE_BANNER}")
    lines.append("")
    lines.append(f"> {data['edge_search_hold']}")
    lines.append("")

    lines.append("## Summary counts")
    lines.append("")
    lines.extend(_counts_md(data))
    lines.append("")

    lines.append("### Subjects by overall state (full population)")
    lines.append("")
    lines.append("| overall state | count |")
    lines.append("| --- | ---: |")
    for state, count in data["counts"]["by_overall_state"].items():
        lines.append(f"| `{state}` | {count} |")
    lines.append("")
    lines.append(
        f"_Charting {('enabled' if data['charting']['enabled'] else 'deferred')}: "
        f"{data['charting']['note']}_"
    )
    lines.append("")

    lines.extend(_section_md("Completed runs", data["completed_runs"]))
    lines.extend(_section_md("Blocked runs", data["blocked_runs"]))
    lines.extend(_section_md("NO-GOs", data["no_gos"]))
    lines.extend(
        _section_md("Open decision surfaces", data["open_decision_surfaces"])
    )

    lines.append("## Validation status")
    lines.append("")
    lines.append(
        "| subject | replay | OOS gate | OOS evidence | robustness | withheld |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for v in data["validation_status"]:
        withheld = ", ".join(v["withheld_statistics"]) or "none"
        lines.append(
            f"| `{v['subject_id']}` | `{v['replay_state']}` | "
            f"`{v['oos_gate_state']}` | {v['oos_evidence_status']} | "
            f"`{v['robustness_state']}` | {withheld} |"
        )
    lines.append("")

    lines.append("## Candidate-review readiness")
    lines.append("")
    lines.append(
        "_Surfaced only when packet evidence exists; never a readiness "
        "verdict or promotion._"
    )
    lines.append("")
    for c in data["candidate_review_readiness"]:
        flag = "evidence" if c["has_candidate_review_evidence"] else "no evidence"
        lines.append(
            f"- `{c['subject_id']}` [{flag}] -- `{c['candidate_review_state']}`"
            f"{_reason(c['candidate_review_reason_code'])}: {c['detail']}"
        )
    lines.append("")

    lines.append("## NO-GO caveats")
    lines.append("")
    any_caveat = False
    for line in data["no_gos"]:
        if line["no_go_caveats"]:
            any_caveat = True
            lines.append(f"- `{line['subject_id']}`:")
            for caveat in line["no_go_caveats"]:
                lines.append(f"  - {caveat}")
    if not any_caveat:
        lines.append("- none")
    lines.append("")

    lines.append("## Artifact links")
    lines.append("")
    for link in data["artifact_links"]:
        flag = "present" if link["present"] else "missing"
        lines.append(
            f"- `{link['subject_id']}` [{link['role']}] "
            f"`{link['path']}` ({flag})"
        )
    lines.append("")

    lines.append("## Withheld statistics and caveats")
    lines.append("")
    withheld = ", ".join(data["withheld_statistics"]) or "none"
    lines.append(f"- withheld statistics: {withheld}")
    for caveat in data["caveats"]:
        lines.append(f"- {caveat}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Weekly report (static HTML, table-based).
# ---------------------------------------------------------------------------
def _state_rows_html(data: dict[str, Any]) -> str:
    return "".join(
        f"<tr><td class='state'>{_esc(state)}</td><td>{_esc(count)}</td></tr>"
        for state, count in data["counts"]["by_overall_state"].items()
    )


def _subject_rows_html(lines: list[dict[str, Any]]) -> str:
    if not lines:
        return "<tr><td colspan='3'>none</td></tr>"
    return "".join(
        f"<tr><td><code>{_esc(line['subject_id'])}</code></td>"
        f"<td class='state'>{_esc(line['overall_state'])}</td>"
        f"<td>{_esc(line['evidence_class'])}</td></tr>"
        for line in lines
    )


def _subject_table_html(title: str, lines: list[dict[str, Any]]) -> str:
    return (
        f"<h2>{_esc(title)}</h2>\n"
        "<table><thead><tr><th>subject</th><th>overall state</th>"
        "<th>evidence</th></tr></thead><tbody>"
        f"{_subject_rows_html(lines)}</tbody></table>\n"
    )


def render_weekly_report_html(data: dict[str, Any]) -> str:
    counts = data["counts"]
    validation_rows = "".join(
        f"<tr><td><code>{_esc(v['subject_id'])}</code></td>"
        f"<td class='state'>{_esc(v['replay_state'])}</td>"
        f"<td class='state'>{_esc(v['oos_gate_state'])}</td>"
        f"<td>{_esc(v['oos_evidence_status'])}</td>"
        f"<td class='state'>{_esc(v['robustness_state'])}</td>"
        f"<td>{_esc(', '.join(v['withheld_statistics']) or 'none')}</td></tr>"
        for v in data["validation_status"]
    )
    review_rows = "".join(
        f"<tr><td><code>{_esc(c['subject_id'])}</code></td>"
        f"<td>{'evidence' if c['has_candidate_review_evidence'] else 'no evidence'}</td>"
        f"<td class='state'>{_esc(c['candidate_review_state'])}</td>"
        f"<td>{_esc(c['detail'])}</td></tr>"
        for c in data["candidate_review_readiness"]
    )
    artifact_rows = "".join(
        f"<tr><td><code>{_esc(link['subject_id'])}</code></td>"
        f"<td>{_esc(link['role'])}</td>"
        f"<td><code>{_esc(link['path'])}</code></td>"
        f"<td>{'present' if link['present'] else 'missing'}</td></tr>"
        for link in data["artifact_links"]
    )
    caveats = "".join(f"<li>{_esc(c)}</li>" for c in data["caveats"])
    withheld = ", ".join(data["withheld_statistics"]) or "none"

    return (
        "<!DOCTYPE html>\n"
        "<html lang='en'>\n<head>\n<meta charset='utf-8'>\n"
        "<title>Lab Weekly Research Report (read-only)</title>\n"
        f"<style>{_CSS}</style>\n</head>\n<body>\n"
        "<h1>Lab Weekly Research Report</h1>\n"
        f"<p>schema <code>{_esc(data['schema_version'])}</code> &mdash; period "
        f"{_esc(data['period'])}</p>\n"
        f"<div class='banner'>{_esc(_DESCRIPTIVE_BANNER)}</div>\n"
        f"<div class='banner'>{_esc(data['edge_search_hold'])}</div>\n"
        "<h2>Summary counts</h2>\n"
        "<table><thead><tr><th>metric</th><th>count</th></tr></thead><tbody>"
        f"<tr><td>subjects</td><td>{_esc(counts['subjects'])}</td></tr>"
        f"<tr><td>completed runs</td><td>{_esc(counts['completed_runs'])}</td></tr>"
        f"<tr><td>blocked runs</td><td>{_esc(counts['blocked_runs'])}</td></tr>"
        f"<tr><td>NO-GOs</td><td>{_esc(counts['no_gos'])}</td></tr>"
        "<tr><td>open decision surfaces</td>"
        f"<td>{_esc(counts['open_decision_surfaces'])}</td></tr>"
        "<tr><td>candidate-review evidence</td>"
        f"<td>{_esc(counts['candidate_review_evidence'])}</td></tr>"
        "</tbody></table>\n"
        "<h2>Subjects by overall state (full population)</h2>\n"
        "<table><thead><tr><th>overall state</th><th>count</th></tr></thead>"
        f"<tbody>{_state_rows_html(data)}</tbody></table>\n"
        f"<p class='caveat'>Charting "
        f"{'enabled' if data['charting']['enabled'] else 'deferred'}: "
        f"{_esc(data['charting']['note'])}</p>\n"
        + _subject_table_html("Completed runs", data["completed_runs"])
        + _subject_table_html("Blocked runs", data["blocked_runs"])
        + _subject_table_html("NO-GOs", data["no_gos"])
        + _subject_table_html(
            "Open decision surfaces", data["open_decision_surfaces"]
        )
        + "<h2>Validation status</h2>\n"
        "<table><thead><tr><th>subject</th><th>replay</th><th>OOS gate</th>"
        "<th>OOS evidence</th><th>robustness</th><th>withheld</th></tr></thead>"
        f"<tbody>{validation_rows}</tbody></table>\n"
        "<h2>Candidate-review readiness</h2>\n"
        "<p class='caveat'>Surfaced only when packet evidence exists; never a "
        "readiness verdict or promotion.</p>\n"
        "<table><thead><tr><th>subject</th><th>evidence</th><th>state</th>"
        "<th>detail</th></tr></thead>"
        f"<tbody>{review_rows}</tbody></table>\n"
        "<h2>Artifact links</h2>\n"
        "<table><thead><tr><th>subject</th><th>role</th><th>path</th>"
        "<th>present</th></tr></thead>"
        f"<tbody>{artifact_rows}</tbody></table>\n"
        f"<h2>Withheld statistics and caveats</h2>\n"
        f"<p>Withheld statistics: {_esc(withheld)}.</p>\n<ul>{caveats}</ul>\n"
        "</body>\n</html>\n"
    )
