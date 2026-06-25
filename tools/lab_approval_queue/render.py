"""Deterministic static renderers for the lab approval / gate queue.

Both renderers emit a pure read-only document: tables and text only, no forms,
no buttons, no ``<script>``, no network fetch, no auto-refresh. Output is a
deterministic function of the data model, so two renders are byte-identical.
A queue surface is especially load-bearing here: it must never render an
approve / reject / promote control.
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
    lines.append("# Lab Approval / Gate Queue (read-only)")
    lines.append("")
    lines.append(f"_schema: `{data['schema_version']}` -- {data['surface_kind']}_")
    lines.append("")
    lines.append(
        "> Read-only operator gate queue. It displays pending human gates and "
        "blockers; it does not execute them. No approve, reject, promote, run, "
        "or notification control."
    )
    lines.append("")
    lines.append(f"> {data['edge_search_hold']}")
    lines.append("")

    summary = data["queue_summary"]
    lines.append("## Queue summary")
    lines.append("")
    lines.append(f"- subjects: {summary['subject_count']}")
    lines.append(
        f"- operator gate pending (human decision): "
        f"{summary['operator_gate_pending_count']}"
    )
    lines.append(f"- blocked validation: {summary['blocked_validation_count']}")
    lines.append(f"- NO-GO: {summary['no_go_count']}")
    lines.append(
        f"- candidate-review packets created (evidence-backed): "
        f"{summary['candidate_review_packet_created_count']}"
    )
    lines.append("")
    lines.append(f"> {summary['honest_state_note']}")
    lines.append("")
    lines.append("### Entries by queue status")
    lines.append("")
    lines.append("| queue status | count |")
    lines.append("| --- | ---: |")
    for status, count in summary["by_queue_status"].items():
        lines.append(f"| `{status}` | {count} |")
    lines.append("")

    lines.append("## Caveats")
    lines.append("")
    for caveat in data["caveats"]:
        lines.append(f"- {caveat}")
    lines.append("")

    lines.append("## Queue entries")
    lines.append("")
    for entry in data["entries"]:
        lines.append(
            f"### {entry['subject_id']} -- `{entry['queue_status']}`"
        )
        lines.append("")
        lines.append(f"- label: {entry['subject_label']}")
        lines.append(f"- overall state: `{entry['overall_state']}`")
        lines.append(
            f"- actionable by operator: {entry['actionable_by_operator']}"
        )
        gate = entry["operator_gate"]
        lines.append(
            f"- operator gate: `{gate['state']}` ({gate['reason_code']})"
        )
        lines.append(
            f"- candidate-review packet created: "
            f"{entry['candidate_review_packet_created']}"
        )
        no_packet = entry["no_candidate_review_packet_reason"]
        if no_packet:
            lines.append(
                f"- no candidate-review packet reason: `{no_packet['code']}` "
                f"-- {no_packet['detail']}"
            )
        blocked_review = entry["blocked_review_reason"]
        if blocked_review:
            lines.append(
                f"- blocked review reason: `{blocked_review['code']}` "
                f"-- {blocked_review['detail']}"
            )
        if entry["human_decision"]:
            hd = entry["human_decision"]
            lines.append(
                f"- human decision pending: `{hd['decision_kind']}` "
                f"(executable here: {hd['executable_here']}; owner: {hd['owner']})"
            )
        if entry["blockers"]:
            lines.append("- blockers:")
            for blk in entry["blockers"]:
                lines.append(
                    f"  - `{blk['blocker_kind']}` @ {blk['stage']}: "
                    f"`{blk['state']}` ({blk['reason_code']}) -- {blk['detail']}"
                )
        else:
            lines.append("- blockers: none")
        lines.append("- artifact references:")
        for ref in entry["artifact_refs"]:
            flag = "present" if ref["present"] else "missing"
            lines.append(f"  - `{ref['path']}` [{ref['role']}] ({flag})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Static HTML renderer.
# ---------------------------------------------------------------------------
def _status_table_rows(summary: dict[str, Any]) -> str:
    rows = []
    for status, count in summary["by_queue_status"].items():
        rows.append(
            f"<tr><td class='state'>{_esc(status)}</td>"
            f"<td>{_esc(count)}</td></tr>"
        )
    return "".join(rows)


def _entry_html(entry: dict[str, Any]) -> str:
    parts: list[str] = []
    parts.append(
        f"<h3>{_esc(entry['subject_id'])} "
        f"&mdash; <span class='state'>{_esc(entry['queue_status'])}</span></h3>"
    )

    gate = entry["operator_gate"]
    no_packet = entry["no_candidate_review_packet_reason"]
    blocked_review = entry["blocked_review_reason"]
    status_rows = [
        ("label", entry["subject_label"], None),
        ("overall state", entry["overall_state"], None),
        ("actionable by operator", entry["actionable_by_operator"], None),
        ("operator gate", gate["state"], gate["reason_code"]),
        (
            "candidate-review packet created",
            entry["candidate_review_packet_created"],
            None,
        ),
        (
            "no candidate-review packet reason",
            no_packet["code"] if no_packet else "",
            no_packet["detail"] if no_packet else None,
        ),
        (
            "blocked review reason",
            blocked_review["code"] if blocked_review else "",
            blocked_review["detail"] if blocked_review else None,
        ),
    ]
    status_html = "".join(
        f"<tr><td>{_esc(label)}</td>"
        f"<td class='state'>{_esc(value)}</td>"
        f"<td>{_esc(reason or '')}</td></tr>"
        for label, value, reason in status_rows
    )
    parts.append(
        "<table><thead><tr><th>field</th><th>value</th><th>detail</th></tr>"
        f"</thead><tbody>{status_html}</tbody></table>"
    )

    if entry["human_decision"]:
        hd = entry["human_decision"]
        parts.append(
            "<div class='banner'>Human decision pending: "
            f"<code>{_esc(hd['decision_kind'])}</code>. Executable here: "
            f"{_esc(hd['executable_here'])}. Owner: {_esc(hd['owner'])}.</div>"
        )

    if entry["blockers"]:
        blk_rows = "".join(
            f"<tr><td>{_esc(blk['blocker_kind'])}</td>"
            f"<td>{_esc(blk['stage'])}</td>"
            f"<td class='state'>{_esc(blk['state'])}</td>"
            f"<td>{_esc(blk['reason_code'])}</td>"
            f"<td>{_esc(blk['detail'])}</td></tr>"
            for blk in entry["blockers"]
        )
        parts.append("<h4>Blockers</h4>")
        parts.append(
            "<table><thead><tr><th>kind</th><th>stage</th><th>state</th>"
            "<th>reason</th><th>detail</th></tr></thead><tbody>"
            f"{blk_rows}</tbody></table>"
        )
    else:
        parts.append("<p class='caveat'>Blockers: none.</p>")

    drill_rows = "".join(
        f"<tr><td>{_esc(ref['role'])}</td>"
        f"<td><code>{_esc(ref['path'])}</code></td>"
        f"<td>{'present' if ref['present'] else 'missing'}</td></tr>"
        for ref in entry["artifact_refs"]
    )
    parts.append("<h4>Artifact references</h4>")
    parts.append(
        "<table><thead><tr><th>role</th><th>path</th><th>present</th></tr>"
        f"</thead><tbody>{drill_rows}</tbody></table>"
    )
    return "".join(parts)


def render_html(data: dict[str, Any]) -> str:
    summary = data["queue_summary"]
    caveats = "".join(f"<li>{_esc(c)}</li>" for c in data["caveats"])
    entries = "".join(_entry_html(e) for e in data["entries"])

    return (
        "<!DOCTYPE html>\n"
        "<html lang='en'>\n<head>\n<meta charset='utf-8'>\n"
        "<title>Lab Approval / Gate Queue (read-only)</title>\n"
        f"<style>{_CSS}</style>\n</head>\n<body>\n"
        "<h1>Lab Approval / Gate Queue</h1>\n"
        f"<p>schema <code>{_esc(data['schema_version'])}</code> &mdash; "
        f"{_esc(data['surface_kind'])}</p>\n"
        "<div class='banner'>Read-only operator gate queue. It displays pending "
        "human gates and blockers; it does not execute them. No approve, reject, "
        "promote, run, or notification control.</div>\n"
        f"<div class='banner'>{_esc(data['edge_search_hold'])}</div>\n"
        "<h2>Queue summary</h2>\n"
        "<table><thead><tr><th>metric</th><th>count</th></tr></thead><tbody>"
        f"<tr><td>subjects</td><td>{_esc(summary['subject_count'])}</td></tr>"
        "<tr><td>operator gate pending (human decision)</td>"
        f"<td>{_esc(summary['operator_gate_pending_count'])}</td></tr>"
        "<tr><td>blocked validation</td>"
        f"<td>{_esc(summary['blocked_validation_count'])}</td></tr>"
        f"<tr><td>NO-GO</td><td>{_esc(summary['no_go_count'])}</td></tr>"
        "<tr><td>candidate-review packets created (evidence-backed)</td>"
        f"<td>{_esc(summary['candidate_review_packet_created_count'])}</td></tr>"
        "</tbody></table>\n"
        f"<div class='banner'>{_esc(summary['honest_state_note'])}</div>\n"
        "<h2>Entries by queue status</h2>\n"
        "<table><thead><tr><th>queue status</th><th>count</th></tr></thead>"
        f"<tbody>{_status_table_rows(summary)}</tbody></table>\n"
        f"<h2>Caveats</h2>\n<ul>{caveats}</ul>\n"
        f"<h2>Queue entries</h2>\n{entries}\n"
        "</body>\n</html>\n"
    )
